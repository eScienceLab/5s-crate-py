# 5-Safes RO-Crate Library

Python library for the creation and manipulation of 5-Safes RO-Crates. This library is built on the [RO-Crate python library](https://github.com/ResearchObject/ro-crate-py), and is intended to provide support specifically for the creation of 5-Safes RO-Crates.

## Installation

Currently this package is installable only from source. To do this, prepare your python virtual environment:
```bash
python -m pip install rocrate
```

Then the library can installed using:
```bash
python -m pip install .
```

For development work, install this library in editable mode:
```bash
python -m pip install -e .
```

## Usage

To load the library and create the framework RO-Crate:

```python
from fivesafe_crate import FiveSafesCrate

crate = FiveSafesCrate(
    root_dataset_id="https://tre72.example.org/activities/A123/current",
    record_identifier="https://tre72.example.org/activities/A123",
    identifier="https://tre72.example.org/activities/A123/current"
)
```

To add a user:

```python
user_provenance = {
    'full_name': 'Josiah Stinkney Carberry',
    'id': 'jcarberry',
    'orcid': 'https://orcid.org/0000-0002-1825-0097'
}

crate.add_person_from_prov(user_provenance)
```

To write out the RO-Crate:

```python
crate.write("./")
```

