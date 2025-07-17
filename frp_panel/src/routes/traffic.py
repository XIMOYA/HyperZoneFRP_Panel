from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta, date
from sqlalchemy import func
from src.models.user import db, User
from src.models.tunnel import Tunnel
from src.models.traffic import TrafficLog, TrafficSummary

traffic_bp = Blueprint('traffic', __name__)

@traffic_bp.route('/traffic/realtime', methods=['GET'])
@jwt_required()
def get_realtime_traffic():
    """获取实时流量数据"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': '用户不存在'}), 404
        
        # 获取参数
        tunnel_id = request.args.get('tunnel_id')
        
        # 构建查询条件
        query = TrafficLog.query.filter_by(user_id=user_id)
        
        if tunnel_id:
            query = query.filter_by(tunnel_id=tunnel_id)
        
        # 获取最近10分钟的数据
        ten_minutes_ago = datetime.utcnow() - timedelta(minutes=10)
        logs = query.filter(TrafficLog.timestamp >= ten_minutes_ago).order_by(TrafficLog.timestamp).all()
        
        return jsonify({
            'traffic_logs': [log.to_dict() for log in logs]
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'获取实时流量数据失败: {str(e)}'}), 500

@traffic_bp.route('/traffic/daily', methods=['GET'])
@jwt_required()
def get_daily_traffic():
    """获取每日流量统计"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': '用户不存在'}), 404
        
        # 获取参数
        tunnel_id = request.args.get('tunnel_id')
        days = int(request.args.get('days', 7))  # 默认7天
        
        # 限制最大查询天数
        if days > 30:
            days = 30
        
        # 计算开始日期
        start_date = date.today() - timedelta(days=days-1)
        
        # 构建查询条件
        query = TrafficSummary.query.filter_by(user_id=user_id)
        
        if tunnel_id:
            query = query.filter_by(tunnel_id=tunnel_id)
        
        # 获取日期范围内的数据
        summaries = query.filter(TrafficSummary.date >= start_date).order_by(TrafficSummary.date).all()
        
        return jsonify({
            'traffic_summaries': [summary.to_dict() for summary in summaries]
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'获取每日流量统计失败: {str(e)}'}), 500

@traffic_bp.route('/traffic/summary', methods=['GET'])
@jwt_required()
def get_traffic_summary():
    """获取流量汇总统计"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': '用户不存在'}), 404
        
        # 获取用户所有隧道的总流量
        total_upload = db.session.query(func.sum(TrafficSummary.upload)).filter_by(user_id=user_id).scalar() or 0
        total_download = db.session.query(func.sum(TrafficSummary.download)).filter_by(user_id=user_id).scalar() or 0
        
        # 获取用户所有隧道
        tunnels = Tunnel.query.filter_by(user_id=user_id).all()
        
        # 获取每个隧道的流量统计
        tunnel_stats = []
        for tunnel in tunnels:
            tunnel_upload = db.session.query(func.sum(TrafficSummary.upload)).filter_by(
                user_id=user_id, tunnel_id=tunnel.id).scalar() or 0
            tunnel_download = db.session.query(func.sum(TrafficSummary.download)).filter_by(
                user_id=user_id, tunnel_id=tunnel.id).scalar() or 0
            
            tunnel_stats.append({
                'tunnel_id': tunnel.id,
                'tunnel_name': tunnel.name,
                'upload': tunnel_upload,
                'download': tunnel_download,
                'total': tunnel_upload + tunnel_download
            })
        
        # 按总流量排序
        tunnel_stats.sort(key=lambda x: x['total'], reverse=True)
        
        return jsonify({
            'total_upload': total_upload,
            'total_download': total_download,
            'total': total_upload + total_download,
            'tunnel_stats': tunnel_stats
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'获取流量汇总统计失败: {str(e)}'}), 500

@traffic_bp.route('/traffic/log', methods=['POST'])
@jwt_required()
def log_traffic():
    """记录流量数据（内部API，由frpc客户端调用）"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': '用户不存在'}), 404
        
        data = request.get_json()
        
        # 验证必需字段
        required_fields = ['tunnel_id', 'upload', 'download']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} 不能为空'}), 400
        
        # 验证隧道是否存在且属于当前用户
        tunnel = Tunnel.query.filter_by(id=data['tunnel_id'], user_id=user_id).first()
        if not tunnel:
            return jsonify({'error': '隧道不存在或无权限'}), 404
        
        # 创建流量日志
        traffic_log = TrafficLog(
            user_id=user_id,
            tunnel_id=data['tunnel_id'],
            upload=data['upload'],
            download=data['download'],
            timestamp=datetime.utcnow()
        )
        
        db.session.add(traffic_log)
        
        # 更新用户总流量
        user.total_traffic += data['upload'] + data['download']
        
        # 更新或创建每日流量汇总
        today = date.today()
        summary = TrafficSummary.query.filter_by(
            user_id=user_id,
            tunnel_id=data['tunnel_id'],
            date=today
        ).first()
        
        if summary:
            summary.upload += data['upload']
            summary.download += data['download']
        else:
            summary = TrafficSummary(
                user_id=user_id,
                tunnel_id=data['tunnel_id'],
                upload=data['upload'],
                download=data['download'],
                date=today
            )
            db.session.add(summary)
        
        db.session.commit()
        
        return jsonify({
            'message': '流量数据记录成功'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'记录流量数据失败: {str(e)}'}), 500

