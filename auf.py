from typing import Type, Callable, Optional
from dataclass_factory import validate, Factory, Schema, NameStyle
import os
from dataclasses import dataclass


def get_settings(cls: Type, data: dict=os.environ, schema: Optional[Schema]=None):
    if schema is None:
        factory = Factory()
    else:
        factory = Factory(
            schemas= {cls: schema(name_style=NameStyle.ignore)}
        )
    # data = { name: (h := handler(name)) if h is not None else field.default for name, field in cls.__dataclass_fields__}
    return factory.load(data, cls)



def validate(*fields: str, dynamic: bool = False, alias_by_func_name: bool = True):
    def dec(func):
        def wrap(self, *args):
            if alias_by_func_name:
                fields += (func.__name__,)
            if dynamic:
                validators = self.__auf_dynamic_validators
            else:
                validators = self.__auf_validators
            for field in fields:
                validators.update({field: func})
            return func
        return wrap
    return dec


def decorator(get_data: Callable, *, get_data_params: list = None , dataclass_set: Optional[dict]=None):
    if dataclass_set is None:
        dataclass_set = {}
    if get_data_params is None:
        get_data_params = []
    data = get_data(*get_data_params)
    def wrap(cls):
        cls = dataclass(cls, **dataclass_set)
        cls.__auf_validators = {}
        cls.__auf_dynamic_validators = {}
        cls.__init__ = lambda self: super().__init__(data)
        def post_init(self):
            for name, field in self.__dataclass_fields__.items():
                if name in self.__auf_validators:
                    self.__dataclass_fields__[name] = self.__auf_validators[name](data.get([name]))
        
        def get_attr(self, attr):
            if attr in self.__auf_dynamic_validators:
                return self.__auf_dynamic_validators[attr](data.get(attr))
            
        cls.__post_init__ = post_init
        return cls
    return wrap
