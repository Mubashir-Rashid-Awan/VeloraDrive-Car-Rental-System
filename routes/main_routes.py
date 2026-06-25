from flask import Blueprint, render_template, request
from database.connection import get_db_connection

main_bp = Blueprint('main', __name__)


def _row_to_dict(cursor, row):
    if row is None:
        return None
    cols = [col[0] for col in cursor.description]
    return dict(zip(cols, row))


def _rows_to_list(cursor, rows):
    cols = [col[0] for col in cursor.description]
    return [dict(zip(cols, r)) for r in rows]


@main_bp.route('/')
def index():
    try:
        conn   = get_db_connection()
        cursor = conn.cursor()

        # Featured cars (6)
        cursor.execute("""
            SELECT TOP 6 c.*, cat.category_name,
                COALESCE((SELECT AVG(CAST(r.rating AS FLOAT)) FROM Reviews r WHERE r.car_id = c.car_id), 0) AS avg_rating,
                COALESCE((SELECT COUNT(*) FROM Reviews r WHERE r.car_id = c.car_id), 0) AS review_count
            FROM Cars c
            LEFT JOIN Car_Categories cat ON cat.category_id = c.category_id
            WHERE c.availability_status = 'Available'
            ORDER BY c.created_at DESC
        """)
        featured_cars = _rows_to_list(cursor, cursor.fetchall())

        # Categories
        cursor.execute("SELECT * FROM Car_Categories")
        categories = _rows_to_list(cursor, cursor.fetchall())

        # Stats
        cursor.execute("SELECT COUNT(*) FROM Cars")
        total_cars = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM Users")
        total_users = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM Bookings WHERE booking_status IN ('Confirmed','Completed')")
        total_bookings = cursor.fetchone()[0]

        # Testimonials
        cursor.execute("""
            SELECT TOP 6 r.rating, r.comment, u.full_name, u.profile_image
            FROM Reviews r
            JOIN Users u ON u.user_id = r.user_id
            ORDER BY r.created_at DESC
        """)
        testimonials = _rows_to_list(cursor, cursor.fetchall())

        conn.close()
        return render_template('index.html',
            featured_cars=featured_cars,
            categories=categories,
            total_cars=total_cars,
            total_users=total_users,
            total_bookings=total_bookings,
            testimonials=testimonials
        )
    except Exception as e:
        return render_template('index.html',
            featured_cars=[], categories=[], total_cars=0,
            total_users=0, total_bookings=0, testimonials=[],
            db_error=str(e)
        )


@main_bp.route('/about')
def about():
    return render_template('about.html')


@main_bp.route('/contact')
def contact():
    return render_template('contact.html')
