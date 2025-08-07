# Runway Surfaces
In the USA, airports and aviation are regulated by the [Federal Aviation Administration (FAA)](https://www.faa.gov/). Per [Far Part 77](https://www.ecfr.gov/current/title-14/chapter-I/subchapter-E/part-77), runways in an airport have "imaginary zones" which, in practice, are 3D surfaces that create zones around a runway. This module, following the regulations, generates mathematical models of the imaginary zones through lists of coordinates.

## Usage
Use the command `python runway_surfaces --help` for help with using the module

Check `docs/_build/html` in the project for module documentation\
The command is as follows:\
`python runway_surfaces CSVFILE POSITION_X POSITION_Y ELEVATION EAE`
| ARGUMENT | DESCRIPTION |
| ---------- | ---------- |
| CSVFILE | `CSVFILE` is the `.csv` file that contains all the runways and their information|
| POSITION_X | `POSITION_X` is the x-coordinate in degrees of the position in the airport |
| POSITION_Y | `POSITION_Y` is the y-coordinate in degrees of the position in the airport |
| ELEVATION | `ELEVATION` is the elevation in feet of the position in the airport |
| EAE | `EAE` is the Established Airport Elevation |

## CSV Format

| name | type | approaches | coords | end names | special surface |
| ----- | ----- | ----- | ----- | ----- | ----- |
| This is the name of the runway | This is the type of the runway. Acceptable values are `utility`, `visual`, `non_precision_instrument`, and `precision_instrument` | This is the type of approaches at either end of the runway. E.g if runway `10-3` has approach types `visual` at one end and `non_precision_instrument` at the other, a value of `visual non_precision_instrument` is accepted. Acceptable values are `visual`, `non_precision_instrument`, and `precision_instrument` | The coordinates of both ends of the runway go here in the form `(x y) (x y)` | The ends of the runway should be named here in the form `end1 end2` | Per regulation, runways with specially prepared hard surfaces need to be treated differently. This value is either `true` or `false` |

## Docs

#### Please note that all internal calculation is done in feet