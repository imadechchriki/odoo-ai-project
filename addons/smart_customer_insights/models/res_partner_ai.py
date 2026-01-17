from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class ResPartnerAI(models.Model):
    _inherit = 'res.partner'

    ai_sentiment = fields.Selection([
        ('positive', 'Positif'),
        ('neutral', 'Neutre'),
        ('negative', 'Négatif')
    ], string='Sentiment IA', readonly=True)
    
    # AJOUT DU CHAMP MANQUANT
    ai_confidence_score = fields.Float(
        string='Score de Confiance',
        digits=(5, 2),
        readonly=True,
        help='Score de confiance de l\'analyse IA (0-100%)'
    )
    
    ai_summary = fields.Text(string='Résumé IA', readonly=True)
    ai_recommendations = fields.Text(string='Recommandations IA', readonly=True)
    ai_last_analysis = fields.Datetime(string='Dernière Analyse', readonly=True)
    
    insight_ids = fields.One2many('customer.insight', 'partner_id', 
                                  string='Insights IA')
    insight_count = fields.Integer(compute='_compute_insight_count')

    @api.depends('insight_ids')
    def _compute_insight_count(self):
        for partner in self:
            partner.insight_count = len(partner.insight_ids)

    def action_analyze_with_ai(self):
        """Bouton pour lancer l'analyse IA"""
        self.ensure_one()
        from ..lib.huggingface_api import HuggingFaceAPI
        
        try:
            api = HuggingFaceAPI()
            
            # Préparer le contexte client
            context = self._prepare_customer_context()
            
            # Analyser avec l'IA
            result = api.analyze_customer(context)
            
            _logger.info(f"📊 Résultat analyse: {result}")
            
            # CORRECTION: Sauvegarder le score de confiance
            confidence_percent = result.get('confidence', 0.5) * 100  # Convertir 0.85 -> 85
            
            # Mettre à jour les champs
            self.write({
                'ai_sentiment': result.get('sentiment', 'neutral'),
                'ai_confidence_score': confidence_percent,  # AJOUT ICI
                'ai_summary': result.get('summary', ''),
                'ai_recommendations': result.get('recommendations', ''),
                'ai_last_analysis': fields.Datetime.now()
            })
            
            _logger.info(f"✅ Sauvegardé - Sentiment: {result.get('sentiment')}, Score: {confidence_percent:.1f}%")
            
            # Créer un insight
            self.env['customer.insight'].create({
                'partner_id': self.id,
                'insight_type': 'analysis',
                'content': result.get('summary', ''),
                'sentiment': result.get('sentiment', 'neutral'),
                'confidence_score': confidence_percent,  # AJOUT ICI AUSSI
            })
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': f'Analyse terminée: {result.get("sentiment").upper()} ({confidence_percent:.0f}% confiance)',
                    'type': 'success',
                    'sticky': False,
                }
            }
        except Exception as e:
            _logger.error(f"❌ Erreur analyse IA: {str(e)}", exc_info=True)
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': f'Erreur: {str(e)}',
                    'type': 'danger',
                    'sticky': True,
                }
            }

    def _prepare_customer_context(self):
        """Prépare les données client pour l'IA"""
        return {
            'name': self.name,
            'email': self.email or '',
            'phone': self.phone or '',
            'comment': self.comment or 'Pas de notes',
            'city': self.city or '',
            'country': self.country_id.name if self.country_id else ''
        }

    def action_view_insights(self):
        """Ouvrir les insights du client"""
        return {
            'name': 'Insights IA',
            'view_mode': 'tree,form',
            'res_model': 'customer.insight',
            'type': 'ir.actions.act_window',
            'domain': [('partner_id', '=', self.id)],
            'context': {'default_partner_id': self.id}
        }