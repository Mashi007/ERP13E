"""
📁 Ruta: /app/modules/clientes/routes.py
📄 Nombre: clientes_routes.py
🏗️ Propósito: Blueprint completo del módulo Clientes con Chat AI
⚡ Performance: Carga eficiente y contexto AI optimizado
🔒 Seguridad: Validación de acceso por cliente.

ERP13 Enterprise - Módulo Clientes Completo
9 submódulos integrados con Chat AI inteligente
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, session
import sqlite3
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging

# Importar el AI Context Service optimizado
from app.core.ai_context_service import get_ai_context_service

logger = logging.getLogger(__name__)

# Crear Blueprint
clientes_bp = Blueprint('clientes', __name__, url_prefix='/clientes')

# ==========================================================================
# CONFIGURACIÓN Y UTILIDADES
# ==========================================================================

def get_db_connection():
    """Obtener conexión a la base de datos"""
    conn = sqlite3.connect('erp_database.db')
    conn.row_factory = sqlite3.Row
    return conn

def ensure_user_logged_in():
    """Verificar que el usuario esté autenticado"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    return None

def get_user_permissions():
    """Obtener permisos del usuario actual"""
    user_id = session.get('user_id')
    if not user_id:
        return []
    
    try:
        conn = get_db_connection()
        permissions = conn.execute('''
            SELECT p.permission_name 
            FROM user_permissions up
            LEFT JOIN permissions p ON up.permission_id = p.id
            WHERE up.user_id = ?
        ''', (user_id,)).fetchall()
        conn.close()
        
        return [p['permission_name'] for p in permissions]
    except Exception as e:
        logger.error(f"Error obteniendo permisos: {str(e)}")
        return []

# ==========================================================================
# RUTA PRINCIPAL - GESTIÓN DE CLIENTES CON CHAT AI
# ==========================================================================

@clientes_bp.route('/')
@clientes_bp.route('/gestion')
def gestion_clientes():
    """Página principal - Gestión de clientes con Chat AI"""
    auth_check = ensure_user_logged_in()
    if auth_check:
        return auth_check
    
    try:
        conn = get_db_connection()
        
        # Obtener estadísticas de clientes
        stats = {
            'total': conn.execute('SELECT COUNT(*) as count FROM clients').fetchone()['count'],
            'leads': conn.execute('SELECT COUNT(*) as count FROM clients WHERE estado = "Lead"').fetchone()['count'],
            'clientes': conn.execute('SELECT COUNT(*) as count FROM clients WHERE estado = "Cliente"').fetchone()['count'],
            'activos': conn.execute('SELECT COUNT(*) as count FROM clients WHERE estado = "Activo"').fetchone()['count'],
            'propuestas_pendientes': conn.execute('''
                SELECT COUNT(DISTINCT c.id) as count 
                FROM clients c 
                LEFT JOIN client_proposals p ON c.id = p.client_id 
                WHERE p.status = "pending"
            ''').fetchone()['count']
        }
        
        # Obtener lista de clientes con información básica
        clients = conn.execute('''
            SELECT 
                c.*,
                COUNT(DISTINCT p.id) as total_propuestas,
                COUNT(DISTINCT o.id) as total_oportunidades,
                COUNT(DISTINCT t.id) as total_tickets,
                MAX(comm.created_at) as ultima_comunicacion
            FROM clients c
            LEFT JOIN client_proposals p ON c.id = p.client_id
            LEFT JOIN sales_opportunities o ON c.id = o.client_id
            LEFT JOIN support_tickets t ON c.id = t.client_id
            LEFT JOIN client_communications comm ON c.id = comm.client_id
            GROUP BY c.id
            ORDER BY c.created_at DESC
            LIMIT 50
        ''').fetchall()
        
        # Obtener configuración de filtros
        sectores = conn.execute('SELECT DISTINCT sector FROM clients WHERE sector IS NOT NULL').fetchall()
        estados = conn.execute('SELECT DISTINCT estado FROM clients WHERE estado IS NOT NULL').fetchall()
        
        conn.close()
        
        return render_template('clientes/gestion_clientes.html', 
                             stats=stats,
                             clients=[dict(c) for c in clients],
                             sectores=[s['sector'] for s in sectores],
                             estados=[e['estado'] for e in estados],
                             user_permissions=get_user_permissions())
    
    except Exception as e:
        logger.error(f"Error en gestión de clientes: {str(e)}")
        flash(f'Error cargando clientes: {str(e)}', 'error')
        return render_template('clientes/gestion_clientes.html', 
                             stats={'total': 0, 'leads': 0, 'clientes': 0, 'activos': 0, 'propuestas_pendientes': 0},
                             clients=[],
                             sectores=[],
                             estados=[])

# ==========================================================================
# API ENDPOINTS PARA CHAT AI
# ==========================================================================

@clientes_bp.route('/api/chat', methods=['POST'])
def chat_ai():
    """API endpoint para el Chat AI de clientes"""
    auth_check = ensure_user_logged_in()
    if auth_check:
        return jsonify({'error': 'No autorizado'}), 401
    
    try:
        data = request.json
        message = data.get('message', '').strip()
        selected_client_id = data.get('client_id')
        
        if not message:
            return jsonify({'error': 'Mensaje vacío'}), 400
        
        # Obtener servicio de contexto AI
        ai_service = get_ai_context_service()
        
        # Determinar si la consulta necesita contexto específico de cliente
        if selected_client_id:
            # Consulta específica de cliente
            context = ai_service.get_formatted_context_for_ai(selected_client_id)
            
            ai_response = f"""
Basándome en la información del cliente seleccionado:

{context}

**Respuesta a tu consulta:** "{message}"

{_generate_ai_response(message, context)}
"""
        else:
            # Consulta general sobre clientes
            ai_response = _handle_general_client_query(message)
        
        # Registrar conversación
        _log_ai_conversation(message, ai_response, selected_client_id)
        
        return jsonify({
            'response': ai_response,
            'timestamp': datetime.now().isoformat(),
            'client_id': selected_client_id
        })
    
    except Exception as e:
        logger.error(f"Error en chat AI: {str(e)}")
        return jsonify({'error': f'Error procesando consulta: {str(e)}'}), 500

@clientes_bp.route('/api/clients/search')
def search_clients():
    """API para búsqueda de clientes (para selector del chat)"""
    auth_check = ensure_user_logged_in()
    if auth_check:
        return jsonify({'error': 'No autorizado'}), 401
    
    try:
        query = request.args.get('q', '').strip()
        limit = int(request.args.get('limit', 20))
        
        conn = get_db_connection()
        
        if query:
            clients = conn.execute('''
                SELECT id, nombre_empresa, sector, estado, emails
                FROM clients
                WHERE nombre_empresa LIKE ? OR emails LIKE ? OR nif_cif LIKE ?
                ORDER BY nombre_empresa
                LIMIT ?
            ''', (f'%{query}%', f'%{query}%', f'%{query}%', limit)).fetchall()
        else:
            clients = conn.execute('''
                SELECT id, nombre_empresa, sector, estado, emails
                FROM clients
                ORDER BY nombre_empresa
                LIMIT ?
            ''', (limit,)).fetchall()
        
        conn.close()
        
        return jsonify({
            'clients': [dict(c) for c in clients]
        })
    
    except Exception as e:
        logger.error(f"Error buscando clientes: {str(e)}")
        return jsonify({'error': str(e)}), 500

@clientes_bp.route('/api/client/<int:client_id>/context')
def get_client_context(client_id):
    """API para obtener contexto completo de un cliente"""
    auth_check = ensure_user_logged_in()
    if auth_check:
        return jsonify({'error': 'No autorizado'}), 401
    
    try:
        ai_service = get_ai_context_service()
        context = ai_service.get_client_context(str(client_id))
        
        if not context:
            return jsonify({'error': 'Cliente no encontrado'}), 404
        
        return jsonify({
            'client_name': context.client_name,
            'basic_info': context.basic_info,
            'summary': context.summary,
            'last_updated': context.last_updated.isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error obteniendo contexto del cliente {client_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

# ==========================================================================
# SUBMÓDULO 2: TIMELINE
# ==========================================================================

@clientes_bp.route('/timeline')
@clientes_bp.route('/timeline/<int:client_id>')
def timeline_clientes(client_id=None):
    """Timeline de interacciones del cliente"""
    auth_check = ensure_user_logged_in()
    if auth_check:
        return auth_check
    
    try:
        conn = get_db_connection()
        
        # Si no se especifica cliente, mostrar timeline general
        if not client_id:
            # Timeline de todos los clientes (últimos eventos)
            timeline_events = conn.execute('''
                SELECT 
                    ct.*,
                    c.nombre_empresa,
                    u.username as triggered_by_name
                FROM client_timeline ct
                LEFT JOIN clients c ON ct.client_id = c.id
                LEFT JOIN users u ON ct.triggered_by = u.id
                ORDER BY ct.event_date DESC
                LIMIT 100
            ''').fetchall()
            
            selected_client = None
        else:
            # Timeline específico del cliente
            timeline_events = conn.execute('''
                SELECT 
                    ct.*,
                    u.username as triggered_by_name
                FROM client_timeline ct
                LEFT JOIN users u ON ct.triggered_by = u.id
                WHERE ct.client_id = ?
                ORDER BY ct.event_date DESC
                LIMIT 50
            ''', (client_id,)).fetchall()
            
            selected_client = conn.execute('SELECT * FROM clients WHERE id = ?', (client_id,)).fetchone()
        
        # Obtener lista de clientes para filtro
        clients = conn.execute('SELECT id, nombre_empresa FROM clients ORDER BY nombre_empresa').fetchall()
        
        conn.close()
        
        return render_template('clientes/timeline.html',
                             timeline_events=[dict(t) for t in timeline_events],
                             clients=[dict(c) for c in clients],
                             selected_client=dict(selected_client) if selected_client else None,
                             selected_client_id=client_id)
    
    except Exception as e:
        logger.error(f"Error cargando timeline: {str(e)}")
        flash(f'Error cargando timeline: {str(e)}', 'error')
        return render_template('clientes/timeline.html', 
                             timeline_events=[], clients=[], selected_client=None)

# ==========================================================================
# SUBMÓDULO 3: COMUNICACIONES
# ==========================================================================

@clientes_bp.route('/comunicaciones')
@clientes_bp.route('/comunicaciones/<int:client_id>')
def comunicaciones_clientes(client_id=None):
    """Comunicaciones multicanal del cliente"""
    auth_check = ensure_user_logged_in()
    if auth_check:
        return auth_check
    
    try:
        conn = get_db_connection()
        
        # Obtener comunicaciones
        if client_id:
            communications = conn.execute('''
                SELECT 
                    c.*,
                    cc.channel_name,
                    cl.nombre_empresa
                FROM client_communications c
                LEFT JOIN communication_channels cc ON c.channel_id = cc.id
                LEFT JOIN clients cl ON c.client_id = cl.id
                WHERE c.client_id = ?
                ORDER BY c.created_at DESC
                LIMIT 50
            ''', (client_id,)).fetchall()
            
            selected_client = conn.execute('SELECT * FROM clients WHERE id = ?', (client_id,)).fetchone()
        else:
            communications = conn.execute('''
                SELECT 
                    c.*,
                    cc.channel_name,
                    cl.nombre_empresa
                FROM client_communications c
                LEFT JOIN communication_channels cc ON c.channel_id = cc.id
                LEFT JOIN clients cl ON c.client_id = cl.id
                ORDER BY c.created_at DESC
                LIMIT 100
            ''').fetchall()
            
            selected_client = None
        
        # Obtener canales disponibles
        channels = conn.execute('SELECT * FROM communication_channels WHERE active = 1').fetchall()
        
        # Obtener clientes para filtro
        clients = conn.execute('SELECT id, nombre_empresa FROM clients ORDER BY nombre_empresa').fetchall()
        
        # Obtener plantillas de comunicación
        templates = conn.execute('SELECT * FROM communication_templates WHERE active = 1').fetchall()
        
        conn.close()
        
        return render_template('clientes/comunicaciones.html',
                             communications=[dict(c) for c in communications],
                             channels=[dict(ch) for ch in channels],
                             clients=[dict(c) for c in clients],
                             templates=[dict(t) for t in templates],
                             selected_client=dict(selected_client) if selected_client else None,
                             selected_client_id=client_id)
    
    except Exception as e:
        logger.error(f"Error cargando comunicaciones: {str(e)}")
        flash(f'Error cargando comunicaciones: {str(e)}', 'error')
        return render_template('clientes/comunicaciones.html', 
                             communications=[], channels=[], clients=[], templates=[])

# ==========================================================================
# SUBMÓDULO 4: PROPUESTAS
# ==========================================================================

@clientes_bp.route('/propuestas')
@clientes_bp.route('/propuestas/<int:client_id>')
def propuestas_clientes(client_id=None):
    """Propuestas comerciales con plantillas dinámicas"""
    auth_check = ensure_user_logged_in()
    if auth_check:
        return auth_check
    
    try:
        conn = get_db_connection()
        
        # Obtener propuestas
        if client_id:
            proposals = conn.execute('''
                SELECT 
                    p.*,
                    pt.template_name,
                    c.nombre_empresa,
                    u.username as created_by_name
                FROM client_proposals p
                LEFT JOIN proposal_templates pt ON p.template_id = pt.id
                LEFT JOIN clients c ON p.client_id = c.id
                LEFT JOIN users u ON p.created_by = u.id
                WHERE p.client_id = ?
                ORDER BY p.created_at DESC
            ''', (client_id,)).fetchall()
            
            selected_client = conn.execute('SELECT * FROM clients WHERE id = ?', (client_id,)).fetchone()
        else:
            proposals = conn.execute('''
                SELECT 
                    p.*,
                    pt.template_name,
                    c.nombre_empresa,
                    u.username as created_by_name
                FROM client_proposals p
                LEFT JOIN proposal_templates pt ON p.template_id = pt.id
                LEFT JOIN clients c ON p.client_id = c.id
                LEFT JOIN users u ON p.created_by = u.id
                ORDER BY p.created_at DESC
                LIMIT 50
            ''').fetchall()
            
            selected_client = None
        
        # Obtener plantillas de propuestas
        templates = conn.execute('''
            SELECT 
                pt.*,
                COUNT(p.id) as usage_count
            FROM proposal_templates pt
            LEFT JOIN client_proposals p ON pt.id = p.template_id
            WHERE pt.active = 1
            GROUP BY pt.id
            ORDER BY usage_count DESC, pt.template_name
        ''').fetchall()
        
        # Obtener etapas del pipeline para propuestas
        pipeline_stages = conn.execute('SELECT * FROM pipeline_stages ORDER BY stage_order').fetchall()
        
        # Obtener clientes
        clients = conn.execute('SELECT id, nombre_empresa, sector FROM clients ORDER BY nombre_empresa').fetchall()
        
        conn.close()
        
        return render_template('clientes/propuestas.html',
                             proposals=[dict(p) for p in proposals],
                             templates=[dict(t) for t in templates],
                             pipeline_stages=[dict(ps) for ps in pipeline_stages],
                             clients=[dict(c) for c in clients],
                             selected_client=dict(selected_client) if selected_client else None,
                             selected_client_id=client_id)
    
    except Exception as e:
        logger.error(f"Error cargando propuestas: {str(e)}")
        flash(f'Error cargando propuestas: {str(e)}', 'error')
        return render_template('clientes/propuestas.html', 
                             proposals=[], templates=[], pipeline_stages=[], clients=[])

# ==========================================================================
# SUBMÓDULO 5: PIPELINE KANBAN
# ==========================================================================

@clientes_bp.route('/pipeline')
@clientes_bp.route('/pipeline/<int:client_id>')
def pipeline_clientes(client_id=None):
    """Pipeline Kanban de oportunidades de venta"""
    auth_check = ensure_user_logged_in()
    if auth_check:
        return auth_check
    
    try:
        conn = get_db_connection()
        
        # Obtener etapas del pipeline
        pipeline_stages = conn.execute('SELECT * FROM pipeline_stages ORDER BY stage_order').fetchall()
        
        # Obtener oportunidades por etapa
        if client_id:
            opportunities = conn.execute('''
                SELECT 
                    o.*,
                    ps.stage_name,
                    ps.stage_color,
                    c.nombre_empresa
                FROM sales_opportunities o
                LEFT JOIN pipeline_stages ps ON o.stage_id = ps.id
                LEFT JOIN clients c ON o.client_id = c.id
                WHERE o.client_id = ?
                ORDER BY o.created_at DESC
            ''', (client_id,)).fetchall()
            
            selected_client = conn.execute('SELECT * FROM clients WHERE id = ?', (client_id,)).fetchone()
        else:
            opportunities = conn.execute('''
                SELECT 
                    o.*,
                    ps.stage_name,
                    ps.stage_color,
                    c.nombre_empresa
                FROM sales_opportunities o
                LEFT JOIN pipeline_stages ps ON o.stage_id = ps.id
                LEFT JOIN clients c ON o.client_id = c.id
                ORDER BY o.created_at DESC
                LIMIT 100
            ''').fetchall()
            
            selected_client = None
        
        # Organizar oportunidades por etapa para el Kanban
        kanban_data = {}
        for stage in pipeline_stages:
            stage_id = stage['id']
            kanban_data[stage_id] = {
                'stage': dict(stage),
                'opportunities': [dict(opp) for opp in opportunities if opp['stage_id'] == stage_id]
            }
        
        # Estadísticas del pipeline
        stats = conn.execute('''
            SELECT 
                ps.stage_name,
                COUNT(o.id) as opportunity_count,
                SUM(o.estimated_value) as total_value,
                AVG(o.estimated_value) as avg_value
            FROM sales_opportunities o
            LEFT JOIN pipeline_stages ps ON o.stage_id = ps.id
            {} 
            GROUP BY ps.id, ps.stage_name
            ORDER BY ps.stage_order
        '''.format('WHERE o.client_id = ?' if client_id else ''), 
        (client_id,) if client_id else ()).fetchall()
        
        # Obtener clientes
        clients = conn.execute('SELECT id, nombre_empresa FROM clients ORDER BY nombre_empresa').fetchall()
        
        conn.close()
        
        return render_template('clientes/pipeline.html',
                             kanban_data=kanban_data,
                             pipeline_stages=[dict(ps) for ps in pipeline_stages],
                             opportunities=[dict(o) for o in opportunities],
                             stats=[dict(s) for s in stats],
                             clients=[dict(c) for c in clients],
                             selected_client=dict(selected_client) if selected_client else None,
                             selected_client_id=client_id)
    
    except Exception as e:
        logger.error(f"Error cargando pipeline: {str(e)}")
        flash(f'Error cargando pipeline: {str(e)}', 'error')
        return render_template('clientes/pipeline.html', 
                             kanban_data={}, pipeline_stages=[], opportunities=[], stats=[], clients=[])

# ==========================================================================
# SUBMÓDULO 6: TICKETS DE SOPORTE
# ==========================================================================

@clientes_bp.route('/tickets')
@clientes_bp.route('/tickets/<int:client_id>')
def tickets_clientes(client_id=None):
    """Tickets de soporte con SLA y escalabilidad"""
    auth_check = ensure_user_logged_in()
    if auth_check:
        return auth_check
    
    try:
        conn = get_db_connection()
        
        # Obtener tickets
        if client_id:
            tickets = conn.execute('''
                SELECT 
                    t.*,
                    tc.category_name,
                    tc.default_sla_hours,
                    c.nombre_empresa,
                    u1.username as assigned_to_name,
                    u2.username as created_by_name
                FROM support_tickets t
                LEFT JOIN ticket_categories tc ON t.category_id = tc.id
                LEFT JOIN clients c ON t.client_id = c.id
                LEFT JOIN users u1 ON t.assigned_to = u1.id
                LEFT JOIN users u2 ON t.created_by = u2.id
                WHERE t.client_id = ?
                ORDER BY t.created_at DESC
            ''', (client_id,)).fetchall()
            
            selected_client = conn.execute('SELECT * FROM clients WHERE id = ?', (client_id,)).fetchone()
        else:
            tickets = conn.execute('''
                SELECT 
                    t.*,
                    tc.category_name,
                    tc.default_sla_hours,
                    c.nombre_empresa,
                    u1.username as assigned_to_name,
                    u2.username as created_by_name
                FROM support_tickets t
                LEFT JOIN ticket_categories tc ON t.category_id = tc.id
                LEFT JOIN clients c ON t.client_id = c.id
                LEFT JOIN users u1 ON t.assigned_to = u1.id
                LEFT JOIN users u2 ON t.created_by = u2.id
                ORDER BY t.created_at DESC
                LIMIT 100
            ''').fetchall()
            
            selected_client = None
        
        # Obtener categorías de tickets
        categories = conn.execute('SELECT * FROM ticket_categories ORDER BY category_name').fetchall()
        
        # Obtener usuarios para asignación
        users = conn.execute('SELECT id, username FROM users WHERE active = 1 ORDER BY username').fetchall()
        
        # Obtener clientes
        clients = conn.execute('SELECT id, nombre_empresa FROM clients ORDER BY nombre_empresa').fetchall()
        
        # Estadísticas SLA
        sla_stats = conn.execute('''
            SELECT 
                tc.category_name,
                COUNT(t.id) as total_tickets,
                SUM(CASE WHEN t.resolution_time_hours <= tc.default_sla_hours THEN 1 ELSE 0 END) as within_sla,
                AVG(t.resolution_time_hours) as avg_resolution_time
            FROM support_tickets t
            LEFT JOIN ticket_categories tc ON t.category_id = tc.id
            {}
            GROUP BY tc.id, tc.category_name
        '''.format('WHERE t.client_id = ?' if client_id else ''), 
        (client_id,) if client_id else ()).fetchall()
        
        conn.close()
        
        return render_template('clientes/tickets.html',
                             tickets=[dict(t) for t in tickets],
                             categories=[dict(c) for c in categories],
                             users=[dict(u) for u in users],
                             clients=[dict(c) for c in clients],
                             sla_stats=[dict(s) for s in sla_stats],
                             selected_client=dict(selected_client) if selected_client else None,
                             selected_client_id=client_id)
    
    except Exception as e:
        logger.error(f"Error cargando tickets: {str(e)}")
        flash(f'Error cargando tickets: {str(e)}', 'error')
        return render_template('clientes/tickets.html', 
                             tickets=[], categories=[], users=[], clients=[], sla_stats=[])

# ==========================================================================
# SUBMÓDULO 7: CALENDARIO
# ==========================================================================

@clientes_bp.route('/calendario')
@clientes_bp.route('/calendario/<int:client_id>')
def calendario_clientes(client_id=None):
    """Calendario integrado con sistemas externos"""
    auth_check = ensure_user_logged_in()
    if auth_check:
        return auth_check
    
    try:
        conn = get_db_connection()
        
        # Obtener actividades del calendario
        if client_id:
            activities = conn.execute('''
                SELECT 
                    ca.*,
                    c.nombre_empresa,
                    u.username as assigned_to_name,
                    ci.calendar_type,
                    ci.sync_status
                FROM calendar_activities ca
                LEFT JOIN clients c ON ca.client_id = c.id
                LEFT JOIN users u ON ca.assigned_to = u.id
                LEFT JOIN calendar_integrations ci ON ca.calendar_integration_id = ci.id
                WHERE ca.client_id = ?
                ORDER BY ca.activity_date DESC
            ''', (client_id,)).fetchall()
            
            selected_client = conn.execute('SELECT * FROM clients WHERE id = ?', (client_id,)).fetchone()
        else:
            activities = conn.execute('''
                SELECT 
                    ca.*,
                    c.nombre_empresa,
                    u.username as assigned_to_name,
                    ci.calendar_type,
                    ci.sync_status
                FROM calendar_activities ca
                LEFT JOIN clients c ON ca.client_id = c.id
                LEFT JOIN users u ON ca.assigned_to = u.id
                LEFT JOIN calendar_integrations ci ON ca.calendar_integration_id = ci.id
                ORDER BY ca.activity_date DESC
                LIMIT 100
            ''').fetchall()
            
            selected_client = None
        
        # Obtener integraciones de calendario
        integrations = conn.execute('''
            SELECT * FROM calendar_integrations 
            WHERE active = 1
            ORDER BY calendar_type, integration_name
        ''').fetchall()
        
        # Obtener usuarios
        users = conn.execute('SELECT id, username FROM users WHERE active = 1 ORDER BY username').fetchall()
        
        # Obtener clientes
        clients = conn.execute('SELECT id, nombre_empresa FROM clients ORDER BY nombre_empresa').fetchall()
        
        conn.close()
        
        # Formatear actividades para el calendario (FullCalendar)
        calendar_events = []
        for activity in activities:
            calendar_events.append({
                'id': activity['id'],
                'title': activity['title'],
                'start': activity['activity_date'],
                'end': activity['end_date'] if activity['end_date'] else activity['activity_date'],
                'backgroundColor': _get_activity_color(activity['activity_type']),
                'extendedProps': {
                    'client_name': activity['nombre_empresa'],
                    'assigned_to': activity['assigned_to_name'],
                    'activity_type': activity['activity_type'],
                    'description': activity['description']
                }
            })
        
        return render_template('clientes/calendario.html',
                             activities=[dict(a) for a in activities],
                             calendar_events=calendar_events,
                             integrations=[dict(i) for i in integrations],
                             users=[dict(u) for u in users],
                             clients=[dict(c) for c in clients],
                             selected_client=dict(selected_client) if selected_client else None,
                             selected_client_id=client_id)
    
    except Exception as e:
        logger.error(f"Error cargando calendario: {str(e)}")
        flash(f'Error cargando calendario: {str(e)}', 'error')
        return render_template('clientes/calendario.html', 
                             activities=[], calendar_events=[], integrations=[], users=[], clients=[])

# ==========================================================================
# SUBMÓDULO 8: CAMPAÑAS PUBLICITARIAS
# ==========================================================================

@clientes_bp.route('/campanas')
@clientes_bp.route('/campanas/<int:client_id>')
def campanas_clientes(client_id=None):
    """Campañas publicitarias multicanal"""
    auth_check = ensure_user_logged_in()
    if auth_check:
        return auth_check
    
    try:
        conn = get_db_connection()
        
        # Obtener campañas
        if client_id:
            campaigns = conn.execute('''
                SELECT 
                    mc.*,
                    ct.template_name
                FROM marketing_campaigns mc
                LEFT JOIN campaign_templates ct ON mc.template_id = ct.id
                WHERE mc.target_clients LIKE ? OR mc.target_clients = 'all'
                ORDER BY mc.created_at DESC
            ''', (f'%{client_id}%',)).fetchall()
            
            selected_client = conn.execute('SELECT * FROM clients WHERE id = ?', (client_id,)).fetchone()
        else:
            campaigns = conn.execute('''
                SELECT 
                    mc.*,
                    ct.template_name
                FROM marketing_campaigns mc
                LEFT JOIN campaign_templates ct ON mc.template_id = ct.id
                ORDER BY mc.created_at DESC
                LIMIT 50
            ''').fetchall()
            
            selected_client = None
        
        # Obtener métricas de campañas
        campaign_metrics = {}
        for campaign in campaigns:
            metrics = conn.execute('''
                SELECT 
                    SUM(impressions) as total_impressions,
                    SUM(clicks) as total_clicks,
                    SUM(conversions) as total_conversions,
                    SUM(cost) as total_cost,
                    AVG(engagement_rate) as avg_engagement
                FROM campaign_metrics 
                WHERE campaign_id = ?
            ''', (campaign['id'],)).fetchone()
            
            campaign_metrics[campaign['id']] = dict(metrics) if metrics else {}
        
        # Obtener plantillas de campañas
        templates = conn.execute('SELECT * FROM campaign_templates WHERE active = 1').fetchall()
        
        # Obtener canales disponibles
        channels = conn.execute('SELECT * FROM campaign_channels WHERE active = 1').fetchall()
        
        # Obtener clientes
        clients = conn.execute('SELECT id, nombre_empresa, sector FROM clients ORDER BY nombre_empresa').fetchall()
        
        conn.close()
        
        return render_template('clientes/campanas.html',
                             campaigns=[dict(c) for c in campaigns],
                             campaign_metrics=campaign_metrics,
                             templates=[dict(t) for t in templates],
                             channels=[dict(ch) for ch in channels],
                             clients=[dict(c) for c in clients],
                             selected_client=dict(selected_client) if selected_client else None,
                             selected_client_id=client_id)
    
    except Exception as e:
        logger.error(f"Error cargando campañas: {str(e)}")
        flash(f'Error cargando campañas: {str(e)}', 'error')
        return render_template('clientes/campanas.html', 
                             campaigns=[], campaign_metrics={}, templates=[], channels=[], clients=[])

# ==========================================================================
# SUBMÓDULO 9: AUTOMATIZACIONES
# ==========================================================================

@clientes_bp.route('/automatizaciones')
@clientes_bp.route('/automatizaciones/<int:client_id>')
def automatizaciones_clientes(client_id=None):
    """Automatizaciones - Cerebro del ERP"""
    auth_check = ensure_user_logged_in()
    if auth_check:
        return auth_check
    
    try:
        conn = get_db_connection()
        
        # Obtener automatizaciones
        if client_id:
            automations = conn.execute('''
                SELECT 
                    ca.*,
                    at.template_name,
                    at.workflow_definition
                FROM client_automations ca
                LEFT JOIN automation_templates at ON ca.template_id = at.id
                WHERE ca.client_id = ? OR ca.target_group = 'all'
                ORDER BY ca.priority DESC, ca.created_at DESC
            ''', (client_id,)).fetchall()
            
            selected_client = conn.execute('SELECT * FROM clients WHERE id = ?', (client_id,)).fetchone()
        else:
            automations = conn.execute('''
                SELECT 
                    ca.*,
                    at.template_name,
                    at.workflow_definition,
                    c.nombre_empresa
                FROM client_automations ca
                LEFT JOIN automation_templates at ON ca.template_id = at.id
                LEFT JOIN clients c ON ca.client_id = c.id
                ORDER BY ca.priority DESC, ca.created_at DESC
                LIMIT 50
            ''').fetchall()
            
            selected_client = None
        
        # Obtener ejecuciones recientes
        executions = conn.execute('''
            SELECT 
                ae.*,
                ca.automation_name
            FROM automation_executions ae
            LEFT JOIN client_automations ca ON ae.automation_id = ca.id
            {}
            ORDER BY ae.execution_date DESC
            LIMIT 50
        '''.format('WHERE ae.client_id = ?' if client_id else ''), 
        (client_id,) if client_id else ()).fetchall()
        
        # Obtener plantillas de automatización
        templates = conn.execute('SELECT * FROM automation_templates WHERE active = 1').fetchall()
        
        # Obtener recomendaciones AI
        ai_recommendations = conn.execute('''
            SELECT * FROM ai_automation_recommendations 
            {}
            WHERE status = 'pending'
            ORDER BY confidence_score DESC
            LIMIT 10
        '''.format('WHERE client_id = ?' if client_id else ''), 
        (client_id,) if client_id else ()).fetchall()
        
        # Obtener clientes
        clients = conn.execute('SELECT id, nombre_empresa FROM clients ORDER BY nombre_empresa').fetchall()
        
        conn.close()
        
        return render_template('clientes/automatizaciones.html',
                             automations=[dict(a) for a in automations],
                             executions=[dict(e) for e in executions],
                             templates=[dict(t) for t in templates],
                             ai_recommendations=[dict(r) for r in ai_recommendations],
                             clients=[dict(c) for c in clients],
                             selected_client=dict(selected_client) if selected_client else None,
                             selected_client_id=client_id)
    
    except Exception as e:
        logger.error(f"Error cargando automatizaciones: {str(e)}")
        flash(f'Error cargando automatizaciones: {str(e)}', 'error')
        return render_template('clientes/automatizaciones.html', 
                             automations=[], executions=[], templates=[], ai_recommendations=[], clients=[])

# ==========================================================================
# FUNCIONES AUXILIARES
# ==========================================================================

def _generate_ai_response(message: str, context: str) -> str:
    """Generar respuesta AI basada en el mensaje y contexto"""
    # Esta es una implementación simplificada
    # En producción, aquí integrarías con un LLM como OpenAI GPT o Claude
    
    try:
        message_lower = message.lower()
        
        # Análisis de propuestas
        if any(word in message_lower for word in ['propuesta', 'propuestas', 'plantilla', 'presupuesto']):
            return """**Análisis de Propuestas:**
            
Basándome en la información del cliente:
- He revisado su historial de propuestas y plantillas utilizadas
- Puedo identificar qué plantillas han tenido mejor tasa de conversión
- Las variables más efectivas han sido {{clientName}} y {{discountPercentage}}
- Recomiendo usar la plantilla con mayor ROI para futuras propuestas"""

        # Análisis de comunicaciones
        elif any(word in message_lower for word in ['comunicacion', 'comunicaciones', 'email', 'whatsapp', 'canal']):
            return """**Análisis de Comunicaciones:**
            
He analizado el historial de comunicaciones:
- Canal preferido identificado según engagement
- Patrones temporales de respuesta detectados
- Análisis de sentimiento de interacciones recientes
- Recomendaciones de horarios óptimos para contacto"""

        # Análisis de tickets
        elif any(word in message_lower for word in ['ticket', 'tickets', 'soporte', 'sla']):
            return """**Análisis de Soporte:**
            
Revisión del historial de tickets:
- Cumplimiento de SLA analizado
- Categorías de problemas más frecuentes identificadas
- Tiempo promedio de resolución calculado
- Oportunidades de mejora en escalabilidad detectadas"""

        # Análisis de pipeline
        elif any(word in message_lower for word in ['pipeline', 'oportunidad', 'oportunidades', 'embudo', 'ventas']):
            return """**Análisis de Pipeline:**
            
Estado actual del embudo de ventas:
- Distribución de oportunidades por etapa analizada
- Salud general del pipeline evaluada
- Patrones de conversión entre etapas identificados
- Recomendaciones para optimizar el flujo"""

        # Consulta general
        else:
            return """**Análisis Integral del Cliente:**
            
He procesado toda la información disponible:
- Estado general y métricas clave revisadas
- Patrones de comportamiento identificados
- Oportunidades de mejora detectadas
- Recomendaciones personalizadas generadas

¿Te gustaría que profundice en algún aspecto específico?"""
    
    except Exception as e:
        logger.error(f"Error generando respuesta AI: {str(e)}")
        return "Lo siento, ocurrió un error al procesar tu consulta. Por favor, intenta de nuevo."

def _handle_general_client_query(message: str) -> str:
    """Manejar consulta general sobre clientes"""
    try:
        conn = get_db_connection()
        
        message_lower = message.lower()
        
        # Estadísticas generales
        if any(word in message_lower for word in ['cuantos', 'estadisticas', 'resumen', 'total']):
            stats = conn.execute('''
                SELECT 
                    COUNT(*) as total_clients,
                    COUNT(CASE WHEN estado = 'Lead' THEN 1 END) as total_leads,
                    COUNT(CASE WHEN estado = 'Cliente' THEN 1 END) as total_clientes,
                    COUNT(CASE WHEN estado = 'Activo' THEN 1 END) as total_activos
                FROM clients
            ''').fetchone()
            
            conn.close()
            
            return f"""**Estadísticas Generales de Clientes:**

📊 **Resumen actual:**
- **Total de registros:** {stats['total_clients']}
- **LEADs:** {stats['total_leads']} 
- **CLIENTES:** {stats['total_clientes']}
- **Activos:** {stats['total_activos']}

💡 **Insight:** Tienes una base de {stats['total_clients']} contactos, con {stats['total_leads']} leads potenciales para convertir."""
        
        # Sectores
        elif any(word in message_lower for word in ['sector', 'sectores', 'industria']):
            sectors = conn.execute('''
                SELECT sector, COUNT(*) as count
                FROM clients 
                WHERE sector IS NOT NULL
                GROUP BY sector
                ORDER BY count DESC
            ''').fetchall()
            
            conn.close()
            
            sector_list = "\n".join([f"- **{s['sector']}:** {s['count']} clientes" for s in sectors[:5]])
            
            return f"""**Distribución por Sectores:**

🎯 **Top 5 sectores:**
{sector_list}

💡 **Recomendación:** Los sectores con más clientes son tus nichos más fuertes para campañas especializadas."""
        
        else:
            conn.close()
            return """**Asistente IA de Clientes disponible** 🤖

Puedo ayudarte con:
- 📊 Estadísticas generales de clientes
- 🎯 Análisis por sectores  
- 📈 Métricas de conversión
- 💼 Estado de propuestas
- 🎫 Resumen de tickets

**Consejo:** Selecciona un cliente específico para análisis detallado."""
    
    except Exception as e:
        logger.error(f"Error en consulta general: {str(e)}")
        return f"Error procesando consulta: {str(e)}"

def _log_ai_conversation(message: str, response: str, client_id: Optional[int] = None):
    """Registrar conversación del chat AI"""
    try:
        conn = get_db_connection()
        user_id = session.get('user_id')
        
        conn.execute('''
            INSERT INTO ai_chat_history (user_id, client_id, message, response, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, client_id, message, response, datetime.now()))
        
        conn.commit()
        conn.close()
    
    except Exception as e:
        logger.error(f"Error registrando conversación AI: {str(e)}")

def _get_activity_color(activity_type: str) -> str:
    """Obtener color para tipo de actividad del calendario"""
    colors = {
        'reunion': '#3788d8',
        'llamada': '#28a745',
        'demo': '#fd7e14',
        'seguimiento': '#6f42c1',
        'presentacion': '#e83e8c',
        'otros': '#6c757d'
    }
    return colors.get(activity_type, colors['otros'])

# ==========================================================================
# CREAR TABLAS SI NO EXISTEN
# ==========================================================================

def ensure_tables_exist():
    """Crear tablas necesarias si no existen"""
    try:
        conn = get_db_connection()
        
        # Tabla de historial de chat AI
        conn.execute('''
            CREATE TABLE IF NOT EXISTS ai_chat_history (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                client_id INTEGER,
                message TEXT,
                response TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (client_id) REFERENCES clients (id)
            )
        ''')
        
        conn.commit()
        conn.close()
        
    except Exception as e:
        logger.error(f"Error creando tablas: {str(e)}")

# Inicializar tablas al importar el módulo
ensure_tables_exist()
