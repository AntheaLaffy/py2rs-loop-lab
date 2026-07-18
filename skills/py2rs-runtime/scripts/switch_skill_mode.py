#!/usr/bin/env python3
"""Safely switch one project skill role between prompt and scaffold modes."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import sys
from typing import Any


ROLE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
MODES = ("prompt", "scaffold")
VARIANT_FILE = ".py2rs-skill-variant.json"


def is_within(path: Path, root: Path) -> bool:
    path = path.resolve()
    root = root.resolve()
    return path == root or path.is_relative_to(root)


def read_skill_name(skill: Path) -> str:
    lines = (skill / "SKILL.md").read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError(f"Skill has no YAML frontmatter: {skill}")
    for line in lines[1:]:
        if line.strip() == "---":
            break
        match = re.match(r"^name:\s*['\"]?([^'\"\s]+)['\"]?\s*$", line)
        if match:
            return match.group(1)
    raise ValueError(f"Skill frontmatter has no simple name field: {skill}")


def load_variant(skill: Path) -> dict[str, Any]:
    marker = skill / VARIANT_FILE
    try:
        value = json.loads(marker.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise ValueError(f"Skill variant marker is missing: {marker}") from error
    except json.JSONDecodeError as error:
        raise ValueError(f"Skill variant marker is invalid JSON: {marker}") from error
    if value.get("schema_version") != 1:
        raise ValueError(f"Unsupported skill variant marker schema: {marker}")
    return value


def read_variant(skill: Path, role: str, mode: str) -> dict[str, Any]:
    marker = skill / VARIANT_FILE
    value = load_variant(skill)
    if value.get("role") != role or value.get("mode") != mode:
        raise ValueError(
            f"Skill variant marker does not match role={role}, mode={mode}: {marker}"
        )
    evidence = value.get("validation_evidence")
    if value.get("validated") is not True or not isinstance(evidence, str) or not evidence:
        raise ValueError(f"Skill variant has no validation evidence: {marker}")
    evidence_path = (skill / evidence).resolve()
    if (
        not is_within(evidence_path, skill)
        or not evidence_path.is_file()
        or evidence_path in {(skill / "SKILL.md").resolve(), marker.resolve()}
    ):
        raise ValueError(f"Skill variant validation evidence is missing: {evidence_path}")
    return value


def matching_skills(
    discovery_roots: list[Path], skill_name: str, role: str
) -> list[Path]:
    matches: list[Path] = []
    seen: set[str] = set()
    for root in discovery_roots:
        for current, directories, files in os.walk(root, followlinks=False):
            candidates = []
            current_path = Path(current)
            if "SKILL.md" in files:
                candidates.append(current_path)
            for directory in directories:
                linked = current_path / directory
                if linked.is_symlink() and (linked / "SKILL.md").is_file():
                    candidates.append(linked)
            for candidate in candidates:
                try:
                    candidate_name = read_skill_name(candidate)
                except (OSError, UnicodeDecodeError, ValueError):
                    continue
                try:
                    candidate_role = load_variant(candidate).get("role")
                except (OSError, UnicodeDecodeError, ValueError):
                    candidate_role = None
                absolute = str(candidate.absolute())
                if (
                    candidate_name == skill_name or candidate_role == role
                ) and absolute not in seen:
                    seen.add(absolute)
                    matches.append(candidate.absolute())
    return matches


def build_plan(
    *,
    role: str,
    current_mode: str,
    target_mode: str,
    active: Path,
    archive_root: Path,
    discovery_roots: list[Path],
) -> dict[str, Any]:
    if not ROLE.match(role):
        raise ValueError("--role must use lowercase letters, digits, and hyphens")
    discovery_roots = [root.resolve() for root in discovery_roots]
    active = active.resolve()
    archive_root = archive_root.resolve()
    if not discovery_roots:
        raise ValueError("At least one --discovery-root is required")
    if not any(is_within(active, root) and active != root for root in discovery_roots):
        raise ValueError("Active skill must be a strict child of a discovery root")
    if any(is_within(archive_root, root) for root in discovery_roots):
        raise ValueError("Archive root must be outside every discovery root")
    if not (active / "SKILL.md").is_file():
        raise ValueError("Active skill is missing SKILL.md")
    read_variant(active, role, current_mode)
    skill_name = read_skill_name(active)
    duplicates = [
        path
        for path in matching_skills(discovery_roots, skill_name, role)
        if path != active.absolute()
    ]
    if duplicates:
        rendered = ", ".join(str(path) for path in duplicates)
        raise ValueError(f"Duplicate discoverable skill variants found: {rendered}")

    pending_journal = archive_root / role / ".switch-journal.json"
    if pending_journal.exists():
        raise ValueError(
            f"Pending switch journal must be recovered or acknowledged: {pending_journal}"
        )

    if current_mode == target_mode:
        inactive_mode = next(mode for mode in MODES if mode != current_mode)
        inactive = archive_root / role / inactive_mode
        if not (inactive / "SKILL.md").is_file():
            raise ValueError(f"Inactive mode is missing SKILL.md: {inactive}")
        read_variant(inactive, role, inactive_mode)
        if read_skill_name(inactive) != skill_name:
            raise ValueError("Active and archived variants must use the same skill name")
        return {
            "status": "already_active",
            "role": role,
            "mode": target_mode,
            "skill_name": skill_name,
            "active": str(active),
            "archived_inactive": str(inactive),
        }

    role_archive = archive_root / role
    current_archive = role_archive / current_mode
    target_archive = role_archive / target_mode
    if current_archive.exists():
        raise ValueError(f"Refusing to overwrite existing archive: {current_archive}")
    if not (target_archive / "SKILL.md").is_file():
        raise ValueError(f"Target mode is missing SKILL.md: {target_archive}")
    read_variant(target_archive, role, target_mode)
    if read_skill_name(target_archive) != skill_name:
        raise ValueError("Active and archived variants must use the same skill name")
    devices = {active.stat().st_dev, target_archive.stat().st_dev, role_archive.stat().st_dev}
    if len(devices) != 1:
        raise ValueError("Active and archived variants must be on the same filesystem")

    return {
        "status": "ready",
        "role": role,
        "current_mode": current_mode,
        "target_mode": target_mode,
        "skill_name": skill_name,
        "active": str(active),
        "archive_current_to": str(current_archive),
        "activate_from": str(target_archive),
        "archive_root": str(archive_root),
        "notes_update": {
            "mode": target_mode,
            "active": notes_path(active),
            "archived": notes_path(current_archive),
        },
    }


def notes_path(path: Path) -> str:
    project = Path.cwd().resolve()
    try:
        return str(path.relative_to(project))
    except ValueError:
        return str(path)


def apply_plan(plan: dict[str, Any]) -> dict[str, Any]:
    if plan["status"] == "already_active":
        return plan
    active = Path(plan["active"])
    current_archive = Path(plan["archive_current_to"])
    target_archive = Path(plan["activate_from"])
    role_archive = current_archive.parent
    lock = role_archive / ".switch.lock"
    journal = role_archive / ".switch-journal.json"
    role_archive.mkdir(parents=True, exist_ok=True)
    if journal.exists():
        raise RuntimeError(f"Pending switch journal must be handled first: {journal}")
    lock_owned = False
    try:
        try:
            descriptor = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        except FileExistsError as error:
            raise RuntimeError(
                f"Another switch or interrupted recovery owns: {lock}"
            ) from error
        lock_owned = True
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(str(os.getpid()))
        if journal.exists():
            raise RuntimeError(f"Pending switch journal must be handled first: {journal}")
        read_variant(active, plan["role"], plan["current_mode"])
        read_variant(target_archive, plan["role"], plan["target_mode"])
        if current_archive.exists():
            raise RuntimeError(f"Archive destination appeared during switch: {current_archive}")
        journal.write_text(
            json.dumps({**plan, "phase": "prepared"}, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        active.rename(current_archive)
        journal.write_text(
            json.dumps({**plan, "phase": "current_archived"}, indent=2, sort_keys=True)
            + "\n",
            encoding="utf-8",
        )
        target_archive.rename(active)
        journal.write_text(
            json.dumps(
                {**plan, "phase": "switched_pending_notes"},
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
        return {
            **plan,
            "status": "switched",
            "notes_update_required": True,
            "fresh_session_required": True,
        }
    except Exception as error:
        if not journal.exists():
            raise
        try:
            if not target_archive.exists() and active.exists():
                read_variant(active, plan["role"], plan["target_mode"])
                active.rename(target_archive)
            if not active.exists() and current_archive.exists():
                current_archive.rename(active)
            restored = (
                active.exists()
                and target_archive.exists()
                and not current_archive.exists()
            )
            if restored:
                read_variant(active, plan["role"], plan["current_mode"])
                read_variant(target_archive, plan["role"], plan["target_mode"])
                journal.unlink()
            else:
                raise RuntimeError("Filesystem does not match the pre-switch state")
        except Exception as rollback_error:
            journal.write_text(
                json.dumps(
                    {
                        **plan,
                        "phase": "manual_recovery_required",
                        "switch_error": str(error),
                        "rollback_error": str(rollback_error),
                    },
                    indent=2,
                    sort_keys=True,
                )
                + "\n",
                encoding="utf-8",
            )
            raise RuntimeError(
                f"Switch failed and rollback needs manual recovery from {journal}: "
                f"{rollback_error}"
            ) from error
        raise
    finally:
        if lock_owned:
            lock.unlink(missing_ok=True)


def acknowledge_notes(role: str, archive_root: Path) -> dict[str, Any]:
    if not ROLE.match(role):
        raise ValueError("--role must use lowercase letters, digits, and hyphens")
    archive_root = archive_root.resolve()
    role_archive = (archive_root / role).resolve()
    if role_archive.parent != archive_root:
        raise ValueError("Role archive must be a strict child of archive root")
    lock = role_archive / ".switch.lock"
    journal = role_archive / ".switch-journal.json"
    if lock.exists():
        raise RuntimeError(f"Cannot acknowledge while switch lock exists: {lock}")
    try:
        value = json.loads(journal.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise ValueError(f"No pending switch journal: {journal}") from error
    except json.JSONDecodeError as error:
        raise ValueError(f"Invalid pending switch journal: {journal}") from error
    if value.get("phase") != "switched_pending_notes" or value.get("role") != role:
        raise ValueError(f"Journal is not ready for NOTES acknowledgement: {journal}")
    journal.unlink()
    return {
        "status": "notes_acknowledged",
        "role": role,
        "mode": value["target_mode"],
        "fresh_session_required": True,
    }


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--role", required=True)
    result.add_argument("--current-mode", choices=MODES)
    result.add_argument("--target-mode", choices=MODES)
    result.add_argument("--active", type=Path)
    result.add_argument("--archive-root", type=Path, required=True)
    result.add_argument("--discovery-root", type=Path, action="append", default=[])
    result.add_argument("--apply", action="store_true")
    result.add_argument("--ack-notes", action="store_true")
    return result


def main() -> int:
    args = parser().parse_args()
    try:
        if args.ack_notes:
            print(
                json.dumps(
                    acknowledge_notes(args.role, args.archive_root),
                    indent=2,
                    sort_keys=True,
                )
            )
            return 0
        if not args.current_mode or not args.target_mode or not args.active:
            raise ValueError(
                "--current-mode, --target-mode, and --active are required unless --ack-notes is used"
            )
        plan = build_plan(
            role=args.role,
            current_mode=args.current_mode,
            target_mode=args.target_mode,
            active=args.active,
            archive_root=args.archive_root,
            discovery_roots=args.discovery_root,
        )
        output = apply_plan(plan) if args.apply else {**plan, "dry_run": True}
        print(json.dumps(output, indent=2, sort_keys=True))
        return 0
    except (OSError, RuntimeError, ValueError) as error:
        print(json.dumps({"status": "error", "error": str(error)}, indent=2), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
