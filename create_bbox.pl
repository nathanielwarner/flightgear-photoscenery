#!/usr/bin/perl
#############################################################################
# Wrapper for Nathaniels Flightgear Ortophoto generator creator.py,         #
# to fetch images for a bigger area.                                        #
#                                                                           #
#  WARNING: Only do this for providers whose TOS allow this!                #
#  WARNING: This may really strain remote ressources and cost the provider  #
#           real $$$, so use with care and if in doubt, ask before using!   #
#                                                                           #
#############################################################################
#  This program is free software; you can redistribute it and/or modify     #
#  it under the terms of the GNU General Public License as published by     #
#  the Free Software Foundation; either version 2 of the License, or        #
#  (at your option) any later version.                                      #
#                                                                           #
#  This program is distributed in the hope that it will be useful,          #
#  but WITHOUT ANY WARRANTY; without even the implied warranty of           #
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the            #
#  GNU General Public License for more details.                             #
#                                                                           #
#  You should have received a copy of the GNU General Public License        #
#  along with this program; if not, write to the Free Software              #
#  Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111, USA.   #
#############################################################################

use strict;
use Getopt::Long qw(:config no_ignore_case);
use Data::Dumper qw(Dumper);

my $latLL=0;
my $lonLL=0;
my $latUR=0;
my $lonUR=0;

my $arg_ok = GetOptions (
    'latll|latLL=f'  => \$latLL,
    'lonll|lonLL=f'  => \$lonLL,
    'latur|latUR=f'  => \$latUR,
    'lonur|lonUR=f'  => \$lonUR
);
if (!$arg_ok | $#ARGV < 0 || !$latLL || !$lonLL || !$latUR || !$lonUR ) {
        if (!$arg_ok) { print "Did you forget to separate creator.py options with \"--\"?\n"; }
        
        print "Use FGFS ortophoto creator.py to fetch a bigger area.\n";
        print "Synopsis:\n";
        print "  ./create_bbox.pl <options> -- <creator.py options>\n";
        print "  ./create_bbox.pl --latLL <lat> --lonLL <lon> --latUR <lat> --lonUR <lon> -- <creator.py opts>\n";
        print " LL=lowerleft corner, UR=upper right corner\n";
        print " Note: creator.py options must be given at the end after double-dash (... -- <creator.py opts>)\n";
        print "\nExample: download Innsbruck region to Achensee (dry run)\n";
        print "`./create_bbox.pl --latLL 47.1967 --lonLL 11.1984 --latUR 47.5321 --lonUR 11.7682 -- \\\n";
        print "                         --cols 6 --scenery_folder /usr/share/games/flightgear/OrtoPhoto/ --dry_run`\n";
        exit 9;
}

# print some warning
print "\nWARNING: Only do this for providers whose TOS allow this!\n";
print "WARNING: This may really strain remote ressources and cost the provider\n";
print "         real \$\$\$, so use with care and if in doubt, ask before using!\n\n";
sleep(5);

# Sample the tiles and download the indexes that weren't downloaded in this run
my %seenIDX = ();
for (my $lat=$latLL; $lat <= $latUR; $lat=$lat+0.05) {
    for (my $lon=$lonLL; $lon <= $lonUR; $lon=$lon+0.05) {
	my $cmd = "python3 creator.py --lat \"$lat\" --lon \"$lon\" --info_only";
	print "cmd=$cmd\n";
        my $output = `$cmd`;
        if ($output !~ /Index: (\d+)/) {
            print "ERROR: could not get tile index from command result.\n";
            print "       result was: $output\n";
            exit 9;
        }
        my $tileIDX = $1;
        if ( !exists($seenIDX{$tileIDX}) ) {
            # needs download
            print "Tile $tileIDX needs download\n";
            $seenIDX{$tileIDX} = 1;
            
  	    my $cmd = "python3 creator.py --index $tileIDX @ARGV";
            print "cmd=$cmd\n";
            $output = `python3 creator.py --index $tileIDX @ARGV`;
            print $output;
	    print "\n";
            
        } else {
            # already fetched
            #print "$lat, $lon: $tileIDX\n";
        }
        
    }
}


print "all done.\n"
