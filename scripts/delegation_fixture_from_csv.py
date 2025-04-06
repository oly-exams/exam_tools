import csv
import json


def parse(input):
    indata = csv.reader(input)

    data = []
    for row in indata:
        entry = {}
        entry["model"] = "ipho_core.delegation"
        entry["fields"] = {
            "name": row[1],
            "country": row[0],
        }
        data.append(entry)

    print(json.dumps(data, sort_keys=True, indent=4, separators=(",", ": ")))


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Convert CSV to Delegation fixture")
    parser.add_argument("file", type=argparse.FileType("rU"), help="Input CSV file")
    args = parser.parse_args()

    parse(args.file)
