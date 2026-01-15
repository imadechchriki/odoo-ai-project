import requests
import json
import logging
from odoo import _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class HuggingFaceAPI:
    """Classe pour gérer les appels à l'API HuggingFace"""
    
    # Modèles gratuits HuggingFace
    SENTIMENT_MODEL = "distilbert-base-uncased-finetuned-sst-2-english"
    SUMMARY_MODEL = "facebook/bart-large-cnn"
    
    def __init__(self):
        # Récupérer la clé API depuis les paramètres système
        self.api_key = self._get_api_key()
        self.api_url = "https://api-inference.huggingface.co/models/"
        self.headers = {"Authorization": f"Bearer {self.api_key}"}
    
    def _get_api_key(self):
        """Récupère la clé API depuis ir.config_parameter"""
        from odoo import api, SUPERUSER_ID
        env = api.Environment.cr, SUPERUSER_ID, {}
        # Pour le développement, vous pouvez hardcoder temporairement
        # return "hf_votre_cle_ici"
        
        # En production, stocker dans les paramètres système
        ICP = env['ir.config_parameter'].sudo()
        api_key = ICP.get_param('smart_customer_insights.hf_api_key', default='')
        
        if not api_key:
            raise UserError(_(
                "Clé API HuggingFace non configurée.\n"
                "Allez dans Paramètres → Techniques → Paramètres Système\n"
                "Créez une clé: smart_customer_insights.hf_api_key"
            ))
        return api_key
    
    def analyze_sentiment(self, text):
        """Analyse le sentiment d'un texte"""
        try:
            url = f"{self.api_url}{self.SENTIMENT_MODEL}"
            response = requests.post(
                url,
                headers=self.headers,
                json={"inputs": text},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    label = result[0][0]['label'].lower()
                    score = result[0][0]['score']
                    
                    # Mapper les labels
                    sentiment_map = {
                        'positive': 'positive',
                        'negative': 'negative',
                        'neutral': 'neutral'
                    }
                    
                    return {
                        'sentiment': sentiment_map.get(label, 'neutral'),
                        'score': score
                    }
            else:
                _logger.warning(f"Erreur API Sentiment: {response.status_code}")
                return {'sentiment': 'neutral', 'score': 0.5}
                
        except Exception as e:
            _logger.error(f"Erreur analyse sentiment: {str(e)}")
            return {'sentiment': 'neutral', 'score': 0.5}
    
    def generate_summary(self, text, max_length=150):
        """Génère un résumé du texte"""
        try:
            url = f"{self.api_url}{self.SUMMARY_MODEL}"
            response = requests.post(
                url,
                headers=self.headers,
                json={
                    "inputs": text,
                    "parameters": {"max_length": max_length}
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    return result[0].get('summary_text', text[:200])
            
            return text[:200] + "..."
            
        except Exception as e:
            _logger.error(f"Erreur génération résumé: {str(e)}")
            return text[:200] + "..."
    
    def analyze_customer(self, customer_data):
        """Analyse complète d'un client"""
        # Construire le texte à analyser
        text_parts = []
        
        if customer_data.get('comment'):
            text_parts.append(f"Notes: {customer_data['comment']}")
        
        text_parts.append(f"Client: {customer_data.get('name', 'Unknown')}")
        
        if customer_data.get('city'):
            text_parts.append(f"Ville: {customer_data['city']}")
        
        full_text = ". ".join(text_parts)
        
        # Analyser le sentiment
        sentiment_result = self.analyze_sentiment(full_text)
        
        # Générer un résumé
        summary = self.generate_summary(full_text, max_length=100)
        
        # Générer des recommandations basiques
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
        """Génère des recommandations basées sur le sentiment"""
        recommendations = []
        
        if sentiment == 'positive':
            recommendations.append("✅ Client satisfait - Opportunité de upselling")
            recommendations.append("💡 Suggérer un programme de fidélité")
        elif sentiment == 'negative':
            recommendations.append("⚠️ Client insatisfait - Contact prioritaire requis")
            recommendations.append("🎯 Planifier un appel de suivi")
        else:
            recommendations.append("📊 Client neutre - Maintenir l'engagement")
            recommendations.append("📧 Envoyer une enquête de satisfaction")
        
        if not customer_data.get('email'):
            recommendations.append("📧 Ajouter un email pour la communication")
        
        return "\n".join(recommendations)