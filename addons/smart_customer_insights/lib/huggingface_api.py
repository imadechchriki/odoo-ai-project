import requests
import json
import logging
import re
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class HuggingFaceAPI:
    """
    Classe pour gérer l'IA via Google Gemini.
    (Le nom de classe est conservé pour la compatibilité avec ton module Odoo existant)
    """
    
    def __init__(self, env=None):
        self.env = env
        # TA CLÉ API
        self.api_key = ""
    
    def analyze_sentiment(self, text):
        """Analyse le sentiment avec Gemini 2.0 Flash Experimental"""
        if not self.api_key:
            _logger.error("Clé API manquante")
            return {'sentiment': 'neutral', 'score': 0.0}

        try:
            # Nettoyage du texte HTML provenant d'Odoo
            clean_text = re.sub(r'<[^>]+>', '', text).strip()
            _logger.info(f"Texte envoyé à Gemini: {clean_text}")
            
            # --- CONFIGURATION API ---
            # Utilisation de la version beta pour le modèle expérimental 2.0
            model_name = "gemini-1.5-flash"
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={self.api_key}"
            
            # Prompt strict demandant du JSON
            prompt = f"""Tu es un assistant CRM expert.
Analyse le sentiment de ce message client.
Réponds UNIQUEMENT avec un objet JSON respectant ce format :
{{
  "sentiment": "positive", "negative" ou "neutral",
  "score": un nombre entre 0.0 et 1.0 (confiance)
}}

Message client : "{clean_text}"
"""
            
            payload = {
                "contents": [{
                    "parts": [{
                        "text": prompt
                    }]
                }],
                # Force la réponse en JSON (Nouveauté Gemini 1.5/2.0)
                "generationConfig": {
                    "temperature": 0.1,
                    "response_mime_type": "application/json"
                }
            }
            
            # Appel API
            response = requests.post(
                url,
                headers={"Content-Type": "application/json"},
                json=payload,
                timeout=10
            )
            
            # Gestion des erreurs HTTP (404, 400, 500)
            if response.status_code != 200:
                _logger.error(f"Erreur Gemini {response.status_code}: {response.text}")
                # Fallback neutre pour ne pas bloquer Odoo
                return {'sentiment': 'neutral', 'score': 0.5}

            # Traitement de la réponse
            result = response.json()
            
            try:
                # Extraction du texte de la réponse
                candidate = result['candidates'][0]['content']['parts'][0]['text']
                
                # Conversion du texte JSON en dictionnaire Python
                data = json.loads(candidate)
                
                sentiment = data.get('sentiment', 'neutral').lower()
                score = data.get('score', 0.5)
                
                _logger.info(f"Résultat Gemini: {sentiment} (Confiance: {score})")
                return {'sentiment': sentiment, 'score': score}

            except (KeyError, IndexError, json.JSONDecodeError) as e:
                _logger.warning(f"Erreur de lecture de la réponse JSON: {e}")
                return {'sentiment': 'neutral', 'score': 0.5}
                
        except Exception as e:
            _logger.exception(f"Exception critique dans analyze_sentiment: {str(e)}")
            return {'sentiment': 'neutral', 'score': 0.5}
    
    def generate_summary(self, text, max_length=150):
        """Génère un résumé simple (local pour économiser l'API)"""
        if not text: return ""
        clean_text = re.sub(r'<[^>]+>', '', text).strip()
        sentences = [s.strip() for s in clean_text.split('.') if s.strip()]
        if len(sentences) <= 2:
            return clean_text
        return '. '.join(sentences[:2]) + '.'
    
    def analyze_customer(self, customer_data):
        """Fonction principale appelée par le bouton Odoo"""
        text_parts = []
        
        if customer_data.get('comment'):
            text_parts.append(str(customer_data['comment']))
        
        full_text = " ".join(text_parts) if text_parts else f"Client {customer_data.get('name', 'Unknown')}"
        
        # 1. Analyse via API
        sentiment_result = self.analyze_sentiment(full_text)
        
        # 2. Génération résumé local
        summary = self.generate_summary(full_text)
        
        # 3. Recommandations basées sur le sentiment
        recommendations = self._generate_recommendations(
            sentiment_result['sentiment'],
            customer_data
        )
        
        return {
            'sentiment': sentiment_result['sentiment'],
            'confidence': sentiment_result['score'],
            'summary': summary,
            'recommendations': recommendations
        }
    
    def _generate_recommendations(self, sentiment, customer_data):
        """Logique métier pour les recommandations"""
        recommendations = []
        
        if sentiment == 'positive':
            recommendations.append("✅ Client satisfait - Proposer un upselling")
            recommendations.append("⭐ Demander un avis positif")
        elif sentiment == 'negative':
            recommendations.append("⚠️ Attention requise - Appeler le client")
            recommendations.append("🎫 Créer un ticket de support prioritaire")
        else:
            recommendations.append("ℹ️ Client neutre - Envoyer newsletter")
        
        if not customer_data.get('email'):
            recommendations.append("📧 Email manquant - À demander")
        
        return "\n".join(recommendations)