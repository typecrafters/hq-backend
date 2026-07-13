from pydantic import BaseModel, ConfigDict, model_validator
from pydantic.alias_generators import to_camel

class ResetPassword(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)
    
    password: str
    confirm_password: str

    @model_validator(mode='after')
    def passwords_match(self) -> 'ResetPassword':
        if self.password != self.confirm_password:
            raise ValueError('Passwords do not match.')
        return self
