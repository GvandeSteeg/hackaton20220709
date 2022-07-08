import logging
import os
from collections import defaultdict
from csv import DictWriter
from datetime import datetime
from pprint import pprint

import requests


def extract_date_and_pipeline(request_dict: dict[str, str]):
    results_dict = {
        "data_import": 0,
        "mapping": 0,
        "snps": 0,
        "assembly": 0,
        "rna-seq": 0,
        "annotation": 0,
    }
    date = datetime.strptime(request_dict["Created"], "%a %b %d %H:%M:%S %Y")
    split = request_dict["Subject"].lower().split()
    index = split.index("trigger")
    target = split[index + 1 :]
    if "data" in target and "import" in target:
        target_data = target.index("data")
        data_import = f"{target[target_data]}_{target[target_data + 1]}"
        target[0] = data_import
        target.pop(1)
    for key in results_dict:
        if key in target:
            results_dict[key] += 1

    return date, results_dict


def count(*items: dict[str, str]):
    fdict = defaultdict(lambda: defaultdict(int))
    for item in items:
        item_date, results_dict = extract_date_and_pipeline(item)
        item_date = item_date.strftime("%Y/%m")
        for key, value in results_dict.items():
            fdict[item_date][key] += value

    for d in fdict:
        fdict[d]["requests"] = max(fdict[d].values())
        fdict[d] = dict(fdict[d])
    fdict = dict(fdict)

    return fdict


def convert_to_csv(data_dict: dict[str, dict[str, int]]):
    rows = {}
    for date, data_requests in sorted(data_dict.items()):
        row = {
            "Year/Month": date,
            "Requests": data_requests["requests"],
            "Data_Import": data_requests["data_import"],
            "Assembly": data_requests["assembly"],
            "Annotation": data_requests["annotation"],
            "Mapping": data_requests["mapping"],
            "SNP_Calling": data_requests["snps"],
            "RNA-seq": data_requests["rna-seq"],
        }
        year = int(row["Year/Month"].split("/")[0])
        try:
            rows[year] += [row]
        except KeyError:
            rows[year] = [row]

    for years, data in rows.items():
        with open(f"{years}_results.csv", "w") as fout:
            csvout = DictWriter(
                fout,
                fieldnames=[
                    "Year/Month",
                    "Requests",
                    "Data_Import",
                    "Assembly",
                    "Annotation",
                    "Mapping",
                    "SNP_Calling",
                    "RNA-seq",
                ],
            )
            csvout.writeheader()
            csvout.writerows(data)


s = requests.Session()

password = os.environ["PASSWORD"]
logging.info("Getting cookies")
s.post("https://rt.sanger.ac.uk", {"user": "gv4", "pass": password})

header = {"Referer": "https://rt.sanger.ac.uk"}
s.headers.update(header)

params = {"query": "Requestor.EmailAddress='sapp@sanger.ac.uk'"}
url = "https://rt.sanger.ac.uk/REST/1.0/search/ticket"
logging.info("Searching SAPP tickets")
r = s.post(url, params=params).content.decode("utf-8").strip().split("\n")[2:]
tickets = {int(x[0][:-1]) for x in map(lambda r: r.split(), r) if "trigger" in x}

url = "https://rt.sanger.ac.uk/REST/1.0/ticket/{0}/show"
myld = []
for i, ticket in enumerate(tickets):
    if i and i % 10 == 0:
        logging.info(f"Parsing tickets: {i}/{len(tickets)}")
    elif i == len(tickets)-1:
        logging.info(f"Parsing tickets: {len(tickets)}/{len(tickets)}")
    r = s.post(url.format(ticket)).content.decode("utf-8").strip().split("\n")[2:]

    myl = [x for x in map(lambda x: x.split(": "), r) if len(x) > 1]
    myld.append(dict(myl))

logging.info("Counting data")
convert_to_csv(count(*myld))
