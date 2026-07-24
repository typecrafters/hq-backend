from fastapi import APIRouter, HTTPException

from app.dependencies import RequiresAuth, RequiresLegalPageService
from app.schemas.request.update_legal_page import UpdateLegalPage
from app.schemas.response.item_response import ItemResponse
from app.schemas.response.legal_page_response import LegalPageResponse

router = APIRouter(prefix='/legal')


@router.get('/{slug}', response_model=ItemResponse[LegalPageResponse])
def get_legal_page(
    slug: str,
    legal_page_service: RequiresLegalPageService
):
    page = legal_page_service.get_by_slug(slug)
    
    if page is None:
        raise HTTPException(404, 'Legal page not found.')

    return ItemResponse(message='Legal page retrieved', item=LegalPageResponse.from_model(page))


@router.patch('/{slug}', response_model=ItemResponse[LegalPageResponse])
def update_legal_page(
    slug: str,
    data: UpdateLegalPage,
    current: RequiresAuth,
    legal_page_service: RequiresLegalPageService
):
    if not current.user.can('write:legal'):
        raise HTTPException(403, 'Forbidden.')

    page = legal_page_service.update(
        slug,
        title=data.title,
        content_markdown=data.content_markdown,
    )

    if page is None:
        raise HTTPException(404, 'Legal page not found.')

    return ItemResponse(message='Legal page updated', item=LegalPageResponse.from_model(page))
