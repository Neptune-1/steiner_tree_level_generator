import itertools
from random import randint

from steiner_tree import SteinerTree


# points = ((0, 2), (1, 6), (2, 0), (3, 2), (3, 5), (5, 3), (5, 6), (7, 2))
# points = ((2, 3), (1, 9), (3, 5), (4, 1), (5, 4), (6, 5), (7, 9), (10, 2), (10, 8))


def get_points(grid, n):
    points = set()

    for i in range(n):
        points.add(grid[randint(0, len(grid) - 1)])
        grid = [(x, y) for (x, y) in grid if
                ((x not in [x for (x, y) in points]) and (y not in [y for (x, y) in points]))]
        if len(grid) == 0:
            break
    # plt.scatter([x for (x, y) in points], [y for (x, y) in points])
    # plt.show()

    return points


if __name__ == "__main__":
    terminals = ((2, 3), (1, 9), (3, 5), (4, 1), (5, 4), (6, 5), (7, 9), (10, 2), (10, 8))
    steiner_tree = SteinerTree(terminals)
    steiner_tree.start()
    complexity = steiner_tree.complexity()
    ideal_complexity = complexity[2]
    print("IDEAL:", ideal_complexity)

    data = []
    for ds in range(3):
        size = (9+ds, 9+ds)
        grid = list(itertools.combinations(range(max(size)), 2))
        grid += [(y, x) for (x, y) in grid]
        grid += [(x, x) for x in range(max(size))]

        for _ in range(1):
            terminals = tuple(get_points(grid.copy(), randint(8, 10)))
            steiner_tree = SteinerTree(terminals)
            steiner_tree.start()
            complexity = steiner_tree.complexity()
            solution = steiner_tree.manhattan_solution(show=False)
            if complexity[2] < ideal_complexity * 500:
                print(complexity)
                print("POINTS:")
                print([[x, y] for (x, y) in terminals])
                print("SOLUTION:")
                print(solution)
                data.append([[[x, y] for (x, y) in terminals], int(complexity[0]), solution, 9+ds, complexity[2]])
            print("_______________________________________________________")

    with open("tree.dart", "w") as f:
        data.sort(key=lambda x: x[4], reverse=True)
        f.write("List trees = "+str(data)+";")
    print("DONE")
