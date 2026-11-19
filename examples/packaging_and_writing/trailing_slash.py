"""Trailing slash bug: ro-crate-py breaks a Five Safes snapshot on load + save.

The Five Safes spec gives the Root Data Entity an absolute @id with no
trailing slash (e.g. .../activities/A123/versions/1), and the metadata
descriptor's "about" points to the same value.

ro-crate-py (0.16.0) always adds "/" to a Dataset's @id. So:
  1. load a spec-style crate    -> root @id gains a "/"
  2. save it again              -> root @id has "/", "about" does not
  3. load the saved file again  -> fails: the two no longer match

Output: slash_snapshot-ro-crate-metadata.json, slash_resaved-ro-crate-metadata.json
"""
import json
from pathlib import Path

from rocrate.rocrate import ROCrate

HERE = Path(__file__).parent
ORIGINAL = HERE / "slash_snapshot-ro-crate-metadata.json"
RESAVED = HERE / "slash_resaved-ro-crate-metadata.json"
SNAPSHOT_ID = "https://tre72.example.org/activities/A123/versions/1"

# 0. a minimal snapshot written the way the Five Safes spec shows it (no slash)
spec_style = {
    "@context": "https://w3id.org/ro/crate/1.3/context",
    "@graph": [
        {
            "@id": "ro-crate-metadata.json",
            "@type": "CreativeWork",
            "about": {"@id": SNAPSHOT_ID},
            "conformsTo": {"@id": "https://w3id.org/ro/crate/1.3"},
        },
        {
            "@id": SNAPSHOT_ID,
            "@type": "Dataset",
            "identifier": {"@id": SNAPSHOT_ID},
            "version": 1,
            "datePublished": "2026-11-19T00:00:00+00:00",
        },
    ],
}
with open(ORIGINAL, "w") as f:
    json.dump(spec_style, f, indent=2)
print("0. written spec-style snapshot, root @id:", SNAPSHOT_ID)

# 1. load it
crate = ROCrate(ORIGINAL)
print("1. after loading, root @id:             ", crate.root_dataset.id, "<- '/' added")

# 2. save it again, unchanged
crate.write_detached(RESAVED)
with open(RESAVED) as f:
    graph = json.load(f)["@graph"]
root = next(e for e in graph if e["@type"] == "Dataset")
descriptor = next(e for e in graph if e["@id"] == "ro-crate-metadata.json")
print("2. after saving, root @id:              ", root["@id"])
print("   after saving, descriptor 'about':    ", descriptor["about"]["@id"], "<- no '/'")

# 3. load the saved file again
try:
    ROCrate(RESAVED)
    print("3. reloaded fine")
except ValueError as e:
    print("3. reloading FAILED:", e)
