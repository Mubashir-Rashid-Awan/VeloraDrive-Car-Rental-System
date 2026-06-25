from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from database.connection import get_db_connection

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email     = request.form.get('email', '').strip().lower()
        phone     = request.form.get('phone', '').strip()
        password  = request.form.get('password', '')
        confirm   = request.form.get('confirm_password', '')

        if not full_name or not email or not password:
            flash('All required fields must be filled.', 'danger')
            return render_template('signup.html')

        if password != confirm:
            flash('Passwords do not match.', 'danger')
            return render_template('signup.html')

        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'danger')
            return render_template('signup.html')

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT user_id FROM Users WHERE email = ?", email)
            if cursor.fetchone():
                flash('An account with this email already exists.', 'warning')
                conn.close()
                return render_template('signup.html')

            pw_hash = generate_password_hash(password)
            cursor.execute(
                "INSERT INTO Users (full_name, email, password_hash, phone) VALUES (?, ?, ?, ?)",
                full_name, email, pw_hash, phone or None
            )
            conn.commit()
            conn.close()
            flash('Account created successfully! Please log in.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            flash(f'Registration failed: {e}', 'danger')
            return render_template('signup.html')

    return render_template('signup.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email    = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        role     = request.form.get('role', 'user')

        if not email or not password:
            flash('Please enter email and password.', 'danger')
            return render_template('login.html')

        try:
            conn   = get_db_connection()
            cursor = conn.cursor()

            if role == 'admin':
                cursor.execute("SELECT admin_id, full_name, password_hash, role_name FROM Admins WHERE email = ?", email)
                row = cursor.fetchone()
                conn.close()
                if row and check_password_hash(row.password_hash, password):
                    session.clear()
                    session['admin_id']   = row.admin_id
                    session['admin_name'] = row.full_name
                    session['role']       = row.role_name
                    flash(f'Welcome back, {row.full_name}!', 'success')
                    return redirect(url_for('admin.dashboard'))
                flash('Invalid admin credentials.', 'danger')
                return render_template('login.html')
            else:
                cursor.execute(
                    "SELECT user_id, full_name, password_hash, profile_image FROM Users WHERE email = ?", email
                )
                row = cursor.fetchone()
                conn.close()
                if row and check_password_hash(row.password_hash, password):
                    session.clear()
                    session['user_id']   = row.user_id
                    session['user_name'] = row.full_name
                    session['user_img']  = row.profile_image
                    flash(f'Welcome back, {row.full_name}!', 'success')
                    return redirect(url_for('main.index'))
                flash('Invalid email or password.', 'danger')
                return render_template('login.html')

        except Exception as e:
            flash(f'Login error: {e}', 'danger')
            return render_template('login.html')

    return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))
