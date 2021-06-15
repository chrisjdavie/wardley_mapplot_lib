import json
from pathlib import Path
from typing import List, Tuple

from adjustText import adjust_text
from matplotlib import pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from scipy import interpolate

from wardley_mappoltlib.nodes import \
    Node, build_node_list, graph_from_node_list


VISIBILITY_BOOST = 0.05


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

    plt.vlines(
        range(5), -100, +100,
        linestyles=(0, (5, 5)), colors="lightgrey", zorder=-2)

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


def plot_annotate_nodes_arrows(node_list: List[Node], ax):
    # Sort out axis points
    xx = [node.evolution for node in node_list]
    yy = [node.visibility_rescaled for node in node_list]

    plt.scatter(xx, yy, c="white", edgecolors="black")

    text = [node.title for node in node_list]
    annotations = []

    for x_i, y_i, t_i in zip(xx, yy, text):
        ann = ax.annotate(
            t_i, (x_i, y_i - 0.01), size=12, ha="right", va="bottom")
        annotations.append(
            ann
        )

    collection = []
    for node in node_list:
        if node.arrow:
            plt.hlines(
                node.visibility_rescaled,
                node.evolution,
                node.arrow.evolution,
                color="red",
                linestyles=":"
            )
            arrow = mpatches.FancyArrowPatch(
                (node.arrow.evolution, node.visibility_rescaled),
                (node.arrow.evolution + 0.01, node.visibility_rescaled),
                arrowstyle=mpatches.ArrowStyle.Fancy(
                    head_length=8, head_width=6, tail_width=0.1),
                color="red",
                zorder=10
                # linewidth=2
            )
            ax.add_patch(arrow)
            if node.arrow.type == "inertia":

                dist_back = 0.07
                width = 0.02
                height = 0.075
                x_rect = node.arrow.evolution - dist_back - width
                y_rect = node.visibility_rescaled - height/2
                ax.add_patch(
                    mpatches.Rectangle(
                        (x_rect, y_rect),
                        width,
                        height,
                        color="red"
                    )
                )

    return annotations


def build_connecting_lines(node_list: List[Node]
                           ) -> Tuple[List[Tuple[float]]]:
    xxx_dep = [
        (node.evolution, child.evolution)
        for node in node_list for child in node.children
    ]
    yyy_dep = [
        (node.visibility_rescaled, child.visibility_rescaled)
        for node in node_list for child in node.children
    ]
    return xxx_dep, yyy_dep


def plot_connecting_lines(
        xxx_dep: List[Tuple[float]], yyy_dep: List[Tuple[float]]) -> None:

    for (x_node, x_child), (y_node, y_child) in zip(xxx_dep, yyy_dep):
        plt.plot(
            [x_node, x_child],
            [y_node, y_child],
            c="black", zorder=-1)


def move_annotations_away(
        xxx_dep: List[Tuple[float]], yyy_dep: List[Tuple[float]],
        annotations) -> None:

    # make the annotations not cross the lines
    # get lots of dots along the lines plotted above
    xx_routes = []
    yy_routes = []
    for xx_tmp, yy_tmp in zip(xxx_dep, yyy_dep):
        f = interpolate.interp1d(xx_tmp, yy_tmp, fill_value="extrapolate")
        xx_routes.append(
            np.arange(min(xx_tmp), max(xx_tmp), 0.01)
        )
        yy_routes.append(
            f(xx_routes[-1])
        )
    xx_pts = np.concatenate(xx_routes)
    yy_pts = np.concatenate(yy_routes)

    # shift the annotations away from those points
    adjust_text(annotations,
                x=xx_pts,
                y=yy_pts,
                expand_points=(1.1, 1.2))


def draw_wardley_map_from_json(graph_path: Path):
    with graph_path.open("r") as graph_fh:
        graph_data = json.load(graph_fh)
    node_list: List[Node] = build_node_list(graph_data["nodes"])
    graph_from_node_list(node_list)

    fig = plt.figure(figsize=[12.8, 9.6])
    ax = fig.add_subplot()

    setup_plot(ax)
    plt.title(graph_data["title"], weight="bold", fontsize=14)
    # shift visibility
    for node in node_list:
        node.visibility_rescaled += VISIBILITY_BOOST
    annotations = plot_annotate_nodes_arrows(node_list, ax)
    xxx_dep, yyy_dep = build_connecting_lines(node_list)
    plot_connecting_lines(xxx_dep, yyy_dep)
    move_annotations_away(xxx_dep, yyy_dep, annotations)


if __name__ == "__main__":

    data_dir = Path("lul_algo")
    graph_path = data_dir / "4_api_n_TDD.json"
    draw_wardley_map_from_json(graph_path)

    image_path = data_dir / (graph_path.stem+".svg")
    plt.savefig(image_path)

    plt.show()


# graph_path = Path("fusion/data.json")

# draw_wardley_map_from_json(graph_path)

# # a rectangle
# # rect = mpatches.Rectangle(

# # )
# plt.show()
