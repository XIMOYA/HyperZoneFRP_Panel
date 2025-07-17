from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from src.models.user import db, User
from src.models.user_group import UserGroup
from src.models.log import OperationLog

user_groups_bp = Blueprint('user_groups', __name__)

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

@user_groups_bp.route('/user-groups', methods=['GET'])
@jwt_required()
def get_user_groups():
    """获取用户组列表（仅管理员）"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': '用户不存在'}), 404
        
        # 检查权限
        if not user.is_admin:
            return jsonify({'error': '权限不足，只有管理员可以查看所有用户组'}), 403
        
        user_groups = UserGroup.query.all()
        
        return jsonify({
            'user_groups': [group.to_dict() for group in user_groups]
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'获取用户组列表失败: {str(e)}'}), 500

@user_groups_bp.route('/user-groups/<int:group_id>', methods=['GET'])
@jwt_required()
def get_user_group(group_id):
    """获取单个用户组详情（仅管理员）"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': '用户不存在'}), 404
        
        # 检查权限
        if not user.is_admin:
            return jsonify({'error': '权限不足，只有管理员可以查看用户组详情'}), 403
        
        user_group = UserGroup.query.get(group_id)
        
        if not user_group:
            return jsonify({'error': '用户组不存在'}), 404
        
        return jsonify({
            'user_group': user_group.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'获取用户组详情失败: {str(e)}'}), 500

@user_groups_bp.route('/user-groups', methods=['POST'])
@jwt_required()
def create_user_group():
    """创建用户组（仅管理员）"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': '用户不存在'}), 404
        
        # 检查权限
        if not user.is_admin:
            return jsonify({'error': '权限不足，只有管理员可以创建用户组'}), 403
        
        data = request.get_json()
        
        # 验证必需字段
        if not data.get('name'):
            return jsonify({'error': '用户组名称不能为空'}), 400
        
        # 检查用户组名称是否重复
        existing_group = UserGroup.query.filter_by(name=data['name']).first()
        if existing_group:
            return jsonify({'error': '用户组名称已存在'}), 400
        
        # 创建用户组
        user_group = UserGroup(
            name=data['name'],
            max_tunnels=data.get('max_tunnels', 5),
            max_traffic=data.get('max_traffic', 10737418240),  # 默认10GB
            upload_speed_limit=data.get('upload_speed_limit'),
            download_speed_limit=data.get('download_speed_limit'),
            description=data.get('description'),
            is_default=data.get('is_default', False)
        )
        
        # 如果设置为默认组，取消其他默认组
        if user_group.is_default:
            default_groups = UserGroup.query.filter_by(is_default=True).all()
            for group in default_groups:
                group.is_default = False
        
        db.session.add(user_group)
        db.session.commit()
        
        # 记录日志
        log_operation(user_id, 'create', 'user_group', user_group.id, user_group.name)
        
        return jsonify({
            'message': '用户组创建成功',
            'user_group': user_group.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'创建用户组失败: {str(e)}'}), 500

@user_groups_bp.route('/user-groups/<int:group_id>', methods=['PUT'])
@jwt_required()
def update_user_group(group_id):
    """更新用户组（仅管理员）"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': '用户不存在'}), 404
        
        # 检查权限
        if not user.is_admin:
            return jsonify({'error': '权限不足，只有管理员可以更新用户组'}), 403
        
        user_group = UserGroup.query.get(group_id)
        
        if not user_group:
            return jsonify({'error': '用户组不存在'}), 404
        
        data = request.get_json()
        
        # 更新字段
        if 'name' in data:
            # 检查名称是否重复
            existing_group = UserGroup.query.filter_by(name=data['name']).filter(UserGroup.id != group_id).first()
            if existing_group:
                return jsonify({'error': '用户组名称已存在'}), 400
            
            user_group.name = data['name']
        
        if 'max_tunnels' in data:
            user_group.max_tunnels = data['max_tunnels']
        if 'max_traffic' in data:
            user_group.max_traffic = data['max_traffic']
        if 'upload_speed_limit' in data:
            user_group.upload_speed_limit = data['upload_speed_limit']
        if 'download_speed_limit' in data:
            user_group.download_speed_limit = data['download_speed_limit']
        if 'description' in data:
            user_group.description = data['description']
        
        # 处理默认组设置
        if 'is_default' in data:
            if data['is_default'] and not user_group.is_default:
                # 如果设置为默认组，取消其他默认组
                default_groups = UserGroup.query.filter_by(is_default=True).all()
                for group in default_groups:
                    group.is_default = False
            
            user_group.is_default = data['is_default']
        
        user_group.updated_at = datetime.utcnow()
        db.session.commit()
        
        # 记录日志
        log_operation(user_id, 'update', 'user_group', user_group.id, user_group.name)
        
        return jsonify({
            'message': '用户组更新成功',
            'user_group': user_group.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'更新用户组失败: {str(e)}'}), 500

@user_groups_bp.route('/user-groups/<int:group_id>', methods=['DELETE'])
@jwt_required()
def delete_user_group(group_id):
    """删除用户组（仅管理员）"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': '用户不存在'}), 404
        
        # 检查权限
        if not user.is_admin:
            return jsonify({'error': '权限不足，只有管理员可以删除用户组'}), 403
        
        user_group = UserGroup.query.get(group_id)
        
        if not user_group:
            return jsonify({'error': '用户组不存在'}), 404
        
        # 检查是否有用户正在使用该用户组
        users_in_group = User.query.filter_by(user_group_id=group_id).first()
        
        if users_in_group:
            return jsonify({'error': '该用户组正在被用户使用，无法删除'}), 400
        
        # 检查是否为默认组
        if user_group.is_default:
            return jsonify({'error': '默认用户组不能删除'}), 400
        
        group_name = user_group.name
        
        db.session.delete(user_group)
        db.session.commit()
        
        # 记录日志
        log_operation(user_id, 'delete', 'user_group', group_id, group_name)
        
        return jsonify({
            'message': '用户组删除成功'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'删除用户组失败: {str(e)}'}), 500

@user_groups_bp.route('/user-groups/<int:group_id>/users', methods=['GET'])
@jwt_required()
def get_users_in_group(group_id):
    """获取用户组中的用户列表（仅管理员）"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': '用户不存在'}), 404
        
        # 检查权限
        if not user.is_admin:
            return jsonify({'error': '权限不足，只有管理员可以查看用户组成员'}), 403
        
        user_group = UserGroup.query.get(group_id)
        
        if not user_group:
            return jsonify({'error': '用户组不存在'}), 404
        
        # 获取该组的所有用户
        users = User.query.filter_by(user_group_id=group_id).all()
        
        return jsonify({
            'users': [user.to_dict() for user in users]
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'获取用户组成员失败: {str(e)}'}), 500

@user_groups_bp.route('/users/<int:user_id>/group', methods=['PUT'])
@jwt_required()
def assign_user_to_group(user_id):
    """将用户分配到用户组（仅管理员）"""
    try:
        admin_id = get_jwt_identity()
        admin = User.query.get(admin_id)
        
        if not admin:
            return jsonify({'error': '用户不存在'}), 404
        
        # 检查权限
        if not admin.is_admin:
            return jsonify({'error': '权限不足，只有管理员可以分配用户组'}), 403
        
        target_user = User.query.get(user_id)
        
        if not target_user:
            return jsonify({'error': '目标用户不存在'}), 404
        
        data = request.get_json()
        
        if 'group_id' not in data:
            return jsonify({'error': '用户组ID不能为空'}), 400
        
        group_id = data['group_id']
        
        # 如果group_id为null，表示移除用户组
        if group_id is None:
            target_user.user_group_id = None
            db.session.commit()
            
            # 记录日志
            log_operation(admin_id, 'remove_from_group', 'user', target_user.id, target_user.username)
            
            return jsonify({
                'message': '用户已从用户组中移除'
            }), 200
        
        # 验证用户组是否存在
        user_group = UserGroup.query.get(group_id)
        
        if not user_group:
            return jsonify({'error': '用户组不存在'}), 404
        
        # 更新用户的用户组
        target_user.user_group_id = group_id
        db.session.commit()
        
        # 记录日志
        log_operation(
            admin_id, 
            'assign_to_group', 
            'user', 
            target_user.id, 
            target_user.username,
            details=f"分配到用户组: {user_group.name}"
        )
        
        return jsonify({
            'message': '用户已分配到用户组',
            'user': target_user.to_dict(),
            'user_group': user_group.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'分配用户组失败: {str(e)}'}), 500

