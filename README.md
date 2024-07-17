# TIGA Tag Morph Editor Tool
This is a python project to enable the mass-editing/updating of tags (including Base UDTs, Site UDTs, instances, and atomic tag structures).

The tag morph tool can be used to write python functions which will update existing tag structures to a desired future state. Real use case examples include:
- Updating all template parameters within a UDT structure
- Adding maximum time-to-collect-history to all historized tags
- Update all tags from OPC-DA to OPC-UA
- Uniformitization of parameter names
- updates to all expression tag formulas of a given style

## Getting Started
To run the tag morph tool requires a source tag export file. The file is opened using the python `with` syntax
### Example TagProcessor
```python
from parse.tag_process import TagProcessor
from parse.node_strategies import namespace_parameter_addition

source_file = 'path/to/tags.json' # Tag Source File here
area = 'North' # Area to be processed (name of the source tag folder)

with TagProcessor(
    source_file,
    area,
    atomic_process_steps = [ 
    ],
    udtInstance_process_steps = [ 
    ],
    udtType_process_steps = [
        namespace_parameter_addition
    ],
) as processor:
    processor.process()
    processor.to_file('path/to/updated tags.json')
```
The above will iterate over all tag nodes. On identifying a udtType node, it will add namespace parameters to the udtType.

To dive deeper, lets look at the `namespace_parameter_addition` function:

### Node Strategy Example

```python
def parameters_addition(parameters: list[TagParameter], node: Node) -> Node:
    """
    Checks if the node has parameters associated with it, and adds the TagParameters from parameters if it does exist
    """
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
```

Here, we use the generic `parameters_addition` function and make a special helper `namespace_parameter_addition` for our specific case of adding `namespaceFlag` and `namespace`

For every `node strategy`, it is expected that the function takes a `Node` object as a function input and also returns a `Node` object. More on the Node object below:

### Node Object
The node object represents every tag entry in the `tags.json` export. The object produces the value -or- null if it does not exist. Additionally, often there are `bindings` inside of the tag export object. These have another object `Binding` that represent them. The following roughly outlines `Node` and `Binding`:
#### Node
```python
@dataclass
class Node:
    path: str
    id: int 
    id_log: list[tuple[int, TagType]]
    name: str = field(default_factory=str)
    tagType: TagType = field(default_factory=str) #type: ignore
    dataType: str|None = None
    valueSource: ValueSource = None
    enabled: Binding|None = None
    historyEnabled: Binding|None = None 
    sourceTagPath: Binding|None = None
    historyMaxAge: int|None = None
    typeId: str|None = None
    expression: str|None= None
    parameters: list[TagParameter]|None = None
    alarms: dict|None = None
    opcItemPath: Binding|None = None
    tags: dict|None = None
    _extras: dict = field(default_factory=dict)
```

In addition to the mentioned export data, other data is tracked through the `Node` object:
- `Path` (str): Tracks the directory path to the given node
- `id` (int): A unique key identifier assigned to the node during processing
- `id_log` (int): A list of ids traced to get to the given node. This is similar to the `path` but produces a lists of `node` id's, rather than a string of node names joined with a `/`

#### Binding
There is more going on under the hood with `Binding`, but it can be visualized as the following:
```python
@dataclass
class Binding:
    binding: bool|str
    bindType: str|None = None    
```
If a node parameter can be an instance of a Binding, keep this structure in mind to work with it.
