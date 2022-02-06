from dataclasses import dataclass
import json
from pathlib import Path
from typing import List, Tuple

from adjustText import adjust_text
from matplotlib import pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.legend_handler import HandlerLine2D, HandlerNpoints
import matplotlib.patches as mpatches
import numpy as np
from scipy import interpolate

from wardley_mappoltlib.nodes import \
    Arrow, Node, build_node_list, graph_from_node_list


VISIBILITY_BOOST = 0.05


@dataclass
class ArrowStyle:
    color: str
    linestyle: str
    label: str = ""


ARROW_STYLES = {
    "driven": ArrowStyle("red", ":", "Evolution driven by research"),
    "required": ArrowStyle("green", "--", "Evolution required for working reactor"),
    "inertia": ArrowStyle("red", "-")
}


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


def plot_annotate_nodes(node_list: List[Node], ax):
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

    return annotations


class InertiaArrow(Line2D):

    def __init__(self, xdata, ydata, **kw):
        super().__init__(
            xdata,
            ydata,
            marker=">",
            markevery=(1, 1),
            **kw
        )

    @classmethod
    def from_arrow(cls, arrow: Arrow, visibility):
        arrow_style: str = ARROW_STYLES[arrow.type]
        return cls(
            [arrow.evolution_start, arrow.evolution],
            [visibility, visibility],
            **arrow_style.__dict__
        )


class HandlerWplArrow(HandlerNpoints):

    def __init__(self, marker_pad=0.3, numpoints=None, **kw) -> None:
        super().__init__(marker_pad=marker_pad, numpoints=numpoints, **kw)

    def create_artists(
            self, legend, orig_handle: InertiaArrow,
            xdescent, ydescent, width, height, fontsize,
            trans):

        xdata, xdata_marker = self.get_xdata(legend, xdescent, ydescent,
                                             width, height, fontsize)
        ydata = np.full_like(xdata, (height - ydescent) / 2)
        legline = Line2D(xdata, ydata, markevery=orig_handle.get_markevery())

        self.update_prop(legline, orig_handle, legend)

        legline.set_transform(trans)

        return [legline, legline]


def plot_arrow(node_list: List[Node], ax):

    for node in node_list:
        if node.arrows:
            for arrow_data in node.arrows:
                line = InertiaArrow.from_arrow(
                    arrow_data, node.visibility_rescaled)

                ax.add_line(line)

    # for node in node_list:
    #     if node.arrows:
    #         for arrow_data in node.arrows:
    #             arrow_style = ARROW_STYLES[arrow_data.type]

    #             color = "red"
    #             linestyle = ":"
    #             if arrow_data.type == "required":
    #                 color = "green"
    #                 linestyle = "--"

    #             plt.hlines(
    #                 node.visibility_rescaled,
    #                 arrow_data.evolution_start,
    #                 arrow_data.evolution,
    #                 color=arrow_style.color,
    #                 linestyles=arrow_style.linestyle
    #             )
    #             arrow = mpatches.FancyArrowPatch(
    #                 (arrow_data.evolution, node.visibility_rescaled),
    #                 (arrow_data.evolution + 0.01, node.visibility_rescaled),
    #                 arrowstyle=mpatches.ArrowStyle.Fancy(
    #                     head_length=8, head_width=6, tail_width=0.1),
    #                 color=arrow_style.color,
    #                 zorder=10
    #                 # linewidth=2
    #             )
    #             ax.add_patch(arrow)
    #             # ax.annotate(
    #             #     '',
    #             #     xy=(arrow_data.evolution_start, node.visibility_rescaled),
    #             #     xytext=(
    #             #         arrow_data.evolution_start,
    #             #         node.visibility_rescaled
    #             #     ),
    #             #     arrowprops={"arrowstyle": "->"}
    #             # )
    #             if arrow_data.type == "inertia":

    #                 dist_back = 0.07
    #                 width = 0.02
    #                 height = 0.075
    #                 x_rect = arrow_data.evolution - dist_back - width
    #                 y_rect = node.visibility_rescaled - height/2
    #                 ax.add_patch(
    #                     mpatches.Rectangle(
    #                         (x_rect, y_rect),
    #                         width,
    #                         height,
    #                         color=arrow_style.color
    #                     )
    #                 )


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
    adjust_text(
        annotations,
        x=xx_pts,
        y=yy_pts,
        expand_points=(1.1, 1.2)
    )


def draw_wardley_map_from_json(data_path: Path):
    with data_path.open("r") as data_fh:
        data_data = json.load(data_fh)
    node_list: List[Node] = build_node_list(data_data["nodes"])
    graph_from_node_list(node_list)

    fig = plt.figure(figsize=[12.8, 9.6])
    ax = fig.add_subplot()

    setup_plot(ax)
    plt.title(data_data["title"], weight="bold", fontsize=14)
    # shift visibility
    for node in node_list:
        node.visibility_rescaled += VISIBILITY_BOOST
    annotations = plot_annotate_nodes(node_list, ax)
    plot_arrow(node_list, ax)
    xxx_dep, yyy_dep = build_connecting_lines(node_list)
    plot_connecting_lines(xxx_dep, yyy_dep)
    move_annotations_away(xxx_dep, yyy_dep, annotations)
    return ax, node_list


def draw_data_from_json(data_path: Path):
    with data_path.open("r") as data_fh:
        data_data = json.load(data_fh)
    node_list: List[Node] = build_node_list(data_data["nodes"])
    graph_from_node_list(node_list)

    fig = plt.figure(figsize=[12.8, 9.6])
    ax = fig.add_subplot()

    ax.spines["top"].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    for tick in ax.get_xmajorticklabels():
        tick.set_visible(False)
    for tick in ax.get_ymajorticklabels():
        tick.set_visible(False)
    plt.xticks([])
    plt.yticks([])
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    # setup_plot(ax)
    plt.title(data_data["title"], weight="bold", fontsize=14)
    # shift visibility
    for node in node_list:
        node.visibility_rescaled += VISIBILITY_BOOST
    annotations = plot_annotate_nodes(node_list, ax)
    xxx_dep, yyy_dep = build_connecting_lines(node_list)
    plot_connecting_lines(xxx_dep, yyy_dep)
    move_annotations_away(xxx_dep, yyy_dep, annotations)

    # TODO
    # - lines grey, less emphasis
    # - icons bigger


if __name__ == "__main__":

    data_dir = Path("fusion")
    data_path = data_dir / "simplified.json"
    # draw_data_from_json(data_path)
    ax, node_list = draw_wardley_map_from_json(data_path)

    image_path = data_dir / (data_path.stem+".svg")

    lengend_arrows = [
        InertiaArrow.from_arrow(Arrow(0, 0, "driven"), 0),
        InertiaArrow.from_arrow(Arrow(0, 0, "required"), 0)
    ]

    ax.legend(
        handles=lengend_arrows,
        handler_map={
            InertiaArrow: HandlerWplArrow()
        })

    plt.savefig(image_path)
