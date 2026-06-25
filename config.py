import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'velora-drive-secret-2024-xK9mN3pQ')

    DB_SERVER   = os.environ.get('DB_SERVER',   '.\SQLEXPRESS')
    DB_NAME     = os.environ.get('DB_NAME',     'RentACarDB')
    # DB_USER     = os.environ.get('DB_USER',     'sa')
    # DB_PASSWORD = os.environ.get('DB_PASSWORD', 'YourStrong!Passw0rd')
    DB_DRIVER   = os.environ.get('DB_DRIVER',   'ODBC Driver 17 for SQL Server')

    @staticmethod
    def get_connection_string():
        return (
            f"DRIVER={{{Config.DB_DRIVER}}};"
            f"SERVER={Config.DB_SERVER};"
            f"DATABASE={Config.DB_NAME};"
            # f"UID={Config.DB_USER};"
            # f"PWD={Config.DB_PASSWORD};"
            "Trusted_Connection=yes;"
            "TrustServerCertificate=yes;"
        )
