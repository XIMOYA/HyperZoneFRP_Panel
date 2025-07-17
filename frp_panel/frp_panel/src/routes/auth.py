from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from flask_mail import Message, Mail
from datetime import datetime, timedelta
import re
from src.models.user import db, User
from src.models.verification import EmailVerification
from src.models.log import OperationLog

auth_bp = Blueprint('auth', __name__)

def is_valid_email(email):
    """验证邮箱格式"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def is_valid_password(password):
    """验证密码强度"""
    if len(password) < 8:
        return False, "密码长度至少8位"
    if not re.search(r'[A-Za-z]', password):
        return False, "密码必须包含字母"
    if not re.search(r'\d', password):
        return False, "密码必须包含数字"
    return True, ""

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

@auth_bp.route('/send-verification-code', methods=['POST'])
def send_verification_code():
    """发送邮箱验证码"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        purpose = data.get('purpose', 'register')  # register, reset_password
        
        if not email:
            return jsonify({'error': '邮箱不能为空'}), 400
            
        if not is_valid_email(email):
            return jsonify({'error': '邮箱格式不正确'}), 400
        
        # 检查邮箱是否已注册（仅注册时检查）
        if purpose == 'register':
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                return jsonify({'error': '该邮箱已被注册'}), 400
        
        # 检查是否频繁发送验证码
        recent_verification = EmailVerification.query.filter_by(
            email=email, purpose=purpose
        ).filter(
            EmailVerification.created_at > datetime.utcnow() - timedelta(minutes=1)
        ).first()
        
        if recent_verification:
            return jsonify({'error': '请勿频繁发送验证码，请稍后再试'}), 429
        
        # 创建验证码
        verification = EmailVerification(email=email, purpose=purpose)
        db.session.add(verification)
        db.session.commit()
        
        # 发送邮件（这里使用模拟发送，实际项目中需要配置SMTP）
        # TODO: 配置Flask-Mail发送真实邮件
        print(f"发送验证码到 {email}: {verification.code}")
        
        return jsonify({
            'message': '验证码已发送，请查收邮件',
            'expires_in': 600  # 10分钟
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'发送验证码失败: {str(e)}'}), 500

@auth_bp.route('/register', methods=['POST'])
def register():
    """用户注册"""
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        verification_code = data.get('verification_code', '')
        
        # 验证输入
        if not all([username, email, password, verification_code]):
            return jsonify({'error': '所有字段都不能为空'}), 400
            
        if not is_valid_email(email):
            return jsonify({'error': '邮箱格式不正确'}), 400
            
        is_valid, password_error = is_valid_password(password)
        if not is_valid:
            return jsonify({'error': password_error}), 400
        
        # 验证验证码
        verification = EmailVerification.query.filter_by(
            email=email, purpose='register'
        ).order_by(EmailVerification.created_at.desc()).first()
        
        if not verification or not verification.is_valid(verification_code):
            return jsonify({'error': '验证码无效或已过期'}), 400
        
        # 检查用户名和邮箱是否已存在
        if User.query.filter_by(username=username).first():
            return jsonify({'error': '用户名已存在'}), 400
            
        if User.query.filter_by(email=email).first():
            return jsonify({'error': '邮箱已被注册'}), 400
        
        # 创建用户
        user = User(username=username, email=email, email_verified=True)
        user.set_password(password)
        
        # 标记验证码为已使用
        verification.mark_as_used()
        
        db.session.add(user)
        db.session.commit()
        
        # 记录日志
        log_operation(user.id, 'create', 'user', user.id, username)
        
        return jsonify({
            'message': '注册成功',
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'注册失败: {str(e)}'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """用户登录"""
    try:
        data = request.get_json()
        username_or_email = data.get('username', '').strip()
        password = data.get('password', '')
        
        if not all([username_or_email, password]):
            return jsonify({'error': '用户名/邮箱和密码不能为空'}), 400
        
        # 查找用户（支持用户名或邮箱登录）
        user = User.query.filter(
            (User.username == username_or_email) | 
            (User.email == username_or_email.lower())
        ).first()
        
        if not user or not user.check_password(password):
            log_operation(None, 'login', 'user', None, username_or_email, 
                         status='failed', error_message='用户名或密码错误')
            return jsonify({'error': '用户名或密码错误'}), 401
        
        if not user.is_active:
            return jsonify({'error': '账户已被禁用'}), 403
        
        # 更新最后登录时间
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        # 生成JWT token
        access_token = create_access_token(
            identity=user.id,
            expires_delta=timedelta(days=7)
        )
        
        # 记录日志
        log_operation(user.id, 'login', 'user', user.id, user.username)
        
        return jsonify({
            'message': '登录成功',
            'access_token': access_token,
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'登录失败: {str(e)}'}), 500

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """获取用户信息"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': '用户不存在'}), 404
        
        return jsonify({
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'获取用户信息失败: {str(e)}'}), 500

@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """更新用户信息"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': '用户不存在'}), 404
        
        data = request.get_json()
        
        # 更新允许的字段
        if 'real_name' in data:
            user.real_name = data['real_name'].strip()
        if 'phone' in data:
            user.phone = data['phone'].strip()
        if 'id_card' in data:
            user.id_card = data['id_card'].strip()
            
        db.session.commit()
        
        # 记录日志
        log_operation(user_id, 'update', 'user', user_id, user.username)
        
        return jsonify({
            'message': '信息更新成功',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'更新失败: {str(e)}'}), 500

