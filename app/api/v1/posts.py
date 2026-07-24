from fastapi import APIRouter, HTTPException

from app.dependencies import RequiresAuth, RequiresPostService
from app.schemas.request.create_post import CreatePost
from app.schemas.request.update_post import UpdatePost
from app.schemas.response.item_response import ItemResponse
from app.schemas.response.list_response import ListResponse
from app.schemas.response.post_response import PostResponse

router = APIRouter(prefix='/posts')


@router.get('/', response_model=ListResponse[PostResponse])
def list_posts(
    current: RequiresAuth,
    post_service: RequiresPostService,
    limit: int | None = None,
    offset: int | None = None
):
    if not current.user.can('read:post'):
        raise HTTPException(403, 'Forbidden.')

    limit = min(max(1, limit), 50) if limit else 50
    offset = max(0, offset) if offset else 0

    posts = post_service.get_all(limit, offset)
    total = post_service.count_all()

    items = [PostResponse.from_model(p) for p in posts]

    return ListResponse(
        message='Posts retrieved',
        items=items,
        meta={'total': total, 'limit': limit, 'offset': offset}
    )


@router.get('/{id}', response_model=ItemResponse[PostResponse])
def get_post_by_id(
    id: int,
    current: RequiresAuth,
    post_service: RequiresPostService
):
    if not current.user.can('read:post'):
        raise HTTPException(403, 'Forbidden.')

    post = post_service.get_by_id(id)

    if post is None:
        raise HTTPException(404, 'Post not found.')
    return ItemResponse(message='Post retrieved', item=PostResponse.from_model(post))


@router.post('/', status_code=201, response_model=ItemResponse[PostResponse])
def create_post(
    data: CreatePost,
    current: RequiresAuth,
    post_service: RequiresPostService
):
    if not current.user.can('write:post'):
        raise HTTPException(403, 'Forbidden.')

    post = post_service.create(
        title=data.title,
        author=current.user.id,
        content=data.content,
        status=data.status,
        featured=data.featured,
        slug=data.slug,
        lang=data.lang,
    )

    return ItemResponse(message='Post created', item=PostResponse.from_model(post))


@router.patch('/{id}', status_code=200, response_model=ItemResponse[PostResponse])
def update_post(
    id: int,
    data: UpdatePost,
    current: RequiresAuth,
    post_service: RequiresPostService
):
    if not current.user.can('write:post'):
        raise HTTPException(403, 'Forbidden.')

    post = post_service.update(
        id,
        title=data.title,
        content=data.content,
        status=data.status,
        featured=data.featured,
        slug=data.slug,
        lang=data.lang,
    )

    if post is None:
        raise HTTPException(404, 'Post not found.')

    return ItemResponse(message='Post updated', item=PostResponse.from_model(post))


@router.delete('/{id}', status_code=204)
def delete_post(
    id: int,
    current: RequiresAuth,
    post_service: RequiresPostService
):
    if not current.user.can('delete:post'):
        raise HTTPException(403, 'Forbidden.')

    result = post_service.delete(id)

    if not result:
        raise HTTPException(404, 'Post not found.')
