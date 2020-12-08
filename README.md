# FlightGear PhotoScenery

This project brings support for photoscenery to FlightGear, the free and open-source flight simulator.
The photoscenery is an overlay, which overrides the traditional scenery textures when there is a satellite orthophoto available for the current tile.
It is fully compatible with Atmospheric Light Scattering (as well as the default pipeline), and works with your existing scenery.

Normally, FlightGear uses generic terrain textures. Photoscenery allows you to recognize the terrain, improving your experience when flying with visual flight rules (VFR).

![Traditional vs photoscenery comparison](screenshots/ksba-photo-comparison-compositor.jpg)

## Getting it

This project has now been merged into upstream FlightGear, so you no longer need to apply patches or build from source! Visit the [FlightGear nightly builds website](http://download.flightgear.org/builds/nightly/) to obtain the latest build for your platform of choice. If you're downloading the FlightGear Data package separately, please note that you should obtain this [from Git](https://sourceforge.net/p/flightgear/fgdata/ci/next/tree/), since this package is out of date on the nightly builds.

## Using It

### Prerequisites

In addition to [FlightGear nightly](http://download.flightgear.org/builds/nightly/), you'll need [Python 3](https://www.python.org/downloads/), along with the [requests package](https://pypi.org/project/requests/). Also, clone this repo (`git clone https://github.com/nathanielwarner/flightgear-photoscenery`) to get the `creator.py` script.

### Instructions

Set aside a folder that you'll use to save photoscenery. In these instructions, I'll specify it as `/home/yourname/photoscenery`.

Photoscenery is created by providing satellite orthophotos for the [scenery tiles](http://wiki.flightgear.org/Tile_Index_Scheme) you want. The [creator.py](creator.py) script automates the download of these orthophotos from ArcGIS servers. To use it, provide either the index of the tile you want (`--index`), or a latitude and longitude (`--lat` and `--lon`).

For example, to make photoscenery for the tile containing the Eiffel Tower, you would first find its coordinates. (Latitude 48.858, Longitude 2.295) Then, you run the script, providing the coordinates and your download folder.

```
python creator.py --scenery_folder /home/yourname/photoscenery --lat 48.858 --lon 2.295
```

_Note: If your system uses Python 2, you'll need to run `python3` instead of `python`._

When you run FlightGear, you'll need to go to the "Add-ons" tab of the launcher, and add the folder where you saved it (`/home/yourname/photoscenery` in this example) as an "Additional scenery folder".

Once you're loaded in (after pressing "Fly" in the launcher), you can toggle Satellite Photoscenery on and off in the Rendering settings menu (View -> Rendering Options) in FlightGear.

## Manual Instructions

You'll need to have an `Orthophotos/` subdirectory in one of your scenery folders, alongside `Terrain/`, `Buildings/`, etc. You could put it in existing custom scenery packages, or keep your orthophotos in a separate package (for example to use them with TerraSync).

The `Orthophotos/` subdirectory is further split by geographic location to mirror other scenery subdirectories. The orthophotos themselves are normal PNG files, named after their tile number. You can determine the tile number you need, as well as the base path in which to save it, by using the [creator.py](creator.py) script, passing `--info_only` as an argument to show tile information only rather than automatically download the photo.

**_Attention: You no longer need to flip the orthophoto vertically._**
