from typing import Self, Union
from dataclasses import asdict, dataclass, field

@dataclass
class OPCItemPath:
    obj: Union[str, dict]

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

    def to_obj(self):
        bind_dict = {'binding': self.binding}
        if self.bindType is not None:
            bind_dict['bindType'] = self.bindType
        return bind_dict

@dataclass(order=True)
class Parameters:
    namespace: dict|None
    namespaceFlag: dict|None

    @classmethod
    def from_obj(cls, node_dict: dict):
        struct_dict = {key: val for key, val in node_dict.items() if key in cls.__annotations__}
        return cls(**struct_dict)

@dataclass(order=True)
class Node:
    path: str
    name: str = ''
    tagType: str = ''
    valueSource: str|None = None
    historyEnabled: bool|dict|None = None 
    historyMaxAge: int|None = None
    typeId: str|None = None
    expression: str|None= None
    parameters: dict|None = None
    alarms: dict|None = None
    opcItemPath: OPCItemPath|None = None
    tags: dict|None = None
    _extras: dict = field(default_factory=dict)

    def __post_init__(self):
        self.exceptions = ['opcItemPath', '_extras', 'path']

    @classmethod
    def from_obj(cls, node_dict: dict, path: str) -> Self:
        """
        Construct Node object from a json tag provider object
        """
        struct_dict = {}
        struct_dict['_extras'] = {key: val for key, val in node_dict.items() if key not in cls.__annotations__}
        if 'opcItemPath' in node_dict:
            struct_dict['opcItemPath'] = OPCItemPath(node_dict['opcItemPath'])
        return cls(path=path, **struct_dict)

    def to_obj(self) -> tuple[dict, str]:
        """
        return Node object to json-style dict + path string
        """
        data_dict = {key: val for key, val in asdict(self).items()
            if val is not None
            and key not in self.exceptions}
        if self.opcItemPath is not None:
            data_dict['opcItemPath'] = self.opcItemPath
        return (data_dict | self._extras, self.path)

