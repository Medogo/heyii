"""Services de notifications."""

# ========================================
# src/integrations/notifications/email.py
# ========================================
"""Service d'envoi d'emails."""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional


class EmailService:
    """Service d'envoi d'emails."""

    def __init__(
            self,
            smtp_host: str = "smtp.gmail.com",
            smtp_port: int = 587,
            username: str = "",
            password: str = "",
    ):
        """
        Initialiser le service email.

        Args:
            smtp_host: Serveur SMTP
            smtp_port: Port SMTP
            username: Nom d'utilisateur
            password: Mot de passe
        """
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.username = username
        self.password = password

    async def send_email(
            self,
            to: List[str],
            subject: str,
            body: str,
            html: bool = False,
            cc: Optional[List[str]] = None,
            bcc: Optional[List[str]] = None,
    ) -> bool:
        """
        Envoyer un email.

        Args:
            to: Destinataires
            subject: Sujet
            body: Corps du message
            html: True si HTML
            cc: CC
            bcc: BCC

        Returns:
            True si envoyé avec succès
        """
        try:
            msg = MIMEMultipart("alternative")
            msg["From"] = self.username
            msg["To"] = ", ".join(to)
            msg["Subject"] = subject

            if cc:
                msg["Cc"] = ", ".join(cc)

            # Ajouter le corps
            mime_type = "html" if html else "plain"
            msg.attach(MIMEText(body, mime_type))

            # Tous les destinataires
            all_recipients = to + (cc or []) + (bcc or [])

            # Envoyer
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg, to_addrs=all_recipients)

            print(f"✅ Email envoyé à {len(all_recipients)} destinataires")
            return True

        except Exception as e:
            print(f"❌ Erreur envoi email: {e}")
            return False

    async def send_order_notification(
            self, order_id: str, pharmacy_name: str, total_amount: float, to: List[str]
    ) -> bool:
        """
        Envoyer une notification de commande.

        Args:
            order_id: ID commande
            pharmacy_name: Nom pharmacie
            total_amount: Montant total
            to: Destinataires

        Returns:
            True si succès
        """
        subject = f"Nouvelle commande - {order_id}"

        body = f"""
Nouvelle commande reçue via l'agent IA:

Commande: {order_id}
Pharmacie: {pharmacy_name}
Montant: {total_amount:.2f}€

Pour plus de détails, consultez le dashboard.
"""

        return await self.send_email(to, subject, body)

    async def send_validation_required(
            self, order_id: str, reason: str, to: List[str]
    ) -> bool:
        """
        Notifier qu'une validation humaine est requise.

        Args:
            order_id: ID commande
            reason: Raison
            to: Destinataires

        Returns:
            True si succès
        """
        subject = f"⚠️ Validation requise - {order_id}"

        body = f"""
Une commande nécessite une validation humaine:

Commande: {order_id}
Raison: {reason}

Merci de valider cette commande dans le dashboard.
"""

        return await self.send_email(to, subject, body)

