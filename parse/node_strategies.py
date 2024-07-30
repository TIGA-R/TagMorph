from collections import namedtuple
from dataclasses import asdict, dataclass, field
from typing import Callable, Literal, Self
from .tag_dataclasses import Binding, Node, TagParameter, ValueSource
from itertools import permutations
import logging

from rich.traceback import install

install()

type OldString = str
type NewString = str

logging.basicConfig(
    filename='C:\\Users\\Bobby.Miller\\MGY\\tagmorph\\logs\\log.txt',
    format="%(asctime)s | %(levelname)s | %(message)s |>",
)

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


def expression_format(
        # expression_set: set, 
        node: Node
    ) -> Node:
    """
    Correcting expressions to remove isNull/toString expressions. Takes a few forms in our tags. 

    Added expression_set for now to print out expressions, but likely to remove later, in favor of logging.
    (removed for now)
    """
    if node.expression is None\
    or 'isNull' not in node.expression\
    or 'toString' not in node.expression:
        return node
    tank_set = {'Top Level', 'Interface Level', 'Tank Shut In'}
    for item in tank_set:
        if item in node.expression:
            node.expression = '\r\n'.join((line[1:] for line in node.expression.split('\r\n')[1:-1]))
            return node
    # Hard-coded fix to edge case
    if '{[.]OPC}' in node.expression:
        node.expression = 'if({Alarm Condition},\r\n\tif({[.]OPC}, concat(\"1 - \", {Alarm State}), concat(\"0 - \", {Normal State})),\r\n\tif({[.]OPC}, concat(\"1 - \", {Normal State}), concat(\"0 - \", {Alarm State}))\r\n)'
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
        node.opcItemPath.convert_to_parameter()
        node.opcItemPath.binding = "{namespaceFlag}={namespace};s=" + node.opcItemPath.binding
    return node

def add_min_history(node: Node, hours: int) -> Node:
    """
    Set a minimum history to any/all tags with history enabled (truthy)
    """
    if isinstance(node.historyEnabled, bool) and node.historyEnabled:
        node.historyMaxAge = hours
    return node

def opc_path_change(replace_dict: dict[OldString, NewString], node: Node) -> Node:
    """
    Generic function to substitute opc path substring
    """
    if node.opcItemPath is not None \
    and node.valueSource == 'opc' \
    and isinstance(node.opcItemPath.binding, str):
        for old_str, new_str in replace_dict.items():
            if not old_str in node.opcItemPath.binding:
                continue
            if new_str in node.opcItemPath.binding:
                continue
            prefix_in = False
            for perm in permutations(('_t_', '_p_', '_e_'), 2):
                if new_str.replace(perm[0], perm[1]) in node.opcItemPath.binding:
                    prefix_in = True
                    break
            if prefix_in:
                continue
            lp_device = False
            if old_str == '_LP' or old_str =='_HP':
                for item in [
                'COBRA_HP_RD',
                'CREED_1H_HP_RD',
                'CREED_1H_LP_RD',
                'CREED_5H_HP_RD',
                'CREED_5H_LP_RD',
                'SUPER_HP_RD',
                'TANGO_HP_RD',
                'TANGO_LP_RD',
                'BOONE_HP_RD',
                'BOONE_LP_RD',
                'TBK_LP_HP_RD',
                'KEYS_HP_RD',
                'M_ANN_HP_LP_RD',
                ]:
                    if item in node.opcItemPath.binding:
                        lp_device = True
                        break
            if lp_device:
                continue

            node.opcItemPath.binding = node.opcItemPath.binding.replace(old_str, new_str).replace('__', '_')
    return node

def binding_change(replace_dict: dict[OldString, NewString], node:Node) -> Node:
    """
    Function for modifying all bindings inside of a tag export
    """
    for field in node.binding_fields:
        bind_field = getattr(node, field)
        binding = bind_field.binding
        if isinstance(binding, bool):
            continue
        db_flag = False
        # if '_SP Adder' in binding:
        #     db_flag = True
            # breakpoint()
        for old_str, new_str in replace_dict.items():
            if old_str == '__SP Adder' and db_flag:
                breakpoint()
                
            if old_str in binding \
            and new_str not in binding:
                prefix_in = False
                for perm in permutations(('_t_', '_p_', '_e_'), 2):
                    if new_str.replace(perm[0], perm[1]) in binding:
                        prefix_in = True
                        if db_flag:
                            breakpoint()
                        break
                if prefix_in:
                    continue
                if db_flag: breakpoint()
                binding = binding.replace(old_str, new_str).replace('_'+new_str, new_str)
        setattr(bind_field, 'binding', binding)
    return node

def history_update(node: Node) -> Node:
    """
    Eliminate historyEnabled parameter from node and modify to be strictly True
    """
    if node.historyEnabled is not None and node.historyEnabled.obj_type is dict:
        node.historyEnabled.binding = True
    return node

def type_prefix_removal(node: Node) -> Node:
    """
    remove extra [{tag provider}]_types_ prefix from child UDTs
    """
    if node.typeId:
        node.typeId = node.typeId.split(']_types_/')[1] if ']_types_/' in node.typeId else node.typeId
    return node

def type_case_wrapper() -> Callable:
    """
    Function used to address ignition bug which does not properly apply UDTs to instances if case does not match perfectly.
        Requires processing to work in the following order: types, then instances. 
        This is currently the preferred approach, but may need to be considered if this approach needs to change.
    """
    udt_name_set = set()
    def type_case_correction(
        missing_udt_dict: dict,
        node: Node,
    ) -> Node:
        nonlocal udt_name_set
        if '_types_/' in node.path:
            udt_name_set.add(node.path.lstrip('_types_/') + '/' + node.name)
            return node
        if node.path == '_types_':
            return node
        udt_name_tuple = tuple(udt_name_set)
        if node.typeId is None:
            return node
        if (node.typeId not in udt_name_set 
            and node.typeId.lower() in set(name.lower() for name in udt_name_set)):
            name_index = tuple(name.lower() 
                for name in udt_name_tuple).index(node.typeId.lower())        
            node.typeId = udt_name_tuple[name_index]
            missing_udt_dict[node.path] = node.typeId
        return node
    return type_case_correction

def name_addition(name_set: set, node: Node) -> Node:
    """
    logging function to track node names - no modifications
    """
    name_set.add(node.name)
    return node

def match_parameter_addition(match_string: str, parameter_set: set, node: Node) -> Node:
    if node.parameters is None:
        return node
    for parameter in node.parameters:
        if match_string in parameter.name:
            parameter_set.add(parameter.name)
    return node

type AlarmMode = Literal[
    'AboveValue',
    'BelowValue',
    'OnCondition',
    'BadQuality',
    'OutOfEngRange',
    'BetweenValues',
    'AnyChange',
    'Equal',
    'Inequality',
    'Bit',
    'OutsideValues',
    
]
type Priority = Literal[
    'Critical',
    'High',
    'Medium',
    'Low',
    'Diagnostic'
]
@dataclass(frozen=True, eq=True)
class AlarmBinding:
    value: str
    bindType: str

@dataclass(frozen=True, eq=True)
class Alarm:
    mode: AlarmMode
    priority: AlarmBinding|Priority
    name: str
    # path: str
    setpointA: float|None = None
    setpointB: float|None = None
    activeCondition: AlarmBinding|None = None
    # _extras: dict = field(default_factory=dict)


    @classmethod
    def from_obj(
        cls, 
        node_dict: dict,
        # path: str, 
    ) -> Self:

        """
        Construct Node object from a json tag provider object
        """
        struct_dict: dict[str, str|float|AlarmBinding|AlarmMode] = {key: val 
            if not isinstance(val, dict) 
            else AlarmBinding(val['value'], val['bindType']) 
            for key, val in node_dict.items() 
            if key in cls.__annotations__ 
            }
        # struct_dict['_extras'] = {key: val 
        #     for key, val in node_dict.items() 
        #     if key not in cls.__annotations__}
        return cls(**struct_dict) 

    def to_obj(self) -> dict:
        """
        return Node object to json-style dict + path string
        """
        data_dict = {key: val 
            if 'Binding' not in str(self.__annotations__[key]) 
            else getattr(self, key).to_obj() 
            for key, val in asdict(self).items()
            if val is not None
        }
        return data_dict

def build_alarm_set(alarm_set: set[Alarm], node: Node) -> Node:
    if node.alarms is None:
        return node
    for alarm in node.alarms:
        if alarm.get('mode') is None \
        or alarm.get('priority') is None:
            continue
        try:
            alarm_set.add(Alarm.from_obj(alarm))
        except TypeError:
            breakpoint()
            print(Alarm.from_obj(alarm))
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

def parameter_change(replace_dict: dict[OldString, NewString], node: Node) -> Node:
    """
    Replace parameter substring from old_str to new_str
    """
    if node.parameters is None:
        return node
    for parameter in node.parameters:
        if parameter.name == 'Device01':
            continue
        for old_str, new_str in replace_dict.items():
            if old_str in parameter.name \
            and new_str not in parameter.name:
                prefix_in = False
                for perm in permutations(('_t_', '_p_', '_e_'), 2):
                    if new_str.replace(perm[0], perm[1]) in parameter.name:
                        prefix_in = True
                        break
                if prefix_in:
                    continue
                parameter.name = parameter.name.replace(old_str, new_str).replace('__', '_')
            if parameter.value is None:
                continue
            if isinstance(parameter.value, int):
                continue
            if isinstance(parameter.value, Binding) \
            and isinstance(parameter.value.binding, str) \
            and old_str in parameter.value.binding \
            and new_str not in parameter.value.binding:
                prefix_in = False
                for perm in permutations(('_t_', '_p_', '_e_'), 2):
                    if new_str.replace(perm[0], perm[1]) in parameter.value.binding:
                        prefix_in = True
                        break
                if prefix_in:
                    continue
                parameter.value.binding = parameter.value.binding.replace(old_str, new_str).replace('__', '_')
            
            if isinstance(parameter.value, str) \
            and old_str in parameter.value \
            and new_str not in parameter.value:
                prefix_in = False
                for perm in permutations(('_t_', '_p_', '_e_'), 2):
                    if new_str.replace(perm[0], perm[1]) in parameter.value:
                        prefix_in = True
                        break
                if prefix_in:
                    continue
                parameter.value = parameter.value.replace(old_str, new_str).replace('__', '_')

    return node

def parameters_addition(parameters: list[TagParameter], node: Node) -> Node:
    if node.parameters is None:
        return node
    node.parameters += parameters
    return node

def namespace_parameter_addition(node: Node) -> Node:
    """
    Adds namespace and namspaceFlag to parameter list for OPC-UA transform
    """
    namespace_list = [
        TagParameter('namespaceFlag', 'string', 'ns'),
        TagParameter('namespace', 'string', '2'),
    ]
    return parameters_addition(namespace_list, node)

def parameters_remove(parameters: list[str], node: Node) -> Node:
    """
    Remove parameter from tag parameter list
    """
    if node.parameters is None:
        return node
    node.parameters = [parameter for parameter in node.parameters if parameter.name not in parameters]
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

def type_dict_build(
        name_dict: dict[str, int], 
        type_dict: dict[int, tuple[str, str, str, str]], # name, tag type, type ID, path
        node: Node
    ) -> Node:
    if node.tagType == 'AtomicTag':
        return node
    if node.typeId is not None:
        type_dict[node.id] = (node.name, node.tagType, node.typeId, node.path)
        name_dict[node.path.lstrip('_types_/') + '/' + node.name] = node.id
    else:
        type_dict[node.id] = (node.name, node.tagType, '', node.path)
        name_dict[node.path.lstrip('_types_/') + '/' + node.name] = node.id
    return node

def atom_tag_dict_build(
    atom_dict: dict[int, tuple[str, int]], 
    atomic_type: ValueSource|list[ValueSource],
    node: Node
) -> Node:
    if not node.tagType == 'AtomicTag':
        return node
    if isinstance(atomic_type, str) and not node.valueSource == atomic_type:
        return node
    if isinstance(atomic_type, list) and node.valueSource not in atomic_type:
        return node
    if not node.id_log:
        logging.warning(
            f'Node removed without id_log parent: ' + \
            f'Name: {node.name}, ' + \
            f'Path: {node.path}'
        )
        return node
    atom_dict[node.id] = (node.name, node.id_log[0][0])
    return node

def alarm_enabled_parameter_update(node: Node) -> Node:
    if node.alarms is None:
        return node
    for alarm in node.alarms:
        enabled = alarm.get('enabled')
        if enabled is not None \
        and isinstance(enabled, dict) \
        and '_p_' not in enabled['value']:
            enabled['value'] = enabled['value'].replace('_', '_p_')
    return node


def udt_instance_dict_build(
    udt_inst_dict: dict[int, str],
    node: Node,
) -> Node:
    if node.tagType == 'UdtInstance': 
    # and (node.enabled is None or node.enabled.binding):
        udt_inst_dict[node.id] = (node.path + '/' + node.name)
    return node

def print_node(node_num: int, node: Node) -> Node:
    if node.id == node_num:
        print((node.id, node.path + '/' + node.name))
    return node


def atomic_tag_set_build(
    atomic_tag_set: set[tuple[str, int, int]],
    node: Node
) -> Node:
    folder_list = [
        "FACILITY",
        "ESP",
        "METER",
        "PLUNGER",
        "POC",
        "PUMP",
        "REMOTE DEVICE",
        "TANK",
        "VALVE",
        "VESSEL",
        "WELL",
        "FLARE",
        "COMPRESSOR",
    ]
    if node.tagType != 'AtomicTag':
        return node
    for folder in folder_list:
        if '/'+folder+'/' in node.path:
            if '(Message)' in node.name:
                atomic_tag_set.add((node.name.replace(' (Message)', ''), 1, 0))
                atomic_tag_set.discard((node.name.replace(' (Message)', ''), 0, 0))
            else:
                if (node.name, 1, 0) in atomic_tag_set:
                    return node
                atomic_tag_set.add((node.name.replace(' (Message)', ''), 0, 1 if node.dataType == 'String' else 0))
            return node
    return node

def update_tag_group(node: Node) -> Node:
    if node.tagType != 'AtomicTag':
        return node
    if node.tagGroup is not None and node.tagGroup != 'Default':
        return node
    if node.valueSource != 'opc':
        return node
    group_dict = {
        "FACILITY": "Facility",
        "ESP": "ESP",
        "METER": "Meter",
        "PLUNGER": "Plunger",
        "POC": "POC",
        "PUMP": "Pump",
        "REMOTE DEVICE": "Remote Device",
        "TANK": "Tank",
        "VALVE": "Valve",
        "VESSEL": "Vessel",
        "WELL": "Well",
        "FLARE": "Flare",
        "COMPRESSOR": "Compressor",
    }
    for group in group_dict.keys():
        if '/'+group+'/' in node.path:
            node.tagGroup = group_dict[group]
    return node
