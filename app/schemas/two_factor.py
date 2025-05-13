from pydantic import BaseModel, constr
from typing import List

class TwoFactorSetupInitiateResponse(BaseModel):
    otpauth_uri: str  
    totp_secret: str  
    qr_code_image: str 
    backup_codes: List[str] 

class TwoFactorSetupVerifyEnableRequest(BaseModel):
    totp_secret: str 
    totp_code: constr(min_length=6, max_length=6) 
    backup_codes: List[str] 

class TwoFactorDisableResponse(BaseModel):
    detail: str = "2FA ha sido deshabilitada."

class LoginResponseBase(BaseModel):
    
    pass

class AccessTokenResponse(LoginResponseBase): 
    access_token: str
    token_type: str = "bearer"
    # Opcional: para informar al frontend si se estableció la cookie de "recordar dispositivo"
    # remember_device_set: Optional[bool] = None

class TwoFactorChallengeResponse(LoginResponseBase):
    detail: str = "Se requiere código de autenticación de dos factores."
    two_factor_token: str
    # Opcional: user_id si no se usa un token y se quiere identificar al usuario
    # user_id: int

class TwoFactorLoginVerifyRequest(BaseModel):

    two_factor_token: str
    totp_code: constr(min_length=6, max_length=8)
    remember_device: Optional[bool] = False