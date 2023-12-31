import copy
import functools
from itertools import permutations, combinations
import networkx as nx
import numpy as np
import interference_subgraph_generation
import knowledge_graph_utils

import os
def main():

    knowledge_graph = knowledge_graph_utils.get_knowledge_graph(
        'data/input_graphs/System_Architecture.xml',
        'data/input_graphs/Deployment_Config.yaml')
    file_path = 'data/callgraph_generator/temporal_callgraph_W1.npy'
    architecture = knowledge_graph_utils.get_architecture_callgraph(knowledge_graph)
    deployment = knowledge_graph_utils.get_deployment_graph(knowledge_graph)

    distinct_paths = interference_subgraph_generation.get_distinct_paths(
        knowledge_graph_utils.get_architecture_callgraph(knowledge_graph))
    colors = ['teal', 'purple', 'green']
    path_map = {}
    for index, path in enumerate(distinct_paths):
        assert len(colors) <= len(distinct_paths)
        for node in path:
            path_map[node] = colors[index]
    color_map = ['red' if "worker" in node else path_map[node] for node in knowledge_graph]

    knowledge_graph_utils.plot_graph(knowledge_graph, layout=nx.layout.kamada_kawai_layout, color_map=color_map)
    knowledge_graph_utils.plot_graph(architecture, layout=nx.layout.spring_layout)
    knowledge_graph_utils.plot_graph(deployment, layout=nx.layout.planar_layout)

    query_predicate_stacks = generate_query_predicate_stacks(knowledge_graph, 'worker1', file_path)
    query_predicate_impact_lists = []

    for query_predicate_pair in query_predicate_stacks:
        query_stack = query_predicate_pair['query']
        predicate_stack = query_predicate_pair['predicate']

        query_predicate_impact_list = compute_list_of_impacted_pairs(query_stack, predicate_stack)
        query_predicate_impact_lists.append(query_predicate_impact_list)

    ground_truth = generate_ground_truth(query_predicate_impact_lists, query_predicate_stacks)
    ground_truth['query'] = query_stack
    ground_truth['predicate'] = predicate_stack

    print("ground-truth generated!")
    return ground_truth

def generate_query_predicate_stacks(knowledge_graph, host_node,file_path):
    architecture = knowledge_graph_utils.get_architecture_callgraph(knowledge_graph)
    deployment = knowledge_graph_utils.get_deployment_graph(knowledge_graph)

    if os.path.exists(file_path):
        execution_orders = np.load(file_path, allow_pickle=True)
    else:
        execution_orders = create_temporal_callgraph(architecture, file_path)
    service_paths = interference_subgraph_generation.get_distinct_paths(architecture)
    path_of_service = {service: index for index, path in enumerate(service_paths) for service in path}

    nodes_at_host = [node for node in deployment.nodes if [node, host_node] in deployment.edges]
    execution_orders_at_host = list(
        filter(lambda execution_order_function: all(node in execution_order_function for node in nodes_at_host), execution_orders))

    query_predicate_stacks = []
    for execution_order in execution_orders_at_host:
        path_a_index = path_of_service[execution_order[0]]
        query = []
        predicate = []
        for time, service in enumerate(execution_order):
            stack_entry = {'service': service, 'starting_time': 0, 'ending_time': time + 1, 'resource_consumption': 1}
            if path_of_service[service] == path_a_index:
                query.append(stack_entry)
            else:
                predicate.append(stack_entry)

        for index, entry in enumerate(query[1:]):
            entry['starting_time'] = query[index]['ending_time']

        for index, entry in enumerate(predicate[1:]):
            entry['starting_time'] = predicate[index]['ending_time']

        query_predicate_stacks.append({'query': query, 'predicate': predicate})

    return query_predicate_stacks


def create_temporal_callgraph(call_graph: nx.DiGraph, file_path, file_suffix: str = ""):
    paths = interference_subgraph_generation.get_distinct_paths(call_graph)
    temporal_paths = []
    for combination in combinations(paths, 2):
        permut = permute_paths(*combination)
        temporal_paths.extend(permut)
    with open(file_path, 'wb') as outfile:
        np.save(outfile, np.array(temporal_paths, dtype=object))
    return temporal_paths


def permute_paths(a, b):
    """Find all possible permutations for order of calls in two paths"""
    concatenated = a + b
    result = []
    for permutation in permutations(concatenated):
        valid_permutation = True
        iter_a = 0
        iter_b = 0
        for element in permutation:
            if element in a:
                if a.index(element) < iter_a:
                    valid_permutation = False
                    break
                iter_a = a.index(element)
            if element in b:
                if b.index(element) < iter_b:
                    valid_permutation = False
                    break
                iter_b = b.index(element)
        if valid_permutation:
            result.append(permutation)
    return result

def compute_list_of_impacted_pairs(source_stack, target_stack):
    sorted_source_stack = sorted(copy.deepcopy(source_stack), key=lambda entry: entry['starting_time'], reverse=True)
    sorted_target_stack = sorted(copy.deepcopy(target_stack), key=lambda entry: entry['starting_time'], reverse=True)
    result_list = []

    while sorted_source_stack:
        current_source_node = sorted_source_stack.pop()
        current_target_list = []
        while sorted_target_stack and current_source_node['ending_time'] > sorted_target_stack[-1]['starting_time']:
            current_target_node = sorted_target_stack.pop()
            current_target_list.append(current_target_node.copy())
            if current_source_node['ending_time'] < current_target_node['ending_time']:
                current_target_node['starting_time'] = current_source_node['ending_time']
                sorted_target_stack.append(current_target_node)
        result_list.append(compute_probability_and_magnitude_of_interference(current_source_node, current_target_list))

    return result_list

def compute_probability_and_magnitude_of_interference(source_node, target_list):
    total_source_time = source_node['ending_time'] - source_node['starting_time']
    total_interference_probability = 0
    result = []
    for current_target_node in target_list:
        total_target_time = min(current_target_node['ending_time'], source_node['ending_time']) - current_target_node[
            'starting_time']
        current_magnitude = source_node['resource_consumption'] + current_target_node['resource_consumption']
        if current_magnitude < 1:
            current_magnitude = 0
        else:
            current_magnitude = current_magnitude - 1
        interference_probability = total_target_time / total_source_time
        total_interference_probability += interference_probability
        result.append({'source_node': source_node['service'], 'target_node': current_target_node['service'],
                       'probability': interference_probability, 'magnitude': current_magnitude})
    return result

def expected_impact_of_query_stack(query_predicate_impact_list):
    result = {}
    for query_node in query_predicate_impact_list:
        result[query_node[0]['source_node']] = sum([entry['magnitude'] * entry['probability'] for entry in query_node])
    return result
def sum_of_probability(query_predicate_impact_list, target_node):
    sum_of_probabilities = 0
    for entry in query_predicate_impact_list:
        for element in entry:
            if element['target_node'] == target_node:
                sum_of_probabilities += element['probability']
    return sum_of_probabilities


def generate_ground_truth(query_predicate_impact_lists, query_predicate_stacks):
    query_services = [entry['service'] for entry in query_predicate_stacks[0]['query']]
    predicate_services = [entry['service'] for entry in query_predicate_stacks[0]['predicate']]
    source_target_combinations = [(a, b) for a in query_services for b in predicate_services]

    rankings = {}
    for combination in source_target_combinations:
        rankings[combination] = rank_graphs(*combination, query_predicate_impact_lists)

    return rankings


def rank_graphs(source, target, graphs: list):
    return sorted(graphs,
                  key=functools.cmp_to_key(lambda graphA, graphB: compare_graphs(graphA, graphB, source, target)))


def compare_graphs(a, b, source, target):
    relevant_entry_a = list(filter(len, a))
    relevant_entry_b = list(filter(len, b))
    relevant_entry_a = list(filter(lambda x: x[0]['source_node'] == source, relevant_entry_a))
    relevant_entry_b = list(filter(lambda x: x[0]['source_node'] == source, relevant_entry_b))

    if relevant_entry_a and relevant_entry_b:
        relevant_entry_a = relevant_entry_a[0]
        relevant_entry_b = relevant_entry_b[0]
        probability_a = sum([entry['probability'] for entry in relevant_entry_a if entry['target_node'] == target])
        probability_b = sum([entry['probability'] for entry in relevant_entry_b if entry['target_node'] == target])
        if probability_b - probability_a == 0:
            impact_a = sum_of_probability(a, target)
            impact_b = sum_of_probability(b, target)
            return impact_a - impact_b

        else:
            return probability_b - probability_a
    else:
        if len(relevant_entry_a) == len(relevant_entry_b):
            return 0
        elif not relevant_entry_a:
            return 1
        else:
            return -1


if __name__ == '__main__':
    main()
    print("DONE!")