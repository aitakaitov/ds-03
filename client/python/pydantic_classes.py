from pydantic import BaseModel


class GetQuery(BaseModel):
    key: str


class PutQuery(BaseModel):
    key: str
    value: str


class DeleteQuery(BaseModel):
    key: str


class GetResponse(BaseModel):
    key: str
    value: str
    code: int


class CodeResponse(BaseModel):
    code: int
