from fastapi import APIRouter, HTTPException
from app.dependencies import RequiresAuth, RequiresFileService
from app.schemas.request.sign_upload import SignUpload
from app.schemas.response.item_response import ItemResponse

router = APIRouter(prefix='/uploads')


@router.post('/', response_model=ItemResponse[str])
def create_upload_link(data: SignUpload, current: RequiresAuth, file_service: RequiresFileService):
    if not data.key.startswith(f'profilePictures/{current.user.id}@'):
        raise HTTPException(403, 'Forbidden.')

    url = file_service.sign_upload(data.key)
    return ItemResponse(message="Signed upload URL generated.", item=url)