from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import json
from datetime import datetime
from src.models.user import db, User
from src.models.node import Node
from src.models.tunnel import Tunnel
from src.models.log import OperationLog

tunnels_bp = Blueprint('tunnels', __name__)

def log_operation(user_id, action, resource_type, resource_id=None, resource_name=None, 
                 details=None, status='success', error_message=None):
    """记录操作日志"""
    try:
        log = OperationLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            resource_name=resource_name,
            details=details,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            status=status,
            error_message=error_message
        )
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        print(f"记录日志失败: {e}")

@tunnels_bp.route('/tunnels', methods=['GET'])
@jwt_required()
def get_tunnels():
    """获取隧道列表"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': '用户不存在'}), 404
        
        # 获取查询参数
        node_id = request.args.get('node_id', type=int)
        tunnel_type = request.args.get('type')
        status = request.args.get('status')
        
        # 构建查询
        query = Tunnel.query
        
        # 管理员可以查看所有隧道，普通用户只能查看自己的隧道
        if not user.is_admin:
            query = query.filter_by(user_id=user_id)
        
        # 按节点过滤
        if node_id:
            query = query.filter_by(node_id=node_id)
        
        # 按类型过滤
        if tunnel_type:
            query = query.filter_by(type=tunnel_type)
        
        # 按状态过滤
        if status:
            query = query.filter_by(status=status)
        
        tunnels = query.order_by(Tunnel.created_at.desc()).all()
        
        # 包含节点信息
        result = []
        for tunnel in tunnels:
            tunnel_dict = tunnel.to_dict()
            if tunnel.node:
                tunnel_dict['node'] = {
                    'id': tunnel.node.id,
                    'name': tunnel.node.name,
                    'host': tunnel.node.host,
                    'status': tunnel.node.status
                }
            result.append(tunnel_dict)
        
        return jsonify({
            'tunnels': result
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'获取隧道列表失败: {str(e)}'}), 500

@tunnels_bp.route('/tunnels', methods=['POST'])
@jwt_required()
def create_tunnel():
    """创建隧道"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # 验证必需字段
        required_fields = ['name', 'type', 'local_port', 'node_id']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} 不能为空'}), 400
        
        # 验证节点是否存在（所有用户都可以使用任何节点创建隧道）
        node = Node.query.get(data['node_id'])
        if not node:
            return jsonify({'error': '节点不存在'}), 404
        
        # 检查隧道名称是否重复
        existing_tunnel = Tunnel.query.filter_by(
            name=data['name'], 
            user_id=user_id
        ).first()
        
        if existing_tunnel:
            return jsonify({'error': '隧道名称已存在'}), 400
        
        # 验证隧道类型
        valid_types = ['tcp', 'udp', 'http', 'https']
        if data['type'] not in valid_types:
            return jsonify({'error': f'隧道类型必须是: {", ".join(valid_types)}'}), 400
        
        # 处理自定义域名
        custom_domains = data.get('custom_domains')
        if custom_domains:
            if isinstance(custom_domains, list):
                custom_domains = json.dumps(custom_domains)
            elif not isinstance(custom_domains, str):
                return jsonify({'error': '自定义域名格式错误'}), 400
        
        # 创建隧道
        tunnel = Tunnel(
            name=data['name'],
            type=data['type'],
            local_ip=data.get('local_ip', '127.0.0.1'),
            local_port=data['local_port'],
            remote_port=data.get('remote_port'),
            custom_domains=custom_domains,
            subdomain=data.get('subdomain'),
            description=data.get('description'),
            node_id=data['node_id'],
            user_id=user_id
        )
        
        db.session.add(tunnel)
        db.session.commit()
        
        # 记录日志
        log_operation(user_id, 'create', 'tunnel', tunnel.id, tunnel.name)
        
        return jsonify({
            'message': '隧道创建成功',
            'tunnel': tunnel.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'创建隧道失败: {str(e)}'}), 500

@tunnels_bp.route('/tunnels/<int:tunnel_id>', methods=['GET'])
@jwt_required()
def get_tunnel(tunnel_id):
    """获取单个隧道信息"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': '用户不存在'}), 404
        
        # 查找隧道
        if user.is_admin:
            tunnel = Tunnel.query.get(tunnel_id)
        else:
            tunnel = Tunnel.query.filter_by(id=tunnel_id, user_id=user_id).first()
        
        if not tunnel:
            return jsonify({'error': '隧道不存在'}), 404
        
        tunnel_dict = tunnel.to_dict()
        if tunnel.node:
            tunnel_dict['node'] = tunnel.node.to_dict()
        
        return jsonify({
            'tunnel': tunnel_dict
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'获取隧道信息失败: {str(e)}'}), 500

@tunnels_bp.route('/tunnels/<int:tunnel_id>', methods=['PUT'])
@jwt_required()
def update_tunnel(tunnel_id):
    """更新隧道"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': '用户不存在'}), 404
        
        # 查找隧道
        if user.is_admin:
            tunnel = Tunnel.query.get(tunnel_id)
        else:
            tunnel = Tunnel.query.filter_by(id=tunnel_id, user_id=user_id).first()
        
        if not tunnel:
            return jsonify({'error': '隧道不存在'}), 404
        
        data = request.get_json()
        
        # 更新字段
        if 'name' in data:
            # 检查名称是否重复
            existing_tunnel = Tunnel.query.filter_by(
                name=data['name'], 
                user_id=user_id
            ).filter(Tunnel.id != tunnel_id).first()
            
            if existing_tunnel:
                return jsonify({'error': '隧道名称已存在'}), 400
            
            tunnel.name = data['name']
        
        if 'type' in data:
            valid_types = ['tcp', 'udp', 'http', 'https']
            if data['type'] not in valid_types:
                return jsonify({'error': f'隧道类型必须是: {", ".join(valid_types)}'}), 400
            tunnel.type = data['type']
        
        if 'local_ip' in data:
            tunnel.local_ip = data['local_ip']
        if 'local_port' in data:
            tunnel.local_port = data['local_port']
        if 'remote_port' in data:
            tunnel.remote_port = data['remote_port']
        if 'subdomain' in data:
            tunnel.subdomain = data['subdomain']
        if 'description' in data:
            tunnel.description = data['description']
        
        # 处理自定义域名
        if 'custom_domains' in data:
            custom_domains = data['custom_domains']
            if custom_domains:
                if isinstance(custom_domains, list):
                    custom_domains = json.dumps(custom_domains)
                elif not isinstance(custom_domains, str):
                    return jsonify({'error': '自定义域名格式错误'}), 400
            tunnel.custom_domains = custom_domains
        
        tunnel.updated_at = datetime.utcnow()
        db.session.commit()
        
        # 记录日志
        log_operation(user_id, 'update', 'tunnel', tunnel.id, tunnel.name)
        
        return jsonify({
            'message': '隧道更新成功',
            'tunnel': tunnel.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'更新隧道失败: {str(e)}'}), 500

@tunnels_bp.route('/tunnels/<int:tunnel_id>', methods=['DELETE'])
@jwt_required()
def delete_tunnel(tunnel_id):
    """删除隧道"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': '用户不存在'}), 404
        
        # 查找隧道
        if user.is_admin:
            tunnel = Tunnel.query.get(tunnel_id)
        else:
            tunnel = Tunnel.query.filter_by(id=tunnel_id, user_id=user_id).first()
        
        if not tunnel:
            return jsonify({'error': '隧道不存在'}), 404
        
        tunnel_name = tunnel.name
        
        db.session.delete(tunnel)
        db.session.commit()
        
        # 记录日志
        log_operation(user_id, 'delete', 'tunnel', tunnel_id, tunnel_name)
        
        return jsonify({
            'message': '隧道删除成功'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'删除隧道失败: {str(e)}'}), 500

@tunnels_bp.route('/tunnels/<int:tunnel_id>/start', methods=['POST'])
@jwt_required()
def start_tunnel(tunnel_id):
    """启动隧道"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': '用户不存在'}), 404
        
        # 查找隧道
        if user.is_admin:
            tunnel = Tunnel.query.get(tunnel_id)
        else:
            tunnel = Tunnel.query.filter_by(id=tunnel_id, user_id=user_id).first()
        
        if not tunnel:
            return jsonify({'error': '隧道不存在'}), 404
        
        # TODO: 实现实际的隧道启动逻辑
        # 这里需要与frpc进行交互，启动对应的代理
        
        tunnel.status = 'running'
        tunnel.updated_at = datetime.utcnow()
        db.session.commit()
        
        # 记录日志
        log_operation(user_id, 'start', 'tunnel', tunnel.id, tunnel.name)
        
        return jsonify({
            'message': '隧道启动成功',
            'tunnel': tunnel.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'启动隧道失败: {str(e)}'}), 500

@tunnels_bp.route('/tunnels/<int:tunnel_id>/stop', methods=['POST'])
@jwt_required()
def stop_tunnel(tunnel_id):
    """停止隧道"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': '用户不存在'}), 404
        
        # 查找隧道
        if user.is_admin:
            tunnel = Tunnel.query.get(tunnel_id)
        else:
            tunnel = Tunnel.query.filter_by(id=tunnel_id, user_id=user_id).first()
        
        if not tunnel:
            return jsonify({'error': '隧道不存在'}), 404
        
        # TODO: 实现实际的隧道停止逻辑
        # 这里需要与frpc进行交互，停止对应的代理
        
        tunnel.status = 'stopped'
        tunnel.updated_at = datetime.utcnow()
        db.session.commit()
        
        # 记录日志
        log_operation(user_id, 'stop', 'tunnel', tunnel.id, tunnel.name)
        
        return jsonify({
            'message': '隧道停止成功',
            'tunnel': tunnel.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'停止隧道失败: {str(e)}'}), 500

@tunnels_bp.route('/tunnels/batch', methods=['POST'])
@jwt_required()
def batch_operation():
    """批量操作隧道"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': '用户不存在'}), 404
        
        data = request.get_json()
        tunnel_ids = data.get('tunnel_ids', [])
        operation = data.get('operation')  # start, stop, delete
        
        if not tunnel_ids:
            return jsonify({'error': '请选择要操作的隧道'}), 400
        
        if operation not in ['start', 'stop', 'delete']:
            return jsonify({'error': '无效的操作类型'}), 400
        
        # 查找隧道
        if user.is_admin:
            tunnels = Tunnel.query.filter(Tunnel.id.in_(tunnel_ids)).all()
        else:
            tunnels = Tunnel.query.filter(
                Tunnel.id.in_(tunnel_ids),
                Tunnel.user_id == user_id
            ).all()
        
        if not tunnels:
            return jsonify({'error': '未找到可操作的隧道'}), 404
        
        success_count = 0
        failed_count = 0
        
        for tunnel in tunnels:
            try:
                if operation == 'start':
                    tunnel.status = 'running'
                elif operation == 'stop':
                    tunnel.status = 'stopped'
                elif operation == 'delete':
                    db.session.delete(tunnel)
                
                tunnel.updated_at = datetime.utcnow()
                
                # 记录日志
                log_operation(user_id, operation, 'tunnel', tunnel.id, tunnel.name)
                
                success_count += 1
                
            except Exception as e:
                failed_count += 1
                print(f"批量操作失败: {e}")
        
        db.session.commit()
        
        return jsonify({
            'message': f'批量操作完成，成功: {success_count}，失败: {failed_count}',
            'success_count': success_count,
            'failed_count': failed_count
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'批量操作失败: {str(e)}'}), 500

