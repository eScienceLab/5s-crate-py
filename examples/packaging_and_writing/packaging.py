"""Packaging files (issue #6).

Shows the ways ro-crate-py can put files into a crate, and the difference
between a packaged COPY (the file goes inside the crate folder) and a
REFERENCE (the metadata only points to a web address; nothing is copied).

Uses the small files in sample_files/.
Output: packaged_crate/
"""
import json
from pathlib import Path

from rocrate.rocrate import ROCrate

HERE = Path(__file__).parent
SAMPLES = HERE / "sample_files"
OUT = HERE / "packaged_crate"

crate = ROCrate()

# 1. copy one file into the crate, keeping its name
crate.add_file(SAMPLES / "analysis.py")

# 2. copy one file, but put it somewhere else (and rename it) inside the crate
crate.add_file(SAMPLES / "analysis.py", dest_path="code/run_analysis.py")

# 3. copy a whole folder AND list every file in it in the metadata
crate.add_tree(SAMPLES / "data", dest_path="data")

# 4. a REFERENCE: only the web address is recorded, nothing is downloaded or copied
crate.add_file("https://example.org/datasets/big_cohort.csv",
               properties={"name": "Large cohort dataset (stays in the TRE)"})

crate.write(OUT)

# --- what ended up where? ---------------------------------------------------
on_disk = sorted(str(p.relative_to(OUT)) for p in OUT.rglob("*") if p.is_file())
print("Files actually copied into packaged_crate/:")
for f in on_disk:
    print("   ", f)

with open(OUT / "ro-crate-metadata.json") as f:
    graph = json.load(f)["@graph"]

print("\nThings listed in the metadata:")
for entity in graph:
    entity_id = entity["@id"]
    if entity_id in ("./", "ro-crate-metadata.json"):
        continue                                    # the crate itself, not content
    if entity_id.startswith("http"):
        kind = "REFERENCE (not copied)"
    elif entity_id.endswith("/"):
        kind = "folder"
    else:
        kind = "packaged copy"
    print(f"    {entity_id:<45} {kind}")

print("\nNote: add_dataset('folder') would list only the folder, not the files")
print("inside it. add_tree (used above) lists every file.")
