import pathlib
from functools import partial
from parse.tag_dataclasses import Node, Binding
from parse.tag_process import TagProcessor
from parse.node_strategies import binding_change, expression_format, history_update, namespace_parameter_addition, opc_path_change, parameter_change, parameters_remove, type_case_correction, type_prefix_removal, update_opc_path

path = str(pathlib.Path(__file__).parent.resolve()) + '/json/'
single_site_file = 'Briscoe Alpha Tags Condensed.json'
single_well_file = 'single well tags.json'
south_site_file = 'South tags.json'
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
    setup_json_changed_tagpath(path+single_site_file, 'tagprepend.json', update_opc_path, assert_tagpath_has_prepend)

### Slow test. Run only sparingly ###
# def test_south_site_file_prepend():
#     setup_json_changed_tagpath(path+south_site_file, 'fulltagprepend.json', update_opc_path, assert_tagpath_has_prepend)

def assert_tagpath_has_no_tilde( node: Node) -> Node:
    if isinstance(node.opcItemPath, Binding):
        if isinstance(node.opcItemPath.binding, str):
            assert "~" not in node.opcItemPath.binding
    return node

def test_single_site_file_no_tilde():
    setup_json_changed_tagpath(path+single_site_file, 'singletilde.json', partial(opc_path_change, '~', '_t_'), assert_tagpath_has_no_tilde)

def test_binding_return_fields():
    node = Node('test', 'test', 'test', enabled=Binding({'binding': True}))
    assert [field for field in node.binding_fields] == ['enabled',]

def test_tilde_removed_from_bindings():
    with TagProcessor(
        path+single_site_file,
        area,
        atomic_process_steps = [partial(binding_change,'~', '_t_'),],
        udtInstance_process_steps = [partial(binding_change,'~', '_t_'),],
        udtType_process_steps = [partial(binding_change,'~', '_t_'),],
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
            partial(binding_change,'~', '_t_'),
            partial(parameter_change,'~', '_t_'),
            ],
        udtInstance_process_steps = [
            partial(binding_change,'~', '_t_'),
            partial(parameter_change,'~', '_t_'),
            ],
        udtType_process_steps = [
            partial(binding_change,'~', '_t_'),
            partial(parameter_change,'~', '_t_'),
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
    udt_name_set = set()
    with TagProcessor(
        path+single_site_file,
        area,
        atomic_process_steps = [partial(type_case_correction, missing_udt_dict, udt_name_set, area),],
        udtInstance_process_steps = [partial(type_case_correction, missing_udt_dict, udt_name_set, area),],
        udtType_process_steps = [partial(type_case_correction, missing_udt_dict, udt_name_set, area),],
    ) as processor:
        processor.process()
        processor.to_file(path + 'case_correction.json')
    assert missing_udt_dict
    missing_udt_dict = {}
    udt_name_set = set()
    with TagProcessor(
        path+'case_correction.json',
        area,
        atomic_process_steps = [partial(type_case_correction, missing_udt_dict, udt_name_set, area),],
        udtInstance_process_steps = [partial(type_case_correction, missing_udt_dict, udt_name_set, area),],
        udtType_process_steps = [partial(type_case_correction, missing_udt_dict, udt_name_set, area),],
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
