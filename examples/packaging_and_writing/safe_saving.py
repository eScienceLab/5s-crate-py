"""Safe saving (issue #7).

ro-crate-py's write() writes straight into the output folder. If it fails part
way, the folder is left half written: some files new, some old, maybe no
metadata file at all. In the HDR-RO-Crate-Toolkits `rocrate-save-tes` script,
that folder also holds the task results it has just downloaded.

The rule (from HDR-RO-Crate-Toolkits#64): if saving fails, the output folder
is left exactly as it was.

How safe_write() does it:
  1. Write the whole crate to a new hidden folder next to the output folder.
  2. Only once that has worked, move the old output folder aside (if there is
     one) as a backup.
  3. Move the new folder into place. If that move fails, put the backup back.
  4. Always delete the new folder if it was not used, and delete the backup
     only after everything has worked.

Two easy mistakes, both found when testing an earlier version:
  - Making the backup folder before knowing there is anything to back up.
    If saving then fails, the empty backup gets "restored" over the real
    output folder, and everything in it is lost.
  - Wrapping every step in the rollback. Only step 3 can leave things half
    done; a failure in step 1 never touched the output folder.

What "the output folder" means after a successful save: exactly what the crate
writes. A crate loaded from a folder also copies that folder's files that are
not in its metadata (ro-crate-py does this), so loading, editing and saving
back to the same folder keeps them. Files in the output folder that the crate
does not know about, and that it was not loaded from, are not kept.

Run this file to see each case. Output: safe_saving_demo/ (remade on each run)
"""
import logging
import shutil
import tempfile
from pathlib import Path

from rocrate.rocrate import ROCrate

logger = logging.getLogger(__name__)


def safe_write(crate, folder):
    """Write `crate` to `folder`, leaving `folder` as it was if saving fails."""

    folder = Path(folder)
    folder.parent.mkdir(parents=True, exist_ok=True)

    # 1. Write everything to a new folder next to the output, so the final move is a rename
    #    on the same disk, not a copy.
    new = Path(tempfile.mkdtemp(dir=folder.parent, prefix=f".{folder.name}.new-"))
    backup = None
    try:
        crate.write(new)

        # 2. Only back up a folder that is really there.
        if folder.exists():
            backup = Path(tempfile.mkdtemp(dir=folder.parent, prefix=f".{folder.name}.old-"))
            backup.rmdir()                   # we only want the unique name
            folder.rename(backup)

        # 3. Put the new folder in place. Only this step needs undoing if it fails.
        try:
            new.rename(folder)
        except OSError:
            if backup is not None:
                backup.rename(folder)
                backup = None
            raise
    finally:
        # 4. The new folder is still here only if it was not used.
        if new.exists():
            shutil.rmtree(new, ignore_errors=True)

    # Everything worked; the old version is no longer needed.
    if backup is not None:
        try:
            shutil.rmtree(backup)
        except OSError as exc:
            logger.warning(f"Saved, but the old version could not be removed from {backup}: {exc}")


# ---------------------------------------------------------------------------
# Walk through the cases.
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    HERE = Path(__file__).parent
    DEMO = HERE / "safe_saving_demo"
    OUTPUT = DEMO / "output_crate"

    def contents():
        if not OUTPUT.exists():
            return "(no folder)"
        return sorted(p.relative_to(OUTPUT).as_posix() for p in OUTPUT.rglob("*") if p.is_file())

    def show(step, *rest):
        print(f"{step:<28}", *rest)

    def leftovers():
        return sorted(p.name for p in DEMO.iterdir() if p.name.startswith("."))

    shutil.rmtree(DEMO, ignore_errors=True)

    # 1. Save a new crate.
    crate = ROCrate()
    crate.add_file(HERE / "sample_files" / "analysis.py")
    safe_write(crate, OUTPUT)
    show("1. new crate saved:", contents())

    # 2. A results file arrives in the folder (like rocrate-save-tes downloading results).
    (OUTPUT / "results.txt").write_text("downloaded results\n")
    show("2. results downloaded:", contents())

    # 3. Saving fails part way. The folder, results included, is unchanged.
    crate = ROCrate(OUTPUT)
    crate.root_dataset["name"] = "Will not be saved"

    def write_then_fail(base_path):
        (Path(base_path) / "half_written.txt").write_text("...")
        raise OSError("disk full")

    crate.write = write_then_fail
    try:
        safe_write(crate, OUTPUT)
    except OSError as e:
        show(f"3. save failed ({e}):", contents(), "<- unchanged")

    # 4. Load, edit and save back to the same folder. The results file is kept.
    crate = ROCrate(OUTPUT)
    crate.root_dataset["name"] = "Edited"
    safe_write(crate, OUTPUT)
    show("4. edited and saved:", contents(), "| name:", ROCrate(OUTPUT).root_dataset["name"])

    show("   leftover hidden folders:", leftovers() or "none")
