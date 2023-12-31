import itertools

import networkx as nx

import knowledge_graph_utils


def get_distinct_paths(graph: nx.DiGraph) -> list:
    start = [node for node, in_degree in graph.in_degree if in_degree == 0]
    end = [node for node, out_degree in graph.out_degree if out_degree == 0]
    paths = [list(nx.all_simple_paths(graph, source, target)) for source, target in itertools.product(start, end)]
    paths = list(map(lambda e: e[0], filter(len, paths)))
    return paths


def is_interference_path(path: list, graph: nx.DiGraph, distinct_paths: list) -> bool:
    hosts = list(filter(lambda n: graph.nodes[n]['type'] == 'host', graph.nodes))

    if not all(True for host in hosts if host in path):
        return False

    for host in hosts:
        if host in path:
            other_hosts = list(filter(lambda h: h != host, hosts))
            for other_host in other_hosts:
                if other_host in path:
                    return False
            break

    distinct_path_occurrences = {index: 0 for index, _ in enumerate(distinct_paths)}
    for node in path:
        for index, distinct_path in enumerate(distinct_paths):
            if node in distinct_path:
                distinct_path_occurrences[index] += 1

    distinct_path_counter = 0
    for value in distinct_path_occurrences.values():
        if value:
            distinct_path_counter += 1

    return distinct_path_counter == 2
