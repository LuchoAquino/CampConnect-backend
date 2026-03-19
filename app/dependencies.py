from fastapi import HTTPException, Header
from jose import jwt, JWTError
import urllib.request
import json
from app.config import settings

# Global cache for the JWKS
_JWKS_CACHE = None

def get_jwks():
    global _JWKS_CACHE
    if _JWKS_CACHE is None:
        jwks_url = f"{settings.SUPABASE_URL}/auth/v1/.well-known/jwks.json"
        try:
            req = urllib.request.Request(jwks_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response:
                _JWKS_CACHE = json.loads(response.read().decode())
        except Exception as e:
            print("Failed to fetch JWKS:", e)
            return {"keys": []}
    return _JWKS_CACHE

async def get_current_user(authorization: str = Header(...)) -> dict:
    """Validates Supabase JWT, dynamically supporting ECC (ES256), RS256, and HS256."""
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")

    token = authorization.split(" ")[1]
    
    # Check the algorithm of the incoming JWT
    try:
        unverified_header = jwt.get_unverified_header(token)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token header format")

    alg = unverified_header.get("alg", "HS256")

    # If it's modern Asymmetric Cryptography (ES256 or RS256)
    if alg in ["RS256", "ES256"]:
        jwks = get_jwks()
        pub_key = {}
        for key in jwks.get("keys", []):
            if key.get("kid") == unverified_header.get("kid"):
                pub_key = key
                break
                
        if not pub_key:
            raise HTTPException(status_code=401, detail="Public signing key not found in JWKS.")
            
        try:
            return jwt.decode(token, pub_key, algorithms=["RS256", "ES256"], audience="authenticated")
        except JWTError as e:
            raise HTTPException(status_code=401, detail=f"Invalid {alg} token: {str(e)}")

    # Legacy Fallback (HS256)
    try:
        return jwt.decode(
            token,
            settings.SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            audience="authenticated"
        )
    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid HS256 token: {str(e)}")
