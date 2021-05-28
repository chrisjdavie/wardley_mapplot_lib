from json import load
import json
from pathlib import Path
from pprint import pprint

import mpl_toolkits.axisartist.axislines as AA
from mpl_toolkits.axisartist.axisline_style import AxislineStyle
from matplotlib import pyplot as plt
from matplotlib.patches import ArrowStyle


graph_file = Path("data_minimal.json")

with graph_file.open("r") as graph_fh:
    graph_data = json.load(graph_fh)

fig = plt.figure(figsize=[12.8, 9.6])
ax = fig.add_subplot()


def setup_plot(ax):
    """
    Sets up Wardley Maps axis pretty close to Wardley's

    Kinda janky and probably not super portable, but works for this use case
    """
    plt.xlabel("Evolution", weight="bold")
    plt.xlim([0, 4])
    plt.xticks(
        [0, 1, 2, 3],
        ["Genesis", "Custom Built",
            "Product (+ rental)", "Commodity (+ utility)"]
    )
    for tick in ax.get_xmajorticklabels():
        tick.set_horizontalalignment("left")
        tick.set_style("italic")
    ax.spines["top"].set_visible(False)

    plt.ylabel("Value Chain", weight="bold")
    plt.ylim([0, 1.1])

    plt.yticks(
        [0, 1],
        ["Invisible", "Visible"]
    )
    for tick in ax.get_ymajorticklabels():
        tick.set_rotation(90)
        tick.set_verticalalignment("bottom")
        tick.set_style("italic")
    ax.spines["right"].set_visible(False)

    ax.plot(1, 0, ">k", transform=ax.get_yaxis_transform(), clip_on=False)
    ax.plot(0, 1, "^k", transform=ax.get_xaxis_transform(), clip_on=False)


setup_plot(ax)

plt.show()
