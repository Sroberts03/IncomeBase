import os
import httpx
from datetime import datetime, timedelta
from jose import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

JWKS_URL = os.getenv("SUPABASE_JWKS_URL")
AUDIENCE = os.getenv("SUPABASE_AUDIENCE", "authenticated")
CACHE_TTL_HOURS = 24 

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

_cached_keys = None
_last_fetch_time = None

async def get_supabase_keys():
    global _cached_keys, _last_fetch_time
    
    now = datetime.now()
    
    should_refresh = (
        _cached_keys is None or 
        _last_fetch_time is None or 
        (now - _last_fetch_time) > timedelta(hours=CACHE_TTL_HOURS)
    )
    
    if should_refresh:
        async with httpx.AsyncClient() as client:
            try:
                print(f"🔄 Refreshing JWKS keys from Supabase... (Next refresh in {CACHE_TTL_HOURS}h)")
                response = await client.get(JWKS_URL)
                response.raise_for_status()
                
                _cached_keys = response.json()["keys"]
                _last_fetch_time = now
            except Exception as e:
                # If the refresh fails but we have old keys, keep using them as a fallback
                if _cached_keys:
                    print(f"⚠️ JWKS refresh failed. Using stale cache. Error: {e}")
                    return _cached_keys
                raise HTTPException(status_code=500, detail="Auth Provider Unavailable")
                
    return _cached_keys

async def get_current_user_id(token: str = Depends(oauth2_scheme)) -> str:
    keys = await get_supabase_keys()
    
    try:
        # We verify the token using the dynamic keys from Supabase
        payload = jwt.decode(
            token, 
            keys, 
            algorithms=["ES256"], 
            audience="authenticated"
        )
        
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="User ID missing")
            
        return user_id
        
    except Exception as e:
        # If the token is expired or forged, it hits here
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session"
        )