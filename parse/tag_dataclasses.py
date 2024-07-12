from typing import Literal, Self, Type, Union
from dataclasses import asdict, dataclass, field, fields

type ValueSource = Literal[
        'opc',
        'expr',
        'reference',
        'memory',
        'db',
        None,
    ]
type TagType = Literal[
        'AtomicTag', 
        'Folder', 
        'UdtType', 
        'UdtInstance',
    ]

@dataclass
class Binding:
    obj: Union[str, dict, bool]

    def __post_init__(self):
        self._obj_type: Type
        if isinstance(self.obj, str) or isinstance(self.obj, bool):
            self._binding =  self.obj
        if isinstance(self.obj, dict):
            self._binding =  self.obj['binding']
        self._obj_type = type(self.obj)

    def convert_to_parameter(self):
        if self.bindType is not None and self.bindType == 'parameter':
            return
        self.obj = {'bindType': 'parameter', 'binding': self.binding}
        self.bindType = 'parameter'
        self.obj_type = dict

    @property
    def binding(self) -> str | bool:
        """The path property."""
        return self._binding

    @binding.setter
    def binding(self, value) -> None:
        if isinstance(value, bool):
            self.obj_type = bool
        self._binding = value

    @property
    def obj_type(self) -> Type:
        return self._obj_type

    @obj_type.setter
    def obj_type(self, value: Type) -> None:
        self._obj_type = value

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
        if isinstance(self.binding, bool):
            return self.binding
        if self.obj_type is dict:
            bind_dict = {'binding': self.binding}
            if self.bindType is not None:
                bind_dict['bindType'] = self.bindType
            return bind_dict
        if self.obj_type in (str, bool):
            return self.binding

@dataclass
class TagParameter:
    name: str
    dataType: str
    value: int|str|Binding|None

    def to_obj(self) -> tuple[str, dict]:
        return_dict = {'dataType': self.dataType}
        if self.value is None:
            pass
        elif isinstance(self.value, int) or isinstance(self.value, str):
            return_dict['value'] = self.value # type: ignore
        elif isinstance(self.value, Binding):
            return_dict['value'] = self.value.to_obj() # type: ignore
        return (self.name, return_dict)
    
    @classmethod
    def from_obj(cls, parameter_name: str, parameter_dict: dict) -> Self:
        name = parameter_name
        dataType = parameter_dict['dataType']
        val = parameter_dict.get('value')
        if val is not None:
            type_dict = {
            int: val,
            str: val,
            dict: Binding(val),
            }
            value = type_dict[type(val)]
            return cls(name, dataType, value)
        return cls(name, dataType, None)

@dataclass(order=True)
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

    def __post_init__(self):
        self.exceptions = ['opcItemPath', '_extras', 'path', 'id', 'id_log']
        self.binding_fields = (field_inst.name 
            for field_inst in fields(self) 
            if isinstance(getattr(self,field_inst.name), Binding))

    @classmethod
    def from_obj(
        cls, 
        node_dict: dict,
        path: str, 
        id: int, 
        id_log: list[tuple[int, TagType]],
    ) -> Self:

        """
        Construct Node object from a json tag provider object
        """
        struct_dict = {key: val 
            if 'Binding' not in str(cls.__annotations__[key]) 
            else Binding(val) 
            for key, val in node_dict.items() 
            if key in cls.__annotations__ 
            and key != 'parameters'
            }
        if 'parameters' in node_dict:
            struct_dict['parameters'] = [
                TagParameter.from_obj(node_name, node_val) 
                for node_name, node_val in node_dict['parameters'].items()
            ] 
        struct_dict['_extras'] = {key: val for key, val in node_dict.items() if key not in cls.__annotations__}
        return cls(id=id, path=path, id_log=id_log, **struct_dict) #type:ignore

    def to_obj(self) -> tuple[dict, str]:
        """
        return Node object to json-style dict + path string
        """
        data_dict = {key: val 
            if 'Binding' not in str(self.__annotations__[key]) 
            else getattr(self, key).to_obj() 
            for key, val in asdict(self).items()
            if val is not None
            and key not in self.exceptions}
        if self.opcItemPath is not None:
            data_dict['opcItemPath'] = self.opcItemPath.to_obj()
        if self.parameters is not None:
            data_dict['parameters'] = {parameter.to_obj()[0]: parameter.to_obj()[1] for parameter in self.parameters}
        return (data_dict | self._extras, self.path)

