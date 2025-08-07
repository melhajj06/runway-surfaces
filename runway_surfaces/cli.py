from .runway import *
from .surfaces import *
from .util import *

from typing import TextIO
import click
import csv


@click.command()
@click.argument("csvfile", type=click.File('r'))
@click.argument("position", type=np.float64, nargs=2)
@click.argument("elevation", type=np.float64, nargs=1)
@click.argument("eae", type=np.float64, nargs=1)
def cli(csvfile: TextIO, position: tuple[np.float64, np.float64], elevation: np.float64, eae: np.float64):
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

    pos = (np.float64(0), np.float64(0), np.float64(elevation))
    info = get_zone_information(pos, runways, eae)
    
    zone = info["zone"]
    if zone == "N/A":
        click.echo(f"{position} was not found in any imaginary zone")
    else:
        if "runway" in info:
            if "end" in info:
                click.echo(f"({str(position[0])},{str(position[1])}) was found in the {zone} Surface for runway {info["runway"]} at end {info["end"]}. The maximum build limit is {info["build_limit"]} feet")
            else:
                click.echo(f"({str(position[0])},{str(position[1])}) was found in the {zone} Surface for runway {info["runway"]}. The maximum build limit is {info["build_limit"]} feet")
        else:
            click.echo(f"({str(position[0])},{str(position[1])}) was found in the {zone} Surface. The maximum build limit is {info["build_limit"]} feet")