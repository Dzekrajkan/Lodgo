from urllib.parse import quote
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema
from backend.config import MAIL_FROM, MAIL_PASSWORD, MAIL_PORT, MAIL_SERVER, MAIL_USERNAME, VEREFI_EMAIL_URL

mail_config = ConnectionConfig(
    MAIL_USERNAME=MAIL_USERNAME,
    MAIL_PASSWORD=MAIL_PASSWORD,
    MAIL_FROM=MAIL_FROM,
    MAIL_SERVER=MAIL_SERVER,
    MAIL_PORT=MAIL_PORT,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
)

async def send_verification_email(email: str, token: str):
    verify_url = f"{VEREFI_EMAIL_URL}/verify_email?token={quote(token)}"

    message = MessageSchema(
        subject="Confirmation email",
        recipients=[email],
        body=f"Follow the link to confirm: {verify_url}",
        subtype="plain",
    )

    fm = FastMail(mail_config)
    await fm.send_message(message)