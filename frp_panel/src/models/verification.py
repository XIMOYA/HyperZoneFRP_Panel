from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import random
import string
from src.models.user import db

class EmailVerification(db.Model):
    """邮箱验证码模型"""
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    code = db.Column(db.String(6), nullable=False)
    purpose = db.Column(db.String(20), nullable=False)  # register, reset_password, change_email
    is_used = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)

    def __init__(self, email, purpose, expires_in_minutes=10):
        self.email = email
        self.purpose = purpose
        self.code = self.generate_code()
        self.expires_at = datetime.utcnow() + timedelta(minutes=expires_in_minutes)

    @staticmethod
    def generate_code():
        """生成6位数字验证码"""
        return ''.join(random.choices(string.digits, k=6))

    def is_expired(self):
        """检查验证码是否过期"""
        return datetime.utcnow() > self.expires_at

    def is_valid(self, code):
        """验证码是否有效"""
        return (not self.is_used and 
                not self.is_expired() and 
                self.code == code)

    def mark_as_used(self):
        """标记验证码为已使用"""
        self.is_used = True

    def __repr__(self):
        return f'<EmailVerification {self.email}>'

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'purpose': self.purpose,
            'is_used': self.is_used,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None
        }

