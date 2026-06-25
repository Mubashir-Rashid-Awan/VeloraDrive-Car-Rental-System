from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from datetime import datetime
from database.connection import get_db_connection

booking_bp = Blueprint('booking', __name__)


def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to continue.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


def _row_to_dict(cursor, row):
    if row is None:
        return None
    cols = [col[0] for col in cursor.description]
    return dict(zip(cols, row))


def _rows_to_list(cursor, rows):
    cols = [col[0] for col in cursor.description]
    return [dict(zip(cols, r)) for r in rows]


def _generate_invoice_number():
    return f"INV-{datetime.now().strftime('%Y%m%d')}-{datetime.now().strftime('%H%M%S')}"


@booking_bp.route('/book/<int:car_id>', methods=['GET', 'POST'])
@login_required
def book_car(car_id):
    try:
        conn   = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT c.*, cat.category_name
            FROM Cars c
            LEFT JOIN Car_Categories cat ON cat.category_id = c.category_id
            WHERE c.car_id = ?
        """, car_id)
        row = cursor.fetchone()
        if not row:
            conn.close()
            flash('Car not found.', 'danger')
            return redirect(url_for('cars.cars_list'))
        cols = [col[0] for col in cursor.description]
        car  = dict(zip(cols, row))

        if car['availability_status'] != 'Available':
            conn.close()
            flash('This car is not available for booking.', 'warning')
            return redirect(url_for('cars.car_detail', car_id=car_id))

        if request.method == 'POST':
            pickup_location = request.form.get('pickup_location', '').strip()
            return_location = request.form.get('return_location', '').strip()
            pickup_date_str = request.form.get('pickup_date', '')
            return_date_str = request.form.get('return_date', '')

            if not all([pickup_location, return_location, pickup_date_str, return_date_str]):
                flash('All fields are required.', 'danger')
                conn.close()
                return render_template('booking.html', car=car)

            pickup_date = datetime.strptime(pickup_date_str, '%Y-%m-%d')
            return_date = datetime.strptime(return_date_str, '%Y-%m-%d')

            if return_date <= pickup_date:
                flash('Return date must be after pickup date.', 'danger')
                conn.close()
                return render_template('booking.html', car=car)

            total_days   = (return_date - pickup_date).days
            total_amount = total_days * float(car['price_per_day'])
            user_id      = session['user_id']

            # Insert booking
            cursor.execute("""
                INSERT INTO Bookings (user_id, car_id, pickup_location, return_location,
                    pickup_date, return_date, total_days, total_amount, booking_status)
                OUTPUT INSERTED.booking_id
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'Pending')
            """, user_id, car_id, pickup_location, return_location,
                pickup_date, return_date, total_days, total_amount)
            booking_id = cursor.fetchone()[0]

            # Update car availability
            cursor.execute("UPDATE Cars SET availability_status='Rented', updated_at=GETDATE() WHERE car_id=?", car_id)

            # Create payment record
            cursor.execute("""
                INSERT INTO Payments (booking_id, amount, payment_method, payment_status)
                VALUES (?, ?, 'Credit Card', 'Unpaid')
            """, booking_id, total_amount)

            # Auto-generate invoice
            inv_number = _generate_invoice_number()
            cursor.execute("""
                INSERT INTO Invoices (booking_id, invoice_number, amount, user_id)
                VALUES (?, ?, ?, ?)
            """, booking_id, inv_number, total_amount, user_id)

            conn.commit()
            conn.close()
            flash('Booking created! Please complete your payment.', 'success')
            return redirect(url_for('booking.payment', booking_id=booking_id))

        conn.close()
        return render_template('booking.html', car=car)
    except Exception as e:
        flash(f'Booking error: {e}', 'danger')
        return redirect(url_for('cars.car_detail', car_id=car_id))


@booking_bp.route('/payment/<int:booking_id>', methods=['GET', 'POST'])
@login_required
def payment(booking_id):
    try:
        conn   = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT b.*, c.car_name, c.brand, c.car_image, c.price_per_day,
                   p.payment_id, p.payment_status, p.payment_method
            FROM Bookings b
            JOIN Cars c ON c.car_id = b.car_id
            LEFT JOIN Payments p ON p.booking_id = b.booking_id
            WHERE b.booking_id = ? AND b.user_id = ?
        """, booking_id, session['user_id'])
        row = cursor.fetchone()
        if not row:
            conn.close()
            flash('Booking not found.', 'danger')
            return redirect(url_for('booking.my_bookings'))

        cols    = [col[0] for col in cursor.description]
        booking = dict(zip(cols, row))

        if request.method == 'POST':
            payment_method = request.form.get('payment_method', 'Credit Card')
            # Simulate payment
            cursor.execute("""
                UPDATE Payments SET payment_status='Paid', payment_method=?, transaction_date=GETDATE()
                WHERE booking_id=?
            """, payment_method, booking_id)
            cursor.execute("""
                UPDATE Bookings SET booking_status='Confirmed' WHERE booking_id=?
            """, booking_id)
            conn.commit()
            conn.close()
            flash('Payment successful! Your booking is confirmed.', 'success')
            return redirect(url_for('booking.invoice', booking_id=booking_id))

        conn.close()
        return render_template('payment.html', booking=booking)
    except Exception as e:
        flash(f'Payment error: {e}', 'danger')
        return redirect(url_for('booking.my_bookings'))


@booking_bp.route('/invoice/<int:booking_id>')
@login_required
def invoice(booking_id):
    try:
        conn   = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT b.*, c.car_name, c.brand, c.model_year, c.car_image,
                   u.full_name, u.email, u.phone,
                   p.payment_method, p.payment_status, p.transaction_date,
                   i.invoice_number, i.issued_date
            FROM Bookings b
            JOIN Cars c  ON c.car_id  = b.car_id
            JOIN Users u ON u.user_id = b.user_id
            LEFT JOIN Payments p ON p.booking_id = b.booking_id
            LEFT JOIN Invoices i ON i.booking_id = b.booking_id
            WHERE b.booking_id = ? AND b.user_id = ?
        """, booking_id, session['user_id'])
        row = cursor.fetchone()
        conn.close()
        if not row:
            flash('Invoice not found.', 'danger')
            return redirect(url_for('booking.my_bookings'))
        cols    = [col[0] for col in cursor.description]
        booking = dict(zip(cols, row))
        return render_template('invoice.html', booking=booking)
    except Exception as e:
        flash(f'Error: {e}', 'danger')
        return redirect(url_for('booking.my_bookings'))


@booking_bp.route('/dashboard/bookings')
@login_required
def my_bookings():
    try:
        conn   = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT b.*, c.car_name, c.brand, c.car_image,
                   p.payment_status, p.payment_method
            FROM Bookings b
            JOIN Cars c ON c.car_id = b.car_id
            LEFT JOIN Payments p ON p.booking_id = b.booking_id
            WHERE b.user_id = ?
            ORDER BY b.created_at DESC
        """, session['user_id'])
        cols     = [col[0] for col in cursor.description]
        bookings = [dict(zip(cols, r)) for r in cursor.fetchall()]
        conn.close()
        return render_template('dashboard.html', bookings=bookings, active_tab='bookings')
    except Exception as e:
        flash(f'Error: {e}', 'danger')
        return redirect(url_for('main.index'))


@booking_bp.route('/dashboard')
@login_required
def dashboard():
    return redirect(url_for('booking.my_bookings'))


@booking_bp.route('/dashboard/profile', methods=['GET', 'POST'])
@login_required
def profile():
    try:
        conn   = get_db_connection()
        cursor = conn.cursor()
        user_id = session['user_id']

        if request.method == 'POST':
            full_name = request.form.get('full_name', '').strip()
            phone     = request.form.get('phone', '').strip()
            profile_image = request.form.get('profile_image', '').strip()

            cursor.execute("""
                UPDATE Users SET full_name=?, phone=?, profile_image=?, updated_at=GETDATE()
                WHERE user_id=?
            """, full_name, phone or None, profile_image or 'default.jpg', user_id)
            conn.commit()
            session['user_name'] = full_name
            flash('Profile updated successfully.', 'success')

        cursor.execute("SELECT * FROM Users WHERE user_id=?", user_id)
        row  = cursor.fetchone()
        cols = [col[0] for col in cursor.description]
        user = dict(zip(cols, row))

        cursor.execute("""
            SELECT b.*, c.car_name, c.brand, c.car_image,
                   p.payment_status
            FROM Bookings b
            JOIN Cars c ON c.car_id = b.car_id
            LEFT JOIN Payments p ON p.booking_id = b.booking_id
            WHERE b.user_id = ?
            ORDER BY b.created_at DESC
        """, user_id)
        cols2    = [col[0] for col in cursor.description]
        bookings = [dict(zip(cols2, r)) for r in cursor.fetchall()]

        conn.close()
        return render_template('dashboard.html', user=user, bookings=bookings, active_tab='profile')
    except Exception as e:
        flash(f'Error: {e}', 'danger')
        return redirect(url_for('booking.my_bookings'))


@booking_bp.route('/review/<int:car_id>', methods=['POST'])
@login_required
def submit_review(car_id):
    rating  = request.form.get('rating', 0)
    comment = request.form.get('comment', '').strip()
    try:
        conn   = get_db_connection()
        cursor = conn.cursor()
        # Only allow review if user has completed booking for this car
        cursor.execute("""
            SELECT 1 FROM Bookings
            WHERE user_id=? AND car_id=? AND booking_status IN ('Confirmed','Completed')
        """, session['user_id'], car_id)
        if not cursor.fetchone():
            flash('You can only review cars you have rented.', 'warning')
            conn.close()
            return redirect(url_for('cars.car_detail', car_id=car_id))

        cursor.execute(
            "INSERT INTO Reviews (user_id, car_id, rating, comment) VALUES (?,?,?,?)",
            session['user_id'], car_id, int(rating), comment
        )
        conn.commit()
        conn.close()
        flash('Review submitted! Thank you.', 'success')
    except Exception as e:
        flash(f'Review error: {e}', 'danger')
    return redirect(url_for('cars.car_detail', car_id=car_id))
