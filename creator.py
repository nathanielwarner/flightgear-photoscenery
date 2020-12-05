import math
import argparse
import requests
import os


def get_tile_width(lat):
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
        return '{lon: %d, lat: %d, x: %d, y: %d}' % (self.lon, self.lat, self.x, self.y)

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

        return '%s%03d%s%02d/%s%03d%s%02d' % (hem, top_lon, pole, top_lat, hem, main_lon, pole, main_lat)

    @classmethod
    def from_index(cls, index):
        lon = (index >> 14) - 180
        lat = ((index - ((lon + 180) << 14)) >> 6) - 90
        y = (index - (((lon + 180) << 14) + ((lat + 90) << 6))) >> 3
        x = index - ((((lon + 180) << 14) + ((lat + 90) << 6)) + (y << 3))
        return Bucket(lon, lat, x, y)

    @classmethod
    def from_lon_lat(cls, d_lon, d_lat):
        lat = math.floor(d_lat)
        y = int((d_lat - lat) * 8)
        width = get_tile_width(lat)
        lon = math.floor(math.floor(d_lon / width) * width)
        if lon < -180:
            lon = -180
        x = int(math.floor((d_lon - lon) / width))
        return Bucket(lon, lat, x, y)


def download(bucket, to):
    out_dir = os.path.join(to, 'Orthophotos', bucket.get_base_path())
    if not os.path.isdir(out_dir):
        os.makedirs(out_dir)
    full_out_path = os.path.join(out_dir, str(bucket.get_index()) + '.png')
    print('Downloading to: ' + full_out_path)

    if os.path.exists(full_out_path):
        print('Target orthophoto already exists')
        return

    bounds = bucket.get_bounds()
    width = int(4096 * ((get_tile_width(bucket.lat)) / 0.125))
    height = 4096
    url = 'http://services.arcgisonline.com/arcgis/rest/services/World_Imagery/MapServer/export' \
          '?bbox=%f,%f,%f,%f&bboxSR=4326&size=%d,%d&imageSR=4326&format=png24&f=image' \
          % (bounds['min_lon'], bounds['min_lat'], bounds['max_lon'], bounds['max_lat'], width, height)
    print('URL: ' + url)

    response = requests.get(url)

    if response.status_code != 200:
        print('Failed to download orthophoto')
        print('Status Code: %d' % response.status_code)
        return
    
    if response.headers['Content-Type'] != 'image/png':
        print('Received invalid response type. Expected "image/png", got "%s"' % response.headers['Content-Type'])
        return

    specified_content_length = int(response.headers['Content-Length'])
    received_content_length = 0

    with open(full_out_path, 'wb') as fd:
        for chunk in response.iter_content(chunk_size=128):
            received_content_length += len(chunk)
            fd.write(chunk)

    if (specified_content_length != received_content_length):
        print('WARNING: Expected %d bytes, but received %d bytes. The downloaded photo may be corrupt.')


def main():
    parser = argparse.ArgumentParser(description='Download photoscenery for a tile. '
                                                 'Provide either index OR lon and lat')
    parser.add_argument('--index', type=int, required=False)
    parser.add_argument('--lon', type=float, required=False)
    parser.add_argument('--lat', type=float, required=False)
    parser.add_argument('--info_only', dest='info_only', action='store_true', default=False)
    parser.add_argument('--scenery_folder', type=str, required=False, default=os.getcwd())
    args = vars(parser.parse_args())
    index = args['index']
    lon = args['lon']
    lat = args['lat']
    info_only = args['info_only']
    to = os.path.abspath(args['scenery_folder'])
    bucket = None
    if index is not None:
        bucket = Bucket.from_index(index)
    elif lon is not None and lat is not None:
        bucket = Bucket.from_lon_lat(lon, lat)
    else:
        print('You gotta give me something!')
        exit(1)

    print('Bucket index: %d' % bucket.get_index())
    print('Base path: %s' % bucket.get_base_path())
    print(bucket.get_bounds())

    if not info_only:
        download(bucket, to)


if __name__ == '__main__':
    main()
