from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from src.models.user import db

class Tunnel(db.Model):
    """FRP隧道模型"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(20), nullable=False)  # tcp, udp, http, https
    local_ip = db.Column(db.String(50), nullable=False, default='127.0.0.1')
    local_port = db.Column(db.Integer, nullable=False)
    remote_port = db.Column(db.Integer, nullable=True)
    custom_domains = db.Column(db.Text, nullable=True)  # JSON格式存储域名列表
    subdomain = db.Column(db.String(100), nullable=True)
    status = db.Column(db.String(20), default='stopped')  # running, stopped, error
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 流量统计
    bytes_in = db.Column(db.BigInteger, default=0)
    bytes_out = db.Column(db.BigInteger, default=0)
    
    # 关联节点和用户
    node_id = db.Column(db.Integer, db.ForeignKey('node.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f'<Tunnel {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'local_ip': self.local_ip,
            'local_port': self.local_port,
            'remote_port': self.remote_port,
            'custom_domains': self.custom_domains,
            'subdomain': self.subdomain,
            'status': self.status,
            'description': self.description,
            'bytes_in': self.bytes_in,
            'bytes_out': self.bytes_out,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'node_id': self.node_id,
            'user_id': self.user_id
        }

