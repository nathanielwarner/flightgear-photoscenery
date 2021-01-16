#!/bin/bash
#
# Looks up all .png's and creates dds with imagemagick from them, if not already done.
# Parameter 1 is optional and specifies the root directory to scan recursively.
#             default is "local dir".
#
# Example: `./create_dds.sh /usr/share/games/flightgear/OrtoPhoto/cols4/Orthophotos/`
#

# Check if NVIDIA texture tools is installed
command -v nvcompress >/dev/null
if [[ $? -gt 0 ]]; then
	echo "ERROR: unmet dependency: 'nvcompress'."
	echo "This tool needs the NVIDIA texture tools (maybe 'apt-get install libnvtt-bin'?)"
	exit 1
fi

root="."; [[ -n "$1" ]] && root="$1"
find $root -name '*.png' | while IFS= read file; do
    dir=$(dirname $file); name=$(basename $file .png);
    echo -n "$file: ";
    if [ -f ${dir}/${name}.dds ]; then
        echo "dds already there";
    else
        echo "convert to dds (dxt1a:${dir}/${name}.dds)";
	nvcompress -bc1a $file ${dir}/${name}.dds.tmp
        mv ${dir}/${name}.dds.tmp ${dir}/${name}.dds;
    fi; done; 

echo "done."
