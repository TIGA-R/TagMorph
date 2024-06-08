
from dataclasses import dataclass
from functools import partial
from typing import Callable
from parse_dataclasses import Node, OPCItemPath


@dataclass
class NodeStrategy:
    node: Node
    process_steps: list[Callable[[Node],Node]]

    def process(self):
        """
        Strategy function for atomic nodes
        """
        for func in self.process_steps:
            self.node = func(self.node)

def key_count() -> Callable[[set], dict]:
    """
    Closure to build a count of keys found in dicts registered to this function
    """
    count_dict = {
    }
    def count_update(group_set: set) -> dict:
        nonlocal count_dict
        for i in group_set:
            if i not in count_dict:
                count_dict[i] = 1
            else:
                count_dict[i] += 1
        return count_dict
    return count_update

def expression_format(expression_set: set, node: Node) -> Node:
    """
    Correcting expressions to remove isNull/toString expressions. Takes a few forms in our tags. 

    Added expression_set for now to print out expressions, but likely to remove later, in favor of logging.
    """
    if node.expression is None\
    or 'isNull' not in node.expression\
    or 'toString' not in node.expression:
        return node
    expression_set.add(node.expression)
    ignore_set = {'Alarm Condition'}
    for item in ignore_set:
        if item in node.expression:
            return node
    tank_set = {'Top Level', 'Interface Level', 'Tank Shut In'}
    for item in tank_set:
        if item in node.expression:
            node.expression = '\r\n'.join((line[1:] for line in node.expression.split('\r\n')[1:-1]))
            return node
    if 'Plunger Status' in node.expression:
        node.expression = 'if' + node.expression.split('if')[1] + 'if' + node.expression.split('if')[3][:-1]
        return node
    else:
        exp = node.expression.split('if')[2].rstrip('\r\n')[:-1].rstrip('\r\n\t ')
        if exp[-1] != ')' and exp[-1] != '"':
            exp += '")'
        elif exp[-1] != ')':
            exp += ')'
        node.expression = 'if' + exp
        return node


def alarm_count(key_count: Callable, node: Node) -> Node: 
    """
    Build count of all alarm keys
    """
    if node.alarms is not None:
        for alarm in node.alarms:
            key_count(set(alarm.keys()))
    return node

def update_opc_path(node: Node) -> Node:
    if isinstance(node.opcItemPath, OPCItemPath) and isinstance(node.opcItemPath.binding, str):
        node.opcItemPath.binding = "{namespaceFlag}={namespace};s=" + node.opcItemPath.binding
    return node

def add_min_history(node: Node, hours: int) -> Node:
    if isinstance(node.historyEnabled, bool) and node.historyEnabled:
        node.historyMaxAge = hours
    return node

def opc_path_change(old_str: str, new_str: str, node: Node) -> Node:
    # REVIEW THIS CODE WITH NODE/OPCITEMPATH CHANGE
    if node.opcItemPath is not None and node.valueSource == 'opc':
        node.opcItemPath.binding = node.opcItemPath.binding.replace(old_str, new_str)
    # if "opcItemPath" in node and node["opcItemPath"] and node["valueSource"] == 'opc':
    #     if isinstance(node["opcItemPath"], str):
    #         node["opcItemPath"] = node["opcItemPath"].replace(old_str, new_str)
    #     if isinstance(node["opcItemPath"], dict):
    #         node["opcItemPath"]["binding"] = node["opcItemPath"]["binding"].replace(old_str, new_str)
    return node

def history_update(node: Node) -> Node:
    if isinstance(node.historyEnabled, dict):
        node.historyEnabled = True
    return node


# alarm_count_dict = key_count()
# expression_set = set()
#
# atomic_process_steps = [
#     partial(alarm_count, alarm_count_dict),
#     partial(expression_format, expression_set),
#     history_update,
#     update_opc_path,
#     partial(opc_path_change, '~', '_t_'),
# ]
#
# NodeStrategry
