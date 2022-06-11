import datetime
import uuid
from typing import Dict, List, Optional, Type

from fastapi import Depends
from motor.core import AgnosticCollection

from app.db.mongo_db import get_mongo
from app.models.user_reviews import UserReview
from app.utils.functions import get_rating


class UserReviewsService:
    """Class with service functions."""

    def __init__(self, model: Type[UserReview], collection: AgnosticCollection):
        self.model = model
        self.collection = collection

    async def add(self, movie_id: uuid.UUID, user_id: str, text: str) -> UserReview:
        review_id = str(uuid.uuid4())
        review_filter = {"review_id": review_id}
        await self.collection.insert_one(
            {
                "movie_id": str(movie_id),
                "review_id": review_id,
                "user_id": user_id,
                "created": datetime.datetime.today().replace(microsecond=0),
                "text": text,
            },
        )
        review = await self.collection.find_one(review_filter)
        return self.model(**review)

    async def get(
        self,
        movie_id: uuid.UUID,
        rating_sort: Optional[str],
        created_sort: Optional[str],
    ) -> Optional[List[UserReview]]:
        """
        Get list of reviews by movie_id.

        :param movie_id: Movie ID
        :param rating_sort: Rating sorting[asc, desc]
        :param created_sort: Created time sorting[asc, desc]
        :return: List of reviews
        """
        movie_filter = {"movie_id": str(movie_id)}
        reviews = self.collection.find(movie_filter)
        if created_sort == "asc":
            reviews.sort("created", 1)
        if created_sort == "desc":
            reviews.sort("created", -1)
        reviews_list = []
        async for review in reviews:
            likes = await self.collection.find_one({"review_id": review["review_id"]}, {"like_by"})
            if "like_by" in likes:
                likes = likes["like_by"]
            dislikes = await self.collection.find_one({"review_id": review["review_id"]}, {"dislike_by"})
            if "dislike_by" in likes:
                dislikes = likes["like_by"]
            rating = get_rating(likes, dislikes)
            review["rating"] = float('{:.1f}'.format(rating))
            reviews_list.append(self.model(**review))
        if rating_sort == "asc":
            reviews_list = sorted(reviews_list, key=lambda x: x.rating)
        if rating_sort == "desc":
            reviews_list = sorted(reviews_list, key=lambda x: x.rating, reverse=True)
        if reviews:
            return reviews_list
        return None

    async def add_like(self, user_id: str, review_id: uuid.UUID) -> Dict[str, int]:
        """
        Add like to review and delete dislike if already have.

        :param user_id: User ID
        :param review_id: Review ID
        :return: User ID
        """
        review_filter = {"review_id": str(review_id)}
        dislike = await self.collection.find_one({"dislike_by": {"$in": [user_id]}}, {"dislike_by": user_id})
        if dislike is not None and dislike["dislike_by"] == user_id:
            await self.collection.update_one(review_filter, {"$pull": {"dislike_by": user_id}}, upsert=True)
        await self.collection.update_one(review_filter, {"$addToSet": {"like_by": user_id}}, upsert=True)
        like = await self.collection.find_one({"like_by": {"$in": [user_id]}}, {"like_by": user_id})
        return like

    async def add_dislike(self, user_id: str, review_id: str) -> Dict[int, str]:
        """
        Add dislike to review and delete like if already have.

        :param user_id: User ID
        :param review_id: Review ID
        :return: User ID
        """
        review_filter = {"review_id": review_id}
        like = await self.collection.find_one({"like_by": {"$in": [user_id]}}, {"like_by": user_id})
        if like is not None and like["like_by"] == user_id:
            await self.collection.update_one(review_filter, {"$pull": {"like_by": user_id}}, upsert=True)
        await self.collection.update_one(review_filter, {"$addToSet": {"dislike_by": user_id}}, upsert=True)
        dislike = await self.collection.find_one({"dislike_by": {"$in": [user_id]}}, {"dislike_by": user_id})
        return dislike


def get_user_reviews_service(
    mongo: AgnosticCollection = Depends(get_mongo),
) -> UserReviewsService:
    """
    :param mongo: Mongo.

    :return: UserReviewsService class
    """
    collection = mongo.get_collection('user_reviews')
    return UserReviewsService(UserReview, collection)
