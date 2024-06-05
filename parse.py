from _typeshed import DataclassInstance
import json
import os
from typing import Callable
import pprint
from dataclasses import dataclass
from typing import Optional, Union

@dataclass
class OPCItemPath:
    obj: Union[str, dict]

    @property
    def binding(self):
        """The path property."""
        if isinstance(self.obj, str):
            return self.obj
        if isinstance(self.obj, dict):
            return self.obj['binding']
    @binding.setter
    def binding(self, value):
        if isinstance(self.obj, str):
            self.obj = value
        if isinstance(self.obj, dict):
            self.obj['binding'] = value

    @property
    def bindType(self) -> Optional[str]:
        """The bindType property."""
        if isinstance(self.obj, dict):
            return self.obj['bindType']
        return None 
    @bindType.setter
    def bindType(self, value):
        if isinstance(self.obj, dict):
            self.obj['bindType'] = value

@dataclass(order=True)
class Parameters:
    namespace: dict|None
    namespaceFlag: dict|None

    @classmethod
    def from_dict(cls, node_dict: dict):
        struct_dict = {key: val for key, val in node_dict.items() if key in cls.__annotations__}
        return cls(**struct_dict)

@dataclass(order=True)
class Node:
    name: str
    tagType: str
    path: str
    historyEnabled: bool|dict|None = None 
    typeId: str|None = None
    expression: str|None= None
    parameters: dict|None = None
    alarms: dict|None = None
    opcItemPath: OPCItemPath|None = None
    tags: dict|None = None

    @classmethod
    def from_dict(cls, node_dict: dict, path: str):
        struct_dict = {key: val for key, val in node_dict.items() if key in cls.__annotations__}
        if 'opcItemPath' in node_dict:
            struct_dict['opcItemPath'] = OPCItemPath(node_dict['opcItemPath'])
        return cls(path=path, **struct_dict)


root = os.path.dirname(os.path.realpath(__file__))
area = 'South'
file = "%s tags.json"%area.lower()
# print(os.path.abspath('south tags.json'))

def atomic_node(node: Node, path: str):
    """
    Strategy function for atomic nodes
    """
    # Path unused in strategy
    _ = path
    # min_atom_set(set(node.keys()))
    # max_atom_set(set(node.keys()))
    if node.alarms is not None:
        for alarm in node.alarms:
            alarm_count_dict(set(alarm.keys()))
    if node.expression is not None:

        if 'isNull' in node.expression and 'toString' in node.expression:
            # Change
            node.expression = alarm_format(node.expression) 

            expression_set.add(node.expression)
    # Change
    node = history_update(node)
    node = update_opc_path(node)
    node = opc_path_change(node, '~', '_t_')
    # removed by request - do not wish to add minimum history at this time.
    # node = add_min_history(node, 6)
    atom_count_dict(set(node.keys()))

def udt_node(node: Node, path: str):
    """
    Strategy function for UDT nodes
    """
    if node.typeId is None:
        return

    tag_name_set.add(node.name)
    # Change 
    node = type_prefix_removal(node)
    node = type_case_correction(node, path)
    if '_types_/' in path:
        udt_name_set.add(path.lstrip('_types_/') + '/' + node.name)
    if 'parameters' in node:
        # change
        node.parameters = parameter_change(node.parameters, '~', '_t_')
        inst_parameter_dict[node.name] = {parameter for parameter in node.parameters} 
    if 'alarms' in node:
        alarm_udt_nodes.add(node.name)
        alarm_udt_node.append(node)
    # udt_count_dict(set(node.keys()))

def udt_base_node(node: Node, path: str) -> None:
    """
    Strategy function for base UDT nodes
    """
    # if 'parameters' not in node:
    #     tags_without_parameters[node.name] = node.typeId
    # tag_name_set.add(node.name)
    udt_name_set.add(path.lstrip('_types_/') + '/' + node.name)
    udt_base_nodes.add(tuple(node.keys()))
    if 'typeId' in node:
        # change
        node = type_prefix_removal(node)
    if 'alarms' in node:
        alarm_udt_base_nodes.add(node.name)
        alarm_udt_base_node.append(node)
    if 'parameters' in node:
        # change
        node.parameters = namespace_parameter_addition(parameter_change(node.parameters, '~', '_t_'))
        node.parameters = parameter_remove(node.parameters, '_Historize')

        parameter_dict[node.name] = {parameter for parameter in node.parameters} 
    # udt_count_dict(set(node.keys()))

def folder_node(node: Node, path: str):
    """
    Strategy function for folder UDT nodes
    """
    _ = path
    folder_name_set.add(node.name)

def minimum_set() -> Callable[[set], set]:
    min_set: set = set()
    initialize: bool = True
    def min_set_update(group_set: set) -> set:
        nonlocal min_set
        nonlocal initialize
        if not group_set:
            return min_set
        if initialize:
            min_set = group_set
            initialize = False
        else:
            min_set = set((item for item in min_set if item in group_set))
        return min_set
    return min_set_update

def maximum_set() -> Callable[[set], set]:
    max_set: set = set()
    def max_set_update(group_set: set) -> set:
        nonlocal max_set
        max_set |= group_set
        return max_set
    return max_set_update

def parameter_change(parameters: dict, old_str: str, new_str: str) -> dict:
    return {parameter.replace(old_str, new_str): val for parameter, val in parameters.items()}

def parameter_remove(parameters: dict, parameter: str) -> dict:
    parameters.pop(parameter, None)
    return parameters

def namespace_parameter_addition(parameters: Parameters) -> Parameters:
    parameters.namespaceFlag = {'dataType': 'String', 'value': 'ns'}
    parameters.namespace = {'dataType': 'String', 'value': '2'}
    return parameters

def update_opc_path(node: Node) -> Node:
    if node.opcItemPath is not None:
        if isinstance(node.opcItemPath, str):
            node.opcItemPath = "{namespaceFlag}={namespace};s=" + node.opcItemPath
        else:
            node.opcItemPath.binding = "{namespaceFlag}={namespace};s=" + node.opcItemPath.binding
    return node

def add_min_history(node: Node, hours: int) -> Node:
    if 'historyEnabled' in node and node['historyEnabled']:
        node['historyMaxAge'] = hours
    return node

def opc_path_change(node: Node, old_str: str, new_str: str) -> Node:
    # REVIEW THIS CODE WITH NODE/OPCITEMPATH CHANGE
    if "opcItemPath" in node and node["opcItemPath"] and node["valueSource"] == 'opc':
        if isinstance(node["opcItemPath"], str):
            node["opcItemPath"] = node["opcItemPath"].replace(old_str, new_str)
        if isinstance(node["opcItemPath"], Node):
            node["opcItemPath"]["binding"] = node["opcItemPath"]["binding"].replace(old_str, new_str)
    return node

def history_update(node: Node) -> Node:
    if isinstance(node.historyEnabled, dict):
        node.historyEnabled = True
    return node

def type_prefix_removal(node: Node) -> Node:
    node.typeId = node.typeId.lstrip('[%s01]_types_/'%area) # type: ignore
    return node

def alarm_format(expression: str) -> str:
    ignore_set = {'Alarm Condition'}
    for item in ignore_set:
        if item in expression:
            return expression
    tank_set = {'Top Level', 'Interface Level', 'Tank Shut In'}
    for item in tank_set:
        if item in expression:
            return '\r\n'.join((line[1:] for line in expression.split('\r\n')[1:-1]))
    if 'Plunger Status' in expression:
        return 'if' + expression.split('if')[1] + 'if' + expression.split('if')[3][:-1]
    else:
        exp = expression.split('if')[2].rstrip('\r\n')[:-1].rstrip('\r\n\t ')
        if exp[-1] != ')' and exp[-1] != '"':
            exp += '")'
        elif exp[-1] != ')':
            exp += ')'
        return 'if' + exp

def type_case_correction(node: Node, path: str) -> Node:
    if path.startswith(area):
        udt_name_tuple = tuple(udt_name_set)
        if node.typeId not in udt_name_set and node.typeId.lower() in set(name.lower() for name in udt_name_set): # type: ignore
            name_index = tuple(name.lower() for name in udt_name_tuple).index(node.typeId.lower()) # type: ignore
            node.typeId = udt_name_tuple[name_index]
            missing_udt_dict[path] = node.typeId
    return node

def key_count() -> Callable[[set], dict]:
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

with open(root + '/' + file, "r") as read_file:
    data = json.load(read_file)

    tags = data['tags']
    type_tags = {}
    area_tags = {}
    types = {}
    dict_set = set()
    tag_type = set()
    tag_name_set = set() 
    folder_name_set = set() 
    tags_without_parameters = {}
    alarm_udt_nodes = set()
    alarm_udt_node = []
    udt_base_nodes = set()
    alarm_udt_base_nodes = set()
    alarm_udt_base_node = []
    expression_set = set()
    udt_name_set = set()
    missing_udt_dict = {}
    parameter_dict = {}
    inst_parameter_dict = {}


    min_atom_set = minimum_set()    
    max_atom_set = maximum_set()
    # atom_count_dict = key_count()
    # udt_count_dict = key_count()
    # alarm_count_dict = key_count()
    for tag in tags:
        # print(type(tag['name']))
        if tag['name'] == '_types_':
            type_tags = tag['tags']
        if tag['name'] == 'South' or tag['name'] == 'North':
            area_tags = tag['tags']
     
    def tag_branch(node, path):
        # print(type(node))
        if isinstance(node, list):
            for i in range(len(node)):
                tag_branch(node[i], path)
        if isinstance(node, dict):
            # print(node.keys())
            if not node:
                return

            
            dict_set.add(tuple(node.keys()))
            tag_type.add(node['tagType'])

            node = Node.from_dict(node, path)
            # print(new_node)
            node_func = {
                'Folder': folder_node,
                'UdtInstance': udt_node,
                'AtomicTag': atomic_node,
                'UdtType': udt_base_node,
            }
            node_func[node.tagType](node, path)
            

            # print(node.keys())
            try: 
                tag_branch(node['tags'], path + '/' + node['name'])
            except KeyError:
                return node
    tag_branch(type_tags, '_types_')
    tag_branch(area_tags, area)

    # print(types[0])

    # tag_branch(area_tags)


    # pprint.pprint(dict_set)
    pprint.pprint(tag_type)
    # pprint.pprint(tags_without_parameters)
    # pprint.pprint(min_atom_set)

    # pprint.pprint(min_atom_set(set()))
    # pprint.pprint(max_atom_set(set()))
    # pprint.pprint('UDT Overwrite Instance Counts')
    # udt_counts = udt_count_dict(set())
    # udt_percents = {key: (val, round(100*val/sorted(udt_counts.values(), reverse=True)[0], 2)) for key, val in udt_counts.items()}
    # pprint.pprint(udt_counts)
    # pprint.pprint(udt_percents)
    

    # print('')
    # pprint.pprint('Atomic Overwrite Instance Counts')
    # atom_counts = atom_count_dict(set())
    # atom_percents = {key: (val, round(100*val/sorted(atom_counts.values(), reverse=True)[0], 2)) for key, val in atom_counts.items()}

    # pprint.pprint(atom_counts)
    # pprint.pprint(atom_percents)
    # print('')
    # pprint.pprint('Alarm Overwrite Instance Counts')
    # alarm_counts = alarm_count_dict(set())
    # alarm_percents = {key: (val, round(100*val/sorted(alarm_counts.values(), reverse=True)[0], 2)) for key, val in alarm_counts.items()}

    # pprint.pprint(atom_counts)
    # pprint.pprint(alarm_percents)
    # pprint.pprint(expression_set)
    # print(len(expression_set))
    ### Solution to updating alarms
    # print(len(expression_set))
    # for expression in expression_set:
    #     print('')
    #     print('-------')
    #     pprint.pprint(expression)
    #     print('^^^^^^^')
    #     print('vvvvvvv')
    #     pprint.pprint(alarm_format(expression))
    #     print('-------')
    # print(len(expression_set))
    pprint.pprint(udt_name_set)
    pprint.pprint(missing_udt_dict)
    # pprint.pprint(alarm_udt_nodes) # corrected for north and south
    # pprint.pprint(alarm_udt_node)# corrected for north and south
    # pprint.pprint(len(alarm_udt_node))# corrected for north and south
    # pprint.pprint(alarm_udt_base_nodes) 
    # pprint.pprint(alarm_udt_base_node)
    # pprint.pprint(len(alarm_udt_base_node))
    # pprint.pprint('---Folders---')
    # pprint.pprint(folder_name_set)
    # pprint.pprint('---UDTs---')
    # pprint.pprint(tag_name_set)
    # print(len(dict_set))
    # print(tags[3]['name'])
    # pprint.pprint(parameter_dict)
    # print('-----------------------------------')
    # print('-----------------------------------')
    # print('-----------------------------------')
    # pprint.pprint(inst_parameter_dict)
    print(OPCItemPath('test_path').binding)
    with open('test.json', 'w', encoding='utf-8') as f:
        json.dump(data, f)
