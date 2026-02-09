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
        # Créer le message
        msg = MIMEMultipart()
        msg['From'] = config.SMTP_USER
        msg['To'] = config.CONTACT_EMAIL
        msg['Subject'] = f"Contact: {subject}"
        
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
        
        # Envoyer via SMTP
        with smtplib.SMTP(config.SMTP_HOST, config.SMTP_PORT) as server:
            server.starttls()
            server.login(config.SMTP_USER, config.SMTP_PASSWORD)
            server.send_message(msg)
        
        logger.info(f"✅ Contact email sent successfully to {config.CONTACT_EMAIL} from {email}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to send contact email: {e}")
        logger.error(f"Check SMTP configuration: SMTP_HOST={config.SMTP_HOST}, SMTP_PORT={config.SMTP_PORT}, SMTP_USER={config.SMTP_USER}")
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
            "SMTP not configured - email not sent. "
            "Configure SMTP_HOST, SMTP_USER, SMTP_PASSWORD in .env to enable email sending."
        )
        return True  # Mode mock
    
    # Run blocking SMTP in thread pool to avoid blocking event loop
    return await asyncio.to_thread(
        _send_email_sync, name, email, phone, company, subject, reference, message
    )

