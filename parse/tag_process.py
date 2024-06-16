from collections.abc import Callable
from dataclasses import dataclass, field
import json
from .tag_dataclasses import Node
from .node_strategies import NodeStrategy


@dataclass
class TagProcessor:
    file: str
    folder_process_steps: list[Callable[[Node],Node]] = field(default_factory=list)
    udtType_process_steps: list[Callable[[Node],Node]] = field(default_factory=list)
    atomic_process_steps: list[Callable[[Node],Node]] = field(default_factory=list)
    udtInstance_process_steps: list[Callable[[Node],Node]] = field(default_factory=list)


    def __enter__(self):
        self.file_obj = open(self.file, mode="r")
        self.data = json.load(self.file_obj)

        tags = self.data['tags']
        for tag in tags:
            if tag['name'] == '_types_':
                self.type_tags = tag['tags']
            if tag['name'] == 'South' or tag['name'] == 'North':
                self.area_tags = tag['tags']
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        _, _, _ = exc_type, exc_val, exc_tb
        if self.file_obj:
            self.file_obj.close()

    def tag_branch(self, node, path):
        if isinstance(node, list):
            for i in range(len(node)):
                self.tag_branch(node[i], path)
        if isinstance(node, dict):
            if not node:
                return
            # Coerce node dict + path to node dataclass object
            node_obj = Node.from_obj(node, path)

            if node_obj.tagType == 'UdtInstance' and node_obj.typeId is None:
                return

            node_process_steps = {
                'Folder': self.folder_process_steps,
                'UdtInstance': self.udtInstance_process_steps,
                'AtomicTag': self.atomic_process_steps,
                'UdtType': self.udtType_process_steps,
            }
            node_obj = NodeStrategy(node_obj, node_process_steps[node_obj.tagType]).process()
            updated_node, path = node_obj.to_obj()

            for key in node:
                node[key] = updated_node[key]
            # node_mods = {key: val for key, val in asdict(node_obj).items() if val is not None and key != 'path'}
            # for key, value in node_mods.items():
            #     node[key] = value
            # path = asdict(node_obj)['path']

            try: 
                self.tag_branch(node['tags'], path + '/' + node['name'])
            except KeyError:
                return node
    
    def process_types(self):
        self.tag_branch(self.type_tags, '_types_')

    def process_tags(self):
        self.tag_branch(self.area_tags, '')
    
    def process(self):
        self.process_types()
        self.process_tags()

    def to_json(self) -> str:
        return json.dumps(self.data)

    def to_file(self, filepath: str) -> None:
        with open(filepath, "w") as f:
            json.dump(self.data, f, indent=2)

if __name__ == '__main__':
    pass
    # root = '\\'.join(os.path.dirname(os.path.realpath(__file__)).split('\\')[:-1]+['tests', 'json'])
    # area = 'South'
    # file = "%s tags.json"%area.lower()
    #
    # atomic_process_steps = [
    #     partial(alarm_count, alarm_count_dict),
    #     partial(expression_format, expression_set),
    #     history_update,
    #     update_opc_path,
    #     partial(opc_path_change, '~', '_t_'),
    # ]
    # 
    # with Parser(root,  
    # file,
    # folder_process_steps,
    # udtType_process_steps,
    # atomic_process_steps,
    # udtInstance_process_steps) as parser:
    #     parser.hello()
    #     
    #
    #
    #     # print(types[0])
    #
    #     # tag_branch(area_tags)
    #
    #
    #     # pprint.pprint(tags_without_parameters)
    #     # pprint.pprint(min_atom_set)
    #
    #     # pprint.pprint(min_atom_set(set()))
    #     # pprint.pprint(max_atom_set(set()))
    #     pprint.pprint('UDT Overwrite Instance Counts')
    #     udt_counts = udt_count_dict(set())
    #     udt_percents = {key: (val, round(100*val/sorted(udt_counts.values(), reverse=True)[0], 2)) for key, val in udt_counts.items()}
    #     # pprint.pprint(udt_counts)
    #     pprint.pprint(udt_percents)
    #     
    #
    #     print('')
    #     pprint.pprint('Atomic Overwrite Instance Counts')
    #     atom_counts = atom_count_dict(set())
    #     atom_percents = {key: (val, round(100*val/sorted(atom_counts.values(), reverse=True)[0], 2)) for key, val in atom_counts.items()}
    #
    #     # pprint.pprint(atom_counts)
    #     pprint.pprint(atom_percents)
    #     print('')
    #     pprint.pprint('Alarm Overwrite Instance Counts')
    #     alarm_counts = alarm_count_dict(set())
    #     alarm_percents = {key: (val, round(100*val/sorted(alarm_counts.values(), reverse=True)[0], 2)) for key, val in alarm_counts.items()}
    #
    #     pprint.pprint(atom_counts)
    #     pprint.pprint(alarm_percents)
    #     # pprint.pprint(expression_set)
    #     # print(len(expression_set))
    #     ### Solution to updating alarms
    #     # print(len(expression_set))
    #     # for expression in expression_set:
    #     #     print('')
    #     #     print('-------')
    #     #     pprint.pprint(expression)
    #     #     print('^^^^^^^')
    #     #     print('vvvvvvv')
    #     #     pprint.pprint(alarm_format(expression))
    #     #     print('-------')
    #     # print(len(expression_set))
    #     # pprint.pprint(udt_name_set)
    #     # pprint.pprint(missing_udt_dict)
    #     # pprint.pprint(alarm_udt_nodes) # corrected for north and south
    #     # pprint.pprint(alarm_udt_node)# corrected for north and south
    #     # pprint.pprint(len(alarm_udt_node))# corrected for north and south
    #     # pprint.pprint(alarm_udt_base_nodes) 
    #     # pprint.pprint(alarm_udt_base_node)
    #     # pprint.pprint(len(alarm_udt_base_node))
    #     # pprint.pprint('---Folders---')
    #     # pprint.pprint(folder_name_set)
    #     # pprint.pprint('---UDTs---')
    #     # pprint.pprint(tag_name_set)
    #     # print(len(dict_set))
    #     # print(tags[3]['name'])
    #     # pprint.pprint(parameter_dict)
    #     # print('-----------------------------------')
    #     # print('-----------------------------------')
    #     # print('-----------------------------------')
    #     # pprint.pprint(inst_parameter_dict)
    #     # with open('test.json', 'w', encoding='utf-8') as f:
    #     #     json.dump(data, f, indent=4)
