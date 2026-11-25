"""Tests for safe_saving.py.

Run from the project root (no extra packages needed):

    python -m unittest discover -s examples/packaging_and_writing -v
"""
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from rocrate.rocrate import ROCrate

from safe_saving import safe_write

SAMPLES = Path(__file__).parent / "sample_files"


def snapshot(folder):
    """Every file in `folder` with its bytes, to check nothing changed."""
    return {p.relative_to(folder).as_posix(): p.read_bytes() for p in folder.rglob("*") if p.is_file()}


def write_then_fail(base_path):
    """Stands in for crate.write: writes part of the crate, then fails."""
    Path(base_path).mkdir(parents=True, exist_ok=True)
    (Path(base_path) / "ro-crate-metadata.json").write_text("half written")
    raise OSError("disk full")


class SafeWriteTests(unittest.TestCase):

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.output = self.tmp / "out"

    def existing_crate(self):
        """An output folder holding a saved crate plus a downloaded results file."""
        crate = ROCrate()
        crate.add_file(SAMPLES / "analysis.py")
        crate.root_dataset["name"] = "Old"
        crate.write(self.output)
        (self.output / "results.txt").write_text("downloaded results")
        return snapshot(self.output)

    def assertNoLeftovers(self):
        self.assertEqual([p.name for p in self.output.parent.iterdir() if p.name.startswith(".")], [])

    # --- saving works ------------------------------------------------------

    def test_new_folder(self):
        crate = ROCrate()
        crate.add_file(SAMPLES / "analysis.py")
        safe_write(crate, self.output)

        self.assertEqual(sorted(snapshot(self.output)), ["analysis.py", "ro-crate-metadata.json"])
        self.assertNoLeftovers()

    def test_creates_missing_parent_folders(self):
        self.output = self.tmp / "a" / "b" / "out"
        safe_write(ROCrate(), self.output)

        self.assertTrue((self.output / "ro-crate-metadata.json").is_file())
        self.assertNoLeftovers()

    def test_replaces_existing_folder(self):
        self.existing_crate()
        crate = ROCrate()
        crate.root_dataset["name"] = "New"
        safe_write(crate, self.output)

        self.assertEqual(sorted(snapshot(self.output)), ["ro-crate-metadata.json"])
        self.assertEqual(ROCrate(self.output).root_dataset["name"], "New")
        self.assertNoLeftovers()

    def test_load_edit_save_same_folder_keeps_files(self):
        self.existing_crate()
        crate = ROCrate(self.output)
        crate.root_dataset["name"] = "Edited"
        safe_write(crate, self.output)

        self.assertEqual(sorted(snapshot(self.output)), ["analysis.py", "results.txt", "ro-crate-metadata.json"])
        self.assertEqual((self.output / "results.txt").read_text(), "downloaded results")
        self.assertEqual(ROCrate(self.output).root_dataset["name"], "Edited")
        self.assertNoLeftovers()

    # --- saving fails: the output folder is left as it was ----------------

    def test_write_fails_existing_folder_unchanged(self):
        before = self.existing_crate()
        crate = ROCrate(self.output)
        crate.write = write_then_fail

        with self.assertRaisesRegex(OSError, "disk full"):
            safe_write(crate, self.output)

        self.assertEqual(snapshot(self.output), before)
        self.assertNoLeftovers()

    def test_write_fails_no_folder_created(self):
        crate = ROCrate()
        crate.write = write_then_fail

        with self.assertRaisesRegex(OSError, "disk full"):
            safe_write(crate, self.output)

        self.assertFalse(self.output.exists())
        self.assertNoLeftovers()

    def test_final_move_fails_old_folder_restored(self):
        before = self.existing_crate()
        real_rename = Path.rename

        def rename(self_path, target):
            if self_path.name.startswith(".out.new-"):
                raise OSError("move failed")
            return real_rename(self_path, target)

        with mock.patch.object(Path, "rename", rename):
            with self.assertRaisesRegex(OSError, "move failed"):
                safe_write(ROCrate(), self.output)

        self.assertEqual(snapshot(self.output), before)
        self.assertNoLeftovers()

    def test_old_version_not_removed_still_saves(self):
        self.existing_crate()
        real_rmtree = shutil.rmtree

        def rmtree(path, *args, **kwargs):
            if Path(path).name.startswith(".out.old-"):
                raise OSError("in use")
            return real_rmtree(path, *args, **kwargs)

        crate = ROCrate()
        crate.root_dataset["name"] = "New"
        with mock.patch("safe_saving.shutil.rmtree", rmtree), self.assertLogs("safe_saving", "WARNING"):
            safe_write(crate, self.output)

        self.assertEqual(ROCrate(self.output).root_dataset["name"], "New")
        old = [p for p in self.tmp.iterdir() if p.name.startswith(".out.old-")]
        self.assertEqual(len(old), 1, "the old version is kept and reported, not lost")


if __name__ == "__main__":
    unittest.main()
