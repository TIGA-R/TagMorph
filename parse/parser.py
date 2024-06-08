from dataclasses import dataclass
import json
import os

@dataclass
class Parser:
    root: str
    file: str

    def __enter__(self):
        self.file_obj = open(self.root + '/' + self.file, mode="r")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        _, _, _ = exc_type, exc_val, exc_tb
        if self.file_obj:
            self.file_obj.close()

    def hello(self):
        print("hello world")

if __name__ == '__main__':
    root = '\\'.join(os.path.dirname(os.path.realpath(__file__)).split('\\')[:-1]+['tests', 'json'])
    area = 'South'
    file = "%s tags.json"%area.lower()

    
    with Parser(root, file) as parser:
        parser.hello()
        

    # def parse(self):
    #
    #     data = json.load(self.file_obj)
    #
    #     tags = data['tags']
    #     type_tags = {}
    #     area_tags = {}
    #     types = {}
    #     dict_set = set()
    #     tag_type = set()
    #     tag_name_set = set() 
    #     folder_name_set = set() 
    #     tags_without_parameters = {}
    #     alarm_udt_nodes = set()
    #     alarm_udt_node = []
    #     udt_base_nodes = set()
    #     alarm_udt_base_nodes = set()
    #     alarm_udt_base_node = []
    #     expression_set = set()
    #     udt_name_set = set()
    #     missing_udt_dict = {}
    #     parameter_dict = {}
    #     inst_parameter_dict = {}
    #
    #
    #     min_atom_set = minimum_set()    
    #     max_atom_set = maximum_set()
    #     atom_count_dict = key_count()
    #     udt_count_dict = key_count()
    #     alarm_count_dict = key_count()
    #     for tag in tags:
    #         # print(type(tag['name']))
    #         if tag['name'] == '_types_':
    #             type_tags = tag['tags']
    #         if tag['name'] == 'South' or tag['name'] == 'North':
    #             area_tags = tag['tags']
    #      
    #     def tag_branch(node, path):
    #         # print(type(node))
    #         if isinstance(node, list):
    #             for i in range(len(node)):
    #                 tag_branch(node[i], path)
    #         if isinstance(node, dict):
    #             # print(node.keys())
    #             if not node:
    #                 return
    #             
    #             dict_set.add(tuple(node.keys()))
    #             tag_type.add(node['tagType'])
    #
    #             # Coerce node dict + path to node dataclass object
    #             node_obj = Node.from_dict(node, path)
    #             # print(new_node)
    #
    #             # alarm_count_dict = key_count()
    #             # expression_set = set()
    #
    #             atomic_process_steps = [
    #                 partial(alarm_count, alarm_count_dict),
    #                 partial(expression_format, expression_set),
    #                 history_update,
    #                 update_opc_path,
    #                 partial(opc_path_change, '~', '_t_'),
    #             ]
    #
    #             node_func = {
    #                 'Folder': folder_node,
    #                 'UdtInstance': udt_node,
    #                 'AtomicTag': NodeStrategy(node_obj, atomic_process_steps).process,
    #                 'UdtType': udt_base_node,
    #             }
    #             try:
    #                 node_func[node_obj.tagType](node_obj)
    #             except (TypeError, ValueError):
    #                 node_func[node_obj.tagType]()
    #             node = {key: val for key, val in asdict(node_obj).items() if val is not None and key != 'path'}
    #             path = asdict(node_obj)['path']
    #           
    #
    #             # print(node.keys())
    #             try: 
    #                 tag_branch(node['tags'], path + '/' + node['name'])
    #             except KeyError:
    #                 return node
    #     tag_branch(type_tags, '_types_')
    #     tag_branch(area_tags, area)
    #
    #     # print(types[0])
    #
    #     # tag_branch(area_tags)
    #
    #
    #     # pprint.pprint(dict_set)
    #     pprint.pprint(tag_type)
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
