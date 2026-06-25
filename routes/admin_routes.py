from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash
from database.connection import get_db_connection
from functools import wraps

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'admin_id' not in session:
            flash('Admin access required.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


def _rows_to_list(cursor, rows):
    cols = [col[0] for col in cursor.description]
    return [dict(zip(cols, r)) for r in rows]


@admin_bp.route('/')
@admin_required
def dashboard():
    try:
        conn   = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM Users")
        total_users = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM Cars")
        total_cars  = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM Bookings")
        total_bookings = cursor.fetchone()[0]
        cursor.execute("SELECT COALESCE(SUM(amount),0) FROM Payments WHERE payment_status='Paid'")
        total_revenue = cursor.fetchone()[0]

        cursor.execute("""
            SELECT TOP 10 b.booking_id, u.full_name, c.car_name,
                   b.booking_status, b.total_amount, b.created_at
            FROM Bookings b
            JOIN Users u ON u.user_id = b.user_id
            JOIN Cars  c ON c.car_id  = b.car_id
            ORDER BY b.created_at DESC
        """)
        recent_bookings = _rows_to_list(cursor, cursor.fetchall())

        cursor.execute("""
            SELECT booking_status, COUNT(*) AS cnt
            FROM Bookings GROUP BY booking_status
        """)
        booking_stats = _rows_to_list(cursor, cursor.fetchall())

        conn.close()
        return render_template('admin_dashboard.html',
            active='overview',
            total_users=total_users,
            total_cars=total_cars,
            total_bookings=total_bookings,
            total_revenue=total_revenue,
            recent_bookings=recent_bookings,
            booking_stats=booking_stats
        )
    except Exception as e:
        flash(f'Error: {e}', 'danger')
        return render_template('admin_dashboard.html', active='overview',
            total_users=0, total_cars=0, total_bookings=0,
            total_revenue=0, recent_bookings=[], booking_stats=[])


# ------------ CARS MANAGEMENT ------------

@admin_bp.route('/cars')
@admin_required
def manage_cars():
    try:
        conn   = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT c.*, cat.category_name
            FROM Cars c
            LEFT JOIN Car_Categories cat ON cat.category_id = c.category_id
            ORDER BY c.created_at DESC
        """)
        cars = _rows_to_list(cursor, cursor.fetchall())
        cursor.execute("SELECT * FROM Car_Categories ORDER BY category_name")
        categories = _rows_to_list(cursor, cursor.fetchall())
        conn.close()
        return render_template('admin_dashboard.html', active='cars', cars=cars, categories=categories)
    except Exception as e:
        flash(f'Error: {e}', 'danger')
        return render_template('admin_dashboard.html', active='cars', cars=[], categories=[])


@admin_bp.route('/cars/add', methods=['POST'])
@admin_required
def add_car():
    try:
        conn   = get_db_connection()
        cursor = conn.cursor()
        f      = request.form
        cursor.execute("""
            INSERT INTO Cars (category_id, car_name, brand, model_year, price_per_day,
                fuel_type, transmission, seating_capacity, car_image, availability_status, description)
            VALUES (?,?,?,?,?,?,?,?,?,?,?)
        """,
            f.get('category_id') or None,
            f.get('car_name'), f.get('brand'), f.get('model_year') or None,
            f.get('price_per_day'), f.get('fuel_type'), f.get('transmission'),
            f.get('seating_capacity') or None, f.get('car_image') or 'default_car.jpg',
            f.get('availability_status', 'Available'), f.get('description')
        )
        conn.commit()
        conn.close()
        flash('Car added successfully.', 'success')
    except Exception as e:
        flash(f'Error adding car: {e}', 'danger')
    return redirect(url_for('admin.manage_cars'))


@admin_bp.route('/cars/edit/<int:car_id>', methods=['POST'])
@admin_required
def edit_car(car_id):
    try:
        conn   = get_db_connection()
        cursor = conn.cursor()
        f      = request.form
        cursor.execute("""
            UPDATE Cars SET category_id=?, car_name=?, brand=?, model_year=?,
                price_per_day=?, fuel_type=?, transmission=?, seating_capacity=?,
                car_image=?, availability_status=?, description=?, updated_at=GETDATE()
            WHERE car_id=?
        """,
            f.get('category_id') or None,
            f.get('car_name'), f.get('brand'), f.get('model_year') or None,
            f.get('price_per_day'), f.get('fuel_type'), f.get('transmission'),
            f.get('seating_capacity') or None, f.get('car_image') or 'default_car.jpg',
            f.get('availability_status'), f.get('description'), car_id
        )
        conn.commit()
        conn.close()
        flash('Car updated successfully.', 'success')
    except Exception as e:
        flash(f'Error updating car: {e}', 'danger')
    return redirect(url_for('admin.manage_cars'))


@admin_bp.route('/cars/delete/<int:car_id>', methods=['POST'])
@admin_required
def delete_car(car_id):
    try:
        conn   = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Cars WHERE car_id=?", car_id)
        conn.commit()
        conn.close()
        flash('Car deleted.', 'success')
    except Exception as e:
        flash(f'Error: {e}', 'danger')
    return redirect(url_for('admin.manage_cars'))


# ------------ BOOKINGS MANAGEMENT ------------

@admin_bp.route('/bookings')
@admin_required
def manage_bookings():
    try:
        conn   = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT b.*, u.full_name AS user_name, c.car_name,
                   p.payment_status, p.payment_method
            FROM Bookings b
            JOIN Users u ON u.user_id = b.user_id
            JOIN Cars  c ON c.car_id  = b.car_id
            LEFT JOIN Payments p ON p.booking_id = b.booking_id
            ORDER BY b.created_at DESC
        """)
        bookings = _rows_to_list(cursor, cursor.fetchall())
        conn.close()
        return render_template('admin_dashboard.html', active='bookings', bookings=bookings)
    except Exception as e:
        flash(f'Error: {e}', 'danger')
        return render_template('admin_dashboard.html', active='bookings', bookings=[])


@admin_bp.route('/bookings/update-status/<int:booking_id>', methods=['POST'])
@admin_required
def update_booking_status(booking_id):
    new_status = request.form.get('status')
    try:
        conn   = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE Bookings SET booking_status=? WHERE booking_id=?", new_status, booking_id)
        if new_status == 'Cancelled' or new_status == 'Completed':
            cursor.execute("""
                UPDATE Cars SET availability_status='Available', updated_at=GETDATE()
                WHERE car_id = (SELECT car_id FROM Bookings WHERE booking_id=?)
            """, booking_id)
        conn.commit()
        conn.close()
        flash(f'Booking status updated to {new_status}.', 'success')
    except Exception as e:
        flash(f'Error: {e}', 'danger')
    return redirect(url_for('admin.manage_bookings'))


# ------------ REVIEWS MANAGEMENT ------------

@admin_bp.route('/reviews')
@admin_required
def manage_reviews():
    try:
        conn   = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT r.*, u.full_name, c.car_name
            FROM Reviews r
            JOIN Users u ON u.user_id = r.user_id
            JOIN Cars  c ON c.car_id  = r.car_id
            ORDER BY r.created_at DESC
        """)
        reviews = _rows_to_list(cursor, cursor.fetchall())
        conn.close()
        return render_template('admin_dashboard.html', active='reviews', reviews=reviews)
    except Exception as e:
        flash(f'Error: {e}', 'danger')
        return render_template('admin_dashboard.html', active='reviews', reviews=[])


@admin_bp.route('/reviews/delete/<int:review_id>', methods=['POST'])
@admin_required
def delete_review(review_id):
    try:
        conn   = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Reviews WHERE review_id=?", review_id)
        conn.commit()
        conn.close()
        flash('Review deleted.', 'success')
    except Exception as e:
        flash(f'Error: {e}', 'danger')
    return redirect(url_for('admin.manage_reviews'))


# ------------ USERS MANAGEMENT ------------

@admin_bp.route('/users')
@admin_required
def manage_users():
    try:
        conn   = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT u.*,
                (SELECT COUNT(*) FROM Bookings b WHERE b.user_id = u.user_id) AS booking_count
            FROM Users u
            ORDER BY u.created_at DESC
        """)
        users = _rows_to_list(cursor, cursor.fetchall())
        conn.close()
        return render_template('admin_dashboard.html', active='users', users=users)
    except Exception as e:
        flash(f'Error: {e}', 'danger')
        return render_template('admin_dashboard.html', active='users', users=[])
