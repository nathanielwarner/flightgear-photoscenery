#!/usr/bin/python3

# Copyright (C) 2021  Nathaniel MacArthur-Warner
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

#  WARNING: Only do this for providers whose TOS allow this!
#  WARNING: This may really strain remote ressources and cost the provider
#           real $$$, so use with care and if in doubt, ask before using!

import math
import argparse
import requests
import logging
import os
import tempfile
from PIL import Image, UnidentifiedImageError


# Ortophoto servers
# The url is a format string. 'tbounds(minlon,minlat,maxlon,maxlat)' is used for tile bounds and 'tsize(width,height)' for tile size, in pixels.
URLS = {
    # ArcGIS. suitable for the entire world. under restrictive license, see https://www.esri.com/en-us/legal/terms/full-master-agreement
    'ArcGIS': 'http://services.arcgisonline.com/arcgis/rest/services/World_Imagery/MapServer/export?bbox={tbounds[0]},{tbounds[1]},{tbounds[2]},{tbounds[3]}&bboxSR=4326&size={tsize[0]},{tsize[1]}&imageSR=4326&format=png24&f=image',
    # PNOA. only Spain. license CC-BY
    # https://pnoa.ign.es/presentacion-y-objetivo
    'PNOA': 'https://www.ign.es/wms-inspire/pnoa-ma?SERVICE=WMS&VERSION=1.1.1&REQUEST=GetMap&LAYERS=OI.OrthoimageCoverage&SRS=EPSG:4326&BBOX={tbounds[0]},{tbounds[1]},{tbounds[2]},{tbounds[3]}&WIDTH={tsize[0]}&HEIGHT={tsize[1]}&FORMAT=image/png',
    # USGS. United States only. Public domain license, see:
    # https://www.usgs.gov/faqs/what-are-terms-uselicensing-map-services-and-data-national-map?qt-news_science_products=0#qt-news_science_products
    'USGS': 'https://basemap.nationalmap.gov/arcgis/rest/services/USGSImageryOnly/MapServer/export?bbox={tbounds[0]},{tbounds[1]},{tbounds[2]},{tbounds[3]}&bboxSR=4326&size={tsize[0]},{tsize[1]}&imageSR=4326&format=png24&f=image',
    #geoportal.gov.pl only Poland (licence unknown, apart general statment as free to download not sure if via this view service)[!!! theight must be set as not larger than 1024 !!!]
    'GeoportalPL': 'https://mapy.geoportal.gov.pl/wss/service/img/guest/ORTO/MapServer/WMSServer?REQUEST=GetMap&VERSION=1.3.0&TRANSPARENT=TRUE&LAYERS=RASTER&STYLES=&CRS=CRS:84&EXCEPTIONS=xml&BBOX={tbounds[0]},{tbounds[1]},{tbounds[2]},{tbounds[3]}&WIDTH={tsize[0]}&HEIGHT={tsize[1]}&FORMAT=image/png',
    # geoservice bayern (DE/Bavaria); License CC-BY  https://geodatenonline.bayern.de/geodatenonline/seiten/wms_dop80cm
    # Max image size is 4000x4000, so you need to supply --theight 1024 or something like that
    'geoservices.bayern.de': 'https://geoservices.bayern.de/wms/v2/ogc_dop80_oa.cgi?version=1.1.1&service=WMS&request=GetMap&layers=by_dop80c&bbox={tbounds[0]},{tbounds[1]},{tbounds[2]},{tbounds[3]}&width={tsize[0]}&height={tsize[1]}&srs=EPSG:4326&exceptions=xml&format=image/png',
}

# Tile height, in degrees. This is a constant for FG
TILE_HEIGHT = 0.125


def get_tile_width(lat):
    """ Gets the width of a FG tile, in degrees. In FG, the width of a tile depends on the latitude """
    tile_table = [[0, 0.125], [22, 0.25], [62, 0.5], [76, 1], [83, 2], [86, 4], [89, 12]]
    for i in range(len(tile_table)):
        if tile_table[i][0] <= abs(lat) < tile_table[i + 1][0]:
            return float(tile_table[i][1])



class Bucket(object):
    def __init__(self, lon, lat, x, y):
        self.lon = lon
        self.lat = lat
        self.x = x
        self.y = y

    def __str__(self):
        return str(self.get_bounds())

    def get_index(self):
        return ((self.lon + 180) << 14) + ((self.lat + 90) << 6) + (self.y << 3) + self.x

    def get_bounds(self):
        width = get_tile_width(self.lat)
        return {
            'min_lat': self.lat + 0.125 * self.y,
            'max_lat': self.lat + 0.125 * (self.y + 1),
            'min_lon': self.lon + self.x * width,
            'max_lon': self.lon + (self.x + 1) * width,
            'center_lat': 0.5 * (self.lat + 0.125 * self.y + self.lat + 0.125 * (self.y + 1)),
            'center_lon': 0.5 * (self.lon + self.x * width + self.lon + (self.x + 1) * width)
        }

    def get_base_path(self):
        top_lon = int(self.lon / 10)
        main_lon = self.lon
        if 0 > self.lon != top_lon * 10:
            top_lon -= 1
        top_lon *= 10

        if top_lon >= 0:
            hem = 'e'
        else:
            hem = 'w'
            top_lon *= -1

        if main_lon < 0:
            main_lon *= -1

        top_lat = int(self.lat / 10)
        main_lat = self.lat
        if 0 > self.lat != top_lat * 10:
            top_lat -= 1

        top_lat *= 10
        if top_lat >= 0:
            pole = 'n'
        else:
            pole = 's'
            top_lat *= -1

        if main_lat < 0:
            main_lat *= -1

        return os.path.join('%s%03d%s%02d' % (hem, top_lon, pole, top_lat), '%s%03d%s%02d' % (hem, main_lon, pole, main_lat))

    @classmethod
    def from_index(cls, index):
        """ Factory method: create a Bucket from a FlightGear index """
        lon = (index >> 14) - 180
        lat = ((index - ((lon + 180) << 14)) >> 6) - 90
        y = (index - (((lon + 180) << 14) + ((lat + 90) << 6))) >> 3
        x = index - ((((lon + 180) << 14) + ((lat + 90) << 6)) + (y << 3))
        return cls(lon, lat, x, y)

    @classmethod
    def from_lon_lat(cls, d_lon, d_lat):
        """ Factory method: create a Bucket from a lon, lat pair """
        lat = math.floor(d_lat)
        y = int((d_lat - lat) * 8)
        width = get_tile_width(lat)
        lon = math.floor(math.floor(d_lon / width) * width)
        if lon < -180:
            lon = -180
        x = int(math.floor((d_lon - lon) / width))
        return cls(lon, lat, x, y)


class ImageProvider:
    """ Downloads a image from a URL """

    def __init__(self, url):
        """
        Params:
            url: format string with the url. 'tbounds(minlon,minlat,maxlon,maxlat)' is used for tile bounds and 'tsize(width,height)' for tile size, in pixels. See examples.
        """
        self._url = url

    def download(self, bucket, outpath, tnum=(1,1), theight=512, dry_run=False):
        """ Downloads a FG bucket and save in outpath.
        A bucket is the final image for FG. A tile is each one of the little images that create a bucket. Many online
        services won't allow downloading huge images at once, and you must cut buckets down into tiles.

        Params:
            bucket: a Bucket object
            outpath: string, path to the output file
            tnum: (cols,rows) number of tiles in the bucket. Use (1,1), (2,2), (4,4)... other pairs are not tested
            theight: height of a tile, in pixels. The width depends on the latitude. Use power of two numbers: 512, 1028, 2048... The final image will have a theight of tsize*tnum
            dry_run: if True, do not donwload anything. Useful for testing
        """

        # final size of a tile, in pixels. Width depends on the latitude. Both sizes must be power of two
        tsize = (int(theight * ((get_tile_width(bucket.lat)) / TILE_HEIGHT)), theight)
        # bounds of the bucket
        bounds = bucket.get_bounds()
        # width of the bucket, in degrees
        bwidth = get_tile_width(bucket.lat)
        # size of the tile, in degrees
        gtwidth = bwidth / tnum[0]
        gtheight = TILE_HEIGHT / tnum[1]
        # An array with files objects with each tile
        ftiles = []

        for r in range(0, tnum[1]):
            for c in range(0, tnum[0]):
                min_lon = bounds['min_lon'] + c * gtwidth
                min_lat = bounds['min_lat'] + r * gtheight
                max_lon = min_lon + gtwidth
                max_lat = min_lat + gtheight
                tbounds = (min_lon, min_lat, max_lon, max_lat)
                ftiles.append(self._download_tile(tbounds=tbounds, tsize=tsize, dry_run=dry_run))
        if not dry_run:
            logging.info('Joining tiles to %s', outpath)
            with open(outpath, 'wb') as fout:
                # note we always combine all tiles, even in the (1,1) case
                self._join(fout, ftiles=ftiles, tnum=tnum,)
        for f in ftiles:
            f.close()

    def _download_tile(self, tbounds, tsize=(512, 256), dry_run=False):
        """ Downloads a tile from the remote server and returns a file object.
        A bucket is the final image for FG. A tile is each one of the little images that create a bucket. Many online
        services won't allow downloading huge images at once, and you must cut buckets down into tiles.

        Params:
            tbounds: bounds of the tile, in degrees
            tsize: size of the tile, in pixels
            dry_run: if True, do not donwload anything. Useful for testing

        Returns:
            The tile, as a file object.
        """

        fout = tempfile.NamedTemporaryFile(mode='w+b')
        url = self._url.format(tbounds=tbounds, tsize=tsize)
        logging.info('Downloading tile=%s from url=%s', fout.name, url)

        if not dry_run:
            response = requests.get(url)

            if response.status_code != 200:
                raise Exception('Failed to download orthophoto. status={}'.format(response.status_code))
            if response.headers['Content-Type'] != 'image/png':
                raise Exception('Received invalid response type. Expected "image/png", got content_type="{}"'.format(response.headers['Content-Type']))

            for chunk in response.iter_content(chunk_size=128):
                fout.write(chunk)

        # move to the begining of the file: it must be read to combine these files into a bucket
        fout.seek(0)
        return fout

    def _join(self, fout, ftiles, tnum=(1,1)):
        """ Join a collection of files (tile images) into a single file.

        Params:
            fout: File object to save the final image
            ftiles: the array of files with the files. First cols, then rows.
            tnum: (cols,rows) in tiles for a bucket
        """
        try:
            images = [Image.open(x) for x in ftiles]
        except UnidentifiedImageError:
            logging.error("PIL.UnidentifiedImageError: this usually means that a tile couldn't be downloaded. Exiting")
            raise
        width = images[0].size[0]
        height = images[0].size[1]
        new_im = Image.new('RGB', (width * tnum[0], height * tnum[1]))
        for c in range(0, tnum[0]):
            for r in range(0, tnum[1]):
                # remember: for paste(), (0,0) is the upper left corner
                new_im.paste(images[r * tnum[0] + c], (c * width, (tnum[1] - r - 1) * height))
        new_im.save(fout)


def main():
    parser = argparse.ArgumentParser(description="Download photoscenery for a tile. Provide either index OR lon and lat")
    parser.add_argument('--index', type=int, required=False, help="FG tile index to download. It has preference on lat,lon")
    parser.add_argument('--lon', type=float, required=False, help="Longitude included inside the tile to download. Ignored if an index is provided")
    parser.add_argument('--lat', type=float, required=False, help="Latitude included inside the tile to download. Ignored if an index is provided")
    parser.add_argument('--info_only', dest='info_only', action='store_true', default=False, help="Print bucket information and exit.")
    parser.add_argument('--theight', type=int, required=False, default=2048, help='''
        Height of a tile, in pixels. Defaults to 2048. The final image will have theight*cols pixels. Use only power of two numbers.
        Note that most orthophoto servers will not serve orthophotos with any dimension greater than 4096.
    ''')
    parser.add_argument('--cols', type=int, default=1, help="Number of rows and cols for tiles in a bucket. Use only power of two numbers ")
    parser.add_argument('--provider', default='ArcGIS', help="Name of the image provider. Currently: ArcGIS (default, covers the whole world), PNOA (Spain), or USGS (United States)")
    parser.add_argument('--dry_run', dest='dry_run', action='store_true', default=False, help="If set, do not download anything, but show what would be downloaded.")
    parser.add_argument('--verbose', dest='verbose', action='store_true', default=False, help="If set, be verbose")
    parser.add_argument('--scenery_folder', type=str, required=False, default=os.getcwd(), help="Scenery directory, for the output")
    parser.add_argument('--overwrite', dest='overwrite', action='store_true', default=False, help='Overwrite the orthophoto if it already exists')
    args = vars(parser.parse_args())

    logging.basicConfig(level=(logging.DEBUG if args['verbose'] else logging.INFO))

    index = args['index']
    lon = args['lon']
    lat = args['lat']
    # create the bucket from the user input
    bucket = None
    if index is not None:
        bucket = Bucket.from_index(index)
    elif lon is not None and lat is not None:
        bucket = Bucket.from_lon_lat(lon, lat)
    else:
        logging.error('You gotta give me lon, lat or index!')
        exit(1)

    print('Bucket: %s. Index: %s' % (bucket, bucket.get_index()))

    if args['info_only']:
        exit(0)


    # create the output directory
    dir_out_path = os.path.join(os.path.abspath(args['scenery_folder']), 'Orthophotos', bucket.get_base_path())

    if not args['dry_run']:
        os.makedirs(dir_out_path, exist_ok=True)
    full_out_path = os.path.join(dir_out_path, str(bucket.get_index()) + '.png')

    if not (args['dry_run'] or args['overwrite']) and os.path.exists(full_out_path):
        logging.error('Target orthophoto already exists, skipping. Pass --overwrite to override this check.')
        exit(1)

    provider = ImageProvider(URLS[args['provider']])
    provider.download(bucket, full_out_path, tnum=(args['cols'],args['cols']), theight=args['theight'], dry_run=args['dry_run'])



if __name__ == '__main__':
    main()
