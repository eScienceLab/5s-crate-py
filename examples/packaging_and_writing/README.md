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
| `safe_saving.py` | Safe saving (#7): if saving fails, the output folder is left as it was. Writes to a new folder first and only then swaps it in, with tests in `test_safe_saving.py` | `safe_saving_demo/` |
| `trailing_slash.py` | Reproduces a ro-crate-py bug: a snapshot with a spec-style root `@id` (no trailing `/`) can't be reloaded after ro-crate-py loads and re-saves it | `slash_*-ro-crate-metadata.json` |
| `writing.py` | Writing crates (#7): to a folder, as a zip, and as a detached metadata file. Shows that `write()` overwrites silently, a sketch of "refuse to overwrite a snapshot", and the extra `/` ro-crate-py adds to detached root IDs | `written_crate/`, `written_crate.zip`, `snapshot-v2-ro-crate-metadata.json` |

```
python examples/packaging_and_writing/packaging.py
python examples/packaging_and_writing/writing.py
python examples/packaging_and_writing/dates.py
python examples/packaging_and_writing/trailing_slash.py
python examples/packaging_and_writing/safe_saving.py
```

To run the safe saving tests (no extra packages needed):

```
python -m unittest discover -s examples/packaging_and_writing -v
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
- **Root IDs get a trailing `/`, which breaks re-saved crates:** ro-crate-py always adds `/`
  to a Dataset `@id`, but the Five Safes spec examples use none (e.g. `.../versions/1`).
  Loading and re-saving such a crate changes the root `@id` but not the descriptor's
  `about`, and the result can't be loaded again. See `trailing_slash.py`.
- **ro-crate-py fills in `datePublished`:** a new crate gets one automatically, and so does
  a crate *loaded* without one (set to the load time). It never sets `dateCreated`.
  Setting `datePublished` to `None` writes `null` to the file, so delete the key instead.
- **A failed `write()` leaves the folder half written:** ro-crate-py writes straight into
  the output folder. `safe_saving.py` writes to a new folder first, and only replaces the
  old one once that has worked. Only make a backup if there is a folder to back up:
  otherwise a failed save "restores" an empty backup over the real folder.
- **Zip quirk:** using `add_tree` and then `write_zip` adds the same files to the zip
  twice (with a warning).
