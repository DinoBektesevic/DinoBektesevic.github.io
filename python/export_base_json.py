import argparse
import json


def guessDatasetContent(datasetEntry):
    """Make an educated quess on what kind of dataset
    JSON entry we are given: an SDSS field, star, Moon
    or a plain label.
    """
    if "fS" in datasetEntry.keys():
        return "dataFields"
    elif "Stellar Magnitude" in datasetEntry.keys():
        return "dataStars"
    elif "mAlt" in datasetEntry.keys():
        return "dataMoon"
    elif "text" in datasetEntry.keys():
        return "AltAzLabels"


def create_base_json(altairJson, baseJson, pretty_print=False, indent=4):
    """Create a base.json file from a given Vega JSON file.

    A base JSON contains all the information required for vega-lite
    to render a plot, but does not contain data. Expected data entries
    are found under the `datasets` key and are named as follows:
        - dataFields
        - dataStars
        - dataMoon

    Vega's default behaviour is to name and refer to individual datasts with
    a sha or a random set of strings. This will be replaced appropriately with
    above keys. 
    """
    with open(altairJson, "r") as f:
        data = json.load(f)

    base = {}
    for key in ("config", "hconcat", "$schema"):
        base[key] = data[key]
        base["datasets"] = {}

    shaContentPairs = {}
    for datasetSha in data["datasets"].keys():
        datasetContent = guessDatasetContent(data["datasets"][datasetSha][0])
        if datasetContent == "AltAzLabels":
            base["datasets"][datasetSha] = data["datasets"][datasetSha]
        else:
            base["datasets"][datasetContent] = []
            shaContentPairs[datasetSha] = datasetContent

    # produce a string from our dict, replace the SHA for sensible column names
    # and write the string to base.json
    baseJsonStr = json.dumps(base)
    for sha, name in shaContentPairs.items():
        baseJsonStr = baseJsonStr.replace(sha, name)
        base = json.loads(baseJsonStr)

    with open(baseJson, "w") as f:
        if pretty_print:
            json.dump(base, f, indent=indent)
        else:
            json.dump(base, f)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a base.json from a Vega JSON file.")

    group = parser.add_mutually_exclusive_group()
    group.add_argument("input", type=str, action="store", nargs="?")
    group.add_argument("-i", "--input-json", default="altair_with_moon_final.json",
                       help="Input Vega JSON plot file from which a base will be made.")
    parser.add_argument("-o", "--output-json", default="base.json",
                        help="Output base JSON file path.")
    parser.add_argument("-p", "--pretty-print", action="store_true",
                        help="Produce a human readable base.json")
    parser.add_argument("--indent", type=int, default=4,
                        help="N. spaces in indentation. Must use --pretty-print.")

    args = parser.parse_args()
    vegaJson = args.input_json if args.input is None else args.input
    create_base_json(vegaJson, args.output_json, args.pretty_print, args.indent)
