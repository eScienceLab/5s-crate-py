"""Writing crates (issue #7).

Shows the three ways ro-crate-py can save a crate, and two things that
matter for Five Safes snapshots:
  - write() silently overwrites, so 5s-crate-py must add the "never overwrite
    a snapshot" rule itself (Doug, #2)
  - detached crates need a full web address as the root ID, and ro-crate-py
    adds a "/" to the end of it

Output: written_crate/, written_crate.zip, snapshot-v2-ro-crate-metadata.json
"""
import json
from pathlib import Path

from rocrate.rocrate import ROCrate

HERE = Path(__file__).parent
SAMPLES = HERE / "sample_files"
RECORD_ID = "https://example.org/records/123"


def read_root(metadata_file):
    with open(metadata_file) as f:
        return json.load(f)["@graph"][0]


# 1. write to a FOLDER: metadata file + every packaged file -----------------
crate = ROCrate()
crate.add_file(SAMPLES / "analysis.py")
crate.root_dataset["name"] = "First version"
crate.write(HERE / "written_crate")
print("1. folder written:", sorted(p.name for p in (HERE / "written_crate").iterdir()))

# 2. writing again OVERWRITES without any warning -----------------------------
crate.root_dataset["name"] = "Second version"
crate.write(HERE / "written_crate")
print("2. name on disk is now:", read_root(HERE / "written_crate" / "ro-crate-metadata.json")["name"],
      "<- the first version is gone, no warning")


# 3. what 5s-crate-py would need to add: refuse to overwrite a snapshot -------
def safe_write(crate, folder):
    """Doug's rule (#2): if a snapshot is already there, don't overwrite it."""
    existing = Path(folder) / "ro-crate-metadata.json"
    if existing.exists() and "version" in read_root(existing):   # has a version -> it's a snapshot
        raise FileExistsError(f"{folder} already holds a snapshot, refusing to overwrite")
    crate.write(folder)


crate.root_dataset["version"] = 1                   # turn it into a "snapshot"
safe_write(crate, HERE / "written_crate")                 # fine: what's on disk isn't a snapshot yet
try:
    safe_write(crate, HERE / "written_crate")             # now it is, so this is refused
except FileExistsError as e:
    print("3. refused:", e.args[0].replace(str(HERE) + "/", ""))

# 4. write as a ZIP: same content, one file -----------------------------------
crate.write_zip(HERE / "written_crate.zip")
print("4. zip written: written_crate.zip")

# 5. write DETACHED: only the metadata file, no folder ------------------------
snapshot_id = f"{RECORD_ID}/versions/2"
detached = ROCrate(root_dataset_id=snapshot_id)     # detached crates need a full web address
detached.write_detached(HERE / "snapshot-v2-ro-crate-metadata.json")

root_id = read_root(HERE / "snapshot-v2-ro-crate-metadata.json")["@id"]
print("5. detached file written: snapshot-v2-ro-crate-metadata.json")
print("   ID I asked for:    ", snapshot_id)
print("   ID it was saved as:", root_id, "<- note the extra '/' at the end")

reloaded = ROCrate(HERE / "snapshot-v2-ro-crate-metadata.json")
print("   reloads fine, root ID:", reloaded.root_dataset.id)
