import json


with open("fusion/complex.json", "r") as fh:
    data = json.load(fh)

for item in data["nodes"]:
    vis = item["visibility"]
    if vis > 2.1 and item["subcat"] == "Targets":
        item["visibility"] += 0.1
        item["visibility"] = round(item["visibility"], 2)

with open("fusion/complex.json", "w") as fh:
    json.dump(data, fh)
