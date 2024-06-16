from typing import Self, Type, Union
from dataclasses import asdict, dataclass, field, fields

@dataclass
class Binding:
    obj: Union[str, dict, bool]

    def __post_init__(self):
        if isinstance(self.obj, str) or isinstance(self.obj, bool):
            self._binding =  self.obj
        if isinstance(self.obj, dict):
            self._binding =  self.obj['binding']

    @property
    def binding(self) -> str | bool:
        """The path property."""
        return self._binding
        # if isinstance(self.obj, str) or isinstance(self.obj, bool):
        #     return self.obj
        # if isinstance(self.obj, dict):
        #     return self.obj['binding']
        # return ''

    @binding.setter
    def binding(self, value) -> None:
        self._binding = value
        # if isinstance(self.obj, str) or isinstance(self.obj, bool):
        #     self.obj = value
        # if isinstance(self.obj, dict):
        #     self.obj['binding'] = value

    @property
    def obj_type(self) -> Type:
        return type(self.obj)

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
        if self.obj_type is dict:
            bind_dict = {'binding': self.binding}
            if self.bindType is not None:
                bind_dict['bindType'] = self.bindType
            return bind_dict
        if self.obj_type in (str, bool):
            return self.binding

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
    name: str = field(default_factory=str)
    tagType: str = field(default_factory=str)
    valueSource: str|None = None
    enabled: Binding|None = None
    historyEnabled: Binding|None = None 
    historyMaxAge: int|None = None
    typeId: str|None = None
    expression: str|None= None
    parameters: dict|None = None
    alarms: dict|None = None
    opcItemPath: Binding|None = None
    tags: dict|None = None
    _extras: dict = field(default_factory=dict)

    def __post_init__(self):
        self.exceptions = ['opcItemPath', '_extras', 'path']
        self.binding_fields = (field_inst.name 
            for field_inst in fields(self) 
            if isinstance(getattr(self,field_inst.name), Binding))

    @classmethod
    def from_obj(cls, node_dict: dict, path: str) -> Self:
        """
        Construct Node object from a json tag provider object
        """
        struct_dict = {key: val if 'Binding' not in str(cls.__annotations__[key]) else Binding(val) for key, val in node_dict.items() 
            if key in cls.__annotations__ 
            }
        struct_dict['_extras'] = {key: val for key, val in node_dict.items() if key not in cls.__annotations__}
        return cls(path=path, **struct_dict) #type:ignore

    def to_obj(self) -> tuple[dict, str]:
        """
        return Node object to json-style dict + path string
        """
        data_dict = {key: val if 'Binding' not in str(self.__annotations__[key]) else getattr(self, key).to_obj() for key, val in asdict(self).items()
            if val is not None
            and key not in self.exceptions}
        if self.opcItemPath is not None:
            data_dict['opcItemPath'] = self.opcItemPath.to_obj()
        return (data_dict | self._extras, self.path)

