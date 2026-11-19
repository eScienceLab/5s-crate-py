"""Part C: load both crates again and compare them.

Expected: the working record (crate_v0) shows Josiah at Leeds;
the snapshot (crate_v1) still shows Manchester, with version 1.
"""
from pathlib import Path

from rocrate.rocrate import ROCrate

HERE = Path(__file__).parent
JOSIAH_ID = "https://orcid.org/0000-0002-1825-0097"  # official test ORCID for a fictional researcher

for folder in ["crate_v0", "crate_v1"]:
    c = ROCrate(HERE / folder)
    root = c.root_dataset
    print(f"--- {folder}")
    print("  Josiah works at:", c.get(JOSIAH_ID)["affiliation"])
    print("  version:       ", root.get("version"))
    print("  identifier:    ", root.get("identifier"))
    print("  datePublished: ", root.get("datePublished"))
