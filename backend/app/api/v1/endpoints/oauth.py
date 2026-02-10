from fastapi import APIRouter, HTTPException, Depends
from google.oauth2 import id_token
from google.auth.transport import requests
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid

from app.core.config import settings
from app.db.session import get_db
from app.models.user import User, UserRole
from app.core.security import create_access_token, create_refresh_token
from pydantic import BaseModel

router = APIRouter()

class GoogleAuthRequest(BaseModel):
    token: str  # Google ID token
    role: str = "renter"  # Default role for new users

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: dict

@router.post("/google", response_model=TokenResponse)
async def google_auth(
    auth_data: GoogleAuthRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Authenticate or register user with Google
    
    This endpoint accepts a Google ID token from the frontend,
    verifies it, and either:
    - Logs in an existing user
    - Creates a new user if email doesn't exist
    """
    try:
        # Verify the Google token
        idinfo = id_token.verify_oauth2_token(
            auth_data.token,
            requests.Request(),
            settings.GOOGLE_CLIENT_ID
        )
        
        # Check if token is from correct issuer
        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise ValueError('Wrong issuer.')
        
        # Extract user data from Google token
        google_id = idinfo['sub']
        email = idinfo['email']
        full_name = idinfo.get('name', '')
        profile_image = idinfo.get('picture', '')
        email_verified = idinfo.get('email_verified', False)
        
    except ValueError as e:
        # Invalid token
        raise HTTPException(
            status_code=401,
            detail=f"Invalid Google token: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to verify Google token: {str(e)}"
        )
    
    # Check if user exists by email or oauth_id
    result = await db.execute(
        select(User).where(
            (User.email == email) | 
            ((User.oauth_provider == "google") & (User.oauth_id == google_id))
        )
    )
    user = result.scalar_one_or_none()
    
    if user:
        # Existing user - update OAuth info if not set
        if not user.oauth_provider:
            user.oauth_provider = "google"
            user.oauth_id = google_id
            if profile_image and not user.profile_image:
                user.profile_image = profile_image
            if email_verified and not user.is_verified:
                user.is_verified = True
            await db.commit()
            await db.refresh(user)
    else:
        # Create new user
        user = User(
            id=uuid.uuid4(),
            email=email,
            full_name=full_name,
            profile_image=profile_image,
            role=UserRole(auth_data.role) if auth_data.role in ["owner", "renter"] else UserRole.RENTER,
            is_active=True,
            is_verified=email_verified,
            oauth_provider="google",
            oauth_id=google_id,
            hashed_password=None  # No password for OAuth users
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
    
    # Generate tokens
    access_token = create_access_token(subject=str(user.id))
    refresh_token = create_refresh_token(subject=str(user.id))
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user={
            "id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "profile_image": user.profile_image,
            "is_verified": user.is_verified
        }
    )

@router.get("/google/config")
async def get_google_config():
    """
    Return Google OAuth configuration for frontend
    """
    return {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI
    }
