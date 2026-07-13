from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class RegisterUser(BaseModel):
    """Request schema for user self-registration.

    Accepts a single ``name`` (split into first_name/last_name internally),
    ``email``, and ``password``.  Uses camelCase JSON keys.
    """

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    name: str
    email: str
    password: str
