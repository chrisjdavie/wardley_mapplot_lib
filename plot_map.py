from copy import copy
from dataclasses import dataclass
from pathlib import Path
from turtle import fillcolor
from typing import Dict, List, Tuple
import json
import os

from adjustText import adjust_text
from matplotlib import pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.legend_handler import HandlerNpoints
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
    "driven": ArrowStyle("C1", ":", "Evolution driven by research"),
    "required": ArrowStyle("C0", "--", "Evolution required for working reactor")
}


def setup_plot(ax):
    """
    Sets up Wardley Maps axis pretty close to Wardley's

    Kinda janky and probably not super portable, but works for this use case
    """
    plt.xlabel("Evolution", weight="bold", size=14)
    plt.xlim([0, 4])
    plt.xticks(
        [0, 1, 2, 3],
        ["Genesis", "Custom Built",
            "Product (+ rental)", "Commodity (+ utility)"],
        size=12
    )
    for tick in ax.get_xmajorticklabels():
        tick.set_horizontalalignment("left")
        tick.set_style("italic")

    plt.vlines(
        range(5), -100, +100,
        linestyles=(0, (5, 5)), colors="lightgrey", zorder=-2)

    ax.spines["top"].set_visible(False)

    plt.ylabel("Value Chain", weight="bold", size=14)
    plt.ylim([0, 1.0 + 2*VISIBILITY_BOOST])

    plt.yticks(
        [0, 1],
        ["Invisible", "Visible"],
        size=12
    )
    for tick in ax.get_ymajorticklabels():
        tick.set_rotation(90)
        tick.set_verticalalignment("bottom")
        tick.set_style("italic")
    ax.spines["right"].set_visible(False)

    ax.plot(1, 0, ">k", transform=ax.get_yaxis_transform(), clip_on=False)
    ax.plot(0, 1, "^k", transform=ax.get_xaxis_transform(), clip_on=False)


def plot_annotate_nodes(node_list: List[Node], ax, subcat_marker_map: Dict[str, str]):
    # Sort out axis points

    remaining: List[Node] = copy(node_list)

    for subcat, marker_style in subcat_marker_map.items():

        xx_subcat: List[Node] = [
            node.evolution for node in node_list if node.subcat == subcat]
        yy_subcat: List[Node] = [
            node.visibility_rescaled for node in node_list if node.subcat == subcat]
        for node in node_list:
            if node.subcat == subcat:
                remaining.remove(node)

        plt.scatter(
            xx_subcat,
            yy_subcat,
            **marker_style,
            s=100
        )

    xx_remain: List[Node] = [node.evolution for node in remaining]
    yy_remain: List[Node] = [node.visibility_rescaled for node in remaining]
    print(xx_remain)
    plt.scatter(
        xx_remain,
        yy_remain,
        c="white",
        edgecolors="black",
        s=100
    )

    xx = [node.evolution for node in node_list]
    yy = [node.visibility_rescaled for node in node_list]
    text = [node.title for node in node_list]
    annotations = []

    for x_i, y_i, t_i in zip(xx, yy, text):
        ann = ax.annotate(
            t_i, (x_i, y_i - 0.01), size=14, ha="left", va="bottom")
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


def build_connecting_lines(node_list: List[Node]
                           ) -> Tuple[List[Tuple[float]], List[Tuple[float]], List[bool]]:
    xxx_dep = [
        (node.evolution, child.evolution)
        for node in node_list for child in node.children
    ]
    yyy_dep = [
        (node.visibility_rescaled, child.visibility_rescaled)
        for node in node_list for child in node.children
    ]
    optional = [
        (node.optional or child.optional) for node in node_list for child in node.children
    ]
    return xxx_dep, yyy_dep, optional


def plot_connecting_lines(
        xxx_dep: List[Tuple[float]],
        yyy_dep: List[Tuple[float]],
        optional: List[bool]
) -> None:

    for (x_node, x_child), (y_node, y_child), opt in zip(xxx_dep, yyy_dep, optional):
        plt.plot(
            [x_node, x_child],
            [y_node, y_child],
            c="lightgrey" if opt else "darkgrey",
            ls="-." if opt else "--",
            zorder=-1
        )


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


def draw_wardley_map_from_json(data_path: Path, subcat_marker_map: Dict[str, str]):
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
    annotations = plot_annotate_nodes(node_list, ax, subcat_marker_map)
    plot_arrow(node_list, ax)
    xxx_dep, yyy_dep, optional = build_connecting_lines(node_list)
    plot_connecting_lines(xxx_dep, yyy_dep, optional)
    # move_annotations_away(xxx_dep, yyy_dep, annotations)
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
    xxx_dep, yyy_dep, _ = build_connecting_lines(node_list)
    plot_connecting_lines(xxx_dep, yyy_dep)
    move_annotations_away(xxx_dep, yyy_dep, annotations)

    # TODO
    # - lines grey, less emphasis
    # - icons bigger


if __name__ == "__main__":

    data_dir = Path("fusion")
    data_path = data_dir / "complex.json"
    # draw_data_from_json(data_path)
    subcat_marker_map: Dict[str, str] = {
        # , "edgecolors": "firebrick"},
        "Laser": {"marker": "^", "c": "C2"},
        "Targets": {"marker": "X", "c": "C3"},
        "Struct": {"marker": "D", "c": "C4"},
        "Plasma Physics": {"marker": "s", "c": "C5"}
    }

    ax, node_list = draw_wardley_map_from_json(data_path, subcat_marker_map)

    image_dir = Path(os.environ.get("IMAGE_DIR", data_dir))
    image_path = image_dir / (data_path.stem+".svg")

    lengend_arrows = [
        InertiaArrow.from_arrow(Arrow(0, 0, "required"), 0),
        InertiaArrow.from_arrow(Arrow(0, 0, "driven"), 0),
        Line2D([], [], label="Necessary link for reactor",
               color="darkgrey", ls="--"),
        Line2D([], [], label="Less necessary link", color="lightgrey", ls="-.")
    ] + [
        Line2D([], [], label=subcat, **marker_style, ls="")
        for subcat, marker_style in subcat_marker_map.items()
    ]

    ax.legend(
        handles=lengend_arrows,
        handler_map={
            InertiaArrow: HandlerWplArrow()
        },
        prop={"size": 12}
    )

    plt.savefig(image_path)
