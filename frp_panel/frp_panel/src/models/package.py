from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from src.models.user import db

class Package(db.Model):
    """套餐模型"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    price = db.Column(db.Float, nullable=False)  # 价格
    duration = db.Column(db.Integer, nullable=False)  # 有效期（天）
    
    # 套餐限制
    max_tunnels = db.Column(db.Integer, nullable=False, default=5)  # 最大隧道数
    max_traffic = db.Column(db.BigInteger, nullable=False, default=10737418240)  # 最大流量（字节）
    upload_speed_limit = db.Column(db.Integer, nullable=True)  # 上传速率限制（KB/s）
    download_speed_limit = db.Column(db.Integer, nullable=True)  # 下载速率限制（KB/s）
    
    # 其他信息
    description = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 反向关联
    user_packages = db.relationship('UserPackage', backref='package', lazy=True)
    
    def __repr__(self):
        return f'<Package {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'price': self.price,
            'duration': self.duration,
            'max_tunnels': self.max_tunnels,
            'max_traffic': self.max_traffic,
            'upload_speed_limit': self.upload_speed_limit,
            'download_speed_limit': self.download_speed_limit,
            'description': self.description,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class UserPackage(db.Model):
    """用户套餐关联模型"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    package_id = db.Column(db.Integer, db.ForeignKey('package.id'), nullable=False)
    
    # 状态信息
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    end_date = db.Column(db.DateTime, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    
    # 使用情况
    used_traffic = db.Column(db.BigInteger, default=0)  # 已使用流量（字节）
    
    # 支付信息
    payment_id = db.Column(db.String(100), nullable=True)  # 支付ID
    payment_method = db.Column(db.String(50), nullable=True)  # 支付方式
    payment_status = db.Column(db.String(20), default='pending')  # 支付状态
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<UserPackage {self.user_id}:{self.package_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'package_id': self.package_id,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'is_active': self.is_active,
            'used_traffic': self.used_traffic,
            'payment_id': self.payment_id,
            'payment_method': self.payment_method,
            'payment_status': self.payment_status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

