import matplotlib.pyplot as plt


# start new plot
plt.clf()
plt.xlabel("Proportional Euclidean Distance")
plt.ylabel("Percentage Timewindows Attended")
plt.title("Test plot")

together = [(0, 1.0, 0.4), (25, 1.0127692669427917, 0.41), (50, 1.016404709797609, 0.41), (75, 1.1043426359673716, 0.42), (100,
                                                                                                                           1.1610446924342996, 0.44), (125, 1.1685687930691457, 0.43), (150, 1.3486407784550272, 0.45), (250, 1.4013999168008104, 0.45)]
together.sort()

for x, y, z in together:
    plt.annotate(str(x), xy=(y, z), size=8)

eucs = [y for (x, y, z) in together]
covers = [z for (x, y, z) in together]

p1 = plt.plot(eucs, covers, color="black", alpha=0.5)
plt.show()
