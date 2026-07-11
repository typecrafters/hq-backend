from fastapi import APIRouter, HTTPException

from app.dependencies import RequiresAuth, RequiresMessageService
from app.schemas.request.create_message import CreateMessage
from app.schemas.request.reply_to_message import ReplyToMessage
from app.schemas.response.item_response import ItemResponse
from app.schemas.response.list_response import ListResponse
from app.schemas.response.message import MessageResponse
router = APIRouter(prefix='/messages')

@router.get('/', response_model=ListResponse[MessageResponse])
def get_all_messages(msg_service: RequiresMessageService, current: RequiresAuth, limit: int | None = None, offset: int | None = None):
    try:
        if not current.user.can('read:message'):
            raise HTTPException(403, 'Forbidden.')
    
        limit = min(max(1, limit), 50) if limit else 50
        offset = max(0, offset) if offset else 0

        messages = msg_service.get_all(limit, offset)
            
        return ListResponse(message='Message found', items=messages)
    except HTTPException as e:
        raise e
    except:
        raise HTTPException(500, 'An unknown error occurred while retrieving the message.')

@router.get('/{id}', response_model=ItemResponse[MessageResponse])
def get_message_by_id(id: int, msg_service: RequiresMessageService, current: RequiresAuth):
    try:
        if not current.user.can('read:message'):
            raise HTTPException(403, 'Forbidden.')
    
        message = msg_service.get_by_id(id)

        if message is None:
            raise HTTPException(404, 'Message not found')
        
        return ItemResponse(message='Message found', item=message)
    except HTTPException as e:
        raise e
    except:
        raise HTTPException(500, 'An unknown error occurred while retrieving the message.')

@router.post('/', status_code=201, response_model=ItemResponse[MessageResponse])
def create_message(data: CreateMessage, msg_service: RequiresMessageService):
    try:
        message = msg_service.create(data.full_name, data.email, data.message)
        return ItemResponse(message='Message saved.', item=message)
    except HTTPException as e:
        raise e
    except Exception as e:
        print(e)
        raise HTTPException(500, 'An unknown error occurred while saving the message.')

@router.patch('/{id}/read', response_model=ItemResponse[MessageResponse])
def set_message_to_read(id: int, msg_service: RequiresMessageService, current: RequiresAuth):
    try:
        if not current.user.can('read:message'):
            raise HTTPException(403, 'Forbidden.')
        
        message = msg_service.read_now(id)

        if message is None:
            raise HTTPException(404, 'Message not found')
        
        return ItemResponse(message='Message updated to read', item=message)

    except HTTPException as e:
        raise e
    except:
        raise HTTPException(500, 'An unknown error occurred while setting the message to read.')

@router.patch('/{id}/reply', response_model=ItemResponse[MessageResponse])
def reply_to_message(id: int, data: ReplyToMessage, msg_service: RequiresMessageService, current: RequiresAuth):
    try:
        if not current.user.can('write:message'):
            raise HTTPException(403, 'Forbidden.')
        
        message = msg_service.reply_now(id, data.reply, current.user.id)

        if message is None:
            raise HTTPException(404, 'Message not found')
        
        msg_service.send_reply(message)
        
        return ItemResponse(message='Message updated to read', item=message)

    except HTTPException as e:
        raise e
    except:
        raise HTTPException(500, 'An unknown error occurred while replying to the message.')
    
@router.delete('/{id}', status_code=204)
def delete_message(id: int, msg_service: RequiresMessageService, current: RequiresAuth):
    try:
        if not current.user.can('delete:message'):
            raise HTTPException(403, 'Forbidden.')
        
        result = msg_service.delete(id)

        if not result:
            raise HTTPException(404, 'Message not found')

    except HTTPException as e:
        raise e
    except:
        raise HTTPException(500, 'An unknown error occurred while deleting the message.')