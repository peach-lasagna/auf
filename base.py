from typing import Type, Callable, Optional
from dataclass_factory import validate, Factory, Schema, NameStyle
import os

def get_settings(cls: Type, data: dict=os.environ, schema: Optional[Schema]=None):
    if schema is None:
        factory = Factory()
    else:
        factory = Factory(
            schemas= {cls: schema(name_style=NameStyle.ignore)} 
        )
    # data = { name: (h := handler(name)) if h is not None else field.default for name, field in cls.__dataclass_fields__}
    return factory.load(data, cls)


