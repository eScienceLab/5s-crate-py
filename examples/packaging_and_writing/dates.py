"""Dates when writing crates (issue #7, using Doug's rules from #8).

Doug's rules (https://github.com/eScienceLab/5s-crate-py/issues/8):
  New working record:    remove the datePublished ro-crate-py adds; set dateCreated = now
  Write working record:  no datePublished yet -> set it to now
                         already has one      -> keep it, set dateModified = now
  Make a snapshot:       dateCreated = now; remove dateModified
  Write the snapshot:    datePublished = now

Also shows a ro-crate-py gotcha: loading a crate that has no datePublished
silently fills one in with the load time.

Output: dates_working/, dates_snapshot/ (deleted and remade on each run)
"""
import json
import shutil
import time
from datetime import datetime, timezone
from pathlib import Path

from rocrate.rocrate import ROCrate

HERE = Path(__file__).parent
WORKING = HERE / "dates_working"
SNAPSHOT = HERE / "dates_snapshot"


def now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def show(step, crate):
    root = crate.root_dataset
    print(f"{step:<34}"
          f" created={root.get('dateCreated', '-')!s:<26}"
          f" published={root.get('datePublished', '-')!s:<26}"
          f" modified={root.get('dateModified', '-')}")


# ---------------------------------------------------------------------------
# The "library" part: what 5s-crate-py would do.
# ---------------------------------------------------------------------------

def new_working_record():
    crate = ROCrate()
    del crate.root_dataset["datePublished"]      # ro-crate-py adds this; not published yet
    crate.root_dataset["dateCreated"] = now()
    return crate


def write_working_record(crate, folder):
    root = crate.root_dataset
    if root.get("datePublished") is None:
        root["datePublished"] = now()            # first time it's written
    else:
        root["dateModified"] = now()             # written before: keep datePublished
    crate.write(folder)


def make_snapshot(working_folder):
    snap = ROCrate(working_folder)               # a separate copy of the working record
    snap.root_dataset["dateCreated"] = now()
    if "dateModified" in snap.root_dataset:
        del snap.root_dataset["dateModified"]
    return snap


def write_snapshot(snap, folder):
    if (Path(folder) / "ro-crate-metadata.json").exists():
        raise FileExistsError(f"{Path(folder).name} already exists, refusing to overwrite a snapshot")
    snap.root_dataset["datePublished"] = now()
    snap.write(folder)


# ---------------------------------------------------------------------------
# Walk through it, pausing a second between steps so the times differ.
# ---------------------------------------------------------------------------

shutil.rmtree(WORKING, ignore_errors=True)
shutil.rmtree(SNAPSHOT, ignore_errors=True)

work = new_working_record()
show("1. new working record", work)
time.sleep(1)

write_working_record(work, WORKING)
show("2. working record written (1st)", work)
time.sleep(1)

work = ROCrate(WORKING)
work.root_dataset["name"] = "edited"
write_working_record(work, WORKING)
show("3. edited and written again", work)
time.sleep(1)

snap = make_snapshot(WORKING)
show("4. snapshot made (not written)", snap)
time.sleep(1)

write_snapshot(snap, SNAPSHOT)
show("5. snapshot written", snap)

try:
    write_snapshot(snap, SNAPSHOT)
except FileExistsError as e:
    print("6. writing the snapshot again ->   refused:", e)

# --- the gotcha -------------------------------------------------------------
print("\nGotcha: a crate saved WITHOUT datePublished...")
crate = new_working_record()
crate.write(HERE / "dates_working")              # plain write, skipping our rules
with open(WORKING / "ro-crate-metadata.json") as f:
    on_disk = json.load(f)["@graph"][0].get("datePublished", "-")
print("   datePublished on disk:   ", on_disk)
time.sleep(1)
print("   datePublished after load:", ROCrate(WORKING).root_dataset.get("datePublished"),
      "<- ro-crate-py filled in the load time")
