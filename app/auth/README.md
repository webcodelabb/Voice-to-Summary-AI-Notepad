# Authentication Module

This directory is a placeholder for implementing authentication in the Voice-to-Summary AI Notepad backend.

## Implementation Options

### JWT Authentication
```python
# Example JWT implementation
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

security = HTTPBearer()

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

### OAuth2 with Google/Microsoft
```python
# Example OAuth2 implementation
from fastapi_oauth2 import OAuth2
from fastapi_oauth2.client import OAuth2Client

oauth2 = OAuth2(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    authorize_url="https://accounts.google.com/o/oauth2/auth",
    token_url="https://oauth2.googleapis.com/token"
)
```

## Integration Steps

1. **Choose Authentication Method**: JWT, OAuth2, or custom
2. **Create Authentication Middleware**: Add to `app/main.py`
3. **Protect Routes**: Add `@requires_auth` decorator to protected endpoints
4. **User Management**: Implement user registration, login, and profile endpoints
5. **Database Integration**: Add user storage (SQLAlchemy, MongoDB, etc.)

## Example Protected Route
```python
from app.auth.jwt_auth import verify_token

@router.post("/transcribe")
async def transcribe_audio(
    file: UploadFile = File(...),
    current_user: dict = Depends(verify_token)
):
    # Only authenticated users can access this endpoint
    return await transcribe_service.transcribe(file)
```

## Environment Variables
Add these to your `.env` file:
```env
JWT_SECRET_KEY=your_jwt_secret_here
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
``` 