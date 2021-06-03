from copy import deepcopy
import json
from pathlib import Path
from pprint import pprint

from adjustText import adjust_text
from matplotlib import pyplot as plt
import numpy as np
from scipy import interpolate

from wardley_mappoltlib.nodes import build_node_list, graph_from_node_list


VISIBILITY_BOOST = 0.05

graph_file = Path("data_minimal.json")

with graph_file.open("r") as graph_fh:
    graph_data = json.load(graph_fh)
node_list = build_node_list(graph_data)
graph_from_node_list(node_list)

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
    plt.ylim([0, 1.0 + 2*VISIBILITY_BOOST])

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


# Sort out axis points
xx = [node.evolution for node in node_list]
yy = [node.visibility_rescaled + VISIBILITY_BOOST for node in node_list]
text = [node.title for node in node_list]
annotations = []

for x_i, y_i, t_i in zip(xx, yy, text):
    annotations.append(
        ax.annotate(t_i, (x_i, y_i - 0.01), ha="center", va="top", size=12)
    )

setup_plot(ax)

plt.scatter(xx, yy, c="white", edgecolors="black")


def plot_connecting_lines(node_list):
    # plot dependency lines
    for node in node_list:
        for child in node.children:
            plt.plot(
                [node.evolution,
                 child.evolution],
                [node.visibility_rescaled + VISIBILITY_BOOST,
                    child.visibility_rescaled + VISIBILITY_BOOST],
                c="black", zorder=-1)

    xx_routes = []
    yy_routes = []
    for node in node_list:
        for child in node.children:
            xx_tmp = [node.evolution, child.evolution]
            yy_tmp = [node.visibility_rescaled + VISIBILITY_BOOST,
                      child.visibility_rescaled + VISIBILITY_BOOST]
            f = interpolate.interp1d(xx_tmp, yy_tmp, fill_value="extrapolate")
            xx_routes.append(
                np.arange(min(xx_tmp), max(xx_tmp), 0.01)
            )
            yy_routes.append(
                f(xx_routes[-1])
            )

    xx_pts = np.concatenate(xx_routes)
    yy_pts = np.concatenate(yy_routes)

    # shift the annotations
    adjust_text(annotations,
                x=xx_pts,
                y=yy_pts,
                expand_points=(1.1, 1.5),
                force_points=0.15)


plot_connecting_lines(node_list)


plt.show()

# TODO
# - graph to object (use dataclass)
# - branching plot
# - node-to-node plot
# - dfs, left-wise line for plotting
# - employ adjust text to avoid overlap
# - more points
# - see!
# - type the functions
