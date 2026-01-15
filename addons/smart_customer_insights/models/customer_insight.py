from odoo import models, fields, api

class CustomerInsight(models.Model):
    _name = 'customer.insight'
    _description = 'Insight Client IA'
    _order = 'create_date desc'

    partner_id = fields.Many2one('res.partner', string='Client', 
                                 required=True, ondelete='cascade')
    insight_type = fields.Selection([
        ('analysis', 'Analyse'),
        ('recommendation', 'Recommandation'),
        ('prediction', 'Prédiction')
    ], string='Type', required=True, default='analysis')
    
    content = fields.Text(string='Contenu', required=True)
    sentiment = fields.Selection([
        ('positive', 'Positif'),
        ('neutral', 'Neutre'),
        ('negative', 'Négatif')
    ], string='Sentiment')
    
    confidence_score = fields.Float(string='Score de Confiance', 
                                    digits=(5, 2))
    
    is_read = fields.Boolean(string='Lu', default=False)
    
    def action_mark_read(self):
        self.is_read = True