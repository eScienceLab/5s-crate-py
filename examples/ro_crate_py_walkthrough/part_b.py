"""Part B: load the working record, take a hand-made "snapshot", then edit the working record.

Output: crate_v1/ (the snapshot, Josiah at Manchester) and an updated
crate_v0/ (the working record, Josiah now at Leeds).

This is NOT a real Five Safes snapshot: dates, immutability, pav:previousVersion
and dct:isVersionOf are all missing. That is the job of 5s-crate-py.
"""
from pathlib import Path

from rocrate.rocrate import ROCrate

HERE = Path(__file__).parent
JOSIAH_ID = "https://orcid.org/0000-0002-1825-0097"  # official test ORCID for a fictional researcher

# 1. load the working record from disk
crate = ROCrate(HERE / "crate_v0")
josiah = crate.get(JOSIAH_ID)
print("Loaded Josiah:", josiah["name"], "/", josiah["affiliation"])

# 2. hand-made snapshot: copy of the working record with version info on the root
snap = ROCrate(HERE / "crate_v0")                   # a separate copy in memory
snap.root_dataset["version"] = 1
snap.root_dataset["identifier"] = "https://example.org/records/123/versions/1"
snap.write(HERE / "crate_v1")

# 3. now Josiah moves job: change him in the WORKING RECORD only
josiah["affiliation"] = "University of Leeds"
crate.write(HERE / "crate_v0")
print("Saved both")
