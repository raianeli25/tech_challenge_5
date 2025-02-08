from pydantic import BaseModel

class Recommendation(BaseModel):
    data: dict