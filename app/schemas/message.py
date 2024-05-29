from pydantic import BaseModel


class Detail(BaseModel):
    msg: str

    class Config:
        from_attributes = True


class Message(BaseModel):
    detail: Detail

    class Config:
        from_attributes = True
