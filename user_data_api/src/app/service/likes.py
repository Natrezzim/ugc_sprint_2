from typing import Optional, Dict, Union, Type
from uuid import UUID

from fastapi import Depends
from motor.core import AgnosticCollection

from app.db.mongo_db import get_mongo
from app.models.film_likes_schema import MovieLikeSchema
from app.utils.functions import get_rating


class MovieLikesService:

    def __init__(self, model: Type[MovieLikeSchema], collection: AgnosticCollection):
        self.model = model
        self.collection = collection

    async def _get_movie_data(self, movie_filter: Dict[str, str]) -> Optional[Dict[str, int]]:

        if movie_document := await self.collection.find_one(movie_filter):
            response_data = {
                "movie_id": movie_document['movie_id'],
                "likes": len(movie_document['like_by']),
                "dislikes": len(movie_document['dislike_by']),
                "rating": movie_document['rating'],
            }
            return response_data

        return None

    async def add_like_dislike(self, user_id: str, movie_id: Union[UUID, str], like: bool) -> MovieLikeSchema:
        movie_id = str(movie_id)
        movie_filter = {
            "movie_id": movie_id,
        }
        if movie := await self.collection.find_one(movie_filter):
            like_by = set(movie['like_by'])
            dislike_by = set(movie['dislike_by'])

            if like and user_id not in dislike_by:
                like_by.add(user_id)
            elif not like and user_id not in like_by:
                dislike_by.add(user_id)
            else:
                movie_response_data = await self._get_movie_data(movie_filter)
                return self.model(**movie_response_data)  # type: ignore[arg-type]

            movie_data = {
                "like_by": list(like_by),
                "dislike_by": list(dislike_by),
                "rating": get_rating(like_by, dislike_by),
            }
            await self.collection.update_one(
                movie_filter,
                {"$set": movie_data},
            )
        else:
            like_by = [user_id] if like else []  # type: ignore[assignment]
            dislike_by = [user_id] if not like else []  # type: ignore[assignment]
            rating = get_rating(like_by, dislike_by)
            movie_data = {
                "movie_id": movie_id,
                "like_by": list(like_by),
                "dislike_by": list(dislike_by),
                "rating": rating,
            }
            await self.collection.insert_one(movie_data)

        movie_response_data = await self._get_movie_data(movie_filter)
        return self.model(**movie_response_data)  # type: ignore[arg-type]

    async def get(self, movie_id: UUID) -> Optional[MovieLikeSchema]:
        movie_filter = {"movie_id": str(movie_id)}
        if movie_response_data := await self._get_movie_data(movie_filter):
            return self.model(**movie_response_data)

        return None

    async def remove_like_dislike(
        self,
        user_id: str,
        movie_id: Union[str, UUID],
        like: bool,
    ) -> Optional[MovieLikeSchema]:
        movie_id = str(movie_id)
        movie_filter = {"movie_id": movie_id}
        if movie_document := await self.collection.find_one(movie_filter):
            like_by = movie_document['like_by']
            dislike_by = movie_document['dislike_by']
            try:
                like_by.remove(user_id) if like else dislike_by.remove(user_id)
            except ValueError:
                raise
            movie_data = {
                "like_by": like_by,
                "dislike_by": dislike_by,
                "rating": get_rating(like_by, dislike_by),
            }
            await self.collection.update_one(
                movie_filter,
                {"$set": movie_data},
            )

            movie_response_data = await self._get_movie_data(movie_filter)
            return self.model(**movie_response_data)  # type: ignore[arg-type]

        return None


def get_user_bookmarks_service(
    mongo: AgnosticCollection = Depends(get_mongo),
) -> MovieLikesService:
    collection = mongo.get_collection('movie_likes')
    return MovieLikesService(MovieLikeSchema, collection)
