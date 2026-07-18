from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock


SCRIPT = Path(__file__).with_name("switch_skill_mode.py")
SPEC = importlib.util.spec_from_file_location("switch_skill_mode", SCRIPT)
assert SPEC and SPEC.loader
switcher = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(switcher)


def make_skill(path: Path, name: str, role: str, mode: str) -> None:
    path.mkdir(parents=True)
    (path / "SKILL.md").write_text(f"---\nname: {name}\ndescription: test\n---\n", encoding="utf-8")
    (path / switcher.VARIANT_FILE).write_text(
        '{"schema_version": 1, "role": '
        f'"{role}", "mode": "{mode}", "validated": true, '
        '"validation_evidence": "unit-test"}\n',
        encoding="utf-8",
    )
    (path / "unit-test").write_text("validated\n", encoding="utf-8")


class SwitchSkillModeTests(unittest.TestCase):
    def test_dry_plan_does_not_move_skills(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            discovery = root / ".claude" / "skills"
            active = discovery / "project-deps"
            archive = root / ".py2rs" / "skill-archive"
            target = archive / "dependency-bootstrap" / "scaffold"
            make_skill(active, "project-deps", "dependency-bootstrap", "prompt")
            make_skill(target, "project-deps", "dependency-bootstrap", "scaffold")
            plan = switcher.build_plan(
                role="dependency-bootstrap",
                current_mode="prompt",
                target_mode="scaffold",
                active=active,
                archive_root=archive,
                discovery_roots=[discovery],
            )
            self.assertEqual(plan["status"], "ready")
            self.assertTrue(active.exists())
            self.assertTrue(target.exists())

    def test_apply_archives_inactive_mode_outside_discovery(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            discovery = root / ".claude" / "skills"
            active = discovery / "project-deps"
            archive = root / ".py2rs" / "skill-archive"
            target = archive / "dependency-bootstrap" / "scaffold"
            make_skill(active, "project-deps", "dependency-bootstrap", "prompt")
            make_skill(target, "project-deps", "dependency-bootstrap", "scaffold")
            (active / "variant.txt").write_text("prompt-version", encoding="utf-8")
            (target / "variant.txt").write_text("scaffold-version", encoding="utf-8")
            plan = switcher.build_plan(
                role="dependency-bootstrap",
                current_mode="prompt",
                target_mode="scaffold",
                active=active,
                archive_root=archive,
                discovery_roots=[discovery],
            )
            result = switcher.apply_plan(plan)
            self.assertEqual(result["status"], "switched")
            self.assertIn("scaffold-version", (active / "variant.txt").read_text())
            archived = archive / "dependency-bootstrap" / "prompt" / "variant.txt"
            self.assertIn("prompt-version", archived.read_text())
            self.assertTrue(result["notes_update_required"])
            journal = archive / "dependency-bootstrap" / ".switch-journal.json"
            self.assertTrue(journal.is_file())
            acknowledged = switcher.acknowledge_notes("dependency-bootstrap", archive)
            self.assertEqual(acknowledged["status"], "notes_acknowledged")
            self.assertFalse(journal.exists())

    def test_archive_inside_discovery_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            discovery = root / ".claude" / "skills"
            active = discovery / "active"
            archive = discovery / "archive"
            make_skill(active, "active", "role", "prompt")
            make_skill(archive / "role" / "scaffold", "active", "role", "scaffold")
            with self.assertRaisesRegex(ValueError, "outside every discovery root"):
                switcher.build_plan(
                    role="role",
                    current_mode="prompt",
                    target_mode="scaffold",
                    active=active,
                    archive_root=archive,
                    discovery_roots=[discovery],
                )

    def test_duplicate_in_second_discovery_root_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            claude = root / ".claude" / "skills"
            codex = root / ".codex" / "skills"
            active = claude / "project-deps"
            duplicate = codex / "project-deps"
            archive = root / ".py2rs" / "skill-archive"
            make_skill(active, "project-deps", "role", "prompt")
            make_skill(duplicate, "project-deps", "role", "prompt")
            make_skill(archive / "role" / "scaffold", "project-deps", "role", "scaffold")
            with self.assertRaisesRegex(ValueError, "Duplicate discoverable"):
                switcher.build_plan(
                    role="role",
                    current_mode="prompt",
                    target_mode="scaffold",
                    active=active,
                    archive_root=archive,
                    discovery_roots=[claude, codex],
                )

    def test_variant_marker_must_match_requested_mode(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            discovery = root / "skills"
            active = discovery / "project-deps"
            archive = root / "archive"
            make_skill(active, "project-deps", "role", "scaffold")
            make_skill(archive / "role" / "scaffold", "project-deps", "role", "scaffold")
            with self.assertRaisesRegex(ValueError, "does not match"):
                switcher.build_plan(
                    role="role",
                    current_mode="prompt",
                    target_mode="scaffold",
                    active=active,
                    archive_root=archive,
                    discovery_roots=[discovery],
                )

    def test_same_role_under_another_name_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            claude = root / ".claude" / "skills"
            codex = root / ".codex" / "skills"
            active = claude / "project-deps"
            duplicate = codex / "alternate-name"
            archive = root / "archive"
            make_skill(active, "project-deps", "role", "prompt")
            make_skill(duplicate, "alternate-name", "role", "prompt")
            make_skill(archive / "role" / "scaffold", "project-deps", "role", "scaffold")
            with self.assertRaisesRegex(ValueError, "Duplicate discoverable"):
                switcher.build_plan(
                    role="role",
                    current_mode="prompt",
                    target_mode="scaffold",
                    active=active,
                    archive_root=archive,
                    discovery_roots=[claude, codex],
                )

    def test_active_cannot_be_the_discovery_root(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            discovery = root / "skills"
            archive = root / "archive"
            make_skill(discovery, "project-deps", "role", "prompt")
            make_skill(archive / "role" / "scaffold", "project-deps", "role", "scaffold")
            with self.assertRaisesRegex(ValueError, "strict child"):
                switcher.build_plan(
                    role="role",
                    current_mode="prompt",
                    target_mode="scaffold",
                    active=discovery,
                    archive_root=archive,
                    discovery_roots=[discovery],
                )

    def test_same_mode_still_requires_archived_counterpart(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            discovery = root / "skills"
            active = discovery / "project-deps"
            archive = root / "archive"
            make_skill(active, "project-deps", "role", "scaffold")
            with self.assertRaisesRegex(ValueError, "Inactive mode is missing"):
                switcher.build_plan(
                    role="role",
                    current_mode="scaffold",
                    target_mode="scaffold",
                    active=active,
                    archive_root=archive,
                    discovery_roots=[discovery],
                )

    def test_preexisting_journal_blocks_plan(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            discovery = root / "skills"
            active = discovery / "project-deps"
            archive = root / "archive"
            target = archive / "role" / "scaffold"
            make_skill(active, "project-deps", "role", "prompt")
            make_skill(target, "project-deps", "role", "scaffold")
            (archive / "role" / ".switch-journal.json").write_text(
                '{"phase": "manual_recovery_required"}\n', encoding="utf-8"
            )
            with self.assertRaisesRegex(ValueError, "Pending switch journal"):
                switcher.build_plan(
                    role="role",
                    current_mode="prompt",
                    target_mode="scaffold",
                    active=active,
                    archive_root=archive,
                    discovery_roots=[discovery],
                )

    def test_journal_write_failure_releases_lock_without_moving_skills(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            discovery = root / "skills"
            active = discovery / "project-deps"
            archive = root / "archive"
            target = archive / "role" / "scaffold"
            make_skill(active, "project-deps", "role", "prompt")
            make_skill(target, "project-deps", "role", "scaffold")
            plan = switcher.build_plan(
                role="role",
                current_mode="prompt",
                target_mode="scaffold",
                active=active,
                archive_root=archive,
                discovery_roots=[discovery],
            )
            original_write_text = Path.write_text

            def fail_journal(path, *args, **kwargs):
                if path.name == ".switch-journal.json":
                    raise OSError("injected journal failure")
                return original_write_text(path, *args, **kwargs)

            with mock.patch.object(Path, "write_text", new=fail_journal):
                with self.assertRaisesRegex(OSError, "injected journal failure"):
                    switcher.apply_plan(plan)
            self.assertTrue(active.exists())
            self.assertTrue(target.exists())
            self.assertFalse((archive / "role" / ".switch.lock").exists())

    def test_ambiguous_activation_race_retains_recovery_journal(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            discovery = root / "skills"
            active = discovery / "project-deps"
            archive = root / "archive"
            target = archive / "role" / "scaffold"
            make_skill(active, "project-deps", "role", "prompt")
            make_skill(target, "project-deps", "role", "scaffold")
            plan = switcher.build_plan(
                role="role",
                current_mode="prompt",
                target_mode="scaffold",
                active=active,
                archive_root=archive,
                discovery_roots=[discovery],
            )
            original_rename = Path.rename

            def inject_occupant(path, target_path):
                result = original_rename(path, target_path)
                if path == active:
                    make_skill(active, "intruder", "other-role", "prompt")
                return result

            with mock.patch.object(Path, "rename", new=inject_occupant):
                with self.assertRaisesRegex(RuntimeError, "manual recovery"):
                    switcher.apply_plan(plan)
            journal = archive / "role" / ".switch-journal.json"
            value = json.loads(journal.read_text(encoding="utf-8"))
            self.assertEqual(value["phase"], "manual_recovery_required")
            self.assertTrue((archive / "role" / "prompt").exists())
            self.assertTrue(target.exists())
            self.assertTrue(active.exists())

    def test_acknowledgement_rejects_role_traversal(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            archive = Path(temporary) / "archive"
            with self.assertRaisesRegex(ValueError, "lowercase letters"):
                switcher.acknowledge_notes("../victim", archive)

    def test_validation_evidence_must_be_a_distinct_file(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            skill = Path(temporary) / "skill"
            make_skill(skill, "project-deps", "role", "prompt")
            marker = skill / switcher.VARIANT_FILE
            value = json.loads(marker.read_text(encoding="utf-8"))
            value["validation_evidence"] = "."
            marker.write_text(json.dumps(value), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "validation evidence is missing"):
                switcher.read_variant(skill, "role", "prompt")


if __name__ == "__main__":
    unittest.main()
