from pydantic import BaseModel


class Contract(BaseModel):
    name: str
    start: int
    duration: int
    price: int

    class Config:
        """
        set this contract to be frozen, so it can be hashable
        hashable behaviour used in approximate beam search contract selector service
        """
        frozen = True