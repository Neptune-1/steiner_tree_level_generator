from collections import Counter
from random import randint

import networkx as nx
from tqdm import tqdm
import itertools
from joblib import Parallel, delayed
import time
import matplotlib.pyplot as plt


def manhattan(p1, p2):
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])


class SteinerTree:

    def __init__(self, terminals: tuple):
        # init terminals
        self.terminals = terminals
        points_x = [x for (x, y) in terminals]
        points_y = [y for (x, y) in terminals]

        # init grid
        grid = list(itertools.combinations(range(max(max(points_x), max(points_y))), 2))
        grid += [(y, x) for (x, y) in grid]
        grid += [(x, x) for x in range(max(max(points_x), max(points_y)))]

        # init grid where could be steiner points
        span_grid = [(x, y) for (x, y) in grid if ((x in points_x) and (y in points_y))]

        self.grid_none_points = [p for p in span_grid if p not in terminals]

        # init graph with terminals
        self.G = nx.Graph()
        self.G.add_nodes_from(terminals)
        for p1 in terminals:
            for p2 in terminals:
                if p1 != p2:
                    self.G.add_edge(p1, p2, weight=manhattan(p1, p2))

        self.statistic = {}
        self.solution_graph = ()

        self.maximum_steiner_points_number = 6

    def calculate_weight(self, steiner_points):
        min_weight = 10000000
        min_tree = None

        G_new = self.G.copy()
        G_new.add_nodes_from(steiner_points)
        for p1 in steiner_points:
            for p2 in self.terminals:
                G_new.add_edge(p1, p2, weight=manhattan(p1, p2))

        for p1 in steiner_points:
            for p2 in steiner_points:
                if p1 != p2:
                    G_new.add_edge(p1, p2, weight=manhattan(p1, p2))

        T = nx.minimum_spanning_tree(G_new)
        weight = T.size(weight='weight')
        if min_weight > weight:
            min_weight = weight
            min_tree = T.edges

        return min_weight, tuple(min_tree)

    def start(self):
        max_steiner_n = self.maximum_steiner_points_number

        t = time.time()
        global_results = []

        for steiner_n in range(max_steiner_n):
            results = Parallel(n_jobs=-2)(
                delayed(self.calculate_weight)(combinations) for combinations in
                tqdm(list(itertools.combinations(self.grid_none_points, steiner_n))))
            global_results += results

        self.statistic = Counter((weight for weight, tree in global_results))
        self.solution_graph = min(global_results, key=lambda res: res[0])[1]
        print(time.time() - t, "s")

    def complexity(self):
        all_cases_n = sum(self.statistic.values())
        best_case = min(self.statistic.keys())
        best_cases_n = self.statistic[best_case]
        return best_case, best_cases_n, best_cases_n / all_cases_n * 1000000, self.statistic

    def manhattan_solution(self, show=True):
        edges = list(self.solution_graph)
        manhattan_edges = []
        for e in self.solution_graph:
            if e[0][0] == e[1][0] or e[0][1] == e[1][1]:
                manhattan_edges += self.line_to_one_lines(e)
                edges.remove(e)

        for e in edges:
            help_p = (e[1][0], e[0][1])
            if randint(0, 1) == 0:
                help_p = (e[0][0], e[1][1])
            if show:
                plt.scatter(help_p[0], help_p[1], c="grey")
            manhattan_edges += self.line_to_one_lines((e[0], help_p))
            manhattan_edges += self.line_to_one_lines((help_p, e[1]))

        if show:
            plt.scatter([x for (x, y) in self.terminals], [y for (x, y) in self.terminals])
            for e in self.solution_graph:
                plt.plot([e[0][0], e[1][0]], [e[0][1], e[1][1]], c="r")
            for e in manhattan_edges:
                plt.plot([e[0][0], e[1][0]], [e[0][1], e[1][1]], c="grey", lw=0.5)
            plt.show()

        return manhattan_edges

    # split horizontal or vertical line to lines with length 1
    @staticmethod
    def line_to_one_lines(edge):
        x1 = edge[0][0]
        x2 = edge[1][0]
        y1 = edge[0][1]
        y2 = edge[1][1]
        if x1 == x2:
            return [[[x1, min(y1, y2) + dy - 1], [x1, min(y1, y2) + dy]] for dy in range(1, abs(y1 - y2) + 1)]
        else:
            return [[[min(x1, x2) + dx - 1, y1], [min(x1, x2) + dx, y1]] for dx in range(1, abs(x1 - x2) + 1)]
