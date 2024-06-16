import pathlib
from functools import partial
from parse.tag_dataclasses import Node, Binding
from parse.tag_process import TagProcessor
from parse.node_strategies import binding_change, opc_path_change, update_opc_path

path = str(pathlib.Path(__file__).parent.resolve()) + '/json/'
single_site_file = 'Briscoe Alpha Tags Condensed.json'
single_well_file = 'single well tags.json'
south_site_file = 'South tags.json'

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
        atomic_process_steps = [strategy,],
        udtInstance_process_steps = [strategy,],
        udtType_process_steps = [strategy,],
    ) as processor:
        processor.process()
        processor.to_file(path + test_file_name)
    with TagProcessor(
        path + test_file_name,
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
    atomic_process_steps = [partial(binding_change,'~', '_t_'),],
    udtInstance_process_steps = [partial(binding_change,'~', '_t_'),],
    udtType_process_steps = [partial(binding_change,'~', '_t_'),],
    ) as processor:
        processor.process()
        processor.to_file(path + 'bindingtest.json')
    with open(path + 'bindingtest.json') as f:
        for line in f:
            assert '{~' not in line
    
parameter_change
