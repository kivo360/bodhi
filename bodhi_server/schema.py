import copy
from copy import deepcopy
from typing import Dict, Iterable, List, Tuple

import networkx as nx
from more_itertools import flatten
from networkx import DiGraph

from bodhi_server import System
from bodhi_server.core import FlexibleModel
from bodhi_server.pytables import *
from bodhi_server.utils import *

NestedNodes = Dict[str, List[str]]


class ChildParentsResponse(FlexibleModel):
    parents: dict
    child: dict
    root_id: str = ""
    json_path: list = []


class ParentChildResponse(FlexibleModel):
    children: dict
    parent: dict


class PrePostSplit(FlexibleModel):
    pre_nodes: List[str]
    post_nodes: List[str]

    def remove_post(self, node_list: List[str]) -> Iterable[str]:
        return filter(lambda x: x not in self.post_nodes, node_list)


def get_shortest_topograph(subgraph: DiGraph) -> Tuple[DiGraph, str]:

    sorted_graphs = list(nx.all_topological_sorts(subgraph))
    graph_len = len(sorted_graphs)
    if graph_len == 0:
        raise ValueError("Must be at least one sort")
    if graph_len == 1:
        return subgraph.subgraph(sorted_graphs[0]).copy(), sorted_graphs[0][0]
    sorted_top = list(sorted(sorted_graphs, lambda x: len(x)))[0]
    root = sorted_top[0]
    return subgraph.subgraph(sorted_top).copy(), root


def get_parent_subgraph(child_id: str, parent_graph: DiGraph):
    predecessors = list(parent_graph.predecessors(child_id))
    predecessors.append(child_id)
    return parent_graph.subgraph(predecessors).copy()


class TraversalManager(FlexibleModel):
    system: System

    @property
    def network(self) -> nx.DiGraph:
        return self.system.net

    def node_name(self, node_id: str) -> str:
        return self.network.nodes[node_id]["name"]

    def node_names(self, node_id_list: List[str]) -> List[str]:
        name_list = []
        for node_id in node_id_list:
            name_list.append(self.node_name(node_id))
        return name_list

    def parents(self, child_id: str) -> dict:
        """Return the parents of a child node .

        Args:
            child_id (str): The child_id

        Returns:
            ChildParentsResponse: Both the child and all parents.
        """
        subgraph = get_parent_subgraph(child_id, self.network)
        json_subgraph, root = get_shortest_topograph(subgraph)
        json_path = nx.shortest_path(json_subgraph, root, child_id)
        subgraph.remove_node(child_id)
        sub_nodes = dict(subgraph.nodes(data=True))

        return ChildParentsResponse(
            child={child_id: self.network.nodes[child_id]},
            parents=sub_nodes,
            json_path=self.node_names(json_path),
            root_id=root,
        )

    def children(self, parent_id: str):
        succs = self.network.successors(parent_id)
        subgraph = self.network.subgraph(succs).copy()
        sub_nodes = dict(subgraph.nodes(data=True))
        return ParentChildResponse(
            parent={parent_id: self.network.nodes[parent_id]}, children=sub_nodes
        )

    def everything(self, node_id: str):
        return self.parents(node_id), self.children(node_id)

    def pre_post_split(self, nodes: NestedNodes) -> PrePostSplit:
        keys, values = nodes.keys(), flatten(nodes.values())
        keys, values = set(keys), set(values)
        # Pre Values
        uncommon = sym_diff(keys, values)
        # Post Process Values
        common = get_common(keys, values)
        return PrePostSplit(pre_nodes=uncommon, post_nodes=common)
