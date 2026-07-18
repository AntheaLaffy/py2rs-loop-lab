#!/usr/bin/env python3
"""Collect bounded crates.io and Cargo dependency evidence for py2rs."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import tomllib
from typing import Any


PROXY_ENV_KEYS = (
    "CARGO_HTTP_PROXY",
    "HTTP_PROXY",
    "HTTPS_PROXY",
    "ALL_PROXY",
    "http_proxy",
    "https_proxy",
    "all_proxy",
)
SEARCH_LINE = re.compile(
    r'^([A-Za-z0-9_-]+)\s*=\s*"([^"]+)"(?:\s*#\s*(.*))?$'
)
CRATE_SPEC = re.compile(r"^([A-Za-z0-9_-]+)(?:@([^@\s]+))?$")
URL_CREDENTIALS = re.compile(r"(https?://)([^/@\s:]+):([^/@\s]+)@", re.I)
TOKEN_ASSIGNMENT = re.compile(
    r"(?i)(token|password|secret|api[_-]?key)(\s*[=:]\s*)([^\s]+)"
)


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def sanitize(text: str) -> str:
    text = URL_CREDENTIALS.sub(r"\1<redacted>@", text)
    return TOKEN_ASSIGNMENT.sub(r"\1\2<redacted>", text)


def configured_proxy(explicit: str | None) -> str | None:
    if explicit:
        return explicit
    if os.environ.get("PY2RS_CRATES_PROXY"):
        return os.environ["PY2RS_CRATES_PROXY"]
    for key in PROXY_ENV_KEYS:
        if os.environ.get(key):
            return os.environ[key]
    return None


def command_env(mode: str, proxy: str | None) -> dict[str, str]:
    env = os.environ.copy()
    for key in PROXY_ENV_KEYS:
        env.pop(key, None)
    env["CARGO_NET_RETRY"] = "1"
    env["CARGO_HTTP_TIMEOUT"] = "20"
    if mode == "proxy" and proxy:
        env["CARGO_HTTP_PROXY"] = proxy
        env["HTTP_PROXY"] = proxy
        env["HTTPS_PROXY"] = proxy
        env["ALL_PROXY"] = proxy
    return env


def run_once(
    command: list[str], cwd: Path, mode: str, proxy: str | None, timeout: int
) -> dict[str, Any]:
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            env=command_env(mode, proxy),
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
        return {
            "mode": mode,
            "command": command,
            "returncode": result.returncode,
            "stdout": sanitize(result.stdout),
            "stderr": sanitize(result.stderr),
        }
    except FileNotFoundError as error:
        return {
            "mode": mode,
            "command": command,
            "returncode": 127,
            "stdout": "",
            "stderr": sanitize(str(error)),
        }
    except subprocess.TimeoutExpired as error:
        return {
            "mode": mode,
            "command": command,
            "returncode": 124,
            "stdout": sanitize(error.stdout or ""),
            "stderr": sanitize(error.stderr or "Command timed out."),
        }


def run_with_fallback(
    command: list[str],
    cwd: Path,
    proxy: str | None,
    *,
    offline_command: list[str] | None = None,
    timeout: int = 120,
) -> dict[str, Any]:
    attempts = [run_once(command, cwd, "direct", None, timeout)]
    if attempts[-1]["returncode"] == 0:
        return {"mode": "direct", "attempts": attempts, "result": attempts[-1]}

    if proxy:
        attempts.append(run_once(command, cwd, "proxy", proxy, timeout))
        if attempts[-1]["returncode"] == 0:
            return {"mode": "proxy", "attempts": attempts, "result": attempts[-1]}

    if offline_command:
        attempts.append(run_once(offline_command, cwd, "offline", None, timeout))
        if attempts[-1]["returncode"] == 0:
            return {"mode": "offline", "attempts": attempts, "result": attempts[-1]}

    return {"mode": "blocked", "attempts": attempts, "result": attempts[-1]}


def write_attempts(path: Path, execution: dict[str, Any]) -> None:
    chunks = []
    for attempt in execution["attempts"]:
        command = " ".join(attempt["command"])
        chunks.append(
            f"## {attempt['mode']} (exit {attempt['returncode']})\n"
            f"$ {command}\n\n"
            f"{attempt['stdout']}\n{attempt['stderr']}".rstrip()
        )
    path.write_text("\n\n".join(chunks) + "\n", encoding="utf-8")


def parse_search_output(output: str) -> list[dict[str, str]]:
    results = []
    for line in output.splitlines():
        match = SEARCH_LINE.match(line.strip())
        if not match:
            continue
        name, version, description = match.groups()
        results.append(
            {
                "crate": name,
                "version": version,
                "description": description or "",
                "source": "crates.io",
            }
        )
    return results


def merge_query_results(
    query_results: list[tuple[str, list[dict[str, str]]]]
) -> list[dict[str, Any]]:
    merged: dict[str, dict[str, Any]] = {}
    for query, results in query_results:
        for result in results:
            name = result["crate"]
            if name not in merged:
                merged[name] = {**result, "matched_queries": []}
            if query not in merged[name]["matched_queries"]:
                merged[name]["matched_queries"].append(query)
    return list(merged.values())


def named_candidate_records(candidates: list[str]) -> list[dict[str, str]]:
    return [
        {"crate": crate, "status": "required_inspection"}
        for crate in sorted(set(candidates))
    ]


def cargo_home() -> Path:
    return Path(os.environ.get("CARGO_HOME", Path.home() / ".cargo"))


def search_local_cache(capability: str, limit: int) -> list[dict[str, str]]:
    tokens = {token for token in re.findall(r"[a-z0-9]+", capability.lower()) if len(token) > 2}
    scored: list[tuple[int, str, dict[str, str]]] = []
    source_root = cargo_home() / "registry" / "src"
    if not source_root.exists():
        return []

    for manifest in source_root.glob("*/*/Cargo.toml"):
        try:
            package = tomllib.loads(manifest.read_text(encoding="utf-8"))["package"]
        except (OSError, KeyError, tomllib.TOMLDecodeError, UnicodeDecodeError):
            continue
        name = str(package.get("name", ""))
        description = str(package.get("description", ""))
        keywords = " ".join(str(item) for item in package.get("keywords", []))
        haystack = f"{name} {description} {keywords}".lower()
        score = sum(1 for token in tokens if token in haystack)
        if score == 0:
            continue
        result = {
            "crate": name,
            "version": str(package.get("version", "unknown")),
            "description": description,
            "source": "cargo-cache",
        }
        scored.append((score, name, result))

    scored.sort(key=lambda item: (-item[0], item[1]))
    return [item[2] for item in scored[:limit]]


def parse_crate_spec(spec: str) -> tuple[str, str | None]:
    match = CRATE_SPEC.match(spec)
    if not match:
        raise ValueError(f"Invalid crate spec: {spec}")
    return match.group(1), match.group(2)


def parse_info_version(output: str) -> str | None:
    for line in output.splitlines():
        match = re.match(r"^version:\s*(\S+)", line.strip())
        if match:
            return match.group(1)
    return None


def probe_manifest(
    crate: str, version: str, features: list[str], no_default_features: bool
) -> str:
    parts = [f'version = "={version}"']
    if no_default_features:
        parts.append("default-features = false")
    if features:
        rendered = ", ".join(json.dumps(feature) for feature in features)
        parts.append(f"features = [{rendered}]")
    dependency = ", ".join(parts)
    return (
        "[package]\n"
        'name = "py2rs-crate-recon-probe"\n'
        'version = "0.0.0"\n'
        'edition = "2021"\n\n'
        "[dependencies]\n"
        f"{json.dumps(crate)} = {{ {dependency} }}\n"
    )


def write_probe_workspace(
    workspace: Path,
    crate: str,
    version: str,
    features: list[str],
    no_default_features: bool,
) -> None:
    (workspace / "src").mkdir(parents=True, exist_ok=True)
    (workspace / "src" / "lib.rs").write_text("", encoding="utf-8")
    (workspace / "Cargo.toml").write_text(
        probe_manifest(crate, version, features, no_default_features),
        encoding="utf-8",
    )


def summarize_metadata(metadata: dict[str, Any], crate: str, version: str) -> dict[str, Any]:
    packages = {package["id"]: package for package in metadata.get("packages", [])}
    nodes = {
        node["id"]: node
        for node in (metadata.get("resolve") or {}).get("nodes", [])
    }
    candidate_id = next(
        (
            package_id
            for package_id, package in packages.items()
            if package.get("name") == crate and package.get("version") == version
        ),
        None,
    )
    if not candidate_id:
        return {"candidate_id": None, "packages": [], "edges": [], "paths": {}}

    queue = [candidate_id]
    paths: dict[str, list[str]] = {candidate_id: [crate]}
    visited: list[str] = []
    edges: list[dict[str, str]] = []
    while queue:
        package_id = queue.pop(0)
        if package_id in visited:
            continue
        visited.append(package_id)
        for dependency in nodes.get(package_id, {}).get("deps", []):
            dependency_id = dependency["pkg"]
            dependency_name = packages.get(dependency_id, {}).get("name", dependency["name"])
            edges.append(
                {
                    "from": packages[package_id]["name"],
                    "to": dependency_name,
                }
            )
            if dependency_id not in paths:
                paths[dependency_id] = paths[package_id] + [dependency_name]
            if dependency_id not in visited:
                queue.append(dependency_id)

    summaries = []
    rendered_paths: dict[str, list[str]] = {}
    for package_id in visited:
        package = packages[package_id]
        node = nodes.get(package_id, {})
        key = f"{package['name']}@{package['version']}"
        rendered_paths[key] = paths[package_id]
        summaries.append(
            {
                "crate": package["name"],
                "version": package["version"],
                "license": package.get("license"),
                "rust_version": package.get("rust_version"),
                "source": package.get("source"),
                "features": node.get("features", []),
            }
        )
    return {
        "candidate_id": candidate_id,
        "packages": summaries,
        "edges": edges,
        "paths": rendered_paths,
    }


def search_command(args: argparse.Namespace) -> int:
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    proxy = configured_proxy(args.proxy)
    queries = args.query or [args.capability]
    collected: list[tuple[str, list[dict[str, str]]]] = []
    query_records = []
    for index, query in enumerate(queries, start=1):
        command = [
            "cargo",
            "search",
            query,
            "--limit",
            str(args.limit),
            "--registry",
            "crates-io",
        ]
        execution = run_with_fallback(command, Path.cwd(), proxy, timeout=60)
        write_attempts(output / f"cargo-search-{index}.txt", execution)
        if execution["mode"] != "blocked":
            results = parse_search_output(execution["result"]["stdout"])
            query_status = "complete"
        else:
            results = search_local_cache(query, args.limit)
            query_status = "local_only" if results else "blocked"
        collected.append((query, results))
        query_records.append(
            {
                "query": query,
                "status": query_status,
                "transport": execution["mode"] if query_status != "local_only" else "cargo-cache",
                "result_count": len(results),
            }
        )

    results = merge_query_results(collected)
    registry_complete = sum(1 for item in query_records if item["status"] == "complete")
    if registry_complete == len(query_records):
        status = "complete"
    elif registry_complete:
        status = "partial"
    elif results:
        status = "local_only"
    else:
        status = "blocked"
    record = {
        "schema_version": 1,
        "generated_at": utc_now(),
        "command": "search",
        "status": status,
        "capability": args.capability,
        "limit": args.limit,
        "proxy_configured": bool(proxy),
        "queries": query_records,
        "registry_results": results,
        "named_candidates": named_candidate_records(args.candidate),
    }
    (output / "search.json").write_text(
        json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return 0 if status != "blocked" else 2


def inspect_command(args: argparse.Namespace) -> int:
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    proxy = configured_proxy(args.proxy)
    crate, requested_version = parse_crate_spec(args.crate)
    with tempfile.TemporaryDirectory(prefix="py2rs-crate-recon-") as temporary:
        workspace = Path(temporary)
        info_command = ["cargo", "info", args.crate, "--registry", "crates-io"]
        info_offline = info_command + ["--offline"]
        info = run_with_fallback(
            info_command,
            workspace,
            proxy,
            offline_command=info_offline,
            timeout=90,
        )
        write_attempts(output / "cargo-info.txt", info)
        selected_version = requested_version or parse_info_version(info["result"]["stdout"])
        if info["mode"] == "blocked" or not selected_version:
            record = {
                "schema_version": 1,
                "generated_at": utc_now(),
                "command": "inspect",
                "status": "blocked",
                "crate": crate,
                "requested_version": requested_version,
                "reason": "cargo info did not provide a usable crate version",
                "proxy_configured": bool(proxy),
            }
            (output / "inspect.json").write_text(
                json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8"
            )
            return 2

        features = [item for item in args.features.split(",") if item] if args.features else []
        write_probe_workspace(
            workspace,
            crate,
            selected_version,
            features,
            args.no_default_features,
        )
        metadata_command = [
            "cargo",
            "metadata",
            "--format-version",
            "1",
            "--manifest-path",
            str(workspace / "Cargo.toml"),
        ]
        metadata = run_with_fallback(
            metadata_command,
            workspace,
            proxy,
            offline_command=metadata_command + ["--offline"],
            timeout=180,
        )
        write_attempts(output / "cargo-metadata-attempts.txt", metadata)

        metadata_value: dict[str, Any] | None = None
        if metadata["mode"] != "blocked":
            try:
                metadata_value = json.loads(metadata["result"]["stdout"])
            except json.JSONDecodeError:
                metadata_value = None
        if metadata_value is not None:
            (output / "cargo-metadata.json").write_text(
                json.dumps(metadata_value, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )

        tree_command = [
            "cargo",
            "tree",
            "--manifest-path",
            str(workspace / "Cargo.toml"),
            "--locked",
            "-e",
            "features",
        ]
        tree = run_with_fallback(
            tree_command,
            workspace,
            proxy,
            offline_command=tree_command + ["--offline"],
            timeout=120,
        )
        write_attempts(output / "cargo-tree.txt", tree)

        complete = metadata_value is not None and tree["mode"] != "blocked"
        graph = summarize_metadata(metadata_value, crate, selected_version) if metadata_value else {}
        record = {
            "schema_version": 1,
            "generated_at": utc_now(),
            "command": "inspect",
            "status": "complete" if complete else "blocked",
            "crate": crate,
            "version": selected_version,
            "requested_features": features,
            "default_features": not args.no_default_features,
            "proxy_configured": bool(proxy),
            "transport": {
                "cargo_info": info["mode"],
                "cargo_metadata": metadata["mode"],
                "cargo_tree": tree["mode"],
            },
            "graph": graph,
        }
        (output / "inspect.json").write_text(
            json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        return 0 if complete else 2


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    subparsers = root.add_subparsers(dest="subcommand", required=True)

    search = subparsers.add_parser("search", help="Search crates.io for one capability")
    search.add_argument("--capability", required=True)
    search.add_argument("--query", action="append", default=[])
    search.add_argument("--candidate", action="append", default=[])
    search.add_argument("--limit", type=int, default=3)
    search.add_argument("--proxy")
    search.add_argument("--output", required=True)
    search.set_defaults(handler=search_command)

    inspect = subparsers.add_parser("inspect", help="Inspect one crate and feature graph")
    inspect.add_argument("--crate", required=True)
    inspect.add_argument("--features", default="")
    inspect.add_argument("--no-default-features", action="store_true")
    inspect.add_argument("--proxy")
    inspect.add_argument("--output", required=True)
    inspect.set_defaults(handler=inspect_command)
    return root


def main() -> int:
    args = parser().parse_args()
    if getattr(args, "limit", 1) < 1:
        raise SystemExit("--limit must be positive")
    try:
        return args.handler(args)
    except ValueError as error:
        print(error, file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
