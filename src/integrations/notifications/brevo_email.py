"""Service d'envoi d'emails avec Brevo (ex-Sendinblue)."""

# ========================================
# src/integrations/notifications/brevo_email.py
# ========================================
"""Service d'envoi d'emails via Brevo API."""
import httpx
from typing import List, Optional, Dict, Any


class BrevoEmailService:
    """Service d'envoi d'emails via Brevo (ex-Sendinblue)."""

    def __init__(self, api_key: str, sender_email: str, sender_name: str = "HEYI"):
        """
        Initialiser le service Brevo.

        Args:
            api_key: Clé API Brevo
            sender_email: Email expéditeur
            sender_name: Nom expéditeur
        """
        self.api_key = api_key
        self.base_url = "https://api.brevo.com/v3"
        self.sender = {"email": sender_email, "name": sender_name}

        self.headers = {
            "accept": "application/json",
            "api-key": self.api_key,
            "content-type": "application/json",
        }

    async def send_email(
            self,
            to: List[Dict[str, str]],
            subject: str,
            html_content: str = None,
            text_content: str = None,
            cc: Optional[List[Dict[str, str]]] = None,
            bcc: Optional[List[Dict[str, str]]] = None,
            reply_to: Optional[Dict[str, str]] = None,
            tags: Optional[List[str]] = None,
            params: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Envoyer un email via Brevo.

        Args:
            to: Liste des destinataires [{"email": "...", "name": "..."}]
            subject: Sujet
            html_content: Contenu HTML
            text_content: Contenu texte brut
            cc: CC
            bcc: BCC
            reply_to: Reply-to
            tags: Tags pour tracking
            params: Paramètres de personnalisation

        Returns:
            True si envoyé avec succès
        """
        try:
            payload = {
                "sender": self.sender,
                "to": to,
                "subject": subject,
            }

            # Contenu
            if html_content:
                payload["htmlContent"] = html_content
            if text_content:
                payload["textContent"] = text_content

            # Options
            if cc:
                payload["cc"] = cc
            if bcc:
                payload["bcc"] = bcc
            if reply_to:
                payload["replyTo"] = reply_to
            if tags:
                payload["tags"] = tags
            if params:
                payload["params"] = params

            # Envoyer
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/smtp/email",
                    json=payload,
                    headers=self.headers,
                    timeout=10,
                )

                response.raise_for_status()
                result = response.json()

                message_id = result.get("messageId")
                print(f"✅ Email envoyé via Brevo - ID: {message_id}")

                return True

        except httpx.HTTPStatusError as e:
            print(f"❌ Erreur HTTP Brevo: {e.response.status_code}")
            print(f"   Response: {e.response.text}")
            return False

        except Exception as e:
            print(f"❌ Erreur envoi email Brevo: {e}")
            return False

    async def send_order_notification(
            self,
            order_id: str,
            pharmacy_name: str,
            total_amount: float,
            items_count: int,
            to_emails: List[str],
    ) -> bool:
        """
        Envoyer une notification de nouvelle commande.

        Args:
            order_id: ID de la commande
            pharmacy_name: Nom de la pharmacie
            total_amount: Montant total
            items_count: Nombre d'items
            to_emails: Emails destinataires

        Returns:
            True si succès
        """
        # Formater les destinataires
        to = [{"email": email} for email in to_emails]

        subject = f"✅ Nouvelle commande - {order_id}"

        # Contenu HTML
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #4CAF50; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background-color: #f9f9f9; }}
                .info-box {{ background-color: white; padding: 15px; margin: 10px 0; border-radius: 5px; }}
                .label {{ font-weight: bold; color: #333; }}
                .value {{ color: #666; }}
                .footer {{ text-align: center; padding: 20px; color: #999; font-size: 12px; }}
                .amount {{ font-size: 24px; color: #4CAF50; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🛒 Nouvelle Commande</h1>
                </div>
                <div class="content">
                    <div class="info-box">
                        <p><span class="label">Numéro de commande:</span> <span class="value">{order_id}</span></p>
                        <p><span class="label">Pharmacie:</span> <span class="value">{pharmacy_name}</span></p>
                        <p><span class="label">Nombre d'articles:</span> <span class="value">{items_count}</span></p>
                        <p><span class="label">Montant total:</span> <span class="amount">{total_amount:.2f} €</span></p>
                    </div>
                    <p style="margin-top: 20px;">
                        Cette commande a été passée via l'agent IA vocal HEYI.
                    </p>
                    <p style="text-align: center; margin-top: 30px;">
                        <a href="https://dashboard.heyi.com/orders/{order_id}" 
                           style="background-color: #4CAF50; color: white; padding: 12px 30px; 
                                  text-decoration: none; border-radius: 5px; display: inline-block;">
                            Voir la commande
                        </a>
                    </p>
                </div>
                <div class="footer">
                    <p>HEYI - Agent IA Pharmaceutique</p>
                    <p>Cet email a été envoyé automatiquement, merci de ne pas répondre.</p>
                </div>
            </div>
        </body>
        </html>
        """

        # Contenu texte (fallback)
        text_content = f"""
Nouvelle commande reçue via l'agent IA HEYI

Commande: {order_id}
Pharmacie: {pharmacy_name}
Nombre d'articles: {items_count}
Montant total: {total_amount:.2f} €

Consultez le dashboard pour plus de détails.
"""

        return await self.send_email(
            to=to,
            subject=subject,
            html_content=html_content,
            text_content=text_content,
            tags=["order", "notification"],
            params={
                "order_id": order_id,
                "pharmacy_name": pharmacy_name,
                "total_amount": total_amount,
            },
        )

    async def send_validation_required(
            self, order_id: str, reason: str, amount: float, to_emails: List[str]
    ) -> bool:
        """
        Envoyer une alerte de validation humaine requise.

        Args:
            order_id: ID de la commande
            reason: Raison de la validation
            amount: Montant
            to_emails: Emails destinataires

        Returns:
            True si succès
        """
        to = [{"email": email} for email in to_emails]

        subject = f"⚠️ VALIDATION REQUISE - {order_id}"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #FF9800; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background-color: #f9f9f9; }}
                .alert-box {{ background-color: #FFF3CD; padding: 15px; margin: 10px 0; 
                             border-left: 4px solid #FF9800; border-radius: 5px; }}
                .info-box {{ background-color: white; padding: 15px; margin: 10px 0; border-radius: 5px; }}
                .label {{ font-weight: bold; color: #333; }}
                .value {{ color: #666; }}
                .reason {{ color: #D32F2F; font-weight: bold; }}
                .footer {{ text-align: center; padding: 20px; color: #999; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>⚠️ Validation Humaine Requise</h1>
                </div>
                <div class="content">
                    <div class="alert-box">
                        <p><strong>ATTENTION:</strong> Cette commande nécessite une validation manuelle avant traitement.</p>
                    </div>
                    <div class="info-box">
                        <p><span class="label">Numéro de commande:</span> <span class="value">{order_id}</span></p>
                        <p><span class="label">Montant:</span> <span class="value">{amount:.2f} €</span></p>
                        <p><span class="label">Raison:</span> <span class="reason">{reason}</span></p>
                    </div>
                    <p style="margin-top: 20px;">
                        Merci de vérifier cette commande et de la valider manuellement dans le dashboard.
                    </p>
                    <p style="text-align: center; margin-top: 30px;">
                        <a href="https://dashboard.heyi.com/orders/{order_id}/validate" 
                           style="background-color: #FF9800; color: white; padding: 12px 30px; 
                                  text-decoration: none; border-radius: 5px; display: inline-block;">
                            Valider la commande
                        </a>
                    </p>
                </div>
                <div class="footer">
                    <p>HEYI - Agent IA Pharmaceutique</p>
                </div>
            </div>
        </body>
        </html>
        """

        text_content = f"""
⚠️ VALIDATION HUMAINE REQUISE

Commande: {order_id}
Montant: {amount:.2f} €
Raison: {reason}

Cette commande nécessite une validation manuelle.
Merci de la valider dans le dashboard: https://dashboard.heyi.com/orders/{order_id}/validate
"""

        return await self.send_email(
            to=to,
            subject=subject,
            html_content=html_content,
            text_content=text_content,
            tags=["validation", "alert", "urgent"],
            params={"order_id": order_id, "reason": reason, "amount": amount},
        )

    async def send_error_alert(
            self, error_message: str, call_id: str, to_emails: List[str]
    ) -> bool:
        """
        Envoyer une alerte d'erreur système.

        Args:
            error_message: Message d'erreur
            call_id: ID de l'appel
            to_emails: Emails destinataires

        Returns:
            True si succès
        """
        to = [{"email": email} for email in to_emails]

        subject = f"🚨 ERREUR SYSTÈME - Appel {call_id}"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #D32F2F; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background-color: #f9f9f9; }}
                .error-box {{ background-color: #FFEBEE; padding: 15px; margin: 10px 0; 
                             border-left: 4px solid #D32F2F; border-radius: 5px; }}
                .footer {{ text-align: center; padding: 20px; color: #999; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🚨 Erreur Système</h1>
                </div>
                <div class="content">
                    <div class="error-box">
                        <p><strong>Appel:</strong> {call_id}</p>
                        <p><strong>Erreur:</strong> {error_message}</p>
                    </div>
                    <p>Intervention technique nécessaire.</p>
                </div>
                <div class="footer">
                    <p>HEYI - Agent IA Pharmaceutique</p>
                </div>
            </div>
        </body>
        </html>
        """

        text_content = f"""
🚨 ERREUR SYSTÈME

Appel: {call_id}
Erreur: {error_message}

Intervention technique nécessaire.
"""

        return await self.send_email(
            to=to,
            subject=subject,
            html_content=html_content,
            text_content=text_content,
            tags=["error", "alert", "critical"],
        )

    async def send_daily_report(
            self,
            date: str,
            total_calls: int,
            total_orders: int,
            total_amount: float,
            success_rate: float,
            to_emails: List[str],
    ) -> bool:
        """
        Envoyer un rapport quotidien.

        Args:
            date: Date du rapport
            total_calls: Nombre d'appels
            total_orders: Nombre de commandes
            total_amount: Montant total
            success_rate: Taux de succès
            to_emails: Emails destinataires

        Returns:
            True si succès
        """
        to = [{"email": email} for email in to_emails]

        subject = f"📊 Rapport quotidien HEYI - {date}"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #2196F3; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background-color: #f9f9f9; }}
                .stats {{ display: flex; justify-content: space-around; margin: 20px 0; }}
                .stat-box {{ background-color: white; padding: 20px; border-radius: 5px; 
                            text-align: center; flex: 1; margin: 0 5px; }}
                .stat-number {{ font-size: 32px; font-weight: bold; color: #2196F3; }}
                .stat-label {{ color: #666; margin-top: 5px; }}
                .footer {{ text-align: center; padding: 20px; color: #999; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📊 Rapport Quotidien</h1>
                    <p>{date}</p>
                </div>
                <div class="content">
                    <div class="stats">
                        <div class="stat-box">
                            <div class="stat-number">{total_calls}</div>
                            <div class="stat-label">Appels</div>
                        </div>
                        <div class="stat-box">
                            <div class="stat-number">{total_orders}</div>
                            <div class="stat-label">Commandes</div>
                        </div>
                    </div>
                    <div class="stats">
                        <div class="stat-box">
                            <div class="stat-number">{total_amount:.0f}€</div>
                            <div class="stat-label">CA Total</div>
                        </div>
                        <div class="stat-box">
                            <div class="stat-number">{success_rate:.1f}%</div>
                            <div class="stat-label">Taux de succès</div>
                        </div>
                    </div>
                </div>
                <div class="footer">
                    <p>HEYI - Agent IA Pharmaceutique</p>
                </div>
            </div>
        </body>
        </html>
        """

        return await self.send_email(
            to=to,
            subject=subject,
            html_content=html_content,
            tags=["report", "daily"],
        )
