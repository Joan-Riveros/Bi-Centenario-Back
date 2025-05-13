from sqlalchemy.orm import Session
from typing import List, Optional

from app.models.user import User 
from app.models.two_factor import User2FASetting
from app.core.encryption_utils import encrypt_data, decrypt_data
import json 

def get_2fa_settings(db: Session, user_id: int) -> Optional[User2FASetting]:
    return db.query(User2FASetting).filter(User2FASetting.user_id == user_id).first()

def enable_2fa(
    db: Session,
    user_id: int,
    unencrypted_totp_secret: str,
    unencrypted_backup_codes: List[str] 
) -> User2FASetting:
    settings = get_2fa_settings(db, user_id)
    if not settings:
        settings = User2FASetting(user_id=user_id)
        db.add(settings)
    
    settings.encrypted_totp_secret = encrypt_data(unencrypted_totp_secret)
    
    encrypted_codes = [encrypt_data(code).decode('latin-1') for code in unencrypted_backup_codes] 
    settings.encrypted_backup_codes = encrypted_codes 

    settings.is_enabled = True

    return settings

def disable_2fa(db: Session, user_id: int) -> Optional[User2FASetting]:
    settings = get_2fa_settings(db, user_id)
    if settings:
        settings.is_enabled = False
        settings.encrypted_totp_secret = None 
        settings.encrypted_backup_codes = None 
        
    return settings

def get_decrypted_totp_secret(db: Session, user_id: int) -> Optional[str]:
    settings = get_2fa_settings(db, user_id)
    if settings and settings.is_enabled and settings.encrypted_totp_secret:
        return decrypt_data(settings.encrypted_totp_secret)
    return None

def verify_and_use_backup_code(db: Session, user_id: int, submitted_code: str) -> bool:
    settings = get_2fa_settings(db, user_id) 
    if not settings or not settings.is_enabled or not settings.encrypted_backup_codes:
        
        return False



    current_encrypted_codes: List[str] = settings.encrypted_backup_codes 

    found_code_encrypted_value = None
    code_index = -1

    for i, enc_code_str in enumerate(current_encrypted_codes):
        
        decrypted_code = decrypt_data(enc_code_str.encode('latin-1'))
        if decrypted_code == submitted_code:
            found_code_encrypted_value = enc_code_str
            code_index = i
            break

    if found_code_encrypted_value:
        
        current_encrypted_codes.pop(code_index)
        settings.encrypted_backup_codes = current_encrypted_codes 

        return True


    return False

def regenerate_encrypted_backup_codes(
    db: Session,
    user_id: int,
    new_unencrypted_backup_codes: List[str]
) -> Optional[User2FASetting]:
    settings = get_2fa_settings(db, user_id)
    if settings and settings.is_enabled:
        encrypted_codes = [encrypt_data(code).decode('latin-1') for code in new_unencrypted_backup_codes]
        settings.encrypted_backup_codes = encrypted_codes
        return settings
    return None