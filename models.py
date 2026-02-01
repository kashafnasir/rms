from extensions import db
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    role = db.Column(db.String(20), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    properties = db.relationship('Property', backref='owner', lazy=True, foreign_keys='Property.owner_id')
    leases_as_tenant = db.relationship('Lease', backref='tenant', lazy=True, foreign_keys='Lease.tenant_id')
    payments = db.relationship('Payment', backref='payer', lazy=True)
    maintenance_requests = db.relationship('MaintenanceRequest', backref='requester', lazy=True, foreign_keys='MaintenanceRequest.tenant_id')
    assigned_maintenance = db.relationship('MaintenanceRequest', backref='assigned_staff', lazy=True, foreign_keys='MaintenanceRequest.staff_id')
    notifications = db.relationship('Notification', backref='user', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Property(db.Model):
    __tablename__ = 'properties'
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    property_type = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    address = db.Column(db.Text, nullable=False)
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    zip_code = db.Column(db.String(20))
    bedrooms = db.Column(db.Integer)
    bathrooms = db.Column(db.Integer)
    area_sqft = db.Column(db.Float)
    rent_amount = db.Column(db.Float, nullable=False)
    security_deposit = db.Column(db.Float)
    description = db.Column(db.Text)
    amenities = db.Column(db.Text)
    availability_status = db.Column(db.String(20), default='available')
    image_path = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    leases = db.relationship('Lease', backref='property', lazy=True)
    maintenance_requests = db.relationship('MaintenanceRequest', backref='property', lazy=True)

class Tenant(db.Model):
    __tablename__ = 'tenants'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    emergency_contact_name = db.Column(db.String(120))
    emergency_contact_phone = db.Column(db.String(20))
    occupation = db.Column(db.String(100))
    employer = db.Column(db.String(100))
    monthly_income = db.Column(db.Float)
    id_proof_type = db.Column(db.String(50))
    id_proof_number = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='tenant_profile', foreign_keys=[user_id])

class Lease(db.Model):
    __tablename__ = 'leases'
    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey('properties.id'), nullable=False)
    tenant_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    monthly_rent = db.Column(db.Float, nullable=False)
    security_deposit = db.Column(db.Float)
    terms_conditions = db.Column(db.Text)
    status = db.Column(db.String(20), default='active')
    payment_due_day = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    payments = db.relationship('Payment', backref='lease', lazy=True)

class Payment(db.Model):
    __tablename__ = 'payments'
    id = db.Column(db.Integer, primary_key=True)
    lease_id = db.Column(db.Integer, db.ForeignKey('leases.id'), nullable=False)
    tenant_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.Date, nullable=False)
    payment_month = db.Column(db.String(7))
    payment_method = db.Column(db.String(50))
    transaction_id = db.Column(db.String(100))
    status = db.Column(db.String(20), default='pending')
    late_fee = db.Column(db.Float, default=0.0)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class MaintenanceRequest(db.Model):
    __tablename__ = 'maintenance_requests'
    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey('properties.id'), nullable=False)
    tenant_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    staff_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50))
    priority = db.Column(db.String(20), default='medium')
    status = db.Column(db.String(20), default='pending')
    reported_date = db.Column(db.DateTime, default=datetime.utcnow)
    assigned_date = db.Column(db.DateTime)
    completed_date = db.Column(db.DateTime)
    cost = db.Column(db.Float)
    resolution_notes = db.Column(db.Text)

class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    notification_type = db.Column(db.String(50))
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)