from flask import Blueprint, render_template, request, jsonify
from database.connection import get_db_connection

cars_bp = Blueprint('cars', __name__)


def _rows_to_list(cursor, rows):
    cols = [col[0] for col in cursor.description]
    return [dict(zip(cols, r)) for r in rows]


@cars_bp.route('/cars')
def cars_list():
    category   = request.args.get('category', '')
    min_price  = request.args.get('min_price', '')
    max_price  = request.args.get('max_price', '')
    search     = request.args.get('search', '').strip()
    sort       = request.args.get('sort', '')
    fuel       = request.args.get('fuel', '')
    trans      = request.args.get('transmission', '')

    query = """
        SELECT c.*, cat.category_name,
            COALESCE((SELECT AVG(CAST(r.rating AS FLOAT)) FROM Reviews r WHERE r.car_id = c.car_id), 0) AS avg_rating,
            COALESCE((SELECT COUNT(*) FROM Reviews r WHERE r.car_id = c.car_id), 0) AS review_count
        FROM Cars c
        LEFT JOIN Car_Categories cat ON cat.category_id = c.category_id
        WHERE 1=1
    """
    params = []

    if category:
        query += " AND cat.category_name = ?"
        params.append(category)
    if min_price:
        query += " AND c.price_per_day >= ?"
        params.append(float(min_price))
    if max_price:
        query += " AND c.price_per_day <= ?"
        params.append(float(max_price))
    if search:
        query += " AND (c.car_name LIKE ? OR c.brand LIKE ?)"
        params.extend([f'%{search}%', f'%{search}%'])
    if fuel:
        query += " AND c.fuel_type = ?"
        params.append(fuel)
    if trans:
        query += " AND c.transmission = ?"
        params.append(trans)

    if sort == 'price_asc':
        query += " ORDER BY c.price_per_day ASC"
    elif sort == 'price_desc':
        query += " ORDER BY c.price_per_day DESC"
    else:
        query += " ORDER BY c.created_at DESC"

    try:
        conn   = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        all_cars = _rows_to_list(cursor, cursor.fetchall())

        cursor.execute("SELECT * FROM Car_Categories ORDER BY category_name")
        categories = _rows_to_list(cursor, cursor.fetchall())
        conn.close()
    except Exception as e:
        all_cars   = []
        categories = []

    return render_template('cars.html',
        cars=all_cars,
        categories=categories,
        selected_category=category,
        min_price=min_price,
        max_price=max_price,
        search=search,
        sort=sort,
        fuel=fuel,
        transmission=trans
    )


@cars_bp.route('/car/<int:car_id>')
def car_detail(car_id):
    try:
        conn   = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT c.*, cat.category_name,
                COALESCE((SELECT AVG(CAST(r.rating AS FLOAT)) FROM Reviews r WHERE r.car_id = c.car_id), 0) AS avg_rating,
                COALESCE((SELECT COUNT(*) FROM Reviews r WHERE r.car_id = c.car_id), 0) AS review_count
            FROM Cars c
            LEFT JOIN Car_Categories cat ON cat.category_id = c.category_id
            WHERE c.car_id = ?
        """, car_id)
        row = cursor.fetchone()
        if not row:
            conn.close()
            return render_template('404.html'), 404

        cols = [col[0] for col in cursor.description]
        car  = dict(zip(cols, row))

        cursor.execute("""
            SELECT r.*, u.full_name, u.profile_image
            FROM Reviews r
            JOIN Users u ON u.user_id = r.user_id
            WHERE r.car_id = ?
            ORDER BY r.created_at DESC
        """, car_id)
        reviews = _rows_to_list(cursor, cursor.fetchall())

        # Related cars
        cursor.execute("""
            SELECT TOP 3 c.*, cat.category_name
            FROM Cars c
            LEFT JOIN Car_Categories cat ON cat.category_id = c.category_id
            WHERE c.car_id != ? AND c.category_id = ?
            ORDER BY NEWID()
        """, car_id, car.get('category_id'))
        related = _rows_to_list(cursor, cursor.fetchall())

        conn.close()
        return render_template('car_detail.html', car=car, reviews=reviews, related_cars=related)
    except Exception as e:
        return render_template('500.html', error=str(e)), 500


# JSON API
@cars_bp.route('/all-cars')
def all_cars_api():
    try:
        conn   = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT c.car_id, c.car_name, c.brand, c.model_year,
                   c.price_per_day, c.fuel_type, c.transmission,
                   c.seating_capacity, c.car_image, c.availability_status,
                   cat.category_name
            FROM Cars c
            LEFT JOIN Car_Categories cat ON cat.category_id = c.category_id
        """)
        cols = [col[0] for col in cursor.description]
        cars = [dict(zip(cols, r)) for r in cursor.fetchall()]
        conn.close()
        return jsonify(cars)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
