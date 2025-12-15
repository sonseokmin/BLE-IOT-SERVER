from pydantic import BaseModel


class RequestModel(BaseModel):
    endNode: str
    cmdCategory: int
    cmdType: int
    parameter: int


class RequestDecryptModel(BaseModel):
    target: str
    msg: str
