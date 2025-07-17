from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from src.models.user import db

class UserGroup(db.Model):
    """用户组模型"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    
    # 权限和限制
    max_tunnels = db.Column(db.Integer, nullable=False, default=5)  # 最大隧道数
    max_traffic = db.Column(db.BigInteger, nullable=False, default=10737418240)  # 最大流量（字节）
    upload_speed_limit = db.Column(db.Integer, nullable=True)  # 上传速率限制（KB/s）
    download_speed_limit = db.Column(db.Integer, nullable=True)  # 下载速率限制（KB/s）
    
    # 其他信息
    description = db.Column(db.Text, nullable=True)
    is_default = db.Column(db.Boolean, default=False)  # 是否为默认组
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 反向关联
    users = db.relationship('User', backref='user_group', lazy=True)
    
    def __repr__(self):
        return f'<UserGroup {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'max_tunnels': self.max_tunnels,
            'max_traffic': self.max_traffic,
            'upload_speed_limit': self.upload_speed_limit,
            'download_speed_limit': self.download_speed_limit,
            'description': self.description,
            'is_default': self.is_default,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

