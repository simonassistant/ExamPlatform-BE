from typing import Annotated

from fastapi import Depends, HTTPException
from starlette import status

from app.data.dao.user_dao import UserDAO
from app.util.util_jwt import oauth2_scheme, jwt_token_decode


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    user_id:str = get_current_user_id(token)
    current_user = UserDAO().get(user_id)
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not exist!",
        )
    if current_user.is_deleted:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user")
    return current_user

def get_current_user_id(token: Annotated[str, Depends(oauth2_scheme)]) -> str:
    user_id = jwt_token_decode(token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials!",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user_id