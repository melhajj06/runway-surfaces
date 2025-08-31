from .runway import *
from .surfaces import *
from .util import *

import click
import csv
from typing import TextIO

@click.command()
@click.argument(
    "csvfile",
    type=click.File('r'),
    help=".csv file containing runway information"
)
@click.argument(
    "position",
    type=np.float64,
    nargs=2,
    help="A 2D coordinate given by the latitude and longitude of a desired position in degrees"
)
@click.argument(
    "elevation",
    type=np.float64,
    nargs=1,
    help="The elevation of the position measured above sea level"
)
@click.argument(
    "eae",
    type=np.float64,
    nargs=1,
    help="The established airport elevation measured above sea level"
)
@click.option(
    "u", "units",
    type=click.Choice(["feet", "meters"]),
    case_sensitive=False,
    default="feet",
    help="Units of the elevation and output"
)
def cli(csvfile: TextIO, position: tuple[np.float64, np.float64], elevation: np.float64, eae: np.float64, units):
    """Get imaginary zone info given a .csv file of runways, CSVFILE, a position, POSITION, and an established airport elevation, EAE
    """

    if not csvfile.name.lower().endswith(".csv"):
        click.echo(f"{csvfile.name} is not a .csv file!")

    runways = []
    csvr = csv.DictReader(csvfile)
    for row in csvr:
        name = row["name"]
        type = row["type"].upper()
        approaches = row["approaches"].upper().split('-')
        coords = row["coords"].split('_')
        coords = [degrees_to_feet((np.float64(coords[0]), np.float64(coords[1])), position), degrees_to_feet((np.float64(coords[2]), np.float64(coords[3])), position)]
        end_names = row["end_names"].split('-')
        special_surface = True if row["special_surface"].lower() == "true" else False

        end1 = RunwayEnd(end_names[0], coords[0], ApproachTypes[approaches[0]])
        end2 = RunwayEnd(end_names[1], coords[1], ApproachTypes[approaches[1]])
        runways.append(Runway(name, RunwayTypes[type], end1, end2, special_surface=special_surface))

    pos = (0, 0, elevation / 0.3048) if units == "meters" else (0, 0, elevation)
    info = get_zone_information(pos, runways, eae)
    
    zone = info["zone"]
    if zone == "N/A":
        click.echo(f"{position} was not found in any imaginary zone")
    else:
        if units == "meters":
            info["build_limit"] = info["build_limit"] * 0.3048
        if "runway" in info:
            if "end" in info:
                click.echo(f"({str(position[0])},{str(position[1])}) was found in the {zone} Surface for runway {info["runway"]} at end {info["end"]}. The maximum build limit is {info["build_limit"]} {units}")
            else:
                click.echo(f"({str(position[0])},{str(position[1])}) was found in the {zone} Surface for runway {info["runway"]}. The maximum build limit is {info["build_limit"]} {units}")
        else:
            click.echo(f"({str(position[0])},{str(position[1])}) was found in the {zone} Surface. The maximum build limit is {info["build_limit"]} {units}")