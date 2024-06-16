from dataclasses import asdict, dataclass
from typing import Callable
from .tag_dataclasses import Binding, Node, OPCItemPath

@dataclass
class NodeStrategy:
    node: Node
    process_steps: list[Callable[[Node],Node]]

    def process(self) -> Node:
        """
        Strategy function for atomic nodes
        """
        for func in self.process_steps:
            self.node = func(self.node)
        return self.node


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

def return_node_unchanged(node: Node) -> Node:
    """
    A base strategy that performs no action - used primarily for testing
    """
    return node


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
    """
    Apply OPC-UA prefix parameters to opcpath string
    """
    if isinstance(node.opcItemPath, Binding) and isinstance(node.opcItemPath.binding, str):
        node.opcItemPath.binding = "{namespaceFlag}={namespace};s=" + node.opcItemPath.binding
    return node

def add_min_history(node: Node, hours: int) -> Node:
    """
    Set a minimum history to any/all tags with history enabled (truthy)
    """
    if isinstance(node.historyEnabled, bool) and node.historyEnabled:
        node.historyMaxAge = hours
    return node

def opc_path_change(old_str: str, new_str: str, node: Node) -> Node:
    """
    Generic function to substitute opc path substring
    """
    # REVIEW THIS CODE WITH NODE/OPCITEMPATH CHANGE
    if node.opcItemPath is not None and node.valueSource == 'opc' and isinstance(node.opcItemPath.binding, str):
        node.opcItemPath.binding = node.opcItemPath.binding.replace(old_str, new_str)
    # if "opcItemPath" in node and node["opcItemPath"] and node["valueSource"] == 'opc':
    #     if isinstance(node["opcItemPath"], str):
    #         node["opcItemPath"] = node["opcItemPath"].replace(old_str, new_str)
    #     if isinstance(node["opcItemPath"], dict):
    #         node["opcItemPath"]["binding"] = node["opcItemPath"]["binding"].replace(old_str, new_str)
    return node

def binding_change(old_str: str, new_str: str, node:Node) -> Node:
    for field in node.binding_fields:
        bind_field = getattr(node, field)
        binding = bind_field.binding
        if isinstance(binding, bool):
            continue
        if old_str in binding:
            setattr(bind_field, 'binding', binding.replace(old_str, new_str))
    return node

    

def history_update(node: Node) -> Node:
    """
    Eliminate historyEnabled parameter from node and modify to be strictly True
    """
    if isinstance(node.historyEnabled, dict):
        node.historyEnabled.binding = True
    return node

def type_prefix_removal(node: Node) -> Node:
    """
    remove extra [{tag provider}]_types_ prefix from child UDTs
    """
    if node.typeId:
        node.typeId = node.typeId.split(']_types_/')[1] if ']_types_/' in node.typeId else node.typeId
    return node

def type_case_correction(missing_udt_dict: dict, udt_name_set: set, area: str, node: Node) -> Node:
    """
    Function used to address ignition bug which does not properly apply UDTs to instances if case does not match perfectly.

    TODO: Function requires testing
    """
    if node.path.startswith(area):
        udt_name_tuple = tuple(udt_name_set)
        if node.typeId not in udt_name_set and node.typeId.lower() in set(name.lower() for name in udt_name_set): # type: ignore
            name_index = tuple(name.lower() for name in udt_name_tuple).index(node.typeId.lower()) # type: ignore
            node.typeId = udt_name_tuple[name_index]
            missing_udt_dict[node.path] = node.typeId
    if '_types_/' in node.path:
        udt_name_set.add(node.path.lstrip('_types_/') + '/' + node.name)
    return node

def name_addition(name_set: set, node: Node) -> Node:
    """
    logging function to track node names - no modifications
    """
    name_set.add(node.name)
    return node

def udt_alarm_node_update(alarm_udt_nodes: set, alarm_udt_node: list, node: Node) -> Node:
    """
    logging function to track alarm nodes in file - no modifications
    """
    if node.alarms is not None:
        alarm_udt_nodes.add(node.name)
        alarm_udt_node.append(node)
    return node

def udt_count_update(udt_count: Callable, node: Node) -> Node:
    """
    logging function to track udt key counts - no modifications
    """
    udt_count(set([key for key, val in asdict(node).items() if val is not None]))
    return node

def parameter_change(inst_parameter_dict: dict, old_str: str, new_str: str, node: Node) -> Node:
    """
    Replace parameter substring from old_str to new_str
    """
    if node.parameters is not None:
        node.parameters = {parameter.replace(old_str, new_str): val for parameter, val in node.parameters.items()}
        inst_parameter_dict[node.name] = {parameter for parameter in node.parameters}
    return node

def namespace_parameter_addition(node: Node) -> Node:
    """
    Adds namespace and namspaceFlag to parameter list for OPC-UA transform
    """
    if node.parameters:
        node.parameters['namespaceFlag'] = {'dataType': 'String', 'value': 'ns'}
        node.parameters['namespace'] = {'dataType': 'String', 'value': '2'}
    return node

def parameter_remove(parameter: str, node: Node) -> Node:
    """
    Remove parameter from tag parameter list
    """
    if node.parameters:
        node.parameters.pop(parameter, None)
    return node

def udt_name_set_addition(udt_name_set: set, node: Node) -> Node:
    """
    Tracking function to add udt names to a set
    """
    udt_name_set.add(node.path.lstrip('_types_/') + '/' + node.name)
    return node

def alarm_udt_base_tracking(alarm_udt_base_nodes: set, alarm_udt_base_node: list, node: Node) -> Node:
    """
    Add alarms to a tracking set and list
    """
    alarm_udt_base_nodes.add(node.name)
    alarm_udt_base_node.append(node)
    return node

