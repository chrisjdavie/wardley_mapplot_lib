import json


with open("fusion/complex.json", "r") as fh:
    data = json.load(fh)

for item in data["nodes"]:
    vis = item["visibility"]
    if vis >= 1.12:
        item["visibility"] -= 0.05
        item["visibility"] = round(item["visibility"], 2)
        print(item["code"])

with open("fusion/complex.json", "w") as fh:
    json.dump(data, fh)
