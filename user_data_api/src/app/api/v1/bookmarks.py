from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from app.models.user_bookmarks import UserBookmarks
from app.service.auth import Auth
from app.service.bookmarks import UserBookmarksService, get_user_bookmarks_service

router = APIRouter()
auth_handler = Auth()


@router.get('/',
            response_model=UserBookmarks,
            description='Получить закладки пользователя',
            )
async def get_bookmarks(
        user_id: str = Depends(auth_handler),
        bookmarks_service: UserBookmarksService = Depends(get_user_bookmarks_service)
):
    bookmarks = await bookmarks_service.get(user_id)
    if not bookmarks:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail='user bookmarks not found')
    return bookmarks


@router.post('/{movie_id}',
             response_model=UserBookmarks,
             description='Добавить фильм в закладки пользователя',
             response_description='Возвращаются закладки пользователя',
             )
async def add_bookmarks(
        movie_id: UUID,
        user_id: str = Depends(auth_handler),
        bookmarks_service: UserBookmarksService = Depends(get_user_bookmarks_service)
):
    bookmarks = await bookmarks_service.add(user_id, movie_id)
    if not bookmarks:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail='user bookmarks not found')
    return bookmarks


@router.delete('/{movie_id}',
               response_model=UserBookmarks,
               description='Удалить фильм из закладок пользователя',
               response_description='Возвращаются закладки пользователя',
               )
async def delete_bookmarks(
        movie_id: UUID,
        user_id: str = Depends(auth_handler),
        bookmarks_service: UserBookmarksService = Depends(get_user_bookmarks_service)
):
    bookmarks = await bookmarks_service.remove(user_id, movie_id)
    if not bookmarks:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail='user bookmarks not found')
    return bookmarks
