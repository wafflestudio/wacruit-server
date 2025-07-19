from pydantic import BaseModel


class CreatePreRegistrationRequest(BaseModel):
    url: str
    generation: str
    is_active: bool


class UpdatePreRegistrationRequest(BaseModel):
    url: str | None = None
    generation: str | None = None
    is_active: bool | None = None


class PreRegistrationResponse(BaseModel):
    id: int
    url: str
    generation: str
    is_active: bool

    class Config:
        orm_mode = True
