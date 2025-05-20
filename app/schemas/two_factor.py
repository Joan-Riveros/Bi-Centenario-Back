from pydantic import BaseModel, constr, model_validator 
from typing import List, Optional

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
    detail: str = "2FA ha sido deshabilitada"

class LoginResponseBase(BaseModel):
    
    pass

class AccessTokenResponse(LoginResponseBase): 
    access_token: str
    token_type: str = "bearer"
    # Opcional: para informar al frontend cookie  "recordar dispositivo"
    # remember_device_set: Optional[bool] = None

class TwoFactorChallengeResponse(LoginResponseBase):
    detail: str = "Se requiere codigo de autenticacion de dos factores"
    two_factor_token: str
    # Opcional: user_id si no se usa un token y se quiere identificar al usuario
    # user_id: int

class TwoFactorLoginVerifyRequest(BaseModel):
    two_factor_token: str 
    totp_code: Optional[constr(min_length=6, max_length=8)] = None
    backup_code: Optional[str] = None 
    remember_device: Optional[bool] = False

    @model_validator(mode='before') 
    def check_code_provided(cls, values):
        totp_code, backup_code = values.get('totp_code'), values.get('backup_code')
        if not totp_code and not backup_code:
            raise ValueError('Se debe proporcionar o "totp_code" o "backup_code"')
        if totp_code and backup_code:
            raise ValueError('Proporciona "totp_code" o "backup_code", pero no ambos')
        return values