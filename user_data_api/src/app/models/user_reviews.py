import datetime
from typing import List, Optional, Dict, Union
from uuid import UUID

from pydantic import BaseModel


class UserReview(BaseModel):
    movie_id: UUID
    review_id: UUID
    user_id: UUID
    created: datetime.datetime
    text: str
    like_by: Optional[List[UUID]] = []
    dislike_by: Optional[List[UUID]] = []
    rating: float = 0.0
