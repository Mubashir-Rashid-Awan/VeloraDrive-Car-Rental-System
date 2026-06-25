from flask import Flask, jsonify, render_template
from config import Config
from database.connection import get_db_connection

from routes.auth          import auth_bp
from routes.main_routes   import main_bp
from routes.cars_routes   import cars_bp
from routes.booking_routes import booking_bp
from routes.admin_routes  import admin_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.secret_key = Config.SECRET_KEY


    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(cars_bp)
    app.register_blueprint(booking_bp)
    app.register_blueprint(admin_bp)

    # -------- Utility routes --------

    @app.route('/test-db')
    def test_db():
        try:
            conn = get_db_connection()
            conn.close()
            return jsonify({"message": "Database Connected Successfully"})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    # -------- Error handlers --------

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template('500.html', error=str(e)), 500

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
