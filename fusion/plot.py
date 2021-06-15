from pathlib import Path
from os import getcwd

from matplotlib import pyplot as plt
import matplotlib.patches as mpatches

from plot_map import draw_wardley_map_from_json

print(getcwd())


data_dir = Path("fusion")
graph_path = data_dir / "data.json"
draw_wardley_map_from_json(graph_path)

rect = mpatches.Rectangle(
    (0, 0.0), 1.2, 0.49,
    color="plum",
    zorder=-2
)
plt.gca().add_patch(rect)

image_path = data_dir / "automated.svg"
plt.savefig(image_path)

plt.show()

# TODO
# Add text for the purple box
