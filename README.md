# Runway Surfaces
In the USA, airports and aviation are regulated by the [Federal Aviation Administration (FAA)](https://www.faa.gov/). Per [Far Part 77](https://www.ecfr.gov/current/title-14/chapter-I/subchapter-E/part-77), runways in an airport have "imaginary zones" which, in practice, are 3D surfaces that create zones around a runway. This module, following the regulations, generates mathematical models of the imaginary zones through lists of coordinates.

## Usage
- Create a `Runway` from `runway` containing all the necessary data such as runway type, approaches, endpoints as coordinates, etc...
- Use the functions in `surfaces` to obtain the vertices or edges of all the surfaces

## Docs
Check `docs` in the project

#### Please note that all internal calculation is done in feet