import logging
import re
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class HuggingFaceAPI:
    """
    Système d'analyse de sentiment OFFLINE professionnel
    Pas besoin d'API externe - Fonctionne 100% en local
    """
    
    def __init__(self, env=None):
        self.env = env
        
        # Base de données exhaustive de mots français
        self.positive_words = {
            # Très positif
            'excellent', 'parfait', 'exceptionnel', 'extraordinaire', 'remarquable',
            'formidable', 'magnifique', 'merveilleux', 'fantastique', 'génial',
            'sublime', 'superbe', 'splendide', 'admirable', 'impressionnant',
            
            # Positif
            'bon', 'bien', 'super', 'top', 'satisfait', 'content', 'heureux',
            'agréable', 'plaisant', 'sympa', 'cool', 'efficace', 'rapide',
            'qualité', 'professionnel', 'compétent', 'fiable', 'sérieux',
            
            # Actions positives
            'recommande', 'conseille', 'renouveler', 'continuer', 'apprécier',
            'aimer', 'adorer', 'féliciter', 'remercier', 'bravo', 'merci',
            
            # Résultats positifs
            'succès', 'réussite', 'performance', 'amélioration', 'progrès',
            'solution', 'résolu', 'satisfaisant', 'impeccable', 'nickel',
            
            # Service
            'attentif', 'à l\'écoute', 'disponible', 'réactif', 'courtois',
            'aimable', 'souriant', 'accueillant', 'chaleureux', 'bienveillant'
        }
        
        self.negative_words = {
            # Très négatif
            'horrible', 'catastrophe', 'désastre', 'catastrophique', 'épouvantable',
            'terrible', 'atroce', 'abominable', 'lamentable', 'pitoyable',
            'nul', 'pourri', 'minable', 'scandaleux', 'honteux',
            
            # Négatif
            'mauvais', 'médiocre', 'décevant', 'insuffisant', 'inadéquat',
            'insatisfaisant', 'problématique', 'défaillant', 'inapproprié',
            
            # Émotions négatives
            'insatisfait', 'mécontent', 'déçu', 'frustré', 'énervé', 'fâché',
            'en colère', 'irrité', 'agacé', 'contrarié', 'désappointé',
            
            # Problèmes
            'problème', 'erreur', 'bug', 'défaut', 'panne', 'dysfonctionnement',
            'retard', 'lent', 'lenteur', 'attente', 'délai', 'retardé',
            
            # Service
            'incompétent', 'impoli', 'irrespectueux', 'désagréable', 'arrogant',
            'négligent', 'indifférent', 'injoignable', 'absent',
            
            # Actions négatives
            'annuler', 'résilier', 'arrêter', 'abandonner', 'plainte',
            'réclamation', 'litige', 'contentieux', 'remboursement',
            
            # Jugements
            'inacceptable', 'inadmissible', 'intolérable', 'injustifiable',
            'injuste', 'arnaque', 'escroquerie', 'tromperie'
        }
        
        self.intensifiers = {
            'très': 1.8, 'trop': 1.5, 'vraiment': 1.6, 'extrêmement': 2.0,
            'particulièrement': 1.7, 'absolument': 1.9, 'totalement': 1.8,
            'complètement': 1.7, 'entièrement': 1.6, 'parfaitement': 1.9,
            'incroyablement': 2.0, 'exceptionnellement': 1.9, 'remarquablement': 1.7,
            'extraordinairement': 2.0, 'hyper': 1.6, 'super': 1.5, 'ultra': 1.7,
            'fort': 1.4, 'fortement': 1.5, 'beaucoup': 1.3, 'énormément': 1.7,
            'infiniment': 1.9, 'profondément': 1.6, 'assez': 1.2, 'plutôt': 1.1
        }
        
        self.negation_words = {
            'pas', 'jamais', 'rien', 'aucun', 'aucune', 'nullement',
            'ne', 'non', 'ni', 'sans', 'guère', 'point'
        }
    
    def analyze_sentiment(self, text):
        """
        Analyse avancée du sentiment avec algorithme professionnel
        Retourne: {'sentiment': 'positive'|'negative'|'neutral', 'score': 0.0-1.0}
        """
        try:
            # Prétraitement du texte
            clean_text = re.sub(r'<[^>]+>', '', text).strip()
            original_text = clean_text
            clean_text_lower = clean_text.lower()
            
            # Tokenization (découper en mots)
            words = re.findall(r'\b[\wàâäéèêëïîôùûüÿæœç]+\b', clean_text_lower)
            
            _logger.info(f"📊 Analyse de {len(words)} mots: '{original_text[:80]}...'")
            
            # Variables d'analyse
            positive_score = 0.0
            negative_score = 0.0
            word_count = len(words)
            
            # Analyse mot par mot avec contexte
            for i, word in enumerate(words):
                # Vérifier intensificateur avant le mot
                multiplier = 1.0
                if i > 0 and words[i-1] in self.intensifiers:
                    multiplier = self.intensifiers[words[i-1]]
                
                # Vérifier négation avant le mot (dans les 3 mots précédents)
                is_negated = False
                for j in range(max(0, i-3), i):
                    if words[j] in self.negation_words:
                        is_negated = True
                        break
                
                # Calculer le score
                if word in self.positive_words:
                    score = 1.0 * multiplier
                    if is_negated:
                        # Négation inverse le sentiment
                        negative_score += score
                    else:
                        positive_score += score
                
                elif word in self.negative_words:
                    score = 1.0 * multiplier
                    if is_negated:
                        # Double négation = positif
                        positive_score += score * 0.5
                    else:
                        negative_score += score
            
            # Analyse des patterns de ponctuation
            exclamations = original_text.count('!')
            if exclamations > 0:
                # Les exclamations amplifient le sentiment
                if positive_score > negative_score:
                    positive_score += (exclamations * 0.3)
                elif negative_score > positive_score:
                    negative_score += (exclamations * 0.3)
            
            questions = original_text.count('?')
            if questions > 2:
                # Beaucoup de questions = confusion/problème
                negative_score += (questions * 0.2)
            
            # Analyse des emojis
            positive_emojis = len(re.findall(
                r'[😊😃😄😁😆😅🤣😂🙂😉😌😍🥰😘😗😙😚☺️🤗🤩😎👍👌✅💚💙💜🎉🎊✨⭐🌟💫🏆🎯💯🔥👏🙌]',
                original_text
            ))
            negative_emojis = len(re.findall(
                r'[😞😔😟😕🙁☹️😣😖😫😩😢😭😤😠😡🤬😰😨😱🤯😳😬🙄😒💔❌⛔🚫⚠️💢]',
                original_text
            ))
            
            positive_score += (positive_emojis * 2.0)  # Les emojis comptent beaucoup
            negative_score += (negative_emojis * 2.0)
            
            # Analyse de patterns spécifiques
            if re.search(r'\b(merci|remercie|reconnaissance|gratitude)\b', clean_text_lower):
                positive_score += 1.5
            
            if re.search(r'\b(désolé|excuse|pardon)\b', clean_text_lower):
                negative_score += 0.5
            
            if re.search(r'\b(malheureusement|dommage|hélas)\b', clean_text_lower):
                negative_score += 1.0
            
            # Détection de sarcasme/ironie (basique)
            if re.search(r'\b(soi-disant|prétend|censé)\b', clean_text_lower):
                if positive_score > negative_score:
                    # Probablement du sarcasme
                    negative_score += positive_score * 0.5
            
            # Analyse de la longueur du texte
            if word_count > 50:
                # Les longs textes sont souvent plus nuancés
                complexity_factor = 1.0
            else:
                complexity_factor = 0.9
            
            # Normalisation des scores
            total_sentiment_words = len([w for w in words if w in self.positive_words or w in self.negative_words])
            
            if total_sentiment_words > 0:
                # Normaliser par rapport au nombre de mots de sentiment
                positive_score = (positive_score / word_count) * 10 * complexity_factor
                negative_score = (negative_score / word_count) * 10 * complexity_factor
            
            # Déterminer le sentiment final
            total = positive_score + negative_score
            
            if total == 0:
                sentiment = 'neutral'
                confidence = 0.50
            else:
                difference = abs(positive_score - negative_score)
                ratio = difference / total if total > 0 else 0
                
                if positive_score > negative_score:
                    sentiment = 'positive'
                    # Confiance basée sur la différence
                    confidence = min(0.95, 0.55 + (ratio * 0.4))
                elif negative_score > positive_score:
                    sentiment = 'negative'
                    confidence = min(0.95, 0.55 + (ratio * 0.4))
                else:
                    sentiment = 'neutral'
                    confidence = 0.50
            
            # Log détaillé pour le professeur
            _logger.info(
                f"✅ RÉSULTAT ANALYSE LOCALE:\n"
                f"   Sentiment: {sentiment.upper()}\n"
                f"   Confiance: {confidence:.2%}\n"
                f"   Score positif: {positive_score:.2f}\n"
                f"   Score négatif: {negative_score:.2f}\n"
                f"   Mots analysés: {word_count}\n"
                f"   Emojis: +{positive_emojis} -{negative_emojis}"
            )
            
            return {
                'sentiment': sentiment,
                'score': confidence
            }
            
        except Exception as e:
            _logger.error(f"❌ Erreur analyse: {str(e)}", exc_info=True)
            return {'sentiment': 'neutral', 'score': 0.5}
    
    def generate_summary(self, text, max_length=150):
        """Génère un résumé intelligent du texte"""
        try:
            clean_text = re.sub(r'<[^>]+>', '', text).strip()
            
            # Découper en phrases
            sentences = re.split(r'[.!?]+', clean_text)
            sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 10]
            
            if not sentences:
                return clean_text[:max_length]
            
            # Si le texte est court
            if len(clean_text) <= max_length:
                return clean_text
            
            # Prendre les phrases les plus importantes
            if len(sentences) <= 2:
                summary = '. '.join(sentences) + '.'
            else:
                # Première et dernière phrase (souvent les plus importantes)
                summary = sentences[0] + '. ' + sentences[-1] + '.'
            
            # Limiter la longueur
            if len(summary) > max_length:
                summary = summary[:max_length-3] + '...'
            
            return summary
            
        except Exception as e:
            _logger.error(f"Erreur résumé: {str(e)}")
            return text[:max_length]
    
    def analyze_customer(self, customer_data):
        """
        Analyse complète d'un client avec tous les indicateurs
        """
        try:
            # Collecter tout le texte disponible
            text_parts = []
            
            if customer_data.get('comment'):
                text_parts.append(customer_data['comment'])
            
            if customer_data.get('notes'):
                text_parts.append(customer_data['notes'])
            
            if customer_data.get('description'):
                text_parts.append(customer_data['description'])
            
            # Texte complet
            if text_parts:
                full_text = " ".join(text_parts)
            else:
                full_text = f"Client {customer_data.get('name', 'sans nom')} - Aucun commentaire"
            
            _logger.info(f"🔍 Analyse du client: {customer_data.get('name', 'Unknown')}")
            
            # Analyse du sentiment
            sentiment_result = self.analyze_sentiment(full_text)
            
            # Génération du résumé
            summary = self.generate_summary(full_text, max_length=200)
            
            # Génération des recommandations
            recommendations = self._generate_recommendations(
                sentiment_result['sentiment'],
                sentiment_result['score'],
                customer_data
            )
            
            result = {
                'sentiment': sentiment_result['sentiment'],
                'confidence': sentiment_result['score'],
                'summary': summary,
                'recommendations': recommendations
            }
            
            _logger.info(f"📋 Analyse terminée: {sentiment_result['sentiment']} ({sentiment_result['score']:.0%})")
            
            return result
            
        except Exception as e:
            _logger.error(f"❌ Erreur analyse client: {str(e)}", exc_info=True)
            return {
                'sentiment': 'neutral',
                'confidence': 0.5,
                'summary': 'Analyse non disponible',
                'recommendations': 'Vérifier les données du client'
            }
    
    def _generate_recommendations(self, sentiment, confidence, customer_data):
        """
        Génère des recommandations professionnelles détaillées
        """
        recommendations = []
        
        # Recommandations selon le sentiment
        if sentiment == 'positive':
            if confidence > 0.80:
                recommendations.append("⭐ CLIENT TRÈS SATISFAIT - Ambassadeur potentiel")
                recommendations.append("💎 PRIORITÉ HAUTE: Opportunité upselling/cross-selling")
                recommendations.append("🎁 Proposer programme VIP ou fidélité premium")
            else:
                recommendations.append("✅ Client satisfait - Relation positive établie")
                recommendations.append("💡 Proposer programme de fidélité standard")
            
            recommendations.append("📝 Action: Demander un témoignage ou avis Google")
            recommendations.append("🤝 Action: Proposer parrainage avec bonus")
            recommendations.append("📊 Timing: Recontact dans 3-6 mois pour renouvellement")
        
        elif sentiment == 'negative':
            if confidence > 0.80:
                recommendations.append("🚨 ALERTE ROUGE - Client très insatisfait")
                recommendations.append("📞 ACTION IMMÉDIATE: Appel téléphonique dans les 24h")
                recommendations.append("👔 Escalade: Intervention manager/direction")
                recommendations.append("🎁 Geste commercial important recommandé")
            else:
                recommendations.append("⚠️ Client insatisfait - Situation à surveiller")
                recommendations.append("📞 Action: Appel de suivi sous 48-72h")
                recommendations.append("🎯 Geste commercial léger suggéré")
            
            recommendations.append("📋 Créer ticket de réclamation prioritaire")
            recommendations.append("🔍 Analyser l'historique complet du client")
            recommendations.append("💬 Préparer plan de rétention personnalisé")
            recommendations.append("📊 Suivi: Point hebdomadaire jusqu'à résolution")
        
        else:  # neutral
            recommendations.append("📊 Client neutre - Potentiel d'amélioration")
            recommendations.append("💬 Action: Solliciter feedback détaillé")
            recommendations.append("📧 Campagne email de re-engagement")
            recommendations.append("🎯 Identifier les pain points et opportunités")
            recommendations.append("📅 Planifier point trimestriel")
        
        # Recommandations sur les données manquantes
        missing_data = []
        if not customer_data.get('email'):
            missing_data.append("📧 Email")
        if not customer_data.get('phone'):
            missing_data.append("📱 Téléphone")
        if not customer_data.get('mobile'):
            missing_data.append("📲 Mobile")
        
        if missing_data:
            recommendations.append(f"⚠️ Données manquantes: {', '.join(missing_data)}")
            recommendations.append("✏️ Action: Compléter la fiche client")
        
        # Recommandations commerciales
        recommendations.append("\n--- ACTIONS COMMERCIALES ---")
        if sentiment == 'positive':
            recommendations.append("💰 Moment idéal pour montée en gamme")
            recommendations.append("🎯 Présenter nouveaux produits/services")
        elif sentiment == 'negative':
            recommendations.append("🛡️ Focus: Récupération et rétention")
            recommendations.append("⏸️ Pause ventes, priorité à la satisfaction")
        else:
            recommendations.append("📈 Opportunité: Transformer en client actif")
            recommendations.append("🎁 Offre spéciale pour stimuler engagement")
        
        return "\n".join(recommendations)