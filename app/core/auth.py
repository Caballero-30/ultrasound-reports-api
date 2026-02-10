from fastapi import Header, Depends, HTTPException
from app.config.dependencies import get_env_settings
from app.config.env_settings import EnvSettings


async def verify_token(
    authorization: str = Header(..., alias="Authorization"),
    env_settings: EnvSettings = Depends(get_env_settings)
):
    token = (authorization or "").strip()
    api_key = env_settings.api_key
    if token != api_key:
        raise HTTPException(status_code=401, detail="Invalid API Key")
