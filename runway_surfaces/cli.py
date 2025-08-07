import csv
import re
import os
import surfaces as sf
import click
from typing import TextIO
import util
import runway as rn

@click.command()
@click.argument("csvfile", type=click.File('r'))
@click.argument("position", type=float, nargs=2)
@click.argument("elevation", type=float, nargs=1)
@click.argument("eae", type=float, nargs=1)
def cli(csvfile: TextIO, position: tuple[float, float], elevation: float, eae: float):
    """Get imaginary zone info given a .csv file of runways, CSVFILE, a position, POSITION, and an established airport elevation, EAE
    """

    if not csvfile.name.lower().endswith(".csv"):
        click.echo(f"{csvfile.name} is not a .csv file!")

    runways = []
    csvr = csv.DictReader(csvfile)
    for row in csvr:
        name = row["name"]
        type = row["type"].upper()
        approaches = row["approaches"].upper().split(' ')
        coords = re.sub(r"[()]", row["coords"], '').split(' ')
        coords = [(coords[0], coords[1]), (coords[2], coords[3])]
        end_names = row["end names"].split(' ')
        special_surface = True if row["special surface"].lower() == "yes" else False

        end1 = rn.RunwayEnd(end_names[0], coords[0], rn.ApproachTypes[approaches[0]])
        end2 = rn.RunwayEnd(end_names[1], coords[1], rn.ApproachTypes[approaches[1]])
        runways.append(rn.Runway(name, rn.RunwayTypes[type], end1, end2, special_surface=special_surface))

    position = util.degrees_to_feet(position)
    info = sf.get_zone_information(util.t3d(position, elevation), runways, eae)
    
    zone = info["zone"]
    if zone == "N/A":
        click.echo(f"{position} was not found in any imaginary zone")
    else:
        if "runway" in info:
            if "end" in info:
                click.echo(f"{position} was found in the {zone} Surface for runway {info["runway"]} at end {info["end"]}. The maximum build height is {info["build_height"]} feet")
            else:
                click.echo(f"{position} was found in the {zone} Surface for runway {info["runway"]}. The maximum build height is {info["build_height"]} feet")
        else:
            click.echo(f"{position} was found in the {zone} Surface. The maximum build height is {info["build_height"]} feet")


