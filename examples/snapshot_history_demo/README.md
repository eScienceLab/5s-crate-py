# Snapshot history demo (ro-crate-py walkthrough)

Small scripts for learning [ro-crate-py](https://github.com/ResearchObject/ro-crate-py)
and trying out snapshot ideas for 5s-crate-py. These are learning examples, not library code.

## Setup

From the project root:

```
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Run in order

Each part uses the folders made by the part before it.

| Script | What it does | Makes |
|---|---|---|
| `part_a.py` | Creates a crate with a person (Josiah) and saves it as the working record | `crate_v0/` |
| `part_b.py` | Takes a hand-made snapshot (version 1), then changes Josiah in the working record only | `crate_v1/`, updates `crate_v0/` |
| `part_c.py` | Loads both and compares them: the snapshot keeps the old data | – |
| `part_d.py` | Demo of "option C" from [#3](https://github.com/eScienceLab/5s-crate-py/issues/3): the caller hands over old snapshots, the library works out the next version and `pav:previousVersion` and checks for mistakes | `crate_v2/` |

```
python examples/snapshot_history_demo/part_a.py
python examples/snapshot_history_demo/part_b.py
python examples/snapshot_history_demo/part_c.py
python examples/snapshot_history_demo/part_d.py
```

To start again, delete the `crate_v*` folders. They are not committed.

## Not covered yet

These are not full Five Safes snapshots: dates (`dateCreated`, `datePublished`,
`dateModified`), `dct:isVersionOf`, egress snapshots and redaction are left out.
