from flask import render_template, request, redirect, url_for, flash, jsonify, send_file, current_app
from flask_login import login_user, logout_user, login_required, current_user
from extensions import db
from models import User, Property, Tenant, Lease, Payment, MaintenanceRequest, Notification
from datetime import datetime, timedelta
from functools import wraps
import os
from werkzeug.utils import secure_filename

# Get app instance for route decorators
def get_app():
    return current_app._get_current_object()

# Use current_app for routes - Flask will bind these when imported
app = current_app

# Decorator for role-based access control
def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated or current_user.role not in roles:
                flash('You do not have permission to access this page.', 'danger')
                return redirect(url_for('dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# ==================== Authentication Routes ====================

@current_app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@current_app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            if not user.is_active:
                flash('⚠️ Your account is pending admin approval.', 'warning')
                return redirect(url_for('login'))
            
            login_user(user)
            flash(f'Welcome back, {user.full_name}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.', 'danger')
    
    return render_template('login.html')

@current_app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('login'))

@current_app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        full_name = request.form.get('full_name')
        phone = request.form.get('phone')
        role = request.form.get('role', 'tenant')
        
        # Check if user exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'danger')
            return redirect(url_for('register'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return redirect(url_for('register'))
        
        # Create new user (inactive by default)
        user = User(
            username=username,
            email=email,
            full_name=full_name,
            phone=phone,
            role=role,
            is_active=False
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        flash('✅ Registration successful! Please wait for admin approval.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

# ==================== Dashboard Routes ====================

@current_app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'admin':
        return redirect(url_for('admin_dashboard'))
    elif current_user.role == 'owner':
        return redirect(url_for('owner_dashboard'))
    elif current_user.role == 'tenant':
        return redirect(url_for('tenant_dashboard'))
    elif current_user.role == 'staff':
        return redirect(url_for('staff_dashboard'))
    else:
        flash('Invalid user role.', 'danger')
        return redirect(url_for('logout'))

@current_app.route('/admin/dashboard')
@login_required
@role_required('admin')
def admin_dashboard():
    total_users = User.query.count()
    pending_users = User.query.filter_by(is_active=False).count()
    total_properties = Property.query.count()
    total_leases = Lease.query.filter_by(status='active').count()
    total_revenue = db.session.query(db.func.sum(Payment.amount)).filter_by(status='completed').scalar() or 0
    
    pending_maintenance = MaintenanceRequest.query.filter_by(status='pending').count()
    recent_payments = Payment.query.order_by(Payment.created_at.desc()).limit(5).all()
    recent_requests = MaintenanceRequest.query.order_by(MaintenanceRequest.reported_date.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html',
                         total_users=total_users,
                         pending_users=pending_users,
                         total_properties=total_properties,
                         total_leases=total_leases,
                         total_revenue=total_revenue,
                         pending_maintenance=pending_maintenance,
                         recent_payments=recent_payments,
                         recent_requests=recent_requests)

@current_app.route('/owner/dashboard')
@login_required
@role_required('owner')
def owner_dashboard():
    my_properties = Property.query.filter_by(owner_id=current_user.id).all()
    active_leases = Lease.query.join(Property).filter(
        Property.owner_id == current_user.id,
        Lease.status == 'active'
    ).count()
    
    total_revenue = db.session.query(db.func.sum(Payment.amount)).join(Lease).join(Property).filter(
        Property.owner_id == current_user.id,
        Payment.status == 'completed'
    ).scalar() or 0
    
    pending_requests = MaintenanceRequest.query.join(Property).filter(
        Property.owner_id == current_user.id,
        MaintenanceRequest.status == 'pending'
    ).count()
    
    return render_template('owner/dashboard.html',
                         properties=my_properties,
                         active_leases=active_leases,
                         total_revenue=total_revenue,
                         pending_requests=pending_requests)

@current_app.route('/tenant/dashboard')
@login_required
@role_required('tenant')
def tenant_dashboard():
    my_lease = Lease.query.filter_by(tenant_id=current_user.id, status='active').first()
    
    if my_lease:
        my_property = my_lease.property
        pending_payments = Payment.query.filter_by(
            lease_id=my_lease.id,
            status='pending'
        ).count()
        
        recent_payments = Payment.query.filter_by(
            lease_id=my_lease.id
        ).order_by(Payment.created_at.desc()).limit(5).all()
        
        my_requests = MaintenanceRequest.query.filter_by(
            tenant_id=current_user.id
        ).order_by(MaintenanceRequest.reported_date.desc()).limit(5).all()
    else:
        my_property = None
        pending_payments = 0
        recent_payments = []
        my_requests = []
    
    return render_template('tenant/dashboard.html',
                         lease=my_lease,
                         property=my_property,
                         pending_payments=pending_payments,
                         recent_payments=recent_payments,
                         maintenance_requests=my_requests)

@current_app.route('/staff/dashboard')
@login_required
@role_required('staff')
def staff_dashboard():
    assigned_requests = MaintenanceRequest.query.filter_by(staff_id=current_user.id).all()
    pending_count = sum(1 for req in assigned_requests if req.status == 'pending')
    in_progress_count = sum(1 for req in assigned_requests if req.status == 'in_progress')
    completed_count = sum(1 for req in assigned_requests if req.status == 'completed')
    
    return render_template('staff/dashboard.html',
                         assigned_requests=assigned_requests,
                         pending_count=pending_count,
                         in_progress_count=in_progress_count,
                         completed_count=completed_count)

# ==================== User Management Routes ====================

@current_app.route('/admin/users')
@login_required
@role_required('admin')
def manage_users():
    users = User.query.all()
    return render_template('admin/users.html', users=users)

@current_app.route('/admin/users/add', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def add_user():
    if request.method == 'POST':
        user = User(
            username=request.form.get('username'),
            email=request.form.get('email'),
            full_name=request.form.get('full_name'),
            phone=request.form.get('phone'),
            address=request.form.get('address'),
            role=request.form.get('role'),
            is_active=True  # Admin-added users are active by default
        )
        user.set_password(request.form.get('password'))
        
        db.session.add(user)
        db.session.commit()
        
        flash('User added successfully!', 'success')
        return redirect(url_for('manage_users'))
    
    return render_template('admin/add_user.html')

@current_app.route('/admin/users/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        user.username = request.form.get('username')
        user.email = request.form.get('email')
        user.full_name = request.form.get('full_name')
        user.phone = request.form.get('phone')
        user.address = request.form.get('address')
        user.role = request.form.get('role')
        user.is_active = request.form.get('is_active') == 'on'
        
        password = request.form.get('password')
        if password:
            user.set_password(password)
        
        db.session.commit()
        flash('User updated successfully!', 'success')
        return redirect(url_for('manage_users'))
    
    return render_template('admin/edit_user.html', user=user)

@current_app.route('/admin/users/delete/<int:user_id>', methods=['POST'])
@login_required
@role_required('admin')
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    
    if user.id == current_user.id:
        flash('You cannot delete your own account.', 'danger')
        return redirect(url_for('manage_users'))
    
    db.session.delete(user)
    db.session.commit()
    
    flash('User deleted successfully!', 'success')
    return redirect(url_for('manage_users'))

# 🔥 NEW: Approve User Route
@current_app.route('/admin/users/approve/<int:user_id>', methods=['POST'])
@login_required
@role_required('admin')
def approve_user(user_id):
    user = User.query.get_or_404(user_id)
    
    user.is_active = True
    db.session.commit()
    
    # Create notification for user
    notification = Notification(
        user_id=user_id,
        title='Account Approved',
        message='Congratulations! Your account has been approved by admin. You can now login and use the system.',
        notification_type='general'
    )
    db.session.add(notification)
    db.session.commit()
    
    flash(f'User {user.username} has been approved successfully!', 'success')
    return redirect(url_for('manage_users'))

# ==================== Property Management Routes ====================

@current_app.route('/properties')
@login_required
def properties():
    if current_user.role == 'admin':
        properties = Property.query.all()
    elif current_user.role == 'owner':
        properties = Property.query.filter_by(owner_id=current_user.id).all()
    else:
        properties = Property.query.filter_by(availability_status='available').all()
    
    return render_template('properties/list.html', properties=properties)

@current_app.route('/properties/add', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'owner')
def add_property():
    if request.method == 'POST':
        property = Property(
            owner_id=current_user.id if current_user.role == 'owner' else request.form.get('owner_id'),
            property_type=request.form.get('property_type'),
            title=request.form.get('title'),
            address=request.form.get('address'),
            city=request.form.get('city'),
            state=request.form.get('state'),
            zip_code=request.form.get('zip_code'),
            bedrooms=request.form.get('bedrooms'),
            bathrooms=request.form.get('bathrooms'),
            area_sqft=request.form.get('area_sqft'),
            rent_amount=request.form.get('rent_amount'),
            security_deposit=request.form.get('security_deposit'),
            description=request.form.get('description'),
            amenities=request.form.get('amenities'),
            availability_status=request.form.get('availability_status', 'available')
        )
        
        # Handle file upload
        if 'image' in request.files:
            file = request.files['image']
            if file.filename:
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                property.image_path = filename
        
        db.session.add(property)
        db.session.commit()
        
        flash('Property added successfully!', 'success')
        return redirect(url_for('properties'))
    
    owners = User.query.filter_by(role='owner').all() if current_user.role == 'admin' else []
    return render_template('properties/add.html', owners=owners)

@current_app.route('/properties/edit/<int:property_id>', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'owner')
def edit_property(property_id):
    property = Property.query.get_or_404(property_id)
    
    # Check ownership
    if current_user.role == 'owner' and property.owner_id != current_user.id:
        flash('You do not have permission to edit this property.', 'danger')
        return redirect(url_for('properties'))
    
    if request.method == 'POST':
        property.property_type = request.form.get('property_type')
        property.title = request.form.get('title')
        property.address = request.form.get('address')
        property.city = request.form.get('city')
        property.state = request.form.get('state')
        property.zip_code = request.form.get('zip_code')
        property.bedrooms = request.form.get('bedrooms')
        property.bathrooms = request.form.get('bathrooms')
        property.area_sqft = request.form.get('area_sqft')
        property.rent_amount = request.form.get('rent_amount')
        property.security_deposit = request.form.get('security_deposit')
        property.description = request.form.get('description')
        property.amenities = request.form.get('amenities')
        property.availability_status = request.form.get('availability_status')
        
        # Handle file upload
        if 'image' in request.files:
            file = request.files['image']
            if file.filename:
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                property.image_path = filename
        
        db.session.commit()
        flash('Property updated successfully!', 'success')
        return redirect(url_for('properties'))
    
    return render_template('properties/edit.html', property=property)

@current_app.route('/properties/delete/<int:property_id>', methods=['POST'])
@login_required
@role_required('admin', 'owner')
def delete_property(property_id):
    property = Property.query.get_or_404(property_id)
    
    # Check ownership
    if current_user.role == 'owner' and property.owner_id != current_user.id:
        flash('You do not have permission to delete this property.', 'danger')
        return redirect(url_for('properties'))
    
    db.session.delete(property)
    db.session.commit()
    
    flash('Property deleted successfully!', 'success')
    return redirect(url_for('properties'))

@current_app.route('/properties/<int:property_id>')
@login_required
def view_property(property_id):
    property = Property.query.get_or_404(property_id)
    return render_template('properties/view.html', property=property)

#  Lease Management Routes 

@current_app.route('/leases')
@login_required
def leases():
    if current_user.role == 'admin':
        leases = Lease.query.all()
    elif current_user.role == 'owner':
        leases = Lease.query.join(Property).filter(Property.owner_id == current_user.id).all()
    elif current_user.role == 'tenant':
        leases = Lease.query.filter_by(tenant_id=current_user.id).all()
    else:
        leases = []
    
    return render_template('leases/list.html', leases=leases)

@current_app.route('/leases/add', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'owner')
def add_lease():
    if request.method == 'POST':
        property_id = request.form.get('property_id')
        tenant_id = request.form.get('tenant_id')
        
        # Check if property is available
        property = Property.query.get(property_id)
        if property.availability_status != 'available':
            flash('Property is not available for lease.', 'danger')
            return redirect(url_for('add_lease'))
        
        lease = Lease(
            property_id=property_id,
            tenant_id=tenant_id,
            start_date=datetime.strptime(request.form.get('start_date'), '%Y-%m-%d').date(),
            end_date=datetime.strptime(request.form.get('end_date'), '%Y-%m-%d').date(),
            monthly_rent=request.form.get('monthly_rent'),
            security_deposit=request.form.get('security_deposit'),
            terms_conditions=request.form.get('terms_conditions'),
            payment_due_day=request.form.get('payment_due_day', 1)
        )
        
        db.session.add(lease)
        
        # Update property status
        property.availability_status = 'occupied'
        
        db.session.commit()
        
        # Create notification for tenant
        notification = Notification(
            user_id=tenant_id,
            title='New Lease Agreement',
            message=f'A new lease agreement has been created for property: {property.title}',
            notification_type='lease_renewal'
        )
        db.session.add(notification)
        db.session.commit()
        
        flash('Lease created successfully!', 'success')
        return redirect(url_for('leases'))
    
    if current_user.role == 'owner':
        properties = Property.query.filter_by(owner_id=current_user.id, availability_status='available').all()
    else:
        properties = Property.query.filter_by(availability_status='available').all()
    
    tenants = User.query.filter_by(role='tenant').all()
    return render_template('leases/add.html', properties=properties, tenants=tenants)

@current_app.route('/leases/<int:lease_id>')
@login_required
def view_lease(lease_id):
    lease = Lease.query.get_or_404(lease_id)
    
    # Check permissions
    if current_user.role == 'tenant' and lease.tenant_id != current_user.id:
        flash('You do not have permission to view this lease.', 'danger')
        return redirect(url_for('dashboard'))
    
    if current_user.role == 'owner' and lease.property.owner_id != current_user.id:
        flash('You do not have permission to view this lease.', 'danger')
        return redirect(url_for('dashboard'))
    
    return render_template('leases/view.html', lease=lease)

# ==================== Payment Management Routes ====================

@current_app.route('/payments')
@login_required
def payments():
    if current_user.role == 'admin':
        payments = Payment.query.all()
    elif current_user.role == 'owner':
        payments = Payment.query.join(Lease).join(Property).filter(
            Property.owner_id == current_user.id
        ).all()
    elif current_user.role == 'tenant':
        payments = Payment.query.filter_by(tenant_id=current_user.id).all()
    else:
        payments = []
    
    return render_template('payments/list.html', payments=payments)

@current_app.route('/payments/add', methods=['GET', 'POST'])
@login_required
def add_payment():
    if request.method == 'POST':
        payment = Payment(
            lease_id=request.form.get('lease_id'),
            tenant_id=request.form.get('tenant_id'),
            amount=request.form.get('amount'),
            payment_date=datetime.strptime(request.form.get('payment_date'), '%Y-%m-%d').date(),
            payment_month=request.form.get('payment_month'),
            payment_method=request.form.get('payment_method'),
            transaction_id=request.form.get('transaction_id'),
            status='completed',
            late_fee=request.form.get('late_fee', 0),
            notes=request.form.get('notes')
        )
        
        db.session.add(payment)
        db.session.commit()
        
        flash('Payment recorded successfully!', 'success')
        return redirect(url_for('payments'))
    
    if current_user.role == 'tenant':
        leases = Lease.query.filter_by(tenant_id=current_user.id, status='active').all()
    elif current_user.role == 'owner':
        leases = Lease.query.join(Property).filter(
            Property.owner_id == current_user.id,
            Lease.status == 'active'
        ).all()
    else:
        leases = Lease.query.filter_by(status='active').all()
    
    return render_template('payments/add.html', leases=leases)

# ==================== Maintenance Routes ====================

@current_app.route('/maintenance')
@login_required
def maintenance():
    if current_user.role == 'admin':
        requests = MaintenanceRequest.query.all()
    elif current_user.role == 'owner':
        requests = MaintenanceRequest.query.join(Property).filter(
            Property.owner_id == current_user.id
        ).all()
    elif current_user.role == 'tenant':
        requests = MaintenanceRequest.query.filter_by(tenant_id=current_user.id).all()
    elif current_user.role == 'staff':
        requests = MaintenanceRequest.query.filter_by(staff_id=current_user.id).all()
    else:
        requests = []
    
    return render_template('maintenance/list.html', requests=requests)

@current_app.route('/maintenance/add', methods=['GET', 'POST'])
@login_required
@role_required('tenant')
def add_maintenance():
    if request.method == 'POST':
        request_obj = MaintenanceRequest(
            property_id=request.form.get('property_id'),
            tenant_id=current_user.id if current_user.role == 'tenant' else request.form.get('tenant_id'),
            title=request.form.get('title'),
            description=request.form.get('description'),
            category=request.form.get('category'),
            priority=request.form.get('priority', 'medium')
        )
        
        db.session.add(request_obj)
        db.session.commit()
        
        flash('Maintenance request submitted successfully!', 'success')
        return redirect(url_for('maintenance'))
    
    if current_user.role == 'tenant':
        lease = Lease.query.filter_by(tenant_id=current_user.id, status='active').first()
        properties = [lease.property] if lease else []
    elif current_user.role == 'owner':
        properties = Property.query.filter_by(owner_id=current_user.id).all()
    else:
        properties = Property.query.all()
    
    return render_template('maintenance/add.html', properties=properties)

@current_app.route('/maintenance/update/<int:request_id>', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'staff', 'owner')
def update_maintenance(request_id):
    maintenance_request = MaintenanceRequest.query.get_or_404(request_id)
    
    if request.method == 'POST':
        maintenance_request.status = request.form.get('status')
        maintenance_request.resolution_notes = request.form.get('resolution_notes')
        maintenance_request.cost = request.form.get('cost')
        
        if request.form.get('staff_id'):
            maintenance_request.staff_id = request.form.get('staff_id')
            maintenance_request.assigned_date = datetime.utcnow()
        
        if maintenance_request.status == 'completed':
            maintenance_request.completed_date = datetime.utcnow()
        
        db.session.commit()
        
        # Send notification to tenant
        notification = Notification(
            user_id=maintenance_request.tenant_id,
            title='Maintenance Request Updated',
            message=f'Your maintenance request "{maintenance_request.title}" status has been updated to: {maintenance_request.status}',
            notification_type='maintenance'
        )
        db.session.add(notification)
        db.session.commit()
        
        flash('Maintenance request updated successfully!', 'success')
        return redirect(url_for('maintenance'))
    
    staff_members = User.query.filter_by(role='staff').all()
    return render_template('maintenance/update.html', request=maintenance_request, staff=staff_members)

# ==================== Notification Routes ====================

@current_app.route('/notifications')
@login_required
def notifications():
    user_notifications = Notification.query.filter_by(user_id=current_user.id).order_by(
        Notification.created_at.desc()
    ).all()
    return render_template('notifications.html', notifications=user_notifications)

@current_app.route('/notifications/mark-read/<int:notification_id>')
@login_required
def mark_notification_read(notification_id):
    notification = Notification.query.get_or_404(notification_id)
    
    if notification.user_id != current_user.id:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('notifications'))
    
    notification.is_read = True
    db.session.commit()
    
    return redirect(url_for('notifications'))

# ==================== Report Routes ====================

@current_app.route('/reports')
@login_required
@role_required('admin', 'owner')
def reports():
    return render_template('reports/index.html')

@current_app.route('/reports/rent-collection')
@login_required
@role_required('admin', 'owner')
def rent_collection_report():
    if current_user.role == 'owner':
        payments = Payment.query.join(Lease).join(Property).filter(
            Property.owner_id == current_user.id
        ).all()
    else:
        payments = Payment.query.all()
    
    total_collected = sum(p.amount for p in payments if p.status == 'completed')
    total_pending = sum(p.amount for p in payments if p.status == 'pending')
    
    return render_template('reports/rent_collection.html',
                         payments=payments,
                         total_collected=total_collected,
                         total_pending=total_pending)

@current_app.route('/reports/occupancy')
@login_required
@role_required('admin', 'owner')
def occupancy_report():
    if current_user.role == 'owner':
        properties = Property.query.filter_by(owner_id=current_user.id).all()
    else:
        properties = Property.query.all()
    
    total_properties = len(properties)
    occupied = sum(1 for p in properties if p.availability_status == 'occupied')
    available = sum(1 for p in properties if p.availability_status == 'available')
    
    occupancy_rate = (occupied / total_properties * 100) if total_properties > 0 else 0
    
    return render_template('reports/occupancy.html',
                         properties=properties,
                         total_properties=total_properties,
                         occupied=occupied,
                         available=available,
                         occupancy_rate=occupancy_rate)

@current_app.route('/reports/maintenance')
@login_required
@role_required('admin', 'owner')
def maintenance_report():
    if current_user.role == 'owner':
        requests = MaintenanceRequest.query.join(Property).filter(
            Property.owner_id == current_user.id
        ).all()
    else:
        requests = MaintenanceRequest.query.all()
    
    pending = sum(1 for r in requests if r.status == 'pending')
    in_progress = sum(1 for r in requests if r.status == 'in_progress')
    completed = sum(1 for r in requests if r.status == 'completed')
    
    return render_template('reports/maintenance.html',
                         requests=requests,
                         pending=pending,
                         in_progress=in_progress,
                         completed=completed)

# ==================== Profile Routes ====================

@current_app.route('/profile')
@login_required
def profile():
    return render_template('profile.html')

@current_app.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        current_user.full_name = request.form.get('full_name')
        current_user.email = request.form.get('email')
        current_user.phone = request.form.get('phone')
        current_user.address = request.form.get('address')
        
        password = request.form.get('password')
        if password:
            current_user.set_password(password)
        
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile'))
    
    return render_template('edit_profile.html')

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

def register_routes(app):
    """Register all routes with the app"""
    # All routes are already decorated with @current_app.route
    # This function is here for clarity but routes are auto-registered
    pass
