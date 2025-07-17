from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from src.models.user import db, User
from src.models.package import Package, UserPackage
from src.models.user_group import UserGroup
from src.models.log import OperationLog

packages_bp = Blueprint('packages', __name__)

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

@packages_bp.route('/packages', methods=['GET'])
@jwt_required()
def get_packages():
    """获取套餐列表"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': '用户不存在'}), 404
        
        # 获取所有激活的套餐
        packages = Package.query.filter_by(is_active=True).all()
        
        return jsonify({
            'packages': [package.to_dict() for package in packages]
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'获取套餐列表失败: {str(e)}'}), 500

@packages_bp.route('/packages/<int:package_id>', methods=['GET'])
@jwt_required()
def get_package(package_id):
    """获取单个套餐详情"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': '用户不存在'}), 404
        
        package = Package.query.get(package_id)
        
        if not package:
            return jsonify({'error': '套餐不存在'}), 404
        
        return jsonify({
            'package': package.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'获取套餐详情失败: {str(e)}'}), 500

@packages_bp.route('/packages', methods=['POST'])
@jwt_required()
def create_package():
    """创建套餐（仅管理员）"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': '用户不存在'}), 404
        
        # 检查权限
        if not user.is_admin:
            return jsonify({'error': '权限不足，只有管理员可以创建套餐'}), 403
        
        data = request.get_json()
        
        # 验证必需字段
        required_fields = ['name', 'price', 'duration', 'max_tunnels', 'max_traffic']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} 不能为空'}), 400
        
        # 检查套餐名称是否重复
        existing_package = Package.query.filter_by(name=data['name']).first()
        if existing_package:
            return jsonify({'error': '套餐名称已存在'}), 400
        
        # 创建套餐
        package = Package(
            name=data['name'],
            price=data['price'],
            duration=data['duration'],
            max_tunnels=data['max_tunnels'],
            max_traffic=data['max_traffic'],
            upload_speed_limit=data.get('upload_speed_limit'),
            download_speed_limit=data.get('download_speed_limit'),
            description=data.get('description')
        )
        
        db.session.add(package)
        db.session.commit()
        
        # 记录日志
        log_operation(user_id, 'create', 'package', package.id, package.name)
        
        return jsonify({
            'message': '套餐创建成功',
            'package': package.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'创建套餐失败: {str(e)}'}), 500

@packages_bp.route('/packages/<int:package_id>', methods=['PUT'])
@jwt_required()
def update_package(package_id):
    """更新套餐（仅管理员）"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': '用户不存在'}), 404
        
        # 检查权限
        if not user.is_admin:
            return jsonify({'error': '权限不足，只有管理员可以更新套餐'}), 403
        
        package = Package.query.get(package_id)
        
        if not package:
            return jsonify({'error': '套餐不存在'}), 404
        
        data = request.get_json()
        
        # 更新字段
        if 'name' in data:
            # 检查名称是否重复
            existing_package = Package.query.filter_by(name=data['name']).filter(Package.id != package_id).first()
            if existing_package:
                return jsonify({'error': '套餐名称已存在'}), 400
            
            package.name = data['name']
        
        if 'price' in data:
            package.price = data['price']
        if 'duration' in data:
            package.duration = data['duration']
        if 'max_tunnels' in data:
            package.max_tunnels = data['max_tunnels']
        if 'max_traffic' in data:
            package.max_traffic = data['max_traffic']
        if 'upload_speed_limit' in data:
            package.upload_speed_limit = data['upload_speed_limit']
        if 'download_speed_limit' in data:
            package.download_speed_limit = data['download_speed_limit']
        if 'description' in data:
            package.description = data['description']
        if 'is_active' in data:
            package.is_active = data['is_active']
        
        package.updated_at = datetime.utcnow()
        db.session.commit()
        
        # 记录日志
        log_operation(user_id, 'update', 'package', package.id, package.name)
        
        return jsonify({
            'message': '套餐更新成功',
            'package': package.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'更新套餐失败: {str(e)}'}), 500

@packages_bp.route('/packages/<int:package_id>', methods=['DELETE'])
@jwt_required()
def delete_package(package_id):
    """删除套餐（仅管理员）"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': '用户不存在'}), 404
        
        # 检查权限
        if not user.is_admin:
            return jsonify({'error': '权限不足，只有管理员可以删除套餐'}), 403
        
        package = Package.query.get(package_id)
        
        if not package:
            return jsonify({'error': '套餐不存在'}), 404
        
        # 检查是否有用户正在使用该套餐
        active_user_packages = UserPackage.query.filter_by(
            package_id=package_id,
            is_active=True
        ).first()
        
        if active_user_packages:
            return jsonify({'error': '该套餐正在被用户使用，无法删除'}), 400
        
        package_name = package.name
        
        db.session.delete(package)
        db.session.commit()
        
        # 记录日志
        log_operation(user_id, 'delete', 'package', package_id, package_name)
        
        return jsonify({
            'message': '套餐删除成功'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'删除套餐失败: {str(e)}'}), 500

@packages_bp.route('/user/packages', methods=['GET'])
@jwt_required()
def get_user_packages():
    """获取当前用户的套餐"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': '用户不存在'}), 404
        
        # 获取用户的套餐
        user_packages = UserPackage.query.filter_by(user_id=user_id).all()
        
        # 获取套餐详情
        result = []
        for user_package in user_packages:
            package = Package.query.get(user_package.package_id)
            if package:
                data = user_package.to_dict()
                data['package'] = package.to_dict()
                result.append(data)
        
        return jsonify({
            'user_packages': result
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'获取用户套餐失败: {str(e)}'}), 500

@packages_bp.route('/packages/<int:package_id>/purchase', methods=['POST'])
@jwt_required()
def purchase_package(package_id):
    """购买套餐"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': '用户不存在'}), 404
        
        package = Package.query.get(package_id)
        
        if not package:
            return jsonify({'error': '套餐不存在'}), 404
        
        if not package.is_active:
            return jsonify({'error': '该套餐已下架'}), 400
        
        data = request.get_json()
        payment_method = data.get('payment_method', 'unknown')
        
        # 计算结束日期
        start_date = datetime.utcnow()
        end_date = start_date + timedelta(days=package.duration)
        
        # 创建用户套餐记录
        user_package = UserPackage(
            user_id=user_id,
            package_id=package_id,
            start_date=start_date,
            end_date=end_date,
            payment_method=payment_method,
            payment_status='pending'  # 初始状态为待支付
        )
        
        db.session.add(user_package)
        db.session.commit()
        
        # 记录日志
        log_operation(user_id, 'purchase', 'package', package.id, package.name)
        
        # TODO: 集成支付系统，这里简化为直接支付成功
        user_package.payment_status = 'success'
        db.session.commit()
        
        # 查找或创建对应的用户组
        user_group = UserGroup.query.filter_by(name=f"{package.name}组").first()
        if not user_group:
            user_group = UserGroup(
                name=f"{package.name}组",
                max_tunnels=package.max_tunnels,
                max_traffic=package.max_traffic,
                upload_speed_limit=package.upload_speed_limit,
                download_speed_limit=package.download_speed_limit,
                description=f"购买{package.name}套餐的用户组"
            )
            db.session.add(user_group)
            db.session.commit()
        
        # 更新用户组
        user.user_group_id = user_group.id
        db.session.commit()
        
        return jsonify({
            'message': '套餐购买成功',
            'user_package': user_package.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'购买套餐失败: {str(e)}'}), 500

