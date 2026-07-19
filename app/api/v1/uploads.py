from fastapi import APIRouter, HTTPException

from app.core.file_requirements import FileRequirements
from app.dependencies import RequiresAuth, RequiresFileService
from app.schemas.request.sign_upload import SignUpload
from app.schemas.response.item_response import ItemResponse

router = APIRouter(prefix='/uploads')

image_requirements = FileRequirements.images()
post_requirements = FileRequirements.posts()


@router.post('/img', response_model=ItemResponse[str])
def for_image(data: SignUpload, current: RequiresAuth, file_service: RequiresFileService):
    try:
        if not current.user.can('write:media'):
            raise HTTPException(403, 'Forbidden.')
        result = image_requirements.are_met(data.content_type, data.size)
        if not result.ok:
            raise HTTPException(result.status_code, result.detail)

        url = file_service.sign_put(data.key, data.content_type)
        return ItemResponse(message='Upload URL signed successfully', item=url)
    except HTTPException as e:
        raise e
    except:
        raise HTTPException(500, 'An unknown error occurred while signing the upload URL.')

@router.post('/post', response_model=ItemResponse[str])
def for_blog_post(data: SignUpload, current: RequiresAuth, file_service: RequiresFileService):
    try:
        if not current.user.can('write:media'):
            raise HTTPException(403, 'Forbidden.')
        result = post_requirements.are_met(data.content_type, data.size)
        if not result.ok:
            raise HTTPException(result.status_code, result.detail)

        url = file_service.sign_put(data.key, data.content_type)
        return ItemResponse(message='Upload URL signed successfully', item=url)
    except HTTPException as e:
        raise e
    except:
        raise HTTPException(500, 'An unknown error occurred while signing the upload URL.')
