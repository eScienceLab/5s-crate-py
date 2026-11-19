# Packaging and writing with ro-crate-py

Small scripts exploring how [ro-crate-py](https://github.com/ResearchObject/ro-crate-py)
(version 0.16) packages files and writes crates, for
[#6](https://github.com/eScienceLab/5s-crate-py/issues/6) and
[#7](https://github.com/eScienceLab/5s-crate-py/issues/7).
These are learning examples, not library code.

## Setup

From the project root:

```
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Scripts

Each script runs on its own.

| Script | What it does | Makes |
| --- | --- | --- |
| `packaging.py` | Packaging files (#6): copying a file, copying to a new path, copying a whole folder, and recording a web address as a reference without copying it | `packaged_crate/` |
| `dates.py` | Dates when writing (#7), following Doug's rules from [#8](https://github.com/eScienceLab/5s-crate-py/issues/8): `dateCreated`, `datePublished` and `dateModified` for working records and snapshots | `dates_working/`, `dates_snapshot/` |
| `writing.py` | Writing crates (#7): to a folder, as a zip, and as a detached metadata file. Shows that `write()` overwrites silently, a sketch of "refuse to overwrite a snapshot", and the extra `/` ro-crate-py adds to detached root IDs | `written_crate/`, `written_crate.zip`, `snapshot-v2-ro-crate-metadata.json` |

```
python examples/packaging_and_writing/packaging.py
python examples/packaging_and_writing/writing.py
python examples/packaging_and_writing/dates.py
```

`sample_files/` holds the small files the scripts package.

To start again, delete the generated outputs listed above. They are not committed.

## Findings so far

- **Copy vs reference:** a local path is copied into the crate; a web address is only
  recorded in the metadata. This matches the "references vs packaged copies"
  distinction in #2.
- **`add_dataset` vs `add_tree`:** `add_dataset("folder")` lists only the folder;
  `add_tree("folder")` also lists every file inside it.
- **`write()` overwrites silently:** 5s-crate-py needs to add the "never overwrite a
  snapshot" rule itself.
- **Detached root IDs get a trailing `/`:** asking for `.../versions/2` gives
  `.../versions/2/`. This may clash with snapshot identifiers written without the slash.
- **ro-crate-py fills in `datePublished`:** a new crate gets one automatically, and so does
  a crate *loaded* without one (set to the load time). It never sets `dateCreated`.
  Setting `datePublished` to `None` writes `null` to the file, so delete the key instead.
- **Zip quirk:** using `add_tree` and then `write_zip` adds the same files to the zip
  twice (with a warning).
