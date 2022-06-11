from pydantic import BaseModel
from uuid import UUID


class MovieLikeSchema(BaseModel):
    movie_id: UUID
    likes: int
    dislikes: int
    rating: float

    class Config:
        schema_extra = {
            "example": {
                "movie_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "likes": 45,
                "dislikes": 10,
                "rating": 4.3,
            }
        }
