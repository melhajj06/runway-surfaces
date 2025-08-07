# Runway Surfaces
In the USA, airports and aviation are regulated by the [Federal Aviation Administration (FAA)](https://www.faa.gov/). Per [Far Part 77](https://www.ecfr.gov/current/title-14/chapter-I/subchapter-E/part-77), runways in an airport have "imaginary zones" which, in practice, are 3D surfaces that create zones around a runway. This module, following the regulations, generates mathematical models of the imaginary zones through lists of coordinates.

## Usage
Use the command `python -m runway_surfaces --help` for help with using the module

Check `docs/_build/html` in the project for module documentation\
The command is as follows:\
`python -m runway_surfaces CSVFILE POSITION_X POSITION_Y ELEVATION EAE`
| ARGUMENT | DESCRIPTION |
| ---------- | ---------- |
| CSVFILE | `CSVFILE` is the `.csv` file that contains all the runways and their information|
| POSITION_X | `POSITION_X` is the x-coordinate in degrees of the position in the airport |
| POSITION_Y | `POSITION_Y` is the y-coordinate in degrees of the position in the airport |
| ELEVATION | `ELEVATION` is the elevation in feet of the position in the airport |
| EAE | `EAE` is the Established Airport Elevation |

## CSV Format

| name | type | approaches | coords | end_names | special_surface |
| ----- | ----- | ----- | ----- | ----- | ----- |
| `(name)` | `utility`, `visual`, `non_precision_instrument`, `precision_instrument` `(type)` | `visual`, `non_precision_instrument`,  `precision_instrument` `(approach)-(approach)` | `(x)-(y)-(x)-(y)` | `(name)-(name)` | `true\|TRUE`,`false\|FALSE` |

## Docs
Documentation for the module can be found in `docs/_build/html`

#### Please note that all internal calculation is done in feet