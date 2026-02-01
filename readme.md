# 🏠 Rental Management System

A comprehensive web-based property rental management system built with Python, Flask, and SQLAlchemy.


##  Features

### Core Functionality

1. **User Management**
   - Role-based access control (Admin, Owner, Tenant, Staff)
   - User authentication and authorization
   - Profile management
   - Password encryption

2. **Property Management**
   - Add, edit, and delete properties
   - Property search and filtering
   - Image upload support
   - Property details (type, location, rent, amenities)
   - Availability status tracking

3. **Tenant Management**
   - Tenant registration and profiles
   - Lease agreement management
   - Payment history tracking
   - Document management

4. **Lease & Agreement Management**
   - Create and manage rental agreements
   - Track lease periods (start/end dates)
   - Automatic lease expiry reminders
   - Terms and conditions documentation

5. **Rent Collection & Payments**
   - Monthly rent invoice generation
   - Multiple payment methods (Cash, Bank Transfer, Online)
   - Payment tracking (paid/pending)
   - Late fee calculation
   - Payment history

6. **Maintenance Requests**
   - Submit maintenance requests
   - Status tracking (Pending, In Progress, Completed)
   - Priority levels (Low, Medium, High, Urgent)
   - Assignment to staff members
   - Resolution notes and cost tracking

7. **Notifications System**
   - Email/SMS alerts for:
     - Rent due dates
     - Lease renewal
     - Maintenance updates
   - In-app notification center

8. **Reports & Analytics**
   - Rent collection reports
   - Tenant occupancy reports
   - Maintenance reports
   - Export functionality (PDF/Excel ready)

9. **Admin Dashboard**
   - System-wide monitoring
   - User and role management
   - Property overview
   - Revenue tracking
   - Maintenance oversight

##  System Requirements

- Python 3.8 or higher
- pip (Python package manager)
- SQLite (included with Python)
- Modern web browser (Chrome, Firefox, Safari, Edge)


### Step : Create Virtual Environment (Recommended)

```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step : Install Dependencies

```bash
pip install -r requirements.txt
```

### Step : Initialize the Database

```bash
python init_db.py
```

This will:
- Create all database tables
- Create a default admin account
- Create sample users for testing (optional)

##  Configuration

The main configuration is in `app.py`. You can modify:

```python
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rental_management.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
```

### Important Security Note
⚠️ **Always change the SECRET_KEY in production!**

## 🚀 Running the Application

### Development Mode

```bash
python app.py
```

The application will be available at: `http://localhost:5000`

## 👥 User Roles

### 1. Admin
**Full system access and control**

- Manage all users and roles
- Manage all properties
- View all leases and payments
- Oversee all maintenance requests
- Generate system-wide reports
- Configure notifications

**Default Credentials:**
- Username: `admin`
- Password: `admin123`

### 2. Property Owner
**Manage owned properties**

- Add and manage properties
- Create lease agreements
- Track rent payments
- View tenant details
- Handle maintenance requests
- Generate property-specific reports

**Test Credentials:**
- Username: `owner1`
- Password: `owner123`

### 3. Tenant
**Access rental information and services**

- View lease details
- Pay rent
- Submit maintenance requests
- View payment history
- Receive notifications

**Test Credentials:**
- Username: `tenant1`
- Password: `tenant123`

### 4. Staff/Maintenance
**Handle maintenance operations**

- View assigned maintenance requests
- Update request status
- Add resolution notes
- Track maintenance costs

**Test Credentials:**
- Username: `staff1`
- Password: `staff123`

## 📁 Project Structure

```
rental_management_system/
│
├── app.py                      # Main application file
├── models.py                   # Database models
├── routes.py                   # Application routes
├── init_db.py                  # Database initialization script
├── requirements.txt            # Python dependencies
│
├── templates/                  # HTML templates
│   ├── base.html              # Base template
│   ├── login.html             # Login page
│   ├── register.html          # Registration page
│   ├── profile.html           # User profile
│   ├── notifications.html     # Notifications
│   │
│   ├── admin/                 # Admin templates
│   │   ├── dashboard.html
│   │   └── users.html
│   │
│   ├── owner/                 # Owner templates
│   │   └── dashboard.html
│   │
│   ├── tenant/                # Tenant templates
│   │   └── dashboard.html
│   │
│   ├── staff/                 # Staff templates
│   │   └── dashboard.html
│   │
│   ├── properties/            # Property templates
│   │   ├── list.html
│   │   ├── add.html
│   │   └── view.html
│   │
│   ├── leases/                # Lease templates
│   │   ├── list.html
│   │   └── add.html
│   │
│   ├── payments/              # Payment templates
│   │   ├── list.html
│   │   └── add.html
│   │
│   ├── maintenance/           # Maintenance templates
│   │   ├── list.html
│   │   ├── add.html
│   │   └── update.html
│   │
│   └── reports/               # Report templates
│       ├── index.html
│       ├── rent_collection.html
│       ├── occupancy.html
│       └── maintenance.html
│
└── static/                    # Static files
    └── uploads/               # Uploaded images
```

## 🗄️ Database Models

### User
- User authentication and profile information
- Role-based access control
- Contact details

### Property
- Property details (type, location, size)
- Rent amount and availability
- Images and documents
- Owner relationship

### Tenant
- Extended tenant information
- Emergency contacts
- Employment details

### Lease
- Rental agreement details
- Start and end dates
- Monthly rent amount
- Terms and conditions

### Payment
- Payment tracking
- Multiple payment methods
- Late fees
- Transaction history

### MaintenanceRequest
- Maintenance issue details
- Priority and status tracking
- Staff assignment
- Cost and resolution notes

### Notification
- User notifications
- Various notification types
- Read/unread status

## 📖 Usage Guide

### Getting Started

1. **First Login**
   - Navigate to `http://localhost:5000`
   - Login with admin credentials
   - Change the default password immediately

2. **Add Users**
   - Admin → Users → Add User
   - Fill in user details and assign role
   - Users receive credentials via email (if configured)

3. **Add Properties**
   - Owner/Admin → Properties → Add Property
   - Fill in property details
   - Upload property images
   - Set rent amount and availability

4. **Create Leases**
   - Owner/Admin → Leases → Add Lease
   - Select property and tenant
   - Set lease period and terms
   - Property status automatically updates

5. **Manage Payments**
   - Tenant makes payment via dashboard
   - Payment recorded by admin/owner
   - Payment history tracked automatically

6. **Handle Maintenance**
   - Tenant submits request
   - Admin/Owner assigns to staff
   - Staff updates status and resolution
   - Tenant receives notifications



##  Security Considerations

1. **Password Security**
   - Passwords are hashed using Werkzeug's security functions
   - Never store plain text passwords
   - Change default credentials immediately

2. **Session Management**
   - Flask-Login handles user sessions
   - Sessions expire after inactivity
   - Logout properly to clear sessions

3. **File Uploads**
   - Validate file types and sizes
   - Store uploads outside web root
   - Use secure filenames

4. **SQL Injection**
   - SQLAlchemy ORM prevents SQL injection
   - Use parameterized queries

5. **CSRF Protection**
   - Implement CSRF tokens for forms
   - Validate all POST requests

6. **Production Deployment**
   - Use HTTPS in production
   - Set strong SECRET_KEY
   - Configure proper permissions
   - Regular security updates

##  Troubleshooting

### Database Issues

**Error: Database locked**
```bash
# Stop the application
# Delete the database file
rm rental_management.db
# Reinitialize
python init_db.py
```

**Error: Table doesn't exist**
```bash
# Reinitialize database
python init_db.py
```

### Login Issues

**Can't login with admin credentials**
- Ensure database is initialized
- Check if admin user exists
- Verify password is correct

### File Upload Issues

**Images not displaying**
- Check `static/uploads` directory exists
- Verify file permissions
- Check image paths in database

### Port Already in Use

**Error: Port 5000 already in use**
```bash
# Find process using port 5000
# On Windows:
netstat -ano | findstr :5000
# Kill the process or use a different port
```




##   Support

For issues, questions, or suggestions:
- Check the troubleshooting section
- Review the documentation
- Contact Kashaf Memon



##  Notes

- This is a complete, working rental management system
- All CRUD operations are fully implemented
- Role-based access control is enforced
- Responsive design works on all devices
- Database migrations supported via Flask-Migrate

---

**Version:** 1.0.0  
**Last Updated:** 2024  
**Developed with:** Python, Flask, SQLAlchemy, Bootstrap 5