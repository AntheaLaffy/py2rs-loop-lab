from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock


SCRIPT = Path(__file__).with_name("crate_recon.py")
SPEC = importlib.util.spec_from_file_location("crate_recon", SCRIPT)
assert SPEC and SPEC.loader
crate_recon = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(crate_recon)


class CrateReconTests(unittest.TestCase):
    def test_parse_search_output(self) -> None:
        output = 'symphonia = "0.5.5" # Audio decoding\nhound = "3.5.1" # WAV\n'
        self.assertEqual(
            [item["crate"] for item in crate_recon.parse_search_output(output)],
            ["symphonia", "hound"],
        )

    def test_merge_query_results_keeps_query_provenance(self) -> None:
        merged = crate_recon.merge_query_results(
            [
                ("wav", [{"crate": "hound", "version": "3", "description": "", "source": "crates.io"}]),
                ("audio decoder", [{"crate": "hound", "version": "3", "description": "", "source": "crates.io"}]),
            ]
        )
        self.assertEqual(len(merged), 1)
        self.assertEqual(merged[0]["matched_queries"], ["wav", "audio decoder"])

    def test_named_candidates_are_mandatory_inspection_records(self) -> None:
        self.assertEqual(
            crate_recon.named_candidate_records(["rodio", "rodio", "symphonia"]),
            [
                {"crate": "rodio", "status": "required_inspection"},
                {"crate": "symphonia", "status": "required_inspection"},
            ],
        )

    def test_sanitize_credentials_and_tokens(self) -> None:
        value = "https://alice:secret@example.test token=abcd"
        sanitized = crate_recon.sanitize(value)
        self.assertNotIn("alice", sanitized)
        self.assertNotIn("secret", sanitized)
        self.assertNotIn("abcd", sanitized)

    def test_proxy_is_used_only_after_direct_failure(self) -> None:
        calls: list[dict[str, str]] = []

        def fake_run(*args, **kwargs):
            env = kwargs["env"]
            calls.append(env)
            if env.get("CARGO_HTTP_PROXY"):
                return subprocess.CompletedProcess(args[0], 0, "ok", "")
            return subprocess.CompletedProcess(args[0], 101, "", "network failed")

        with mock.patch.object(crate_recon.subprocess, "run", side_effect=fake_run):
            result = crate_recon.run_with_fallback(
                ["cargo", "search", "audio"],
                Path.cwd(),
                "http://127.0.0.1:7890",
            )

        self.assertEqual(result["mode"], "proxy")
        self.assertNotIn("CARGO_HTTP_PROXY", calls[0])
        self.assertEqual(calls[1]["CARGO_HTTP_PROXY"], "http://127.0.0.1:7890")

    def test_local_cache_search(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            cargo_home = Path(temporary)
            crate = cargo_home / "registry" / "src" / "index" / "audio-decoder-1.0.0"
            crate.mkdir(parents=True)
            (crate / "Cargo.toml").write_text(
                '[package]\nname = "audio-decoder"\nversion = "1.0.0"\n'
                'description = "WAV audio decoder"\nkeywords = ["wav", "audio"]\n',
                encoding="utf-8",
            )
            with mock.patch.dict(os.environ, {"CARGO_HOME": str(cargo_home)}):
                results = crate_recon.search_local_cache("WAV decoder", 3)
        self.assertEqual(results[0]["crate"], "audio-decoder")
        self.assertEqual(results[0]["source"], "cargo-cache")

    def test_metadata_summary_tracks_dependency_paths(self) -> None:
        metadata = {
            "packages": [
                {"id": "umbrella", "name": "umbrella", "version": "1.0.0"},
                {"id": "backend", "name": "decoder-backend", "version": "2.0.0"},
            ],
            "resolve": {
                "nodes": [
                    {
                        "id": "umbrella",
                        "features": ["wav"],
                        "deps": [{"name": "decoder_backend", "pkg": "backend"}],
                    },
                    {"id": "backend", "features": ["pcm"], "deps": []},
                ]
            },
        }
        graph = crate_recon.summarize_metadata(metadata, "umbrella", "1.0.0")
        self.assertEqual(
            graph["paths"]["decoder-backend@2.0.0"],
            ["umbrella", "decoder-backend"],
        )

    def test_probe_manifest_is_explicit(self) -> None:
        manifest = crate_recon.probe_manifest("rodio", "0.22.2", ["wav"], True)
        self.assertIn('version = "=0.22.2"', manifest)
        self.assertIn("default-features = false", manifest)
        self.assertIn('features = ["wav"]', manifest)

    def test_probe_workspace_has_a_cargo_target(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary)
            crate_recon.write_probe_workspace(
                workspace, "rodio", "0.22.2", ["wav"], True
            )
            self.assertTrue((workspace / "Cargo.toml").is_file())
            self.assertTrue((workspace / "src" / "lib.rs").is_file())


if __name__ == "__main__":
    unittest.main()
