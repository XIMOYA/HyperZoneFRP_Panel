from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # 实名认证相关
    real_name = db.Column(db.String(50), nullable=True)
    id_card = db.Column(db.String(18), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    is_verified = db.Column(db.Boolean, default=False)
    
    # 账户状态
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    email_verified = db.Column(db.Boolean, default=False)
    
    # 用户组关联
    user_group_id = db.Column(db.Integer, db.ForeignKey('user_group.id'), nullable=True)
    
    # 流量统计
    total_traffic = db.Column(db.BigInteger, default=0)  # 总流量使用（字节）
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    
    # 反向关联
    nodes = db.relationship('Node', backref='user', lazy=True)
    tunnels = db.relationship('Tunnel', backref='user', lazy=True)
    operation_logs = db.relationship('OperationLog', backref='user', lazy=True)
    user_packages = db.relationship('UserPackage', backref='user', lazy=True)
    traffic_logs = db.relationship('TrafficLog', backref='user', lazy=True)

    def set_password(self, password):
        """设置密码"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """验证密码"""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

    def to_dict(self, include_sensitive=False):
        data = {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'real_name': self.real_name,
            'phone': self.phone,
            'is_verified': self.is_verified,
            'is_active': self.is_active,
            'is_admin': self.is_admin,
            'email_verified': self.email_verified,
            'user_group_id': self.user_group_id,
            'total_traffic': self.total_traffic,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
        
        if include_sensitive:
            data['id_card'] = self.id_card
            
        return data
