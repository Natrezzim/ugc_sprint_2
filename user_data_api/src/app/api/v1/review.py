import json
from http import HTTPStatus
from typing import List, Union

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response

from app.models.user_reviews import UserReview
from app.service.auth import Auth
from app.service.reviews import UserReviewsService, get_user_reviews_service

router = APIRouter()
auth_handler = Auth()


@router.get(
    '/',
    response_model=List[UserReview],
    description='Получить отзывы пользователя',
)
async def get_reviews(
    movie_id: UUID,
    rating_sort: Union[str, None] = None,
    created_sort: Union[str, None] = None,
    reviews_service: UserReviewsService = Depends(get_user_reviews_service),
) -> List[UserReview]:
    """
    Get list of reviews.

    :param movie_id: Movie ID
    :param rating_sort: Rating sorting[asc, desc]
    :param created_sort: Created time sorting[asc, desc]
    :param reviews_service: UserReviewsService
    :return: List of reviews
    """
    reviews = await reviews_service.get(movie_id, rating_sort, created_sort)
    if not reviews:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='user reviews not found',
        )
    return reviews


@router.post(
    '/{movie_id}',
    response_model=UserReview,
    description='Добавить отзыв о фильме',
    response_description='Возвращается добавленный отзыв',
)
async def add_review(
    movie_id: UUID,
    text: str,
    user_id: str = Depends(auth_handler),
    reviews_service: UserReviewsService = Depends(get_user_reviews_service),
) -> UserReview:
    """
    Add new review to movie.

    :param movie_id: Movie ID
    :param user_id: User id
    :param text: Text of review
    :param reviews_service: UserReviewsService
    :return: Added review
    """
    reviews = await reviews_service.add(movie_id, user_id, text)
    if not reviews:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='movie not found',
        )
    return reviews


@router.post(
    '/like/{review_id}',
    response_model=UserReview,
    description='Добавить лайк к рецензии',
    response_description='Возвращается user_id',
)
async def add_like(
    review_id: UUID,
    user_id: str = Depends(auth_handler),
    reviews_service: UserReviewsService = Depends(get_user_reviews_service),
) -> Response:
    """
    Adding like to review.

    :param review_id: Review ID
    :param user_id: User id
    :param reviews_service: UserReviewsService
    :return: User ID
    """
    reviews = await reviews_service.add_like(user_id, review_id)
    response = {}
    for k, v in reviews.items():
        if k == "like_by":
            response = {k: v}
    if not reviews:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='movie not found',
        )
    return Response(content=json.dumps(response), media_type="application/json")


@router.post(
    '/dislike/{review_id}',
    response_model=UserReview,
    description='Добавить дизлайк к рецензии',
    response_description='Возвращается user_id',
)
async def add_dislike(
    review_id: str,
    user_id: str = Depends(auth_handler),
    reviews_service: UserReviewsService = Depends(get_user_reviews_service),
) -> Response:
    """
    Adding dislike to review.

    :param review_id: Review ID
    :param user_id: User id
    :param reviews_service: UserReviewsService
    :return: User ID
    """
    reviews = await reviews_service.add_dislike(user_id, review_id)
    response = {}
    for k, v in reviews.items():
        if k == "dislike_by": # type: ignore[comparison-overlap]
            response = {k: v}
    if not reviews:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='movie not found',
        )
    return Response(content=json.dumps(response), media_type="application/json")
