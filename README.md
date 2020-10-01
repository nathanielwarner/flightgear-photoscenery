# FlightGear - PhotoScenery Edition

This project brings support for photoscenery to FlightGear, the free and open-source flight simulator.
The photoscenery is an overlay, which overrides the traditional scenery textures when there is a satellite orthophoto available for the current tile.
It is fully compatible with Atmospheric Light Scattering (as well as the default pipeline), and works with your existing scenery.

Normally, FlightGear uses generic terrain textures. Photoscenery allows you to recognize the terrain, improving your experience when flying with visual flight rules (VFR).

![Traditional vs photoscenery comparison](screenshots/photoscenery-comparison-ksba.png)

This is a work in progress. Currently, you need to provide the satellite orthophotos manually, though I'm working on making it automated, so stay tuned!

## Getting it

I plan to release prebuilt binaries for Linux, MacOS, and Windows to coincide with the upcoming release of FlightGear 2020.2. Currently, you need to build from source.

## Building from source

You can use either the `release/2020.2` branches, or the `next` branches. The `next` branches are more bleeding-edge, and are targeting version 2020.3.

1. Clone the official FlightGear base data package at the `next` or `release/2020.2` branch. Apply my patch. ([fgdata.patch](fgdata.patch) in this repository)
2. Clone my patched [SimGear repository](https://github.com/nathanielwarner/simgear) (`git clone https://github.com/nathanielwarner/simgear`). Checkout the branch you're using and follow the normal build and install instructions. You may want to set the install prefix so as not to conflict with an existing installation of simgear.
3. Clone my patched [FlightGear repository](https://github.com/nathanielwarner/flightgear) (`git clone https://github.com/nathanielwarner/flightgear`). Checkout the branch you're using and follow the normal build instructions, making sure that the base data package and simgear location is set to the patched ones you installed.

## Using It

You'll need to have an `Orthophotos/` subdirectory in one of your scenery folders, alongside `Terrain/`, `Buildings/`, etc. You could put it in existing custom scenery packages, or keep your orthophotos in a separate package (for example to use them with TerraSync).

The `Orthophotos/` subdirectory is further split by geographic location to mirror other scenery subdirectories. The orthophotos themselves are named after their tile number. You can determine the tile number you need by using the [latlontotile.py](latlontotile.py) script. For example, to provide photoscenery for tile 991000, you'll provide an orthophoto named `991000.png`. This is a normal PNG file, with the image flipped vertically.

Once you have your orthophotos in place, you're all set! You can toggle the photoscenery on and off in the Rendering settings menu in FlightGear.
