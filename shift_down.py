import json


with open("data.json", "r") as fh:
    data = json.load(fh)

for item in data:
    vis = item["visibility"]
    if vis >= 8:
        item["visibility"] += 3

with open("data_move.json", "w") as fh:
    json.dump(data, fh)
