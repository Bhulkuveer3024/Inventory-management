# Inventory-management

# Inventory Management Web App

This is a secure Django-based inventory and order management system with user roles (System Admin, Store Manager, Sales Staff), email verification, and role-based access control.

## Features
- User authentication and email verification
- Role-based permissions (System Admin, Store Manager, Sales Staff)
- Inventory management (products, stock)
- Order management
- Admin dashboard

## Requirements
- Python 3.12+
- pip
- Git
- (Recommended) Virtual environment tool: `env`

## Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Bhulkuveer3024/Inventory-management.git
   cd Inventory-management/mainapp
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv env
   # On Windows:
   env\Scripts\activate
   # On Mac/Linux:
   source env/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Apply migrations:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create a superuser (admin):**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run the development server:**
   ```bash
   python manage.py runserver
   ```

7. **Access the app:**
   - Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser.
   - Admin panel: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

## Email Verification
- By default, emails are printed to the console. To enable real email sending, update the `EMAIL_BACKEND` and SMTP settings in `mainapp/settings.py`.

## User Roles
- **System Admin:** Full access to everything (admin, inventory, orders)
- **Store Manager:** Can manage inventory and orders
- **Sales Staff:** Can manage orders only

## Security Features
- Password hashing, CSRF protection, session management
- Email verification for new users
- Role-based access control
- Secure default settings

