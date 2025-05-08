from fastapi_mail import FastMail, MessageSchema, MessageType
from pydantic import EmailStr
from typing import Dict, Any 

# Importar la configuracion de correo y otras configuraciones necesarias
from app.core.config import mail_config, PROJECT_NAME, FRONTEND_URL, PASSWORD_RESET_TOKEN_EXPIRE_HOURS

async def send_password_reset_email(email_to: EmailStr, username: str, token: str):
    """
    Envía un correo de restablecimiento de contraseña utilizando fastapi-mail y una plantilla HTML.
    """
   
    reset_url = f"{FRONTEND_URL}/reset-password?token={token}"

    subject = f"Restablecimiento de Contraseña para {PROJECT_NAME}"
    
    # Datos que pasan al HTML
    template_context: Dict[str, Any] = {
        "username": username,
        "project_name": PROJECT_NAME,
        "reset_url": reset_url,
        "expire_hours": PASSWORD_RESET_TOKEN_EXPIRE_HOURS,
        "token": token 
    }

    message = MessageSchema(
        subject=subject,
        recipients=[email_to],  
        template_body=template_context, 
        subtype=MessageType.html 
    )

    fm = FastMail(mail_config) 
    try:
        await fm.send_message(message, template_name="reset_password_email.html") 
        print(f"Correo de restablecimiento enviado exitosamente a: {email_to}")
        return True
    except Exception as e:
        print(f"Error al enviar correo de restablecimiento a {email_to}: {e}")
        
        return False