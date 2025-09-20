"""
📁 Ruta: /app/core/ai_context_service.py
📄 Nombre: ai_context_service.py
🏗️ Propósito: Recopilador de datos de todos los módulos del cliente
⚡ Performance: Consultas optimizadas multi-módulo
🔒 Seguridad: Acceso controlado a datos del cliente

ERP13 Enterprise - AI Context Service
Recopila datos de los 9 módulos del cliente para contexto AI
"""

import json
import sqlite3
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class ClientContext:
    """Contexto completo de un cliente para AI"""
    client_id: str
    client_name: str
    basic_info: Dict[str, Any]
    pipeline_data: Dict[str, Any]
    proposals_data: Dict[str, Any]
    communications_data: Dict[str, Any]
    campaigns_data: Dict[str, Any]
    tickets_data: Dict[str, Any]
    calendar_data: Dict[str, Any]
    timeline_data: Dict[str, Any]
    automations_data: Dict[str, Any]
    summary: Dict[str, Any]
    last_updated: datetime

class AIContextService:
    """Servicio para recopilar contexto de cliente para AI"""
    
    def __init__(self):
        self.db_path = 'erp_database.db'
        self.cache_duration_minutes = 15  # Cache por 15 minutos
        self._context_cache: Dict[str, ClientContext] = {}
    
    def get_db_connection(self):
        """Obtener conexión a la base de datos"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def get_client_context(self, client_id: str, force_refresh: bool = False) -> Optional[ClientContext]:
        """Obtener contexto completo del cliente para AI"""
        try:
            # Verificar cache
            if not force_refresh and client_id in self._context_cache:
                cached_context = self._context_cache[client_id]
                cache_age = datetime.now() - cached_context.last_updated
                
                if cache_age < timedelta(minutes=self.cache_duration_minutes):
                    logger.info(f"Usando contexto cacheado para cliente {client_id}")
                    return cached_context
            
            logger.info(f"Recopilando contexto completo para cliente {client_id}")
            
            # Recopilar datos de todos los módulos
            context = ClientContext(
                client_id=client_id,
                client_name="",
                basic_info={},
                pipeline_data={},
                proposals_data={},
                communications_data={},
                campaigns_data={},
                tickets_data={},
                calendar_data={},
                timeline_data={},
                automations_data={},
                summary={},
                last_updated=datetime.now()
            )
            
            # Datos básicos del cliente
            context.basic_info = self._get_client_basic_info(client_id)
            context.client_name = context.basic_info.get('nombre_empresa', f'Cliente {client_id}')
            
            # Pipeline - Oportunidades de venta
            context.pipeline_data = self._get_client_pipeline_data(client_id)
            
            # Propuestas comerciales
            context.proposals_data = self._get_client_proposals_data(client_id)
            
            # Comunicaciones
            context.communications_data = self._get_client_communications_data(client_id)
            
            # Campañas publicitarias
            context.campaigns_data = self._get_client_campaigns_data(client_id)
            
            # Tickets de soporte
            context.tickets_data = self._get_client_tickets_data(client_id)
            
            # Calendario - Actividades
            context.calendar_data = self._get_client_calendar_data(client_id)
            
            # Timeline - Línea de tiempo
            context.timeline_data = self._get_client_timeline_data(client_id)
            
            # Automatizaciones
            context.automations_data = self._get_client_automations_data(client_id)
            
            # Generar resumen
            context.summary = self._generate_client_summary(context)
            
            # Cachear contexto
            self._context_cache[client_id] = context
            
            logger.info(f"Contexto completo recopilado para {context.client_name}")
            return context
            
        except Exception as e:
            logger.error(f"Error recopilando contexto del cliente {client_id}: {str(e)}")
            return None
    
    def get_formatted_context_for_ai(self, client_id: str, focus_modules: List[str] = None) -> str:
        """Obtener contexto formateado para AI"""
        try:
            context = self.get_client_context(client_id)
            if not context:
                return f"No se encontraron datos para el cliente {client_id}"
            
            # Si no se especifican módulos, incluir todos
            if not focus_modules:
                focus_modules = [
                    'basic_info', 'pipeline', 'proposals', 'communications', 
                    'campaigns', 'tickets', 'calendar', 'timeline', 'automations'
                ]
            
            formatted_context = f"""
INFORMACIÓN DEL CLIENTE: {context.client_name} (ID: {client_id})
Última actualización: {context.last_updated.strftime('%Y-%m-%d %H:%M:%S')}

=== RESUMEN EJECUTIVO ===
{self._format_summary_for_ai(context.summary)}
"""
            
            # Incluir datos por módulos según el foco
            if 'basic_info' in focus_modules and context.basic_info:
                formatted_context += f"\n=== DATOS BÁSICOS ===\n{self._format_basic_info_for_ai(context.basic_info)}"
            
            if 'pipeline' in focus_modules and context.pipeline_data:
                formatted_context += f"\n=== PIPELINE DE VENTAS ===\n{self._format_pipeline_for_ai(context.pipeline_data)}"
            
            if 'proposals' in focus_modules and context.proposals_data:
                formatted_context += f"\n=== PROPUESTAS COMERCIALES ===\n{self._format_proposals_for_ai(context.proposals_data)}"
            
            if 'communications' in focus_modules and context.communications_data:
                formatted_context += f"\n=== COMUNICACIONES ===\n{self._format_communications_for_ai(context.communications_data)}"
            
            if 'campaigns' in focus_modules and context.campaigns_data:
                formatted_context += f"\n=== CAMPAÑAS PUBLICITARIAS ===\n{self._format_campaigns_for_ai(context.campaigns_data)}"
            
            if 'tickets' in focus_modules and context.tickets_data:
                formatted_context += f"\n=== TICKETS DE SOPORTE ===\n{self._format_tickets_for_ai(context.tickets_data)}"
            
            if 'calendar' in focus_modules and context.calendar_data:
                formatted_context += f"\n=== ACTIVIDADES DEL CALENDARIO ===\n{self._format_calendar_for_ai(context.calendar_data)}"
            
            if 'timeline' in focus_modules and context.timeline_data:
                formatted_context += f"\n=== LÍNEA DE TIEMPO ===\n{self._format_timeline_for_ai(context.timeline_data)}"
            
            if 'automations' in focus_modules and context.automations_data:
                formatted_context += f"\n=== AUTOMATIZACIONES ===\n{self._format_automations_for_ai(context.automations_data)}"
            
            return formatted_context
            
        except Exception as e:
            logger.error(f"Error formateando contexto para AI: {str(e)}")
            return f"Error obteniendo información del cliente {client_id}: {str(e)}"
    
    # ==========================================================================
    # MÉTODOS PRIVADOS - RECOPILACIÓN DE DATOS POR MÓDULO
    # ==========================================================================
    
    def _get_client_basic_info(self, client_id: str) -> Dict[str, Any]:
        """Obtener datos básicos del cliente"""
        try:
            conn = self.get_db_connection()
            
            # Datos principales del cliente
            client = conn.execute(
                'SELECT * FROM clients WHERE id = ?', (client_id,)
            ).fetchone()
            
            if not client:
                return {}
            
            # Campos dinámicos del cliente
            dynamic_fields = conn.execute('''
                SELECT field_name, field_value 
                FROM client_dynamic_data 
                WHERE client_id = ?
            ''', (client_id,)).fetchall()
            
            conn.close()
            
            result = dict(client) if client else {}
            
            # Agregar campos dinámicos
            for field in dynamic_fields:
                result[field['field_name']] = field['field_value']
            
            return result
            
        except Exception as e:
            logger.error(f"Error obteniendo datos básicos del cliente {client_id}: {str(e)}")
            self._ensure_tables_exist()
            return {}
    
    def _get_client_pipeline_data(self, client_id: str) -> Dict[str, Any]:
        """Obtener datos del pipeline Kanban - Embudo de ventas"""
        try:
            conn = self.get_db_connection()
            
            # Pipeline Kanban - Oportunidades por etapa (configurable)
            pipeline_stages = conn.execute('''
                SELECT * FROM pipeline_stages 
                ORDER BY stage_order
            ''').fetchall()
            
            # Oportunidades del cliente en cada etapa
            opportunities = conn.execute('''
                SELECT o.*, ps.stage_name, ps.stage_color
                FROM sales_opportunities o
                LEFT JOIN pipeline_stages ps ON o.stage_id = ps.id
                WHERE o.client_id = ? 
                ORDER BY o.updated_at DESC
            ''', (client_id,)).fetchall()
            
            # Estadísticas por etapa
            stage_stats = conn.execute('''
                SELECT 
                    ps.stage_name,
                    ps.stage_order,
                    COUNT(o.id) as opportunity_count,
                    SUM(o.estimated_value) as total_value,
                    AVG(o.days_in_stage) as avg_days_in_stage
                FROM sales_opportunities o
                LEFT JOIN pipeline_stages ps ON o.stage_id = ps.id
                WHERE o.client_id = ?
                GROUP BY ps.id, ps.stage_name
                ORDER BY ps.stage_order
            ''', (client_id,)).fetchall()
            
            # Historial de movimientos entre etapas
            stage_movements = conn.execute('''
                SELECT 
                    from_stage.stage_name as from_stage,
                    to_stage.stage_name as to_stage,
                    sm.moved_at,
                    sm.opportunity_id,
                    o.title as opportunity_title
                FROM stage_movements sm
                LEFT JOIN pipeline_stages from_stage ON sm.from_stage_id = from_stage.id
                LEFT JOIN pipeline_stages to_stage ON sm.to_stage_id = to_stage.id
                LEFT JOIN sales_opportunities o ON sm.opportunity_id = o.id
                WHERE o.client_id = ?
                ORDER BY sm.moved_at DESC
                LIMIT 10
            ''', (client_id,)).fetchall()
            
            conn.close()
            
            return {
                'opportunities': [dict(opp) for opp in opportunities],
                'pipeline_stages': [dict(stage) for stage in pipeline_stages],
                'stage_statistics': [dict(stat) for stat in stage_stats],
                'stage_movements': [dict(movement) for movement in stage_movements],
                'total_opportunities': len(opportunities),
                'pipeline_health': self._calculate_pipeline_health_advanced(opportunities, stage_stats),
                'conversion_analysis': self._analyze_stage_conversions(stage_movements)
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo pipeline Kanban del cliente {client_id}: {str(e)}")
            return {}
    
    def _get_client_proposals_data(self, client_id: str) -> Dict[str, Any]:
        """Obtener propuestas comerciales con plantillas y variables dinámicas"""
        try:
            conn = self.get_db_connection()
            
            # Propuestas con plantillas utilizadas
            proposals = conn.execute('''
                SELECT 
                    p.*,
                    pt.template_name,
                    pt.template_variables,
                    pb.budget_file_path,
                    pb.total_cost,
                    pb.profit_margin
                FROM client_proposals p
                LEFT JOIN proposal_templates pt ON p.template_id = pt.id
                LEFT JOIN proposal_budgets pb ON p.budget_id = pb.id
                WHERE p.client_id = ? 
                ORDER BY p.created_at DESC
                LIMIT 15
            ''', (client_id,)).fetchall()
            
            # Estadísticas de propuestas por plantilla
            template_stats = conn.execute('''
                SELECT 
                    pt.template_name,
                    COUNT(p.id) as proposal_count,
                    AVG(p.total_amount) as avg_amount,
                    SUM(CASE WHEN p.status = 'accepted' THEN 1 ELSE 0 END) as accepted_count,
                    SUM(CASE WHEN p.status = 'accepted' THEN p.total_amount ELSE 0 END) as total_accepted_value
                FROM client_proposals p
                LEFT JOIN proposal_templates pt ON p.template_id = pt.id
                WHERE p.client_id = ?
                GROUP BY pt.id, pt.template_name
            ''', (client_id,)).fetchall()
            
            # Variables utilizadas en propuestas
            variable_usage = conn.execute('''
                SELECT 
                    pv.variable_name,
                    pv.variable_value,
                    pv.proposal_id,
                    p.created_at,
                    p.status
                FROM proposal_variables pv
                LEFT JOIN client_proposals p ON pv.proposal_id = p.id
                WHERE p.client_id = ?
                ORDER BY p.created_at DESC
                LIMIT 50
            ''', (client_id,)).fetchall()
            
            # Análisis de efectividad por tipo de propuesta
            effectiveness_analysis = conn.execute('''
                SELECT 
                    p.proposal_type,
                    COUNT(*) as total_proposals,
                    AVG(p.total_amount) as avg_value,
                    (SUM(CASE WHEN p.status = 'accepted' THEN 1 ELSE 0 END) * 100.0 / COUNT(*)) as conversion_rate,
                    AVG(p.days_to_decision) as avg_decision_time
                FROM client_proposals p
                WHERE p.client_id = ?
                GROUP BY p.proposal_type
            ''', (client_id,)).fetchall()
            
            # Historial de modificaciones de propuestas
            proposal_modifications = conn.execute('''
                SELECT 
                    pm.modification_type,
                    pm.old_value,
                    pm.new_value,
                    pm.modified_at,
                    pm.modified_by,
                    p.title as proposal_title
                FROM proposal_modifications pm
                LEFT JOIN client_proposals p ON pm.proposal_id = p.id
                WHERE p.client_id = ?
                ORDER BY pm.modified_at DESC
                LIMIT 20
            ''', (client_id,)).fetchall()
            
            conn.close()
            
            return {
                'proposals': [dict(prop) for prop in proposals],
                'template_statistics': [dict(stat) for stat in template_stats],
                'variable_usage': [dict(var) for var in variable_usage],
                'effectiveness_analysis': [dict(eff) for eff in effectiveness_analysis],
                'modifications_history': [dict(mod) for mod in proposal_modifications],
                'total_proposals': len(proposals),
                'conversion_rate': self._calculate_proposal_conversion_advanced(proposals),
                'best_performing_template': self._identify_best_template(template_stats),
                'variable_patterns': self._analyze_variable_patterns(variable_usage),
                'pricing_insights': self._generate_pricing_insights(proposals)
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo propuestas del cliente {client_id}: {str(e)}")
            return {}
    
    def _get_client_communications_data(self, client_id: str) -> Dict[str, Any]:
        """Obtener historial de comunicaciones multicanal"""
        try:
            conn = self.get_db_connection()
            
            # Comunicaciones multicanal (emails, SMS, WhatsApp, llamadas)
            communications = conn.execute('''
                SELECT 
                    c.*,
                    cc.channel_name,
                    cc.channel_config
                FROM client_communications c
                LEFT JOIN communication_channels cc ON c.channel_id = cc.id
                WHERE c.client_id = ? 
                ORDER BY c.created_at DESC
                LIMIT 50
            ''', (client_id,)).fetchall()
            
            # Estadísticas por canal
            channel_stats = conn.execute('''
                SELECT 
                    cc.channel_name,
                    COUNT(*) as message_count,
                    AVG(c.response_time_minutes) as avg_response_time,
                    MAX(c.created_at) as last_communication,
                    SUM(CASE WHEN c.sentiment_score > 0 THEN 1 ELSE 0 END) as positive_interactions,
                    AVG(c.sentiment_score) as avg_sentiment
                FROM client_communications c
                LEFT JOIN communication_channels cc ON c.channel_id = cc.id
                WHERE c.client_id = ?
                GROUP BY cc.id, cc.channel_name
            ''', (client_id,)).fetchall()
            
            # Análisis de contenido y sentimiento
            recent_sentiment = conn.execute('''
                SELECT 
                    sentiment_score,
                    content_summary,
                    communication_type,
                    created_at
                FROM client_communications
                WHERE client_id = ? AND sentiment_score IS NOT NULL
                ORDER BY created_at DESC
                LIMIT 10
            ''', (client_id,)).fetchall()
            
            # Plantillas utilizadas en comunicaciones
            template_usage = conn.execute('''
                SELECT 
                    ct.template_name,
                    COUNT(*) as usage_count,
                    AVG(c.engagement_score) as avg_engagement
                FROM client_communications c
                LEFT JOIN communication_templates ct ON c.template_id = ct.id
                WHERE c.client_id = ? AND c.template_id IS NOT NULL
                GROUP BY ct.id, ct.template_name
                ORDER BY usage_count DESC
            ''', (client_id,)).fetchall()
            
            conn.close()
            
            return {
                'communications': [dict(comm) for comm in communications],
                'channel_statistics': [dict(stat) for stat in channel_stats],
                'sentiment_analysis': [dict(sent) for sent in recent_sentiment],
                'template_usage': [dict(template) for template in template_usage],
                'total_communications': len(communications),
                'preferred_channel': self._identify_preferred_channel(channel_stats),
                'communication_patterns': self._analyze_communication_patterns(communications),
                'engagement_score': self._calculate_engagement_score(communications)
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo comunicaciones del cliente {client_id}: {str(e)}")
            return {}
    
    def _get_client_campaigns_data(self, client_id: str) -> Dict[str, Any]:
        """Obtener campañas publicitarias multicanal"""
        try:
            conn = self.get_db_connection()
            
            # Campañas multicanal (Email, WhatsApp, redes sociales)
            campaigns = conn.execute('''
                SELECT 
                    mc.*,
                    ct.template_name,
                    ct.template_content,
                    COUNT(cc.channel_id) as active_channels
                FROM marketing_campaigns mc
                LEFT JOIN campaign_templates ct ON mc.template_id = ct.id
                LEFT JOIN campaign_channels cc ON mc.id = cc.campaign_id
                WHERE mc.target_clients LIKE ? OR mc.target_clients = 'all'
                GROUP BY mc.id
                ORDER BY mc.created_at DESC
                LIMIT 10
            ''', (f'%{client_id}%',)).fetchall()
            
            # Métricas detalladas por canal
            channel_metrics = conn.execute('''
                SELECT 
                    cc.channel_name,
                    SUM(cm.impressions) as total_impressions,
                    SUM(cm.clicks) as total_clicks,
                    SUM(cm.conversions) as total_conversions,
                    SUM(cm.cost) as total_cost,
                    AVG(cm.engagement_rate) as avg_engagement_rate,
                    (SUM(cm.clicks) * 100.0 / NULLIF(SUM(cm.impressions), 0)) as ctr,
                    (SUM(cm.conversions) * 100.0 / NULLIF(SUM(cm.clicks), 0)) as conversion_rate
                FROM campaign_metrics cm
                LEFT JOIN campaign_channels cc ON cm.channel_id = cc.channel_id
                WHERE cm.client_id = ?
                GROUP BY cc.channel_id, cc.channel_name
            ''', (client_id,)).fetchall()
            
            # Segmentación y targeting
            segmentation_analysis = conn.execute('''
                SELECT 
                    cs.segment_name,
                    cs.segment_criteria,
                    COUNT(cm.campaign_id) as campaigns_count,
                    AVG(cm.engagement_rate) as avg_engagement,
                    SUM(cm.conversions) as total_conversions
                FROM campaign_segments cs
                LEFT JOIN marketing_campaigns mc ON cs.campaign_id = mc.id
                LEFT JOIN campaign_metrics cm ON mc.id = cm.campaign_id
                WHERE mc.target_clients LIKE ? OR mc.target_clients = 'all'
                GROUP BY cs.id, cs.segment_name
            ''', (f'%{client_id}%',)).fetchall()
            
            # Variables dinámicas utilizadas en campañas
            campaign_variables = conn.execute('''
                SELECT 
                    cv.variable_name,
                    cv.variable_value,
                    mc.campaign_name,
                    cm.engagement_rate,
                    cm.conversions
                FROM campaign_variables cv
                LEFT JOIN marketing_campaigns mc ON cv.campaign_id = mc.id
                LEFT JOIN campaign_metrics cm ON mc.id = cm.campaign_id
                WHERE mc.target_clients LIKE ? OR mc.target_clients = 'all'
                ORDER BY cm.engagement_rate DESC
            ''', (f'%{client_id}%',)).fetchall()
            
            # Análisis de rendimiento por sector/tipo de cliente
            sector_performance = conn.execute('''
                SELECT 
                    c.sector,
                    COUNT(DISTINCT mc.id) as campaigns_received,
                    AVG(cm.engagement_rate) as avg_engagement,
                    SUM(cm.conversions) as total_conversions,
                    AVG(cm.cost_per_conversion) as avg_cost_per_conversion
                FROM clients c
                LEFT JOIN campaign_targets ct ON c.id = ct.client_id
                LEFT JOIN marketing_campaigns mc ON ct.campaign_id = mc.id
                LEFT JOIN campaign_metrics cm ON mc.id = cm.campaign_id
                WHERE c.id = ?
                GROUP BY c.sector
            ''', (client_id,)).fetchall()
            
            # ROI y análisis financiero
            roi_analysis = conn.execute('''
                SELECT 
                    mc.campaign_name,
                    SUM(cm.cost) as total_investment,
                    SUM(cm.revenue_generated) as total_revenue,
                    ((SUM(cm.revenue_generated) - SUM(cm.cost)) * 100.0 / NULLIF(SUM(cm.cost), 0)) as roi_percentage,
                    AVG(cm.customer_lifetime_value) as avg_clv
                FROM marketing_campaigns mc
                LEFT JOIN campaign_metrics cm ON mc.id = cm.campaign_id
                WHERE mc.target_clients LIKE ? OR mc.target_clients = 'all'
                GROUP BY mc.id, mc.campaign_name
                ORDER BY roi_percentage DESC
            ''', (f'%{client_id}%',)).fetchall()
            
            conn.close()
            
            return {
                'active_campaigns': [dict(camp) for camp in campaigns],
                'channel_metrics': [dict(metric) for metric in channel_metrics],
                'segmentation_analysis': [dict(segment) for segment in segmentation_analysis],
                'campaign_variables': [dict(var) for var in campaign_variables],
                'sector_performance': [dict(perf) for perf in sector_performance],
                'roi_analysis': [dict(roi) for roi in roi_analysis],
                'total_campaigns': len(campaigns),
                'best_performing_channel': self._identify_best_channel(channel_metrics),
                'personalization_effectiveness': self._analyze_personalization_impact(campaign_variables),
                'campaign_recommendations': self._generate_campaign_recommendations(channel_metrics, sector_performance)
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo campañas del cliente {client_id}: {str(e)}")
            return {}
    
    def _get_client_tickets_data(self, client_id: str) -> Dict[str, Any]:
        """Obtener tickets de soporte con escalabilidad y SLA"""
        try:
            conn = self.get_db_connection()
            
            # Tickets con información de escalabilidad
            tickets = conn.execute('''
                SELECT 
                    st.*,
                    tc.category_name,
                    tc.default_sla_hours,
                    tc.escalation_rules,
                    u1.username as assigned_to_name,
                    u2.username as created_by_name,
                    te.escalated_to,
                    te.escalation_reason,
                    te.escalated_at
                FROM support_tickets st
                LEFT JOIN ticket_categories tc ON st.category_id = tc.id
                LEFT JOIN users u1 ON st.assigned_to = u1.id
                LEFT JOIN users u2 ON st.created_by = u2.id
                LEFT JOIN ticket_escalations te ON st.id = te.ticket_id
                WHERE st.client_id = ? 
                ORDER BY st.created_at DESC
                LIMIT 25
            ''', (client_id,)).fetchall()
            
            # Estadísticas SLA y rendimiento
            sla_performance = conn.execute('''
                SELECT 
                    tc.category_name,
                    tc.default_sla_hours,
                    COUNT(st.id) as total_tickets,
                    AVG(st.resolution_time_hours) as avg_resolution_time,
                    SUM(CASE WHEN st.resolution_time_hours <= tc.default_sla_hours THEN 1 ELSE 0 END) as within_sla,
                    (SUM(CASE WHEN st.resolution_time_hours <= tc.default_sla_hours THEN 1 ELSE 0 END) * 100.0 / COUNT(st.id)) as sla_compliance_rate,
                    COUNT(te.id) as escalated_tickets
                FROM support_tickets st
                LEFT JOIN ticket_categories tc ON st.category_id = tc.id
                LEFT JOIN ticket_escalations te ON st.id = te.ticket_id
                WHERE st.client_id = ?
                GROUP BY tc.id, tc.category_name, tc.default_sla_hours
            ''', (client_id,)).fetchall()
            
            # Análisis de escalabilidad y transferencias
            escalation_analysis = conn.execute('''
                SELECT 
                    te.escalation_reason,
                    COUNT(*) as escalation_count,
                    AVG(st.resolution_time_hours) as avg_resolution_after_escalation,
                    u1.username as escalated_from,
                    u2.username as escalated_to
                FROM ticket_escalations te
                LEFT JOIN support_tickets st ON te.ticket_id = st.id
                LEFT JOIN users u1 ON te.escalated_from = u1.id
                LEFT JOIN users u2 ON te.escalated_to = u2.id
                WHERE st.client_id = ?
                GROUP BY te.escalation_reason, te.escalated_from, te.escalated_to
                ORDER BY escalation_count DESC
            ''', (client_id,)).fetchall()
            
            # Patrones de problemas y soluciones
            problem_patterns = conn.execute('''
                SELECT 
                    st.problem_category,
                    st.solution_summary,
                    COUNT(*) as occurrence_count,
                    AVG(st.resolution_time_hours) as avg_resolution_time,
                    AVG(st.customer_satisfaction_score) as avg_satisfaction
                FROM support_tickets st
                WHERE st.client_id = ? AND st.status = 'resolved'
                GROUP BY st.problem_category, st.solution_summary
                HAVING COUNT(*) > 1
                ORDER BY occurrence_count DESC
                LIMIT 10
            ''', (client_id,)).fetchall()
            
            # Análisis de satisfacción y feedback
            satisfaction_analysis = conn.execute('''
                SELECT 
                    st.priority,
                    tc.category_name,
                    AVG(st.customer_satisfaction_score) as avg_satisfaction,
                    COUNT(sf.id) as feedback_count,
                    AVG(sf.overall_rating) as avg_overall_rating,
                    STRING_AGG(sf.feedback_text, ' | ') as recent_feedback
                FROM support_tickets st
                LEFT JOIN ticket_categories tc ON st.category_id = tc.id
                LEFT JOIN support_feedback sf ON st.id = sf.ticket_id
                WHERE st.client_id = ? AND st.status = 'resolved'
                GROUP BY st.priority, tc.id, tc.category_name
            ''', (client_id,)).fetchall()
            
            # Análisis de carga de trabajo por agente
            agent_workload = conn.execute('''
                SELECT 
                    u.username,
                    COUNT(st.id) as assigned_tickets,
                    AVG(st.resolution_time_hours) as avg_resolution_time,
                    SUM(CASE WHEN st.status = 'open' THEN 1 ELSE 0 END) as open_tickets,
                    AVG(st.customer_satisfaction_score) as avg_satisfaction_score
                FROM support_tickets st
                LEFT JOIN users u ON st.assigned_to = u.id
                WHERE st.client_id = ?
                GROUP BY u.id, u.username
                ORDER BY assigned_tickets DESC
            ''', (client_id,)).fetchall()
            
            conn.close()
            
            return {
                'tickets': [dict(ticket) for ticket in tickets],
                'sla_performance': [dict(sla) for sla in sla_performance],
                'escalation_analysis': [dict(esc) for esc in escalation_analysis],
                'problem_patterns': [dict(pattern) for pattern in problem_patterns],
                'satisfaction_analysis': [dict(sat) for sat in satisfaction_analysis],
                'agent_workload': [dict(agent) for agent in agent_workload],
                'total_tickets': len(tickets),
                'overall_sla_compliance': self._calculate_overall_sla_compliance(sla_performance),
                'escalation_rate': self._calculate_escalation_rate(tickets, escalation_analysis),
                'satisfaction_score': self._calculate_support_satisfaction_advanced(satisfaction_analysis),
                'ticket_trends': self._analyze_ticket_trends(tickets),
                'improvement_recommendations': self._generate_support_recommendations(sla_performance, problem_patterns)
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo tickets del cliente {client_id}: {str(e)}")
            return {}
    
    def _get_client_calendar_data(self, client_id: str) -> Dict[str, Any]:
        """Obtener actividades del calendario con integración externa"""
        try:
            conn = self.get_db_connection()
            
            # Actividades con integración de calendario externo
            upcoming_activities = conn.execute('''
                SELECT 
                    ca.*,
                    ct.calendar_type,
                    ct.external_calendar_id,
                    ct.sync_status,
                    u.username as assigned_to_name,
                    STRING_AGG(cap.participant_email, ', ') as participants
                FROM calendar_activities ca
                LEFT JOIN calendar_integrations ct ON ca.calendar_integration_id = ct.id
                LEFT JOIN users u ON ca.assigned_to = u.id
                LEFT JOIN calendar_activity_participants cap ON ca.id = cap.activity_id
                WHERE ca.client_id = ? AND ca.activity_date >= date('now')
                GROUP BY ca.id
                ORDER BY ca.activity_date ASC
                LIMIT 15
            ''', (client_id,)).fetchall()
            
            past_activities = conn.execute('''
                SELECT 
                    ca.*,
                    ct.calendar_type,
                    ct.external_calendar_id,
                    u.username as assigned_to_name,
                    ca.actual_duration_minutes,
                    ca.completion_status,
                    ca.outcome_notes
                FROM calendar_activities ca
                LEFT JOIN calendar_integrations ct ON ca.calendar_integration_id = ct.id
                LEFT JOIN users u ON ca.assigned_to = u.id
                WHERE ca.client_id = ? AND ca.activity_date < date('now')
                ORDER BY ca.activity_date DESC
                LIMIT 15
            ''', (client_id,)).fetchall()
            
            # Análisis de patrones de reuniones
            meeting_patterns = conn.execute('''
                SELECT 
                    ca.activity_type,
                    COUNT(*) as total_meetings,
                    AVG(ca.planned_duration_minutes) as avg_planned_duration,
                    AVG(ca.actual_duration_minutes) as avg_actual_duration,
                    SUM(CASE WHEN ca.completion_status = 'completed' THEN 1 ELSE 0 END) as completed_meetings,
                    AVG(ca.effectiveness_rating) as avg_effectiveness
                FROM calendar_activities ca
                WHERE ca.client_id = ?
                GROUP BY ca.activity_type
                ORDER BY total_meetings DESC
            ''', (client_id,)).fetchall()
            
            # Integración con calendarios externos (Gmail, Outlook, etc.)
            external_sync_status = conn.execute('''
                SELECT 
                    ci.calendar_type,
                    ci.integration_name,
                    ci.sync_status,
                    ci.last_sync_at,
                    ci.sync_errors_count,
                    ci.total_synced_events,
                    COUNT(ca.id) as activities_synced
                FROM calendar_integrations ci
                LEFT JOIN calendar_activities ca ON ci.id = ca.calendar_integration_id AND ca.client_id = ?
                WHERE ci.active = 1
                GROUP BY ci.id, ci.calendar_type, ci.integration_name
            ''', (client_id,)).fetchall()
            
            # Análisis de productividad de reuniones
            productivity_analysis = conn.execute('''
                SELECT 
                    DATE(ca.activity_date) as meeting_date,
                    COUNT(*) as meetings_count,
                    SUM(ca.actual_duration_minutes) as total_meeting_time,
                    AVG(ca.effectiveness_rating) as avg_effectiveness,
                    SUM(CASE WHEN ca.follow_up_required THEN 1 ELSE 0 END) as follow_ups_needed,
                    STRING_AGG(ca.outcome_summary, ' | ') as outcomes_summary
                FROM calendar_activities ca
                WHERE ca.client_id = ? AND ca.activity_date >= date('now', '-30 days')
                GROUP BY DATE(ca.activity_date)
                ORDER BY meeting_date DESC
                LIMIT 30
            ''', (client_id,)).fetchall()
            
            # Recordatorios y notificaciones pendientes
            pending_reminders = conn.execute('''
                SELECT 
                    cr.reminder_type,
                    cr.reminder_message,
                    cr.scheduled_at,
                    cr.delivery_method,
                    ca.title as activity_title,
                    ca.activity_date
                FROM calendar_reminders cr
                LEFT JOIN calendar_activities ca ON cr.activity_id = ca.id
                WHERE ca.client_id = ? AND cr.status = 'pending'
                ORDER BY cr.scheduled_at ASC
            ''', (client_id,)).fetchall()
            
            # Análisis de disponibilidad y conflictos
            availability_analysis = conn.execute('''
                SELECT 
                    u.username,
                    COUNT(ca.id) as scheduled_activities,
                    SUM(ca.planned_duration_minutes) as total_scheduled_minutes,
                    COUNT(CASE WHEN ca.conflict_detected = 1 THEN 1 END) as conflicted_meetings,
                    AVG(ca.preparation_time_minutes) as avg_prep_time
                FROM calendar_activities ca
                LEFT JOIN users u ON ca.assigned_to = u.id
                WHERE ca.client_id = ? AND ca.activity_date >= date('now')
                GROUP BY u.id, u.username
            ''', (client_id,)).fetchall()
            
            conn.close()
            
            return {
                'upcoming_activities': [dict(act) for act in upcoming_activities],
                'past_activities': [dict(act) for act in past_activities],
                'meeting_patterns': [dict(pattern) for pattern in meeting_patterns],
                'external_sync_status': [dict(sync) for sync in external_sync_status],
                'productivity_analysis': [dict(prod) for prod in productivity_analysis],
                'pending_reminders': [dict(reminder) for reminder in pending_reminders],
                'availability_analysis': [dict(avail) for avail in availability_analysis],
                'total_upcoming': len(upcoming_activities),
                'integration_health': self._assess_calendar_integration_health(external_sync_status),
                'meeting_effectiveness': self._calculate_meeting_effectiveness(meeting_patterns),
                'time_utilization': self._analyze_time_utilization(productivity_analysis),
                'scheduling_recommendations': self._generate_scheduling_recommendations(availability_analysis, meeting_patterns)
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo calendario del cliente {client_id}: {str(e)}")
            return {}
    
    def _get_client_timeline_data(self, client_id: str) -> Dict[str, Any]:
        """Obtener línea de tiempo de interacciones con análisis temporal"""
        try:
            conn = self.get_db_connection()
            
            # Eventos de timeline con detalles enriquecidos
            timeline_events = conn.execute('''
                SELECT 
                    ct.*,
                    u.username as triggered_by_name,
                    cam.automation_name as related_automation,
                    STRING_AGG(cte.entity_type || ':' || cte.entity_id, ', ') as related_entities
                FROM client_timeline ct
                LEFT JOIN users u ON ct.triggered_by = u.id
                LEFT JOIN client_automations cam ON ct.automation_id = cam.id
                LEFT JOIN client_timeline_entities cte ON ct.id = cte.timeline_id
                WHERE ct.client_id = ?
                GROUP BY ct.id
                ORDER BY ct.event_date DESC
                LIMIT 50
            ''', (client_id,)).fetchall()
            
            # Hitos importantes y métricas de progreso
            milestones = conn.execute('''
                SELECT 
                    cm.*,
                    mt.milestone_type_name,
                    mt.importance_weight,
                    COUNT(cma.id) as milestone_actions,
                    STRING_AGG(cma.action_description, ' | ') as milestone_activities
                FROM client_milestones cm
                LEFT JOIN milestone_types mt ON cm.milestone_type_id = mt.id
                LEFT JOIN client_milestone_actions cma ON cm.id = cma.milestone_id
                WHERE cm.client_id = ?
                GROUP BY cm.id
                ORDER BY cm.milestone_date DESC
            ''', (client_id,)).fetchall()
            
            # Análisis de patrones temporales
            temporal_patterns = conn.execute('''
                SELECT 
                    strftime('%w', ct.event_date) as day_of_week,
                    strftime('%H', ct.event_date) as hour_of_day,
                    ct.event_type,
                    COUNT(*) as event_count,
                    AVG(ct.impact_score) as avg_impact,
                    AVG(ct.duration_minutes) as avg_duration
                FROM client_timeline ct
                WHERE ct.client_id = ? AND ct.event_date >= date('now', '-90 days')
                GROUP BY strftime('%w', ct.event_date), strftime('%H', ct.event_date), ct.event_type
                ORDER BY event_count DESC
            ''', (client_id,)).fetchall()
            
            # Análisis de momentum y tendencias
            momentum_analysis = conn.execute('''
                SELECT 
                    DATE(ct.event_date) as event_date,
                    COUNT(*) as daily_activity_count,
                    SUM(ct.impact_score) as daily_impact_total,
                    AVG(ct.sentiment_score) as daily_sentiment,
                    STRING_AGG(DISTINCT ct.event_category, ', ') as activity_categories,
                    SUM(CASE WHEN ct.event_type = 'positive_interaction' THEN 1 ELSE 0 END) as positive_events,
                    SUM(CASE WHEN ct.event_type = 'issue_resolution' THEN 1 ELSE 0 END) as issue_resolutions
                FROM client_timeline ct
                WHERE ct.client_id = ? AND ct.event_date >= date('now', '-60 days')
                GROUP BY DATE(ct.event_date)
                ORDER BY event_date DESC
            ''', (client_id,)).fetchall()
            
            # Análisis de ciclos y estacionalidad
            cyclical_analysis = conn.execute('''
                SELECT 
                    strftime('%Y-%m', ct.event_date) as month_year,
                    ct.event_category,
                    COUNT(*) as events_count,
                    AVG(ct.business_value_impact) as avg_business_impact,
                    SUM(ct.revenue_impact) as total_revenue_impact,
                    LEAD(COUNT(*)) OVER (PARTITION BY ct.event_category ORDER BY strftime('%Y-%m', ct.event_date)) as next_month_count
                FROM client_timeline ct
                WHERE ct.client_id = ? AND ct.event_date >= date('now', '-12 months')
                GROUP BY strftime('%Y-%m', ct.event_date), ct.event_category
                ORDER BY month_year DESC, events_count DESC
            ''', (client_id,)).fetchall()
            
            # Correlaciones entre eventos y resultados de negocio
            event_correlations = conn.execute('''
                SELECT 
                    ct.event_type,
                    COUNT(*) as event_frequency,
                    AVG(p.total_amount) as avg_proposal_value_after,
                    COUNT(p.id) as proposals_generated,
                    AVG(st.resolution_time_hours) as avg_support_resolution,
                    COUNT(st.id) as support_tickets_after
                FROM client_timeline ct
                LEFT JOIN client_proposals p ON ct.client_id = p.client_id 
                    AND p.created_at > ct.event_date 
                    AND p.created_at <= datetime(ct.event_date, '+30 days')
                LEFT JOIN support_tickets st ON ct.client_id = st.client_id 
                    AND st.created_at > ct.event_date 
                    AND st.created_at <= datetime(ct.event_date, '+30 days')
                WHERE ct.client_id = ?
                GROUP BY ct.event_type
                HAVING COUNT(*) >= 3
                ORDER BY event_frequency DESC
            ''', (client_id,)).fetchall()
            
            # Análisis de velocidad de progreso
            progress_velocity = conn.execute('''
                SELECT 
                    DATE(ct.event_date) as date,
                    SUM(CASE 
                        WHEN ct.progress_indicator = 'advancement' THEN ct.progress_points
                        WHEN ct.progress_indicator = 'regression' THEN -ct.progress_points
                        ELSE 0 
                    END) as net_progress_points,
                    COUNT(CASE WHEN ct.progress_indicator = 'advancement' THEN 1 END) as advancement_events,
                    COUNT(CASE WHEN ct.progress_indicator = 'regression' THEN 1 END) as regression_events,
                    AVG(ct.client_satisfaction_impact) as avg_satisfaction_impact
                FROM client_timeline ct
                WHERE ct.client_id = ? AND ct.progress_points IS NOT NULL
                GROUP BY DATE(ct.event_date)
                ORDER BY date DESC
                LIMIT 30
            ''', (client_id,)).fetchall()
            
            # Predicciones basadas en patrones históricos
            predictive_insights = conn.execute('''
                SELECT 
                    pi.insight_type,
                    pi.prediction_description,
                    pi.confidence_percentage,
                    pi.expected_timeline_days,
                    pi.recommended_actions,
                    pi.based_on_pattern,
                    pi.generated_at
                FROM predictive_insights pi
                WHERE pi.client_id = ? AND pi.status = 'active'
                ORDER BY pi.confidence_percentage DESC, pi.expected_timeline_days ASC
                LIMIT 10
            ''', (client_id,)).fetchall()
            
            conn.close()
            
            return {
                'timeline_events': [dict(event) for event in timeline_events],
                'milestones': [dict(milestone) for milestone in milestones],
                'temporal_patterns': [dict(pattern) for pattern in temporal_patterns],
                'momentum_analysis': [dict(momentum) for momentum in momentum_analysis],
                'cyclical_analysis': [dict(cycle) for cycle in cyclical_analysis],
                'event_correlations': [dict(corr) for corr in event_correlations],
                'progress_velocity': [dict(velocity) for velocity in progress_velocity],
                'predictive_insights': [dict(insight) for insight in predictive_insights],
                'total_events': len(timeline_events),
                'relationship_duration': self._calculate_relationship_duration_advanced(timeline_events),
                'engagement_trends': self._analyze_engagement_trends(momentum_analysis),
                'business_impact_score': self._calculate_business_impact_score(event_correlations),
                'predictive_accuracy': self._evaluate_prediction_accuracy(predictive_insights),
                'timeline_health_score': self._calculate_timeline_health_score(timeline_events, momentum_analysis)
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo timeline del cliente {client_id}: {str(e)}")
            return {}
    
    def _get_client_automations_data(self, client_id: str) -> Dict[str, Any]:
        """Obtener automatizaciones - Cerebro del ERP con flujos inteligentes"""
        try:
            conn = self.get_db_connection()
            
            # Automatizaciones activas con reglas inteligentes
            automations = conn.execute('''
                SELECT 
                    ca.*,
                    at.template_name,
                    at.workflow_definition,
                    STRING_AGG(ar.rule_condition, ' AND ') as combined_conditions,
                    COUNT(ae.id) as total_executions,
                    AVG(ae.execution_time_seconds) as avg_execution_time
                FROM client_automations ca
                LEFT JOIN automation_templates at ON ca.template_id = at.id
                LEFT JOIN automation_rules ar ON ca.id = ar.automation_id
                LEFT JOIN automation_executions ae ON ca.id = ae.automation_id
                WHERE ca.client_id = ? OR ca.target_group = 'all'
                GROUP BY ca.id
                ORDER BY ca.priority DESC, ca.created_at DESC
            ''', (client_id,)).fetchall()
            
            # Flujos de trabajo dinámicos y triggers
            workflow_analysis = conn.execute('''
                SELECT 
                    aw.workflow_name,
                    aw.trigger_type,
                    aw.trigger_conditions,
                    COUNT(awe.id) as workflow_executions,
                    AVG(awe.success_rate) as avg_success_rate,
                    SUM(awe.actions_completed) as total_actions_completed,
                    AVG(awe.total_execution_time_minutes) as avg_total_time,
                    STRING_AGG(DISTINCT awe.failure_reason, ' | ') as common_failures
                FROM automation_workflows aw
                LEFT JOIN automation_workflow_executions awe ON aw.id = awe.workflow_id
                WHERE aw.client_id = ? OR aw.applies_to_all_clients = 1
                GROUP BY aw.id, aw.workflow_name
                ORDER BY workflow_executions DESC
            ''', (client_id,)).fetchall()
            
            # Análisis de patrones y aprendizaje automático
            pattern_learning = conn.execute('''
                SELECT 
                    ap.pattern_name,
                    ap.pattern_conditions,
                    ap.confidence_score,
                    ap.times_detected,
                    ap.suggested_automation,
                    ap.potential_savings_hours,
                    ap.last_detected_at,
                    COUNT(apa.id) as automation_applications
                FROM automation_patterns ap
                LEFT JOIN automation_pattern_applications apa ON ap.id = apa.pattern_id
                WHERE ap.client_id = ? OR ap.applies_globally = 1
                GROUP BY ap.id
                ORDER BY ap.confidence_score DESC, ap.times_detected DESC
            ''', (client_id,)).fetchall()
            
            # Ejecuciones recientes con detalles de resultado
            recent_executions = conn.execute('''
                SELECT 
                    ae.*,
                    ca.automation_name,
                    aer.step_name,
                    aer.step_result,
                    aer.execution_details,
                    aer.error_message
                FROM automation_executions ae
                LEFT JOIN client_automations ca ON ae.automation_id = ca.id
                LEFT JOIN automation_execution_results aer ON ae.id = aer.execution_id
                WHERE ae.client_id = ?
                ORDER BY ae.execution_date DESC
                LIMIT 20
            ''', (client_id,)).fetchall()
            
            # Análisis de impacto y ROI de automatizaciones
            impact_analysis = conn.execute('''
                SELECT 
                    ca.automation_name,
                    SUM(ai.time_saved_minutes) as total_time_saved,
                    SUM(ai.cost_savings_amount) as total_cost_savings,
                    AVG(ai.error_reduction_percentage) as avg_error_reduction,
                    SUM(ai.tasks_automated) as total_tasks_automated,
                    AVG(ai.user_satisfaction_score) as avg_satisfaction
                FROM client_automations ca
                LEFT JOIN automation_impact ai ON ca.id = ai.automation_id
                WHERE ca.client_id = ? OR ca.target_group = 'all'
                GROUP BY ca.id, ca.automation_name
                ORDER BY total_cost_savings DESC
            ''', (client_id,)).fetchall()
            
            # Integraciones con otros módulos del ERP
            module_integrations = conn.execute('''
                SELECT 
                    ami.module_name,
                    ami.integration_type,
                    COUNT(amie.id) as integration_calls,
                    AVG(amie.response_time_ms) as avg_response_time,
                    SUM(CASE WHEN amie.status = 'success' THEN 1 ELSE 0 END) as successful_calls,
                    STRING_AGG(DISTINCT amie.data_exchanged_summary, ' | ') as data_types
                FROM automation_module_integrations ami
                LEFT JOIN automation_module_integration_executions amie ON ami.id = amie.integration_id
                WHERE ami.client_id = ? OR ami.applies_to_all = 1
                GROUP BY ami.id, ami.module_name
                ORDER BY integration_calls DESC
            ''', (client_id,)).fetchall()
            
            # Recomendaciones de nuevas automatizaciones basadas en IA
            ai_recommendations = conn.execute('''
                SELECT 
                    aar.recommendation_type,
                    aar.suggested_automation_name,
                    aar.description,
                    aar.estimated_time_savings_hours,
                    aar.implementation_complexity,
                    aar.confidence_score,
                    aar.based_on_patterns,
                    aar.generated_at
                FROM ai_automation_recommendations aar
                WHERE aar.client_id = ? AND aar.status = 'pending'
                ORDER BY aar.confidence_score DESC, aar.estimated_time_savings_hours DESC
                LIMIT 10
            ''', (client_id,)).fetchall()
            
            # Análisis de dependencias entre automatizaciones
            dependency_analysis = conn.execute('''
                SELECT 
                    ca1.automation_name as source_automation,
                    ca2.automation_name as dependent_automation,
                    ad.dependency_type,
                    ad.trigger_condition,
                    COUNT(ade.id) as dependency_executions,
                    AVG(ade.success_rate) as dependency_success_rate
                FROM automation_dependencies ad
                LEFT JOIN client_automations ca1 ON ad.source_automation_id = ca1.id
                LEFT JOIN client_automations ca2 ON ad.dependent_automation_id = ca2.id
                LEFT JOIN automation_dependency_executions ade ON ad.id = ade.dependency_id
                WHERE ca1.client_id = ? OR ca2.client_id = ?
                GROUP BY ad.id
                ORDER BY dependency_executions DESC
            ''', (client_id, client_id)).fetchall()
            
            conn.close()
            
            return {
                'active_automations': [dict(auto) for auto in automations],
                'workflow_analysis': [dict(workflow) for workflow in workflow_analysis],
                'pattern_learning': [dict(pattern) for pattern in pattern_learning],
                'recent_executions': [dict(exec) for exec in recent_executions],
                'impact_analysis': [dict(impact) for impact in impact_analysis],
                'module_integrations': [dict(integration) for integration in module_integrations],
                'ai_recommendations': [dict(rec) for rec in ai_recommendations],
                'dependency_analysis': [dict(dep) for dep in dependency_analysis],
                'total_automations': len(automations),
                'automation_effectiveness': self._calculate_automation_effectiveness_advanced(impact_analysis),
                'learning_insights': self._generate_learning_insights(pattern_learning),
                'optimization_opportunities': self._identify_optimization_opportunities(workflow_analysis),
                'intelligence_score': self._calculate_erp_intelligence_score(pattern_learning, ai_recommendations)
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo automatizaciones del cliente {client_id}: {str(e)}")
            return {}
    
    # ==========================================================================
    # MÉTODOS DE FORMATEO PARA AI
    # ==========================================================================
    
    def _format_summary_for_ai(self, summary: Dict[str, Any]) -> str:
        """Formatear resumen ejecutivo para AI"""
        if not summary:
            return "No hay resumen disponible."
        
        return f"""
Estado del cliente: {summary.get('client_status', 'Desconocido')}
Valor total del pipeline: ${summary.get('total_pipeline_value', 0):,.2f}
Tickets abiertos: {summary.get('open_tickets', 0)}
Última interacción: {summary.get('last_interaction', 'N/A')}
Puntuación de satisfacción: {summary.get('satisfaction_score', 'N/A')}/10
Oportunidades activas: {summary.get('active_opportunities', 0)}
"""
    
    def _format_basic_info_for_ai(self, basic_info: Dict[str, Any]) -> str:
        """Formatear información básica para AI"""
        if not basic_info:
            return "No hay información básica disponible."
        
        formatted = f"Empresa: {basic_info.get('nombre_empresa', 'N/A')}\n"
        if basic_info.get('nif_cif'):
            formatted += f"NIF/CIF: {basic_info['nif_cif']}\n"
        if basic_info.get('emails'):
            formatted += f"Email: {basic_info['emails']}\n"
        if basic_info.get('telefonos'):
            formatted += f"Teléfono: {basic_info['telefonos']}\n"
        if basic_info.get('sector'):
            formatted += f"Sector: {basic_info['sector']}\n"
        if basic_info.get('estado'):
            formatted += f"Estado: {basic_info['estado']}\n"
        
        return formatted
    
    def _format_pipeline_for_ai(self, pipeline_data: Dict[str, Any]) -> str:
        """Formatear pipeline para AI"""
        if not pipeline_data or not pipeline_data.get('opportunities'):
            return "No hay oportunidades activas en el pipeline."
        
        formatted = f"Total de oportunidades: {pipeline_data.get('total_opportunities', 0)}\n"
        
        if pipeline_data.get('statistics'):
            formatted += "Distribución por etapa:\n"
            for stat in pipeline_data['statistics']:
                formatted += f"  - {stat.get('stage', 'N/A')}: {stat.get('count', 0)} oportunidades (${stat.get('total_value', 0):,.2f})\n"
        
        # Oportunidades más importantes
        opportunities = pipeline_data.get('opportunities', [])[:5]
        if opportunities:
            formatted += "\nOportunidades principales:\n"
            for opp in opportunities:
                formatted += f"  - {opp.get('title', 'Sin título')}: ${opp.get('estimated_value', 0):,.2f} ({opp.get('stage', 'N/A')})\n"
        
        return formatted
    
    def _format_proposals_for_ai(self, proposals_data: Dict[str, Any]) -> str:
        """Formatear propuestas para AI"""
        if not proposals_data or not proposals_data.get('recent_proposals'):
            return "No hay propuestas recientes."
        
        proposals = proposals_data.get('recent_proposals', [])[:5]
        formatted = f"Propuestas recientes ({len(proposals)}):\n"
        
        for prop in proposals:
            formatted += f"  - {prop.get('title', 'Sin título')}: ${prop.get('total_amount', 0):,.2f} ({prop.get('status', 'N/A')})\n"
        
        if proposals_data.get('conversion_rate'):
            formatted += f"\nTasa de conversión: {proposals_data['conversion_rate']:.1f}%\n"
        
        return formatted
    
    def _format_communications_for_ai(self, communications_data: Dict[str, Any]) -> str:
        """Formatear comunicaciones para AI"""
        if not communications_data or not communications_data.get('recent_communications'):
            return "No hay comunicaciones recientes."
        
        communications = communications_data.get('recent_communications', [])[:5]
        formatted = f"Comunicaciones recientes ({len(communications)}):\n"
        
        for comm in communications:
            formatted += f"  - {comm.get('subject', 'Sin asunto')} ({comm.get('communication_type', 'N/A')}) - {comm.get('created_at', 'N/A')}\n"
        
        if communications_data.get('last_contact_date'):
            formatted += f"\nÚltimo contacto: {communications_data['last_contact_date']}\n"
        
        return formatted
    
    def _format_campaigns_for_ai(self, campaigns_data: Dict[str, Any]) -> str:
        """Formatear campañas para AI"""
        if not campaigns_data or not campaigns_data.get('active_campaigns'):
            return "No participa en campañas activas."
        
        campaigns = campaigns_data.get('active_campaigns', [])[:3]
        formatted = f"Campañas activas ({len(campaigns)}):\n"
        
        for camp in campaigns:
            formatted += f"  - {camp.get('name', 'Sin nombre')}: {camp.get('status', 'N/A')}\n"
        
        if campaigns_data.get('engagement_summary'):
            formatted += f"\nEngagement promedio: {campaigns_data['engagement_summary'].get('avg_engagement', 0):.1f}%\n"
        
        return formatted
    
    def _format_tickets_for_ai(self, tickets_data: Dict[str, Any]) -> str:
        """Formatear tickets para AI"""
        if not tickets_data or not tickets_data.get('recent_tickets'):
            return "No hay tickets de soporte."
        
        tickets = tickets_data.get('recent_tickets', [])[:5]
        formatted = f"Tickets recientes ({len(tickets)}):\n"
        
        for ticket in tickets:
            formatted += f"  - {ticket.get('subject', 'Sin asunto')}: {ticket.get('status', 'N/A')} (Prioridad: {ticket.get('priority', 'N/A')})\n"
        
        if tickets_data.get('satisfaction_score'):
            formatted += f"\nPuntuación de satisfacción: {tickets_data['satisfaction_score']:.1f}/10\n"
        
        return formatted
    
    def _format_calendar_for_ai(self, calendar_data: Dict[str, Any]) -> str:
        """Formatear calendario para AI"""
        upcoming = calendar_data.get('upcoming_activities', [])
        past = calendar_data.get('past_activities', [])
        
        formatted = ""
        
        if upcoming:
            formatted += f"Próximas actividades ({len(upcoming)}):\n"
            for act in upcoming[:3]:
                formatted += f"  - {act.get('title', 'Sin título')}: {act.get('activity_date', 'N/A')}\n"
        
        if past:
            formatted += f"\nActividades recientes ({len(past)}):\n"
            for act in past[:3]:
                formatted += f"  - {act.get('title', 'Sin título')}: {act.get('activity_date', 'N/A')}\n"
        
        if not upcoming and not past:
            formatted = "No hay actividades programadas."
        
        return formatted
    
    def _format_timeline_for_ai(self, timeline_data: Dict[str, Any]) -> str:
        """Formatear timeline para AI"""
        events = timeline_data.get('recent_events', [])
        milestones = timeline_data.get('milestones', [])
        
        formatted = ""
        
        if milestones:
            formatted += f"Hitos importantes:\n"
            for milestone in milestones[:3]:
                formatted += f"  - {milestone.get('title', 'Sin título')}: {milestone.get('milestone_date', 'N/A')}\n"
        
        if events:
            formatted += f"\nEventos recientes ({len(events)}):\n"
            for event in events[:5]:
                formatted += f"  - {event.get('event_type', 'Evento')}: {event.get('description', 'N/A')} ({event.get('event_date', 'N/A')})\n"
        
        if timeline_data.get('relationship_duration'):
            formatted += f"\nDuración de la relación: {timeline_data['relationship_duration']} días\n"
        
        return formatted or "No hay eventos en el timeline."
    
    def _format_automations_for_ai(self, automations_data: Dict[str, Any]) -> str:
        """Formatear automatizaciones para AI"""
        automations = automations_data.get('active_automations', [])
        executions = automations_data.get('recent_executions', [])
        
        formatted = ""
        
        if automations:
            formatted += f"Automatizaciones activas ({len(automations)}):\n"
            for auto in automations[:3]:
                formatted += f"  - {auto.get('name', 'Sin nombre')}: {auto.get('status', 'N/A')}\n"
        
        if executions:
            formatted += f"\nEjecuciones recientes: {len(executions)}\n"
            if automations_data.get('automation_effectiveness'):
                formatted += f"Efectividad promedio: {automations_data['automation_effectiveness']:.1f}%\n"
        
        return formatted or "No hay automatizaciones configuradas."
    
    # ==========================================================================
    # MÉTODOS DE CÁLCULO AVANZADOS - PIPELINE KANBAN
    # ==========================================================================
    
    def _calculate_pipeline_health_advanced(self, opportunities: List[Dict], stage_stats: List[Dict]) -> str:
        """Calcular salud avanzada del pipeline Kanban"""
        if not opportunities or not stage_stats:
            return "Sin datos suficientes"
        
        try:
            total_value = sum(float(opp.get('estimated_value', 0)) for opp in opportunities)
            total_opportunities = len(opportunities)
            
            # Análisis de distribución por etapas
            stage_balance = len([s for s in stage_stats if s.get('opportunity_count', 0) > 0])
            total_stages = len(stage_stats)
            
            # Tiempo promedio en etapas
            avg_days_in_stage = sum(float(s.get('avg_days_in_stage', 0)) for s in stage_stats) / len(stage_stats) if stage_stats else 0
            
            # Criterios de salud
            health_score = 0
            
            if total_value > 100000:
                health_score += 30
            elif total_value > 50000:
                health_score += 20
            elif total_value > 20000:
                health_score += 10
            
            if total_opportunities >= 5:
                health_score += 20
            elif total_opportunities >= 3:
                health_score += 10
            
            if stage_balance >= total_stages * 0.6:
                health_score += 25
            elif stage_balance >= total_stages * 0.4:
                health_score += 15
            
            if avg_days_in_stage <= 14:
                health_score += 25
            elif avg_days_in_stage <= 30:
                health_score += 15
            
            if health_score >= 80:
                return "Excelente"
            elif health_score >= 60:
                return "Buena"
            elif health_score >= 40:
                return "Regular"
            else:
                return "Necesita atención"
                
        except Exception as e:
            logger.error(f"Error calculando salud del pipeline: {str(e)}")
            return "Error en cálculo"
    
    def _analyze_stage_conversions(self, stage_movements: List[Dict]) -> Dict[str, float]:
        """Analizar conversiones entre etapas del pipeline"""
        if not stage_movements:
            return {'overall_conversion': 0.0}
        
        try:
            conversions = {}
            stage_flows = {}
            
            for movement in stage_movements:
                from_stage = movement.get('from_stage')
                to_stage = movement.get('to_stage')
                
                if from_stage and to_stage:
                    flow_key = f"{from_stage} → {to_stage}"
                    stage_flows[flow_key] = stage_flows.get(flow_key, 0) + 1
                    
                    if from_stage not in conversions:
                        conversions[from_stage] = {'total': 0, 'forward': 0}
                    
                    conversions[from_stage]['total'] += 1
                    # Asumir que movimientos hacia etapas posteriores son conversiones positivas
                    if to_stage != from_stage:
                        conversions[from_stage]['forward'] += 1
            
            # Calcular tasas de conversión por etapa
            conversion_rates = {}
            for stage, data in conversions.items():
                if data['total'] > 0:
                    conversion_rates[stage] = (data['forward'] / data['total']) * 100
            
            overall_conversion = sum(conversion_rates.values()) / len(conversion_rates) if conversion_rates else 0.0
            
            return {
                'overall_conversion': overall_conversion,
                'stage_conversions': conversion_rates,
                'most_common_flows': dict(sorted(stage_flows.items(), key=lambda x: x[1], reverse=True)[:5])
            }
            
        except Exception as e:
            logger.error(f"Error analizando conversiones de etapas: {str(e)}")
            return {'overall_conversion': 0.0}
    
    # ==========================================================================
    # MÉTODOS DE CÁLCULO AVANZADOS - COMUNICACIONES MULTICANAL
    # ==========================================================================
    
    def _identify_preferred_channel(self, channel_stats: List[Dict]) -> str:
        """Identificar canal preferido basado en estadísticas"""
        if not channel_stats:
            return "Sin datos"
        
        try:
            best_channel = max(channel_stats, key=lambda x: (
                x.get('message_count', 0) * 0.4 +
                (10 - x.get('avg_response_time', 10)) * 0.3 +
                x.get('avg_sentiment', 0) * 0.3
            ))
            
            return best_channel.get('channel_name', 'Desconocido')
            
        except Exception as e:
            logger.error(f"Error identificando canal preferido: {str(e)}")
            return "Error en análisis"
    
    def _analyze_communication_patterns(self, communications: List[Dict]) -> Dict[str, Any]:
        """Analizar patrones de comunicación"""
        if not communications:
            return {}
        
        try:
            # Análisis temporal
            hours = {}
            days = {}
            channels = {}
            
            for comm in communications:
                created_at = comm.get('created_at', '')
                channel = comm.get('channel_name', 'unknown')
                
                if created_at:
                    try:
                        dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                        hour = dt.hour
                        day = dt.strftime('%A')
                        
                        hours[hour] = hours.get(hour, 0) + 1
                        days[day] = days.get(day, 0) + 1
                        channels[channel] = channels.get(channel, 0) + 1
                    except:
                        continue
            
            return {
                'peak_hours': dict(sorted(hours.items(), key=lambda x: x[1], reverse=True)[:3]),
                'peak_days': dict(sorted(days.items(), key=lambda x: x[1], reverse=True)[:3]),
                'channel_distribution': channels,
                'communication_frequency': len(communications)
            }
            
        except Exception as e:
            logger.error(f"Error analizando patrones de comunicación: {str(e)}")
            return {}
    
    def _calculate_engagement_score(self, communications: List[Dict]) -> float:
        """Calcular puntuación de engagement"""
        if not communications:
            return 0.0
        
        try:
            total_score = 0
            scored_communications = 0
            
            for comm in communications:
                engagement = comm.get('engagement_score', 0)
                response_time = comm.get('response_time_minutes', 0)
                sentiment = comm.get('sentiment_score', 0)
                
                if engagement or response_time or sentiment:
                    score = (
                        engagement * 0.5 +
                        (10 - min(response_time / 60, 10)) * 0.3 +  # Penalizar respuestas lentas
                        max(sentiment, 0) * 0.2  # Solo contar sentimiento positivo
                    )
                    total_score += score
                    scored_communications += 1
            
            return total_score / scored_communications if scored_communications > 0 else 0.0
            
        except Exception as e:
            logger.error(f"Error calculando engagement score: {str(e)}")
            return 0.0
    
    # ==========================================================================
    # MÉTODOS DE CÁLCULO AVANZADOS - PROPUESTAS CON PLANTILLAS
    # ==========================================================================
    
    def _calculate_proposal_conversion_advanced(self, proposals: List[Dict]) -> Dict[str, float]:
        """Calcular conversión avanzada de propuestas"""
        if not proposals:
            return {'overall_rate': 0.0}
        
        try:
            total = len(proposals)
            accepted = sum(1 for prop in proposals if prop.get('status') == 'accepted')
            in_progress = sum(1 for prop in proposals if prop.get('status') in ['pending', 'under_review'])
            rejected = sum(1 for prop in proposals if prop.get('status') in ['rejected', 'cancelled'])
            
            return {
                'overall_rate': (accepted / total) * 100 if total > 0 else 0.0,
                'acceptance_rate': (accepted / total) * 100 if total > 0 else 0.0,
                'pending_rate': (in_progress / total) * 100 if total > 0 else 0.0,
                'rejection_rate': (rejected / total) * 100 if total > 0 else 0.0,
                'total_proposals': total,
                'accepted_count': accepted
            }
            
        except Exception as e:
            logger.error(f"Error calculando conversión de propuestas: {str(e)}")
            return {'overall_rate': 0.0}
    
    def _identify_best_template(self, template_stats: List[Dict]) -> str:
        """Identificar la plantilla más efectiva"""
        if not template_stats:
            return "Sin datos"
        
        try:
            best_template = max(template_stats, key=lambda x: (
                (x.get('accepted_count', 0) / max(x.get('proposal_count', 1), 1)) * 0.6 +
                x.get('total_accepted_value', 0) / 10000 * 0.4
            ))
            
            return best_template.get('template_name', 'Desconocido')
            
        except Exception as e:
            logger.error(f"Error identificando mejor plantilla: {str(e)}")
            return "Error en análisis"
    
    def _analyze_variable_patterns(self, variable_usage: List[Dict]) -> Dict[str, Any]:
        """Analizar patrones de uso de variables {{variable}}"""
        if not variable_usage:
            return {}
        
        try:
            variable_frequency = {}
            variable_success = {}
            
            for usage in variable_usage:
                var_name = usage.get('variable_name')
                status = usage.get('status')
                
                if var_name:
                    variable_frequency[var_name] = variable_frequency.get(var_name, 0) + 1
                    
                    if var_name not in variable_success:
                        variable_success[var_name] = {'total': 0, 'accepted': 0}
                    
                    variable_success[var_name]['total'] += 1
                    if status == 'accepted':
                        variable_success[var_name]['accepted'] += 1
            
            # Calcular success rates
            success_rates = {}
            for var, data in variable_success.items():
                if data['total'] > 0:
                    success_rates[var] = (data['accepted'] / data['total']) * 100
            
            return {
                'most_used_variables': dict(sorted(variable_frequency.items(), key=lambda x: x[1], reverse=True)[:10]),
                'success_rates': success_rates,
                'total_variables_used': len(variable_frequency)
            }
            
        except Exception as e:
            logger.error(f"Error analizando patrones de variables: {str(e)}")
            return {}
    
    def _generate_pricing_insights(self, proposals: List[Dict]) -> Dict[str, Any]:
        """Generar insights de pricing"""
        if not proposals:
            return {}
        
        try:
            amounts = [float(prop.get('total_amount', 0)) for prop in proposals if prop.get('total_amount')]
            
            if not amounts:
                return {}
            
            avg_amount = sum(amounts) / len(amounts)
            min_amount = min(amounts)
            max_amount = max(amounts)
            
            accepted_amounts = [
                float(prop.get('total_amount', 0)) 
                for prop in proposals 
                if prop.get('status') == 'accepted' and prop.get('total_amount')
            ]
            
            sweet_spot = sum(accepted_amounts) / len(accepted_amounts) if accepted_amounts else avg_amount
            
            return {
                'average_proposal_value': avg_amount,
                'min_proposal_value': min_amount,
                'max_proposal_value': max_amount,
                'sweet_spot_value': sweet_spot,
                'total_proposed_value': sum(amounts),
                'value_range_analysis': {
                    'low': len([a for a in amounts if a < avg_amount * 0.7]),
                    'medium': len([a for a in amounts if avg_amount * 0.7 <= a <= avg_amount * 1.3]),
                    'high': len([a for a in amounts if a > avg_amount * 1.3])
                }
            }
            
        except Exception as e:
            logger.error(f"Error generando insights de pricing: {str(e)}")
            return {}
    
    # ==========================================================================
    # MÉTODOS DE CÁLCULO AVANZADOS - CAMPAÑAS MULTICANAL
    # ==========================================================================
    
    def _identify_best_channel(self, channel_metrics: List[Dict]) -> str:
        """Identificar mejor canal de campaña"""
        if not channel_metrics:
            return "Sin datos"
        
        try:
            best_channel = max(channel_metrics, key=lambda x: (
                x.get('conversion_rate', 0) * 0.4 +
                x.get('avg_engagement_rate', 0) * 0.3 +
                (x.get('total_conversions', 0) / max(x.get('total_cost', 1), 1)) * 0.3
            ))
            
            return best_channel.get('channel_name', 'Desconocido')
            
        except Exception as e:
            logger.error(f"Error identificando mejor canal: {str(e)}")
            return "Error en análisis"
    
    def _analyze_personalization_impact(self, campaign_variables: List[Dict]) -> Dict[str, float]:
        """Analizar impacto de personalización"""
        if not campaign_variables:
            return {'impact_score': 0.0}
        
        try:
            personalized_campaigns = []
            non_personalized_campaigns = []
            
            for var in campaign_variables:
                engagement = var.get('engagement_rate', 0)
                conversions = var.get('conversions', 0)
                
                if var.get('variable_value'):  # Tiene personalización
                    personalized_campaigns.append({'engagement': engagement, 'conversions': conversions})
                else:
                    non_personalized_campaigns.append({'engagement': engagement, 'conversions': conversions})
            
            if personalized_campaigns and non_personalized_campaigns:
                avg_personalized_engagement = sum(c['engagement'] for c in personalized_campaigns) / len(personalized_campaigns)
                avg_non_personalized_engagement = sum(c['engagement'] for c in non_personalized_campaigns) / len(non_personalized_campaigns)
                
                improvement = ((avg_personalized_engagement - avg_non_personalized_engagement) / max(avg_non_personalized_engagement, 0.1)) * 100
                
                return {
                    'impact_score': improvement,
                    'personalized_avg_engagement': avg_personalized_engagement,
                    'non_personalized_avg_engagement': avg_non_personalized_engagement
                }
            
            return {'impact_score': 0.0}
            
        except Exception as e:
            logger.error(f"Error analizando impacto de personalización: {str(e)}")
            return {'impact_score': 0.0}
    
    def _generate_campaign_recommendations(self, channel_metrics: List[Dict], sector_performance: List[Dict]) -> List[str]:
        """Generar recomendaciones de campaña"""
        recommendations = []
        
        try:
            if channel_metrics:
                best_channel = self._identify_best_channel(channel_metrics)
                if best_channel != "Sin datos":
                    recommendations.append(f"Enfocar más recursos en el canal {best_channel} que muestra mejor rendimiento")
                
                low_performing = [c for c in channel_metrics if c.get('conversion_rate', 0) < 2.0]
                if low_performing:
                    recommendations.append(f"Revisar estrategia en {len(low_performing)} canales con baja conversión")
            
            if sector_performance:
                high_engagement = [s for s in sector_performance if s.get('avg_engagement', 0) > 5.0]
                if high_engagement:
                    recommendations.append("Aumentar inversión en sectores con alto engagement")
            
            return recommendations[:5]  # Máximo 5 recomendaciones
            
        except Exception as e:
            logger.error(f"Error generando recomendaciones: {str(e)}")
            return ["Error generando recomendaciones"]
    
    # ==========================================================================
    # MÉTODOS DE CÁLCULO AVANZADOS - TICKETS, CALENDARIO, AUTOMATIZACIONES, TIMELINE
    # ==========================================================================
    
    def _calculate_overall_sla_compliance(self, sla_performance: List[Dict]) -> float:
        """Calcular cumplimiento general de SLA"""
        if not sla_performance:
            return 0.0
        
        try:
            total_tickets = sum(p.get('total_tickets', 0) for p in sla_performance)
            total_within_sla = sum(p.get('within_sla', 0) for p in sla_performance)
            
            return (total_within_sla / total_tickets) * 100 if total_tickets > 0 else 0.0
            
        except Exception as e:
            logger.error(f"Error calculando SLA compliance: {str(e)}")
            return 0.0
    
    def _calculate_escalation_rate(self, tickets: List[Dict], escalation_analysis: List[Dict]) -> float:
        """Calcular tasa de escalación"""
        if not tickets:
            return 0.0
        
        try:
            total_tickets = len(tickets)
            escalated_tickets = sum(e.get('escalation_count', 0) for e in escalation_analysis)
            
            return (escalated_tickets / total_tickets) * 100 if total_tickets > 0 else 0.0
            
        except Exception as e:
            logger.error(f"Error calculando tasa de escalación: {str(e)}")
            return 0.0
    
    def _calculate_support_satisfaction_advanced(self, satisfaction_analysis: List[Dict]) -> float:
        """Calcular satisfacción avanzada de soporte"""
        if not satisfaction_analysis:
            return 0.0
        
        try:
            total_satisfaction = 0
            count = 0
            
            for analysis in satisfaction_analysis:
                avg_satisfaction = analysis.get('avg_satisfaction', 0)
                avg_overall_rating = analysis.get('avg_overall_rating', 0)
                
                if avg_satisfaction or avg_overall_rating:
                    combined_score = (avg_satisfaction * 0.6 + avg_overall_rating * 0.4)
                    total_satisfaction += combined_score
                    count += 1
            
            return total_satisfaction / count if count > 0 else 0.0
            
        except Exception as e:
            logger.error(f"Error calculando satisfacción de soporte: {str(e)}")
            return 0.0
    
    def _analyze_ticket_trends(self, tickets: List[Dict]) -> Dict[str, Any]:
        """Analizar tendencias de tickets"""
        if not tickets:
            return {}
        
        try:
            # Análisis temporal
            monthly_counts = {}
            category_trends = {}
            
            for ticket in tickets:
                created_at = ticket.get('created_at', '')
                category = ticket.get('category_name', 'Sin categoría')
                
                if created_at:
                    try:
                        dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                        month_key = dt.strftime('%Y-%m')
                        
                        monthly_counts[month_key] = monthly_counts.get(month_key, 0) + 1
                        category_trends[category] = category_trends.get(category, 0) + 1
                    except:
                        continue
            
            return {
                'monthly_distribution': monthly_counts,
                'category_distribution': category_trends,
                'trend_direction': self._calculate_trend_direction(monthly_counts)
            }
            
        except Exception as e:
            logger.error(f"Error analizando tendencias de tickets: {str(e)}")
            return {}
    
    def _generate_support_recommendations(self, sla_performance: List[Dict], problem_patterns: List[Dict]) -> List[str]:
        """Generar recomendaciones de soporte"""
        recommendations = []
        
        try:
            # Análisis de SLA
            low_sla = [s for s in sla_performance if s.get('sla_compliance_rate', 0) < 80]
            if low_sla:
                recommendations.append(f"Mejorar SLA en {len(low_sla)} categorías con bajo cumplimiento")
            
            # Patrones de problemas recurrentes
            frequent_problems = [p for p in problem_patterns if p.get('occurrence_count', 0) >= 3]
            if frequent_problems:
                recommendations.append("Crear documentación para problemas recurrentes más comunes")
            
            return recommendations[:5]
            
        except Exception as e:
            logger.error(f"Error generando recomendaciones de soporte: {str(e)}")
            return []
    
    def _assess_calendar_integration_health(self, external_sync_status: List[Dict]) -> str:
        """Evaluar salud de integraciones de calendario"""
        if not external_sync_status:
            return "Sin integraciones"
        
        try:
            healthy_integrations = sum(1 for s in external_sync_status if s.get('sync_status') == 'active' and s.get('sync_errors_count', 0) < 3)
            total_integrations = len(external_sync_status)
            
            health_ratio = healthy_integrations / total_integrations
            
            if health_ratio >= 0.9:
                return "Excelente"
            elif health_ratio >= 0.7:
                return "Buena"
            elif health_ratio >= 0.5:
                return "Regular"
            else:
                return "Necesita atención"
                
        except Exception as e:
            logger.error(f"Error evaluando salud de integraciones: {str(e)}")
            return "Error en evaluación"
    
    def _calculate_meeting_effectiveness(self, meeting_patterns: List[Dict]) -> float:
        """Calcular efectividad promedio de reuniones"""
        if not meeting_patterns:
            return 0.0
        
        try:
            total_effectiveness = sum(p.get('avg_effectiveness', 0) for p in meeting_patterns)
            count = len([p for p in meeting_patterns if p.get('avg_effectiveness', 0) > 0])
            
            return total_effectiveness / count if count > 0 else 0.0
            
        except Exception as e:
            logger.error(f"Error calculando efectividad de reuniones: {str(e)}")
            return 0.0
    
    def _analyze_time_utilization(self, productivity_analysis: List[Dict]) -> Dict[str, float]:
        """Analizar utilización del tiempo"""
        if not productivity_analysis:
            return {}
        
        try:
            total_meeting_time = sum(p.get('total_meeting_time', 0) for p in productivity_analysis)
            total_days = len(productivity_analysis)
            avg_effectiveness = sum(p.get('avg_effectiveness', 0) for p in productivity_analysis) / total_days if total_days > 0 else 0
            
            return {
                'avg_daily_meeting_time': total_meeting_time / total_days if total_days > 0 else 0,
                'avg_effectiveness': avg_effectiveness,
                'productivity_score': (avg_effectiveness / 10) * 100  # Normalizar a 100
            }
            
        except Exception as e:
            logger.error(f"Error analizando utilización del tiempo: {str(e)}")
            return {}
    
    def _generate_scheduling_recommendations(self, availability_analysis: List[Dict], meeting_patterns: List[Dict]) -> List[str]:
        """Generar recomendaciones de programación"""
        recommendations = []
        
        try:
            if availability_analysis:
                overloaded_users = [a for a in availability_analysis if a.get('total_scheduled_minutes', 0) > 480]  # Más de 8 horas
                if overloaded_users:
                    recommendations.append(f"{len(overloaded_users)} usuarios con sobrecarga de reuniones")
                
                conflicted_meetings = sum(a.get('conflicted_meetings', 0) for a in availability_analysis)
                if conflicted_meetings > 0:
                    recommendations.append(f"Resolver {conflicted_meetings} conflictos de horarios detectados")
            
            if meeting_patterns:
                ineffective_types = [m for m in meeting_patterns if m.get('avg_effectiveness', 0) < 5]
                if ineffective_types:
                    recommendations.append("Revisar formato de reuniones con baja efectividad")
            
            return recommendations[:5]
            
        except Exception as e:
            logger.error(f"Error generando recomendaciones de programación: {str(e)}")
            return []
    
    def _calculate_automation_effectiveness_advanced(self, impact_analysis: List[Dict]) -> float:
        """Calcular efectividad avanzada de automatizaciones"""
        if not impact_analysis:
            return 0.0
        
        try:
            total_score = 0
            count = 0
            
            for analysis in impact_analysis:
                time_saved = analysis.get('total_time_saved', 0)
                cost_savings = analysis.get('total_cost_savings', 0)
                satisfaction = analysis.get('avg_satisfaction', 0)
                
                # Score compuesto
                effectiveness_score = (
                    min(time_saved / 100, 10) * 0.4 +  # Time savings (normalizado)
                    min(cost_savings / 1000, 10) * 0.4 +  # Cost savings (normalizado)
                    satisfaction * 0.2
                )
                
                total_score += effectiveness_score
                count += 1
            
            return (total_score / count) * 10 if count > 0 else 0.0  # Escalar a 100
            
        except Exception as e:
            logger.error(f"Error calculando efectividad de automatizaciones: {str(e)}")
            return 0.0
    
    def _generate_learning_insights(self, pattern_learning: List[Dict]) -> List[str]:
        """Generar insights de aprendizaje"""
        insights = []
        
        try:
            if pattern_learning:
                high_confidence = [p for p in pattern_learning if p.get('confidence_score', 0) > 0.8]
                if high_confidence:
                    insights.append(f"{len(high_confidence)} patrones detectados con alta confianza")
                
                high_savings = [p for p in pattern_learning if p.get('potential_savings_hours', 0) > 10]
                if high_savings:
                    insights.append(f"Potencial de ahorro de {sum(p.get('potential_savings_hours', 0) for p in high_savings)} horas")
            
            return insights[:5]
            
        except Exception as e:
            logger.error(f"Error generando insights de aprendizaje: {str(e)}")
            return []
    
    def _identify_optimization_opportunities(self, workflow_analysis: List[Dict]) -> List[str]:
        """Identificar oportunidades de optimización"""
        opportunities = []
        
        try:
            if workflow_analysis:
                low_success = [w for w in workflow_analysis if w.get('avg_success_rate', 0) < 0.8]
                if low_success:
                    opportunities.append(f"Optimizar {len(low_success)} flujos con baja tasa de éxito")
                
                slow_workflows = [w for w in workflow_analysis if w.get('avg_total_time_minutes', 0) > 60]
                if slow_workflows:
                    opportunities.append(f"Acelerar {len(slow_workflows)} flujos lentos")
            
            return opportunities[:5]
            
        except Exception as e:
            logger.error(f"Error identificando oportunidades: {str(e)}")
            return []
    
    def _calculate_erp_intelligence_score(self, pattern_learning: List[Dict], ai_recommendations: List[Dict]) -> float:
        """Calcular puntuación de inteligencia del ERP"""
        try:
            patterns_score = len(pattern_learning) * 10  # 10 puntos por patrón detectado
            recommendations_score = len(ai_recommendations) * 15  # 15 puntos por recomendación AI
            
            # Bonus por confianza alta
            high_confidence_bonus = sum(10 for p in pattern_learning if p.get('confidence_score', 0) > 0.9)
            
            total_score = patterns_score + recommendations_score + high_confidence_bonus
            
            return min(total_score, 100)  # Máximo 100 puntos
            
        except Exception as e:
            logger.error(f"Error calculando ERP intelligence score: {str(e)}")
            return 0.0
    
    def _calculate_relationship_duration_advanced(self, timeline_events: List[Dict]) -> Dict[str, Any]:
        """Calcular duración avanzada de relación"""
        if not timeline_events:
            return {'days': 0, 'months': 0, 'years': 0}
        
        try:
            # Obtener fecha más antigua
            oldest_event = min(timeline_events, key=lambda x: x.get('event_date', '9999-12-31'))
            oldest_date_str = oldest_event.get('event_date')
            
            if not oldest_date_str:
                return {'days': 0, 'months': 0, 'years': 0}
            
            oldest_date = datetime.fromisoformat(oldest_date_str.replace('Z', '+00:00'))
            duration = datetime.now() - oldest_date.replace(tzinfo=None)
            
            days = duration.days
            months = days // 30
            years = days // 365
            
            return {
                'days': days,
                'months': months,
                'years': years,
                'relationship_maturity': 'Nuevo' if days < 90 else 'Establecido' if days < 365 else 'Maduro'
            }
            
        except Exception as e:
            logger.error(f"Error calculando duración de relación: {str(e)}")
            return {'days': 0, 'months': 0, 'years': 0}
    
    def _analyze_engagement_trends(self, momentum_analysis: List[Dict]) -> Dict[str, Any]:
        """Analizar tendencias de engagement"""
        if not momentum_analysis:
            return {}
        
        try:
            # Calcular tendencia general
            activities = []
            sentiments = []
            
            for momentum in momentum_analysis:
                activities.append(momentum.get('daily_activity_count', 0))
                if momentum.get('daily_sentiment'):
                    sentiments.append(momentum.get('daily_sentiment', 0))
            
            if len(activities) >= 2:
                activity_trend = 'Creciente' if activities[0] > activities[-1] else 'Decreciente' if activities[0] < activities[-1] else 'Estable'
            else:
                activity_trend = 'Sin datos suficientes'
            
            avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0
            
            return {
                'activity_trend': activity_trend,
                'avg_sentiment': avg_sentiment,
                'sentiment_classification': 'Positivo' if avg_sentiment > 0 else 'Negativo' if avg_sentiment < 0 else 'Neutral',
                'engagement_level': 'Alto' if sum(activities) > len(activities) * 5 else 'Medio' if sum(activities) > len(activities) * 2 else 'Bajo'
            }
            
        except Exception as e:
            logger.error(f"Error analizando tendencias de engagement: {str(e)}")
            return {}
    
    def _calculate_business_impact_score(self, event_correlations: List[Dict]) -> float:
        """Calcular puntuación de impacto de negocio"""
        if not event_correlations:
            return 0.0
        
        try:
            total_impact = 0
            
            for correlation in event_correlations:
                proposals = correlation.get('proposals_generated', 0)
                avg_value = correlation.get('avg_proposal_value_after', 0)
                
                impact = (proposals * 0.6 + min(avg_value / 10000, 10) * 0.4)
                total_impact += impact
            
            return min(total_impact, 100)  # Normalizar a 100
            
        except Exception as e:
            logger.error(f"Error calculando impacto de negocio: {str(e)}")
            return 0.0
    
    def _evaluate_prediction_accuracy(self, predictive_insights: List[Dict]) -> float:
        """Evaluar precisión de predicciones"""
        if not predictive_insights:
            return 0.0
        
        try:
            total_confidence = sum(p.get('confidence_percentage', 0) for p in predictive_insights)
            count = len(predictive_insights)
            
            return total_confidence / count if count > 0 else 0.0
            
        except Exception as e:
            logger.error(f"Error evaluando precisión de predicciones: {str(e)}")
            return 0.0
    
    def _calculate_timeline_health_score(self, timeline_events: List[Dict], momentum_analysis: List[Dict]) -> float:
        """Calcular puntuación de salud del timeline"""
        try:
            # Factores de salud
            activity_score = min(len(timeline_events), 20) * 2  # Máximo 40 puntos por actividad
            
            # Momentum positivo
            momentum_score = 0
            if momentum_analysis:
                positive_days = sum(1 for m in momentum_analysis if m.get('positive_events', 0) > m.get('regression_events', 0))
                momentum_score = min(positive_days * 5, 30)  # Máximo 30 puntos
            
            # Diversidad de eventos
            event_types = set(event.get('event_type', '') for event in timeline_events)
            diversity_score = min(len(event_types) * 3, 30)  # Máximo 30 puntos
            
            total_score = activity_score + momentum_score + diversity_score
            
            return min(total_score, 100)  # Máximo 100 puntos
            
        except Exception as e:
            logger.error(f"Error calculando timeline health score: {str(e)}")
            return 0.0
    
    def _calculate_trend_direction(self, monthly_counts: Dict[str, int]) -> str:
        """Calcular dirección de tendencia"""
        if len(monthly_counts) < 2:
            return "Sin datos suficientes"
        
        try:
            sorted_months = sorted(monthly_counts.items())
            recent_months = sorted_months[-3:]  # Últimos 3 meses
            
            if len(recent_months) < 2:
                return "Sin datos suficientes"
            
            # Comparar tendencia
            values = [count for _, count in recent_months]
            
            if values[-1] > values[0]:
                return "Creciente"
            elif values[-1] < values[0]:
                return "Decreciente"
            else:
                return "Estable"
                
        except Exception as e:
            logger.error(f"Error calculando dirección de tendencia: {str(e)}")
            return "Error en cálculo"
    
    # ==========================================================================
    # SISTEMA DE VARIABLES DINÁMICAS {{variable}}
    # ==========================================================================
    
    def get_dynamic_variables_for_client(self, client_id: str) -> Dict[str, str]:
        """Obtener variables dinámicas específicas del cliente"""
        try:
            context = self.get_client_context(client_id)
            if not context:
                return {}
            
            # Variables básicas del cliente
            variables = {
                '{{clientName}}': context.basic_info.get('nombre_empresa', ''),
                '{{clientId}}': str(client_id),
                '{{clientEmail}}': context.basic_info.get('emails', ''),
                '{{clientPhone}}': context.basic_info.get('telefonos', ''),
                '{{clientSector}}': context.basic_info.get('sector', ''),
                '{{clientStatus}}': context.basic_info.get('estado', 'Activo'),
                '{{clientAddress}}': context.basic_info.get('direccion', ''),
                '{{clientNIF}}': context.basic_info.get('nif_cif', ''),
            }
            
            # Variables de contexto de negocio
            if context.pipeline_data:
                variables.update({
                    '{{totalPipelineValue}}': f"${context.summary.get('total_pipeline_value', 0):,.2f}",
                    '{{activeOpportunities}}': str(context.summary.get('active_opportunities', 0)),
                })
            
            # Variables de fechas
            now = datetime.now()
            variables.update({
                '{{currentDate}}': now.strftime('%Y-%m-%d'),
                '{{currentDateTime}}': now.strftime('%Y-%m-%d %H:%M:%S'),
                '{{currentYear}}': str(now.year),
                '{{currentMonth}}': now.strftime('%B'),
            })
            
            # Variables de empresa (desde configuración)
            company_vars = self._get_company_variables()
            variables.update(company_vars)
            
            return variables
            
        except Exception as e:
            logger.error(f"Error obteniendo variables dinámicas: {str(e)}")
            return {}
    
    def _get_company_variables(self) -> Dict[str, str]:
        """Obtener variables de la empresa desde configuración"""
        try:
            conn = self.get_db_connection()
            
            company_config = conn.execute(
                'SELECT key, value FROM general_config WHERE key LIKE "company_%"'
            ).fetchall()
            
            conn.close()
            
            variables = {}
            for config in company_config:
                key = config['key'].replace('company_', '')
                var_name = f"{{{{companyName}}}}" if key == 'name' else f"{{{{company{key.capitalize()}}}}}"
                variables[var_name] = config['value'] or ''
            
            return variables
            
        except Exception as e:
            logger.error(f"Error obteniendo variables de empresa: {str(e)}")
            return {}
    
    def apply_dynamic_variables(self, content: str, client_id: str) -> str:
        """Aplicar variables dinámicas a contenido"""
        try:
            variables = self.get_dynamic_variables_for_client(client_id)
            
            processed_content = content
            for variable, value in variables.items():
                processed_content = processed_content.replace(variable, str(value))
            
            return processed_content
            
        except Exception as e:
            logger.error(f"Error aplicando variables dinámicas: {str(e)}")
            return content
    
    # ==========================================================================
    # MÉTODO DE GENERACIÓN DE RESUMEN ACTUALIZADO
    # ==========================================================================
    
    def _generate_client_summary(self, context: ClientContext) -> Dict[str, Any]:
        """Generar resumen ejecutivo avanzado del cliente"""
        try:
            summary = {}
            
            # Estado general del cliente
            if context.basic_info.get('estado'):
                summary['client_status'] = context.basic_info['estado']
            
            # Valor total del pipeline
            total_pipeline = 0
            if context.pipeline_data.get('opportunities'):
                for opp in context.pipeline_data['opportunities']:
                    total_pipeline += float(opp.get('estimated_value', 0))
            summary['total_pipeline_value'] = total_pipeline
            
            # Número de oportunidades activas
            summary['active_opportunities'] = len(context.pipeline_data.get('opportunities', []))
            
            # Tickets abiertos
            open_tickets = 0
            if context.tickets_data.get('tickets'):
                for ticket in context.tickets_data['tickets']:
                    if ticket.get('status') in ['open', 'in_progress']:
                        open_tickets += 1
            summary['open_tickets'] = open_tickets
            
            # Última interacción
            last_interaction = None
            if context.communications_data.get('communications'):
                last_interaction = context.communications_data['communications'][0].get('created_at')
            summary['last_interaction'] = last_interaction
            
            # Puntuación de satisfacción avanzada
            if context.tickets_data.get('satisfaction_score'):
                summary['satisfaction_score'] = context.tickets_data['satisfaction_score']
            
            # Métricas de engagement
            if context.communications_data.get('engagement_score'):
                summary['engagement_score'] = context.communications_data['engagement_score']
            
            # Salud del pipeline
            if context.pipeline_data.get('pipeline_health'):
                summary['pipeline_health'] = context.pipeline_data['pipeline_health']
            
            # Efectividad de automatizaciones
            if context.automations_data.get('automation_effectiveness'):
                summary['automation_effectiveness'] = context.automations_data['automation_effectiveness']
            
            # Score de inteligencia del ERP
            if context.automations_data.get('intelligence_score'):
                summary['erp_intelligence_score'] = context.automations_data['intelligence_score']
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generando resumen avanzado: {str(e)}")
            return {}
    
    def _ensure_tables_exist(self):
        """Asegurar que existan las tablas necesarias"""
        conn = self.get_db_connection()
        
        # Tabla principal de clientes
        conn.execute('''
            CREATE TABLE IF NOT EXISTS clients (
                id INTEGER PRIMARY KEY,
                nombre_empresa TEXT,
                nif_cif TEXT,
                emails TEXT,
                telefonos TEXT,
                sector TEXT,
                estado TEXT DEFAULT 'Activo',
                direccion TEXT,
                notas TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabla de campos dinámicos de clientes
        conn.execute('''
            CREATE TABLE IF NOT EXISTS client_dynamic_data (
                id INTEGER PRIMARY KEY,
                client_id INTEGER,
                field_name TEXT,
                field_value TEXT,
                FOREIGN KEY (client_id) REFERENCES clients (id)
            )
        ''')
        
        # Tablas para otros módulos (simplificadas para demo)
        tables_to_create = [
            ('sales_opportunities', '''
                id INTEGER PRIMARY KEY,
                client_id INTEGER,
                title TEXT,
                estimated_value REAL,
                stage TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            '''),
            ('client_proposals', '''
                id INTEGER PRIMARY KEY,
                client_id INTEGER,
                title TEXT,
                total_amount REAL,
                status TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            '''),
            ('client_communications', '''
                id INTEGER PRIMARY KEY,
                client_id INTEGER,
                subject TEXT,
                communication_type TEXT,
                content TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            '''),
            ('marketing_campaigns', '''
                id INTEGER PRIMARY KEY,
                name TEXT,
                target_clients TEXT,
                status TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            '''),
            ('support_tickets', '''
                id INTEGER PRIMARY KEY,
                client_id INTEGER,
                subject TEXT,
                status TEXT,
                priority TEXT,
                resolution_time INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            '''),
            ('calendar_activities', '''
                id INTEGER PRIMARY KEY,
                client_id INTEGER,
                title TEXT,
                activity_date DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            '''),
            ('client_timeline', '''
                id INTEGER PRIMARY KEY,
                client_id INTEGER,
                event_type TEXT,
                description TEXT,
                event_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            '''),
            ('client_automations', '''
                id INTEGER PRIMARY KEY,
                client_id INTEGER,
                name TEXT,
                status TEXT,
                target_group TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ''')
        ]
        
        for table_name, table_schema in tables_to_create:
            conn.execute(f'CREATE TABLE IF NOT EXISTS {table_name} ({table_schema})')
        
        conn.commit()
        conn.close()

# Instancia global del servicio
ai_context_service = AIContextService()

def get_ai_context_service() -> AIContextService:
    """Obtener instancia del servicio de contexto AI"""
    return ai_context_service
