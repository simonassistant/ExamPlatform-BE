from datetime import datetime, timezone, timedelta

import jwt
from fastapi.security import OAuth2PasswordBearer

JWT_TOKEN_SECRET_SALT = "ep2025"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/exam/examinee/login")
def jwt_token_decode(token) -> str:
    payload = jwt.decode(token, key=JWT_TOKEN_SECRET_SALT, algorithms='HS256', options={'verify_signature': True})
    user_id = payload.get("user_id")
    return user_id

def jwt_token_encode(user_id: str) -> str:
    payload = {'user_id': user_id, 'exp': datetime.now(timezone.utc) + timedelta(weeks=1)}
    jwt_token = jwt.encode(payload, JWT_TOKEN_SECRET_SALT, algorithm="HS256")
    return jwt_token
