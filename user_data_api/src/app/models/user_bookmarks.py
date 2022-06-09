from typing import List
from uuid import UUID

from pydantic import BaseModel


class UserBookmarks(BaseModel):
    bookmarks: List[UUID]
