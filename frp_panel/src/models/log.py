from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from src.models.user import db

class OperationLog(db.Model):
    """操作日志模型"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    action = db.Column(db.String(50), nullable=False)  # create, update, delete, start, stop
    resource_type = db.Column(db.String(20), nullable=False)  # node, tunnel, user
    resource_id = db.Column(db.Integer, nullable=True)
    resource_name = db.Column(db.String(100), nullable=True)
    details = db.Column(db.Text, nullable=True)  # JSON格式存储详细信息
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='success')  # success, failed
    error_message = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<OperationLog {self.action} {self.resource_type}>'

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'action': self.action,
            'resource_type': self.resource_type,
            'resource_id': self.resource_id,
            'resource_name': self.resource_name,
            'details': self.details,
            'ip_address': self.ip_address,
            'status': self.status,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class SystemLog(db.Model):
    """系统日志模型"""
    id = db.Column(db.Integer, primary_key=True)
    level = db.Column(db.String(10), nullable=False)  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    module = db.Column(db.String(50), nullable=False)
    message = db.Column(db.Text, nullable=False)
    details = db.Column(db.Text, nullable=True)  # JSON格式存储详细信息
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<SystemLog {self.level} {self.module}>'

    def to_dict(self):
        return {
            'id': self.id,
            'level': self.level,
            'module': self.module,
            'message': self.message,
            'details': self.details,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

