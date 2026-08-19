from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# ============================================================
# مدل کاربران
# ============================================================
class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(11), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(100))
    user_type = db.Column(db.String(20), default='farmer')  # farmer, industry, admin
    balance = db.Column(db.BigInteger, default=0)
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    farms = db.relationship('Farm', backref='owner', lazy=True)

# ============================================================
# مدل مزارع
# ============================================================
class Farm(db.Model):
    __tablename__ = 'farms'
    
    id = db.Column(db.Integer, primary_key=True)
    farmer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    area = db.Column(db.Float, nullable=False)
    crop_type = db.Column(db.String(50))
    region = db.Column(db.String(100))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    vwus = db.relationship('VWU', backref='farm', lazy=True)
    readings = db.relationship('SensorReading', backref='farm', lazy=True)

# ============================================================
# مدل VWU (واحد آب مجازی)
# ============================================================
class VWU(db.Model):
    __tablename__ = 'vwu_units'
    
    id = db.Column(db.Integer, primary_key=True)
    farm_id = db.Column(db.Integer, db.ForeignKey('farms.id'), nullable=False)
    batch_number = db.Column(db.String(50), unique=True, nullable=False)
    water_saved = db.Column(db.Float, nullable=False)
    price_per_unit = db.Column(db.Float)
    total_price = db.Column(db.Float)
    status = db.Column(db.String(20), default='pending')  # pending, verified, listed, sold, cancelled
    buyer_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    buyer = db.relationship('User', foreign_keys=[buyer_id])

# ============================================================
# مدل خوانش‌های سنسور (IoT)
# ============================================================
class SensorReading(db.Model):
    __tablename__ = 'sensor_readings'
    
    id = db.Column(db.Integer, primary_key=True)
    sensor_id = db.Column(db.String(50), nullable=False)
    farm_id = db.Column(db.Integer, db.ForeignKey('farms.id'), nullable=False)
    water_flow = db.Column(db.Float, nullable=False)
    pressure = db.Column(db.Float)
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)