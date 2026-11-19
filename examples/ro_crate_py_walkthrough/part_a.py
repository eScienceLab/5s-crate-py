"""Part A: create a crate, add a person (Josiah), and save it to a folder.

Run part_a.py, then part_b.py, then part_c.py.
Output: crate_v0/ro-crate-metadata.json (the "working record").
"""
from pathlib import Path

from rocrate.rocrate import ROCrate
from rocrate.model.person import Person

HERE = Path(__file__).parent
JOSIAH_ID = "https://orcid.org/0000-0002-1825-0097"  # official test ORCID for a fictional researcher

crate = ROCrate()                                   # 1. empty crate, in memory only
josiah = Person(crate, JOSIAH_ID, properties={      # 2. describe Josiah
    "name": "Josiah Carberry",
    "affiliation": "University of Manchester",
})
crate.add(josiah)                                   # 3. put him in the crate
crate.root_dataset["author"] = josiah               # 4. link him to the crate as author
crate.write(HERE / "crate_v0")                      # 5. save to a folder
print("written crate_v0")
