"""Part D: a small example of "option C" from issue #3.

Option C in one line: the caller hands over the old snapshots, and the
library does the counting, linking and checking.

Run part_a.py, part_b.py and part_c.py first (part_b makes snapshot 1 in crate_v1).
Output: crate_v2/ (snapshot 2, which links back to snapshot 1).

Still NOT a full Five Safes snapshot: dates, egress and dct:isVersionOf are left out
to keep the example short.
"""
from pathlib import Path

from rocrate.rocrate import ROCrate

HERE = Path(__file__).parent
RECORD_ID = "https://example.org/records/123"


# ---------------------------------------------------------------------------
# The "library" part: these functions would live inside 5s-crate-py.
# ---------------------------------------------------------------------------

def read_snapshot_info(folder):
    """Open a snapshot and pull out the two things we need: version and identifier."""
    root = ROCrate(folder).root_dataset
    return {"version": root["version"], "identifier": root["identifier"]}


def work_out_next_snapshot(known_snapshots):
    """Count: next version = highest version + 1. Link: previous = the newest one."""
    if not known_snapshots:
        return {"version": 1, "identifier": f"{RECORD_ID}/versions/1", "previous": None}

    newest = max(known_snapshots, key=lambda s: s["version"])
    new_version = newest["version"] + 1
    return {
        "version": new_version,
        "identifier": f"{RECORD_ID}/versions/{new_version}",
        "previous": newest["identifier"],
    }


def check_version(version, known_snapshots):
    """Check: refuse a version number that is already used or too low."""
    for s in known_snapshots:
        if version <= s["version"]:
            raise ValueError(
                f"version {version} not allowed: snapshot {s['version']} already exists"
            )


# ---------------------------------------------------------------------------
# The "caller" part: this is what the toolkit would do.
# ---------------------------------------------------------------------------

# 1. The caller hands over the snapshots it knows about.
known = [read_snapshot_info(HERE / "crate_v1")]
print("Snapshots I was given:", known)

# 2. The library works out the details of the next snapshot.
details = work_out_next_snapshot(known)
print("Next snapshot will be:", details)

# 3. The library checks the number before using it.
check_version(details["version"], known)

# 4. Make the snapshot: a copy of the working record with the new details on the root.
snap = ROCrate(HERE / "crate_v0")
snap.root_dataset["version"] = details["version"]
snap.root_dataset["identifier"] = details["identifier"]
snap.root_dataset["pav:previousVersion"] = {"@id": details["previous"]}

out = HERE / f"crate_v{details['version']}"
if (out / "ro-crate-metadata.json").exists():
    # Doug's rule from #2: never overwrite an existing snapshot.
    print(f"{out.name} already exists, refusing to overwrite it")
else:
    snap.write(out)
    print(f"written {out.name}")

# 5. The check in action: try to reuse version 1.
print("\nTrying to make another snapshot numbered 1...")
try:
    check_version(1, known)
except ValueError as e:
    print("  refused:", e)

# 6. The weakness: if the caller forgets snapshot 1, the library can't know about it.
print("\nIf the caller forgets to pass any snapshots...")
print("  library would choose:", work_out_next_snapshot([]))
print("  -> version 1 again, a duplicate! (open question 1 on #3)")
