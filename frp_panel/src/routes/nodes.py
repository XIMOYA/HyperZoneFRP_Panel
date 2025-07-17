from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import requests
from datetime import datetime
from src.models.user import db, User
from src.models.node import Node
from src.models.log import OperationLog

nodes_bp = Blueprint('nodes', __name__)

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

def check_node_status(node):
    """检查节点状态"""
    try:
        if not node.dashboard_port:
            return 'unknown'
            
        url = f"http://{node.host}:{node.dashboard_port}/api/serverinfo"
        
        # 如果有认证信息，添加基础认证
        auth = None
        if node.dashboard_user and node.dashboard_password:
            auth = (node.dashboard_user, node.dashboard_password)
            
        response = requests.get(url, auth=auth, timeout=5)
        
        if response.status_code == 200:
            return 'online'
        else:
            return 'error'
            
    except requests.exceptions.RequestException:
        return 'offline'
    except Exception:
        return 'error'

@nodes_bp.route('/nodes', methods=['GET'])
@jwt_required()
def get_nodes():
    """获取节点列表"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': '用户不存在'}), 404
        
        # 所有用户都可以查看节点列表
        nodes = Node.query.all()
        
        # 更新节点状态（异步处理，这里简化为同步）
        for node in nodes:
            old_status = node.status
            new_status = check_node_status(node)
            if old_status != new_status:
                node.status = new_status
                node.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'nodes': [node.to_dict() for node in nodes]
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'获取节点列表失败: {str(e)}'}), 500

@nodes_bp.route('/nodes', methods=['POST'])
@jwt_required()
def create_node():
    """创建节点"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': '用户不存在'}), 404
        
        # 只有管理员可以创建节点
        if not user.is_admin:
            return jsonify({'error': '权限不足，只有管理员可以创建节点'}), 403
        
        data = request.get_json()
        
        # 验证必需字段
        required_fields = ['name', 'host', 'port']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} 不能为空'}), 400
        
        # 检查节点名称是否重复
        existing_node = Node.query.filter_by(name=data['name']).first()
        
        if existing_node:
            return jsonify({'error': '节点名称已存在'}), 400
        
        # 创建节点
        node = Node(
            name=data['name'],
            host=data['host'],
            port=data['port'],
            dashboard_port=data.get('dashboard_port'),
            dashboard_user=data.get('dashboard_user'),
            dashboard_password=data.get('dashboard_password'),
            token=data.get('token'),
            region=data.get('region'),
            description=data.get('description'),
            user_id=user_id
        )
        
        # 检查节点状态
        node.status = check_node_status(node)
        
        db.session.add(node)
        db.session.commit()
        
        # 记录日志
        log_operation(user_id, 'create', 'node', node.id, node.name)
        
        return jsonify({
            'message': '节点创建成功',
            'node': node.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'创建节点失败: {str(e)}'}), 500

@nodes_bp.route('/nodes/<int:node_id>', methods=['GET'])
@jwt_required()
def get_node(node_id):
    """获取单个节点信息"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': '用户不存在'}), 404
        
        # 所有用户都可以查看节点详情
        node = Node.query.get(node_id)
        
        if not node:
            return jsonify({'error': '节点不存在'}), 404
        
        # 更新节点状态
        node.status = check_node_status(node)
        node.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'node': node.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'获取节点信息失败: {str(e)}'}), 500

@nodes_bp.route('/nodes/<int:node_id>', methods=['PUT'])
@jwt_required()
def update_node(node_id):
    """更新节点"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': '用户不存在'}), 404
        
        # 只有管理员可以修改节点
        if not user.is_admin:
            return jsonify({'error': '权限不足，只有管理员可以修改节点'}), 403
        
        node = Node.query.get(node_id)
        
        if not node:
            return jsonify({'error': '节点不存在'}), 404
        
        data = request.get_json()
        
        # 更新字段
        if 'name' in data:
            # 检查名称是否重复
            existing_node = Node.query.filter_by(name=data['name']).filter(Node.id != node_id).first()
            
            if existing_node:
                return jsonify({'error': '节点名称已存在'}), 400
            
            node.name = data['name']
        
        if 'host' in data:
            node.host = data['host']
        if 'port' in data:
            node.port = data['port']
        if 'dashboard_port' in data:
            node.dashboard_port = data['dashboard_port']
        if 'dashboard_user' in data:
            node.dashboard_user = data['dashboard_user']
        if 'dashboard_password' in data:
            node.dashboard_password = data['dashboard_password']
        if 'token' in data:
            node.token = data['token']
        if 'region' in data:
            node.region = data['region']
        if 'description' in data:
            node.description = data['description']
        
        # 更新状态
        node.status = check_node_status(node)
        node.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        # 记录日志
        log_operation(user_id, 'update', 'node', node.id, node.name)
        
        return jsonify({
            'message': '节点更新成功',
            'node': node.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'更新节点失败: {str(e)}'}), 500

@nodes_bp.route('/nodes/<int:node_id>', methods=['DELETE'])
@jwt_required()
def delete_node(node_id):
    """删除节点"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': '用户不存在'}), 404
        
        # 只有管理员可以删除节点
        if not user.is_admin:
            return jsonify({'error': '权限不足，只有管理员可以删除节点'}), 403
        
        node = Node.query.get(node_id)
        
        if not node:
            return jsonify({'error': '节点不存在'}), 404
        
        # 检查是否有关联的隧道
        if node.tunnels:
            return jsonify({'error': '请先删除该节点下的所有隧道'}), 400
        
        node_name = node.name
        
        db.session.delete(node)
        db.session.commit()
        
        # 记录日志
        log_operation(user_id, 'delete', 'node', node_id, node_name)
        
        return jsonify({
            'message': '节点删除成功'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'删除节点失败: {str(e)}'}), 500

@nodes_bp.route('/nodes/<int:node_id>/status', methods=['GET'])
@jwt_required()
def get_node_status(node_id):
    """获取节点详细状态信息"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': '用户不存在'}), 404
        
        # 所有用户都可以查看节点状态
        node = Node.query.get(node_id)
        
        if not node:
            return jsonify({'error': '节点不存在'}), 404
        
        # 获取详细状态信息
        status_info = {
            'status': 'offline',
            'server_info': None,
            'proxies': [],
            'error': None
        }
        
        try:
            if node.dashboard_port:
                base_url = f"http://{node.host}:{node.dashboard_port}"
                auth = None
                if node.dashboard_user and node.dashboard_password:
                    auth = (node.dashboard_user, node.dashboard_password)
                
                # 获取服务器信息
                response = requests.get(f"{base_url}/api/serverinfo", auth=auth, timeout=5)
                if response.status_code == 200:
                    status_info['status'] = 'online'
                    status_info['server_info'] = response.json()
                
                # 获取代理信息
                response = requests.get(f"{base_url}/api/proxy/tcp", auth=auth, timeout=5)
                if response.status_code == 200:
                    status_info['proxies'].extend(response.json().get('proxies', []))
                
                response = requests.get(f"{base_url}/api/proxy/http", auth=auth, timeout=5)
                if response.status_code == 200:
                    status_info['proxies'].extend(response.json().get('proxies', []))
                    
        except requests.exceptions.RequestException as e:
            status_info['error'] = str(e)
        except Exception as e:
            status_info['error'] = str(e)
        
        # 更新节点状态
        node.status = status_info['status']
        node.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify(status_info), 200
        
    except Exception as e:
        return jsonify({'error': f'获取节点状态失败: {str(e)}'}), 500

