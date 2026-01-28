"""Orchestrateur principal de l'agent IA."""
import asyncio
import json
from typing import Optional, Dict, Any

from src.agent.state_machine import StateMachine, ConversationState, ConversationContext
from src.agent.dialogue_manager import dialogue_manager
from src.agent.session import session_manager
from src.services.stt.deepgram_client import DeepgramSTTClient
from src.services.llm.openai_client import OpenAIClient
from src.services.tts.elevenlabs_client import ElevenLabsTTSClient
from src.services.vector_db.qcadrant_client import QdrantClient
from src.business.product_service import ProductService
from src.business.order_service import OrderService


class AgentOrchestrator:
    """Orchestrateur principal qui coordonne tous les services."""

    def __init__(
            self,
            stt_client: DeepgramSTTClient,
            llm_client: OpenAIClient,
            tts_client: ElevenLabsTTSClient,
            qdrant_client: QdrantClient,
            product_service: ProductService,
            order_service: OrderService,
    ):
        self.stt_client = stt_client
        self.llm_client = llm_client
        self.tts_client = tts_client
        self.qdrant_client = qdrant_client
        self.product_service = product_service
        self.order_service = order_service

    async def handle_call_start(self, call_id: str) -> str:
        """Gérer le début d'appel - message d'accueil."""

        # Créer la session
        context = session_manager.create_session(call_id)
        state_machine = StateMachine(context)

        # Transition vers GREETING
        state_machine.transition(ConversationState.GREETING, "Appel entrant")

        # Générer le message d'accueil
        greeting = dialogue_manager.generate_response(
            ConversationState.GREETING,
            {"company": "votre grossiste pharmaceutique"}
        )

        context.add_message("assistant", greeting)

        return greeting

    async def handle_audio_chunk(self, call_id: str, audio_chunk: bytes):
        """Gérer un chunk audio entrant."""
        # Envoyer à Deepgram pour transcription
        await self.stt_client.send_audio(audio_chunk)

    async def handle_transcript(
            self,
            call_id: str,
            transcript: str,
            is_final: bool,
            confidence: float
    ) -> Optional[str]:
        """Gérer une transcription (partielle ou finale)."""

        # Si partiel, on peut afficher mais ne pas traiter
        if not is_final:
            print(f"📝 Transcription partielle: {transcript}")
            return None

        print(f"✅ Transcription finale: {transcript} (confiance: {confidence:.2f})")

        # Récupérer la session
        context = session_manager.get_session(call_id)
        if not context:
            print(f"⚠️  Session non trouvée: {call_id}")
            return None

        # Mettre à jour le contexte
        context.current_transcript = transcript
        context.confidence_scores.append(confidence)
        context.add_message("user", transcript)

        # State machine
        state_machine = StateMachine(context)

        # Traiter selon l'état actuel
        if context.state == ConversationState.GREETING:
            return await self._handle_greeting_state(context, state_machine, transcript)

        elif context.state == ConversationState.COLLECTING:
            return await self._handle_collecting_state(context, state_machine, transcript, confidence)

        elif context.state == ConversationState.CLARIFYING:
            return await self._handle_clarifying_state(context, state_machine, transcript)

        elif context.state == ConversationState.CONFIRMING:
            return await self._handle_confirming_state(context, state_machine, transcript)

        return None

    async def _handle_greeting_state(
            self,
            context: ConversationContext,
            state_machine: StateMachine,
            transcript: str
    ) -> str:
        """Gérer l'état GREETING."""

        # Transition vers COLLECTING
        state_machine.transition(ConversationState.COLLECTING, "Début de commande")

        # Traiter comme premier item
        return await self._handle_collecting_state(context, state_machine, transcript, 0.95)

    async def _handle_collecting_state(
            self,
            context: ConversationContext,
            state_machine: StateMachine,
            transcript: str,
            confidence: float
    ) -> str:
        """Gérer l'état COLLECTING - extraction de produits."""

        # Vérifier si l'utilisateur veut valider
        transcript_lower = transcript.lower()
        validation_keywords = ["c'est tout", "je valide", "confirme", "c'est bon", "terminé", "fini"]

        if any(keyword in transcript_lower for keyword in validation_keywords):
            # Transition vers CONFIRMING
            state_machine.transition(ConversationState.CONFIRMING, "Utilisateur demande validation")

            # Générer récapitulatif
            recap = dialogue_manager.format_recap(context.items)
            response = dialogue_manager.generate_response(
                ConversationState.CONFIRMING,
                {"recap": recap}
            )
            context.add_message("assistant", response)
            return response

        # Vérifier la confiance
        if confidence < 0.70:
            context.increment_attempts()

            if state_machine.should_transfer_to_human():
                state_machine.transition(ConversationState.TRANSFERRING, "Confiance trop basse")
                response = dialogue_manager.generate_response(ConversationState.TRANSFERRING)
                context.add_message("assistant", response)
                return response

            # Demander clarification
            state_machine.transition(ConversationState.CLARIFYING, "Confiance basse")
            response = dialogue_manager.generate_response(ConversationState.CLARIFYING)
            context.add_message("assistant", response)
            return response

        # Extraire le produit et la quantité avec LLM
        try:
            extraction = await self.llm_client.extract_order_items(
                transcript,
                {"conversation_history": context.conversation_history[-5:]}
            )

            extracted_data = json.loads(extraction)
            products = extracted_data.get("products", [])

            if not products:
                # Aucun produit détecté
                response = "Je n'ai pas compris quel produit vous voulez. Pouvez-vous répéter ?"
                context.add_message("assistant", response)
                return response

            # Traiter chaque produit
            responses = []
            for product_data in products:
                product_name = product_data.get("name", "")
                quantity = product_data.get("quantity", 1)
                unit = product_data.get("unit", "boites")

                # Rechercher le produit dans Qdrant
                search_results = await self.qdrant_client.search_product(product_name, limit=3)

                if not search_results:
                    # Produit non trouvé
                    response = dialogue_manager.generate_product_not_found_message(product_name)
                    responses.append(response)
                    continue

                # Prendre le meilleur match
                best_match = search_results[0]
                matched_product = best_match["product"]
                match_score = best_match["score"]

                # Vérifier le stock
                stock_available = await self.product_service.check_stock(
                    matched_product["cip13"],
                    quantity
                )

                if not stock_available:
                    response = dialogue_manager.generate_out_of_stock_message(
                        matched_product["name"]
                    )
                    responses.append(response)
                    continue

                # Ajouter l'item au contexte
                item = {
                    "product_name": matched_product["name"],
                    "product_cip": matched_product["cip13"],
                    "quantity": quantity,
                    "unit": unit,
                    "unit_price": matched_product.get("unit_price", 0),
                    "confidence": match_score,
                    "transcript": transcript,
                }
                context.add_item(item)

                # Générer réponse
                response = dialogue_manager.generate_response(
                    ConversationState.COLLECTING,
                    {
                        "product": matched_product["name"],
                        "quantity": quantity,
                        "unit": unit,
                    }
                )
                responses.append(response)

            final_response = " ".join(responses)
            context.add_message("assistant", final_response)
            return final_response

        except Exception as e:
            print(f"❌ Erreur extraction: {e}")
            state_machine.transition(ConversationState.ERROR, str(e))
            response = dialogue_manager.generate_response(ConversationState.ERROR)
            context.add_message("assistant", response)
            return response

    async def _handle_clarifying_state(
            self,
            context: ConversationContext,
            state_machine: StateMachine,
            transcript: str
    ) -> str:
        """Gérer l'état CLARIFYING."""

        # Revenir à COLLECTING et retraiter
        state_machine.transition(ConversationState.COLLECTING, "Clarification reçue")
        return await self._handle_collecting_state(context, state_machine, transcript, 0.85)

    async def _handle_confirming_state(
            self,
            context: ConversationContext,
            state_machine: StateMachine,
            transcript: str
    ) -> str:
        """Gérer l'état CONFIRMING - validation finale."""

        transcript_lower = transcript.lower()

        # Vérifier confirmation
        if any(word in transcript_lower for word in ["oui", "ok", "valide", "confirme", "d'accord"]):
            # Transition vers PROCESSING
            state_machine.transition(ConversationState.PROCESSING, "Commande validée")

            # Créer la commande
            try:
                order = await self.order_service.create_order(
                    call_id=context.call_id,
                    pharmacy_id=context.pharmacy_id,
                    items=context.items,
                    confidence=context.get_average_confidence(),
                )

                # Transition vers COMPLETED
                state_machine.transition(ConversationState.COMPLETED, "Commande créée")

                response = dialogue_manager.generate_response(
                    ConversationState.COMPLETED,
                    {"order_id": order.order_id}
                )
                context.add_message("assistant", response)
                return response

            except Exception as e:
                print(f"❌ Erreur création commande: {e}")
                state_machine.transition(ConversationState.ERROR, str(e))
                response = dialogue_manager.generate_response(ConversationState.ERROR)
                context.add_message("assistant", response)
                return response

        # Ajout de produits
        elif any(word in transcript_lower for word in ["ajoute", "aussi", "encore", "en plus"]):
            state_machine.transition(ConversationState.COLLECTING, "Ajout produits")
            return await self._handle_collecting_state(context, state_machine, transcript, 0.90)

        # Annulation
        else:
            state_machine.transition(ConversationState.COLLECTING, "Modification demandée")
            response = "D'accord, que voulez-vous modifier ?"
            context.add_message("assistant", response)
            return response