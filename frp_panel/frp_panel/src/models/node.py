from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from src.models.user import db

class Node(db.Model):
    """FRP服务端节点模型"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    host = db.Column(db.String(255), nullable=False)
    port = db.Column(db.Integer, nullable=False, default=7000)
    dashboard_port = db.Column(db.Integer, nullable=True)
    dashboard_user = db.Column(db.String(50), nullable=True)
    dashboard_password = db.Column(db.String(100), nullable=True)
    token = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(20), default='offline')  # online, offline, error
    region = db.Column(db.String(50), nullable=True)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联用户
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # 反向关联
    tunnels = db.relationship('Tunnel', backref='node', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Node {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'host': self.host,
            'port': self.port,
            'dashboard_port': self.dashboard_port,
            'dashboard_user': self.dashboard_user,
            'status': self.status,
            'region': self.region,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'user_id': self.user_id,
            'tunnel_count': len(self.tunnels) if self.tunnels else 0
        }

