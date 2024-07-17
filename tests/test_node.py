import pathlib
from functools import partial
from parse.tag_dataclasses import Node, Binding, ValueSource
from parse.tag_process import TagProcessor
from parse.node_strategies import (
    binding_change,
    build_alarm_set, 
    expression_format, 
    history_update,
    match_parameter_addition,
    namespace_parameter_addition, 
    opc_path_change,
    atom_tag_dict_build, 
    parameter_change, 
    parameters_remove,
    type_case_wrapper,
    type_dict_build, 
    type_prefix_removal,
    udt_instance_dict_build, 
    update_opc_path,
)
from analyze.relationships import SqliteDatatype, build_child_parent, build_test_database, atom_tag_gen_build
from rich.traceback import install

install()

path = str(pathlib.Path(__file__).parent.resolve()) + '/json/'
single_site_file = 'simple single site tags.json'
original_single_site_file = 'single site tags.json'
single_well_file = 'single well tags.json'
south_site_file = 'South tags.json'
north_site_file = 'North tags.json'
area = 'South'

### Too slow. Redesign if needed ###
# def test_json_unchanged():
#     with TagProcessor(
#         path + single_site_file,
#     ) as processor:
#         preprocess_json = processor.to_json()
#         processor.process()
#         postprocess_json = processor.to_json()
#
#     assert preprocess_json == postprocess_json
    
### Too slow. Redesign if needed ###
# def test_json_unchanged_different_processors():
#     with TagProcessor(
#         path + single_site_file,
#     ) as preprocessor:
#         preprocess_json = preprocessor.to_json()
#
#     with TagProcessor(
#         path + single_site_file,
#     ) as postprocessor:
#         postprocessor.process()
#         postprocess_json = postprocessor.to_json()
#
#     assert preprocess_json == postprocess_json

def setup_json_changed_tagpath(source_file_path, test_file_name, strategy, test):
    with TagProcessor(
        source_file_path,
        area,
        atomic_process_steps = [strategy,],
        udtInstance_process_steps = [strategy,],
        udtType_process_steps = [strategy,],
    ) as processor:
        processor.process()
        processor.to_file(path + test_file_name)
    with TagProcessor(
        path + test_file_name,
        area,
        atomic_process_steps = [test,],
        udtInstance_process_steps = [test,],
        udtType_process_steps = [test,],
    ) as test_processor:
        test_processor.process()

def assert_tagpath_has_prepend( node: Node) -> Node:
    if isinstance(node.opcItemPath, Binding):
        if isinstance(node.opcItemPath.binding, str):
            assert "{namespaceFlag}={namespace};s=" in node.opcItemPath.binding
    return node

def test_single_site_file_prepend():
    setup_json_changed_tagpath(
        path+single_site_file,
         'tagprepend.json',
         update_opc_path,
         assert_tagpath_has_prepend,
    )

### Slow test. Run only sparingly ###
# def test_south_site_file_prepend():
#     setup_json_changed_tagpath(path+south_site_file, 'fulltagprepend.json', update_opc_path, assert_tagpath_has_prepend)

def assert_tagpath_has_no_tilde( node: Node) -> Node:
    if isinstance(node.opcItemPath, Binding):
        if isinstance(node.opcItemPath.binding, str):
            assert "~" not in node.opcItemPath.binding
    return node

def test_single_site_file_no_tilde():
    setup_json_changed_tagpath(
        path+single_site_file,
         'singletilde.json',
         partial(opc_path_change, {'~': '_t_'}), 
        assert_tagpath_has_no_tilde
    )

def test_binding_return_fields():
    node = Node(
        path='test',
        id=1, 
        id_log=[], 
        name='test', 
        tagType='UdtInstance', 
        enabled=Binding({'binding': True}),
    )
    assert [field for field in node.binding_fields] == ['enabled',]

def test_tilde_removed_from_bindings():
    with TagProcessor(
        path+single_site_file,
        area,
        atomic_process_steps = [partial(binding_change, {'~': '_t_'}),],
        udtInstance_process_steps = [partial(binding_change, {'~': '_t_'}),],
        udtType_process_steps = [partial(binding_change, {'~': '_t_'}),],
    ) as processor:
        processor.process()
        processor.to_file(path + 'bindingtest.json')
    with open(path + 'bindingtest.json') as f:
        for line in f:
            assert '{~' not in line
    
def test_tilde_removed_from_file():
    with TagProcessor(
        path+single_site_file,
        area,
        atomic_process_steps = [
            partial(binding_change, {'~': '_t_'}),
            partial(parameter_change, {'~': '_t_'}),
            ],
        udtInstance_process_steps = [
            partial(binding_change, {'~': '_t_'}),
            partial(parameter_change, {'~': '_t_'}),
            ],
        udtType_process_steps = [
            partial(binding_change, {'~': '_t_'}),
            partial(parameter_change, {'~': '_t_'}),
            ],
    ) as processor:
        processor.process()
        processor.to_file(path + 'filetildetest.json')
    with open(path + 'filetildetest.json') as f:
        for line in f:
            assert '~' not in line

def test_historize_removed_from_file():
    with TagProcessor(
        path+single_site_file,
        area,
        atomic_process_steps = [history_update,],
        udtInstance_process_steps = [history_update,],
        udtType_process_steps = [history_update,],
    ) as processor:
        processor.process()
        processor.to_file(path + 'historize_delete_test.json')
    with open(path + 'historize_delete_test.json') as f:
        for line in f:
            assert '{_Historize}' not in line

def test_type_prefix_removal():
    with open(path+single_site_file) as f:
        types = False
        for line in f:
            if '_types_/' in line:
                types = True
                break
        assert types
    with TagProcessor(
        path+single_site_file,
        area,
        atomic_process_steps = [type_prefix_removal,],
        udtInstance_process_steps = [type_prefix_removal,],
        udtType_process_steps = [type_prefix_removal,],
    ) as processor:
        processor.process()
        processor.to_file(path + 'type_prefix_removal.json')
    with open(path + 'type_prefix_removal.json') as f:
        for line in f:
            assert '_types_/' not in line

def test_case_correction():
    missing_udt_dict = {}
    type_case_correction = type_case_wrapper()
    with TagProcessor(
        path+original_single_site_file,
        area,
        atomic_process_steps = [
            partial(type_case_correction, missing_udt_dict),
        ],
        udtInstance_process_steps = [
            partial(type_case_correction, missing_udt_dict),
        ],
        udtType_process_steps = [
            partial(type_case_correction, missing_udt_dict),
        ],
    ) as processor:
        processor.process()
        processor.to_file(path + 'case_correction.json')
    assert missing_udt_dict
    missing_udt_dict = {}
    type_case_correction = type_case_wrapper()
    with TagProcessor(
        path+'case_correction.json',
        area,
        atomic_process_steps = [
            partial(type_case_correction, missing_udt_dict),
        ],
        udtInstance_process_steps = [
            partial(type_case_correction, missing_udt_dict),
        ],
        udtType_process_steps = [
            partial(type_case_correction, missing_udt_dict),
        ],
    ) as processor:
        processor.process()
    assert not missing_udt_dict

def test_parameter_removal():
    with TagProcessor(
        path+single_site_file,
        area,
        atomic_process_steps = [
            partial(parameters_remove, ['_Historize']),
            history_update,
        ],
        udtInstance_process_steps = [
            partial(parameters_remove, ['_Historize']),
            history_update,
        ],
        udtType_process_steps = [
            partial(parameters_remove, ['_Historize']),
            history_update,
        ],
    ) as processor:
        processor.process()
        processor.to_file(path + 'parameter_removal.json')
    with open(path + 'parameter_removal.json') as f:
        for line in f:
            assert '_Historize' not in line

def test_namespace_parameter_addition():
    with TagProcessor(
        path+single_site_file,
        area,
        atomic_process_steps = [
            namespace_parameter_addition,
        ],
        udtInstance_process_steps = [
            namespace_parameter_addition,
        ],
        udtType_process_steps = [
            namespace_parameter_addition,
        ],
    ) as processor:
        processor.process()
        processor.to_file(path + 'namespace_parameter_addition.json')
    with open(path + 'namespace_parameter_addition.json') as f:
        found = False
        for line in f:
            if 'namespaceFlag' in line:
                found = True
                break
        assert found
def test_expression_format_success():
    with TagProcessor(
        path+single_site_file,
        area,
        atomic_process_steps = [
            expression_format,
        ],
        udtInstance_process_steps = [
            expression_format,
        ],
        udtType_process_steps = [
            expression_format,
        ],
    ) as processor:
        processor.process()
        processor.to_file(path + 'expression_format.json')
    with open(path + 'expression_format.json') as f:
        for line in f:
            assert 'isNull' not in line
            assert 'toString' not in line

def test_type_node_dict():
    type_dict = {}
    name_dict = {}
    type_case_correction = type_case_wrapper()
    missing_udt_dict = {}
    import time
    start = time.time()
    atom_dict = {}
    udt_inst_dict = {}

    with TagProcessor(
        path+south_site_file,
        area,
        atomic_process_steps = [
            # increment_id,
            partial(atom_tag_dict_build, atom_dict, 'expr'),
            type_prefix_removal,
        ],
        udtInstance_process_steps = [
            # increment_id,
            type_prefix_removal,
            partial(type_case_correction, missing_udt_dict),
            partial(udt_instance_dict_build, udt_inst_dict),
            partial(type_dict_build, name_dict, type_dict),
        ],
        udtType_process_steps = [
            # increment_id,
            type_prefix_removal,
            partial(type_case_correction, missing_udt_dict),
            partial(type_dict_build, name_dict, type_dict),
        ],
    ) as processor:
        processor.process()

    mid = time.time()

    import pprint
    # pprint.pprint(type_dict)
    pc_dict = build_child_parent(type_dict, name_dict)
    # pprint.pprint(type_dict)


    # pprint.pprint({key: val 
    #               for key, val in atom_dict.items()
    #               if 1726 in val[1]['UdtType']})
    # pprint.pprint(atom_dict)
    # pprint.pprint(type_dict[1726])
    # pprint.pprint(type_dict[1052])

    # pprint.pprint(udt_inst_dict)

    atom_tag_gen = atom_tag_gen_build(atom_dict, udt_inst_dict, pc_dict)
    # pprint.pprint(atom_tag_gen)
    
    build_test_database(
    file_path="C:\\Users\\Public\\Documents\\output4",
    table_name="expression_tags",
    data_generator=atom_tag_gen,
    ) 
    # import sqlite3
    # with sqlite3.connect("C:\\Users\\Public\\Documents\\output2") as conn:
    #     c = conn.cursor()
    #     c.execute("""CREATE TABLE IF NOT EXISTS opc_tags (id int,  tagpath TEXT NOT NULL);""")
    #     for idx, line in enumerate(opc_tag_list):
    #         sql = """insert into opc_tags(id, tagpath) values(?, ?)"""
    #         # print(line)
    #         c.execute(sql, (idx, line,))
    #     conn.commit()

    # with open(path+'output.txt', 'w') as f:
    #     for line in opc_tag_list:
    #         f.write(line + '\n')



    # children = get_children(142, pc_dict)
    # parents = get_parents(142, pc_dict)
    # print(parents)
    # parents = get_parents(134, pc_dict)
    # print(children)
    # print(parents)
    finish = time.time()
    print(f"Time to process: {mid-start} s")
    print(f"Time to map: {finish-mid} s")
    assert True

def test_map_underscore():
    parameter_set = set()
    with TagProcessor(
        path+south_site_file,
        area,
        atomic_process_steps = [],
        udtInstance_process_steps = [
            partial(match_parameter_addition, '_', parameter_set),
        ],
        udtType_process_steps = [
            partial(match_parameter_addition, '_', parameter_set),
        ],
    ) as processor:
        processor.process()
    with TagProcessor(
        path+north_site_file,
        'North',
        atomic_process_steps = [],
        udtInstance_process_steps = [
            partial(match_parameter_addition, '_', parameter_set),
        ],
        udtType_process_steps = [
            partial(match_parameter_addition, '_', parameter_set),
        ],
    ) as processor:
        processor.process()
    import pprint
    pprint.pprint(parameter_set)
    assert True

def test_alarm_map():
    alarm_set = set()
    with TagProcessor(
        path+south_site_file,
        area,
        atomic_process_steps = [
            partial(build_alarm_set, alarm_set),
        ],
        udtInstance_process_steps = [
        ],
        udtType_process_steps = [
        ],
    ) as processor:
        processor.process()
    with TagProcessor(
        path+north_site_file,
        'North',
        atomic_process_steps = [
            partial(build_alarm_set, alarm_set),
        ],
        udtInstance_process_steps = [
        ],
        udtType_process_steps = [
        ],
    ) as processor:
        processor.process()
    import pickle
    output = open('alarmdata.pkl', 'wb')
    pickle.dump(alarm_set, output)
    output.close()
    import pprint
    pprint.pprint(alarm_set)
    print(len(alarm_set))
    assert True
