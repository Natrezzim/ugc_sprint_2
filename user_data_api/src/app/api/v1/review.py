from fastapi import APIRouter, Depends, HTTPException, Query, Header

router = APIRouter()


@router.get('/',
            # response_model=list[Model],
            # summary='',
            # description='',
            # response_description='',
            # tags=['']
            )
async def get_likes():
    ...
