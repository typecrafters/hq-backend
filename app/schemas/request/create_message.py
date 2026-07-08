from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

class CreateMessage(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    full_name: str
    email: str
    message: str