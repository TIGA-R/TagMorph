import pathlib
from parse.tag_dataclasses import Node
from parse.tag_process import TagProcessor


path = str(pathlib.Path(__file__).parent.resolve()) + '/json/'
single_site_file = 'Briscoe Alpha Tags Condensed.json'

def return_node_unchanged(node: Node) -> Node:
    return node

def test_json_unchanged():
    with TagProcessor(
        path + single_site_file,
        [return_node_unchanged,],
        [return_node_unchanged,],
        [return_node_unchanged,],
        [return_node_unchanged,],
    ) as processor:
        preprocess_json = processor.to_json()
        processor.process()
        postprocess_json = processor.to_json()

    assert preprocess_json == postprocess_json
    

