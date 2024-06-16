from dataclasses import dataclass, asdict, fields
from typing import Optional

@dataclass
class OPCItemPath:
    obj: str|dict

    @property
    def binding(self) -> str:
        """The path property."""
        if isinstance(self.obj, str):
            return self.obj
        if isinstance(self.obj, dict):
            return self.obj['binding']
        return ''
    @binding.setter
    def binding(self, value) -> None:
        if isinstance(self.obj, str):
            self.obj = value
        if isinstance(self.obj, dict):
            self.obj['binding'] = value

    @property
    def bindType(self) -> str|None:
        """The bindType property."""
        if isinstance(self.obj, dict):
            return self.obj['bindType']
        return None 
    @bindType.setter
    def bindType(self, value) -> None:
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

# @dataclass(order=True)
# class Node:
#     name: str
#     tagType: str
#     path: str
#     valueSource: Optional[str] = None
#     historyEnabled: bool|dict|None = None 
#     historyMaxAge: int|None = None
#     typeId: str|None = None
#     expression: str|None= None
#     parameters: dict|None = None
#     alarms: dict|None = None
#     opcItemPath: OPCItemPath|None = None
#     tags: dict|None = None
#
#     @classmethod
#     def from_dict(cls, node_dict: dict, path: str):
#         struct_dict = {key: val for key, val in node_dict.items() if key in cls.__annotations__}
#         if 'opcItemPath' in node_dict:
#             struct_dict['opcItemPath'] = OPCItemPath(node_dict['opcItemPath'])
#         return cls(path=path, **struct_dict)

if __name__ == '__main__':
    # from parse.node_strategies import Node, Binding
    # import types
    # print(Node.__annotations__)
    # for field in fields(Node):
    #     if isinstance(field.type, types.UnionType):
    #         print('Binding' in str(field.type))

    # node = Node(name='test', tagType='type A', path='path/to/test')
    # print({key: val for key, val in asdict(node).items() if val is not None})

    # from tests.test_node import test_json_unchanged
    # test_json_unchanged()
    from tests.test_node import test_tilde_removed_from_file
    test_tilde_removed_from_file()

    # node = Node('testname', 'testTagType', 'testPath')
    # for f in fields(node):
    #     # print(type(f))
    #     print(type(getattr(node, f.name)))

