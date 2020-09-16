# FlightGear - PhotoScenery Edition

These patches bring support for photoscenery to FlightGear, the free and open-source flight simulator.
The photoscenery is an overlay, which overrides the traditional scenery textures when available.
It is fully compatible with the ALS and default pipelines, and works with your existing scenery.

This is a work in progress. Currently, orthophotos need to be provided manually in the PNG format, placed alongside the tile that they correspond to in the `Terrain/` subdirectory of your scenery. For example, tile 991000 already has the files `991000.stg` and `991000.btg.gz`, and you would put `991000.png` alongside them.

## Getting it

I plan to release prebuilt binaries for Linux, MacOS, and Windows to coincide with the upcoming release of FlightGear 2020.2. Currently, you need to build from source.

## Building from source

1. Clone this repository with submodules. (`git clone --recurse-submodules https://github.com/nathanielwarner/flightgear-photoscenery`)
2. Apply the patches for simgear and fgdata. (provided as `simgear.patch` and `fgdata.patch` respectively)
3. Follow the build and install instructions provided in simgear. You may want to change the install prefix so as not to overwrite another installation of simgear.
4. Follow the build instructions provided in flightgear.

SimGear, as well as the FlightGear base data package (fgdata), need to be patched.
These patches are provided here as `simgear.patch` and `fgdata.patch`.

## Screenshots

All screenshots are with ALS renderer at max quality, and OpenStreetMap buildings enabled.

KSBA area, with photoscenery:

![KSBA photoscenery](screenshots/ksba-photoscenery.png)

Same location, with traditional scenery:

![KSBA traditional scenery](screenshots/ksba-traditional.png)

