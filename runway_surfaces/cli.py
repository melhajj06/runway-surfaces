import csv
import os

def cli_main(argv: list[str]):
    if len(argv) <= 1:
        print("No CSV file provided!")
        return
    
    if len(argv) > 2:
        print("Too many arguments!")
        return

    if not argv[1].endswith(".csv"):
        print("Not a CSV file!")
        return
    
    f = argv[1]
    path = os.path.join(os.getcwd(), f)

    if not os.path.exists(path):
        if not os.path.exists(f):
            print(f"No such file {path} or {f}")
            return
        path = f
    
    with open(path, mode='r') as csvf:
        csvr = csv.DictReader(csvf)
        for row in csvr:
            print(f"Runway: {row["Runway"]}\nType: {row["Type"]}\nApproach Types: {row["Approach Types"]}\nCoordinates: {row["Coordinates"].replace(' ', ", ")}\nSpecial Surface: {row["Special Surface"]}\n")