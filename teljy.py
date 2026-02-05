# ==================================================
# INTÉGRATION TELNYX - Remplacement de Twilio
# ==================================================





# ========================================
# src/core/config.py - AJOUTER
# ========================================
"""
# Remplacer Twilio par Telnyx

class Settings(BaseSettings):
    # ... autres configs ...

    # Telnyx (remplace Twilio)
    telnyx_api_key: str = Field(..., alias="TELNYX_API_KEY")
    telnyx_phone_number: str = Field(..., alias="TELNYX_PHONE_NUMBER")
    telnyx_connection_id: str = Field(..., alias="TELNYX_CONNECTION_ID")
    telnyx_public_key: str = Field(default="", alias="TELNYX_PUBLIC_KEY")
"""

# ========================================
# .env - CONFIGURATION
# ========================================
"""
# Telnyx (remplace Twilio)
TELNYX_API_KEY=KEY017...votre_cle_api
TELNYX_PHONE_NUMBER=+229XXXXXXXX
TELNYX_CONNECTION_ID=1234567890
TELNYX_PUBLIC_KEY=...optionnel_pour_webhooks
"""

# ========================================
# requirements.txt - AJOUTER
# ========================================
"""
# Remplacer twilio par telnyx
telnyx==2.0.0
"""



# ========================================
# GUIDE DE MIGRATION TWILIO → TELNYX
# ========================================
"""
1. REMPLACER les imports:
   from src.services.telephony.twilio_client import TwilioClient
   → from src.services.telephony.telnyx_client import TelnyxClient

2. REMPLACER les méthodes:
   - create_call() → identique
   - send_sms() → identique
   - end_call() → hangup_call()
   - generate_twiml_connect_stream() → stream_audio_start()

3. WEBHOOKS:
   - URL: https://api.heyi.com/webhooks/telnyx/call-control
   - Configurer dans Telnyx Portal → Call Control Applications

4. WEBSOCKET:
   - URL: wss://api.heyi.com/webhooks/telnyx/stream
   - Format audio: PCM 16-bit, 8kHz (comme Twilio)
"""