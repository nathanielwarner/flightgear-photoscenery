# FlightGear PhotoScenery

This project brings support for photoscenery to FlightGear, the free and open-source flight simulator.
The photoscenery is an overlay, which overrides the traditional scenery textures when there is a satellite orthophoto available for the current tile.
It is fully compatible with Atmospheric Light Scattering (as well as the default pipeline), and works with your existing scenery.

Normally, FlightGear uses generic terrain textures. Photoscenery allows you to recognize the terrain, improving your experience when flying with visual flight rules (VFR).

![Traditional vs photoscenery comparison](screenshots/ksba-photo-comparison-compositor.jpg)

## Getting it

This project has now been merged into upstream FlightGear, so you no longer need to apply patches or build from source! Visit the [FlightGear nightly builds website](http://download.flightgear.org/builds/nightly/) to obtain the latest build for your platform of choice. Source code is also available.

## Using It

You'll need to have an `Orthophotos/` subdirectory in one of your scenery folders, alongside `Terrain/`, `Buildings/`, etc. You could put it in existing custom scenery packages, or keep your orthophotos in a separate package (for example to use them with TerraSync).

The `Orthophotos/` subdirectory is further split by geographic location to mirror other scenery subdirectories. The orthophotos themselves are named after their tile number. You can determine the tile number you need by using the [latlontotile.py](latlontotile.py) script. For example, to provide photoscenery for tile 991000, you'll provide an orthophoto named `991000.png`. This is a normal PNG file.

**_Attention: You no longer need to flip the orthophoto vertically._**

Once you have your orthophotos in place, you're all set! You can toggle the photoscenery on and off in the Rendering settings menu in FlightGear.
