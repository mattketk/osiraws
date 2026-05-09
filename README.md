# osiraws: OSIRris RAW Sort
Applet to sort OSIRIS raw diagnostic data (non-overwrite.)

## Installation
```
$ git clone https://github.com/mattketk/osiraws.git
$ cd osiraws/
$ uv sync
$ uv pip install -e .
$ ln -sf .venv/bin/osiraws ~/.local/bin/osiraws
```

## Usage
- List species
`$ osiraws list`

- Sort specified species
`$ osiraws sort <SPECIES>`

- Sort specified species into a specific folder
`$ osiraws sort <SPECIES> -o <DESTINATION>`
