import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import logging
import asyncio
from . import config

logger = logging.getLogger(__name__)

def _send_email_sync(
    name: str,
    email: str,
    phone: Optional[str],
    company: Optional[str],
    subject: str,
    reference: Optional[str],
    message: str
) -> bool:
    """Synchronous email sending helper"""
    try:
        logger.info(f"📧 Preparing to send contact email from {name} <{email}>")
        logger.debug(f"Email details - Subject: {subject}, Reference: {reference or 'None'}")
        
        # Créer le message
        msg = MIMEMultipart()
        msg['From'] = config.SMTP_USER
        msg['To'] = config.CONTACT_EMAIL
        msg['Subject'] = f"Contact: {subject}"
        
        logger.debug(f"Email headers configured - From: {config.SMTP_USER}, To: {config.CONTACT_EMAIL}")
        
        # Corps du message
        body = f"""
Nouveau message de contact reçu:

Nom: {name}
Email: {email}
Téléphone: {phone or 'Non fourni'}
Société: {company or 'Non fournie'}
Sujet: {subject}
Référence annonce: {reference or 'Aucune'}

Message:
{message}
"""
        
        msg.attach(MIMEText(body, 'plain'))
        logger.debug(f"Email body attached, length: {len(body)} characters")
        
        # Envoyer via SMTP
        logger.info(f"🔌 Connecting to SMTP server {config.SMTP_HOST}:{config.SMTP_PORT}")
        with smtplib.SMTP(config.SMTP_HOST, config.SMTP_PORT) as server:
            logger.debug("Starting TLS encryption")
            server.starttls()
            logger.debug(f"Authenticating as {config.SMTP_USER}")
            server.login(config.SMTP_USER, config.SMTP_PASSWORD)
            logger.info("📤 Sending email message...")
            server.send_message(msg)
        
        logger.info(f"✅ Contact email sent successfully to {config.CONTACT_EMAIL} from {email}")
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        logger.error(f"❌ SMTP Authentication failed: {e}")
        logger.error(f"Check SMTP_USER and SMTP_PASSWORD in .env file")
        return False
    except smtplib.SMTPException as e:
        logger.error(f"❌ SMTP error occurred: {e}")
        logger.error(f"SMTP configuration: SMTP_HOST={config.SMTP_HOST}, SMTP_PORT={config.SMTP_PORT}")
        return False
    except Exception as e:
        logger.error(f"❌ Failed to send contact email: {e}")
        logger.error(f"Check SMTP configuration: SMTP_HOST={config.SMTP_HOST}, SMTP_PORT={config.SMTP_PORT}, SMTP_USER={'<configured>' if config.SMTP_USER else '<not set>'}")
        return False

async def send_contact_email(
    name: str,
    email: str,
    phone: Optional[str],
    company: Optional[str],
    subject: str,
    reference: Optional[str],
    message: str
) -> bool:
    """Send contact form email notification"""
    # Vérifier si SMTP est configuré
    if not hasattr(config, 'SMTP_HOST') or not config.SMTP_HOST:
        logger.warning(
            "⚠️  SMTP not configured - email not sent (mock mode). "
            "Configure SMTP_HOST, SMTP_USER, SMTP_PASSWORD in .env to enable email sending."
        )
        logger.info(f"📧 [MOCK MODE] Would have sent email from {name} <{email}> with subject: {subject}")
        return True  # Mode mock
    
    # Run blocking SMTP in thread pool to avoid blocking event loop
    logger.debug(f"Running email send in thread pool for {email}")
    result = await asyncio.to_thread(
        _send_email_sync, name, email, phone, company, subject, reference, message
    )
    logger.debug(f"Email send result for {email}: {'success' if result else 'failure'}")
    return result

