from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from src.models.user import db

class TrafficLog(db.Model):
    """流量日志模型"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    tunnel_id = db.Column(db.Integer, db.ForeignKey('tunnel.id'), nullable=False)
    
    # 流量数据
    upload = db.Column(db.BigInteger, default=0)  # 上传流量（字节）
    download = db.Column(db.BigInteger, default=0)  # 下载流量（字节）
    
    # 时间信息
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<TrafficLog {self.user_id}:{self.tunnel_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'tunnel_id': self.tunnel_id,
            'upload': self.upload,
            'download': self.download,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }


class TrafficSummary(db.Model):
    """流量汇总模型（按天）"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    tunnel_id = db.Column(db.Integer, db.ForeignKey('tunnel.id'), nullable=False)
    
    # 流量数据
    upload = db.Column(db.BigInteger, default=0)  # 上传流量（字节）
    download = db.Column(db.BigInteger, default=0)  # 下载流量（字节）
    
    # 日期
    date = db.Column(db.Date, nullable=False)
    
    # 创建唯一索引
    __table_args__ = (
        db.UniqueConstraint('user_id', 'tunnel_id', 'date', name='uix_traffic_summary'),
    )
    
    def __repr__(self):
        return f'<TrafficSummary {self.user_id}:{self.tunnel_id}:{self.date}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'tunnel_id': self.tunnel_id,
            'upload': self.upload,
            'download': self.download,
            'date': self.date.isoformat() if self.date else None
        }

