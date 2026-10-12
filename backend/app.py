from flask_cors import CORS
from extensions import limiter
from flask import Flask
from sqlalchemy import text
from sqlalchemy.engine import URL
from dotenv import load_dotenv
import os

from models import db
from auth import auth_bp
from tickets import tickets_bp
from flask_jwt_extended import JWTManager


load_dotenv()


app = Flask(__name__)
CORS(
    app,
    resources={
        r"/api/*": {
            "origins": [
                "http://localhost:5173",
                "http://127.0.0.1:5173"
            ]
        }
    }
)
limiter.init_app(app)



# ==========================================
# JWT CONFIGURATION
# ==========================================

jwt_secret_key = os.getenv("JWT_SECRET_KEY")

if not jwt_secret_key:
    raise RuntimeError(
        "JWT_SECRET_KEY is missing. Set it in the backend .env file."
    )

app.config["JWT_SECRET_KEY"] = jwt_secret_key

jwt = JWTManager(app)





# ==========================================
# DATABASE CONFIGURATION
# ==========================================

db_url = URL.create(
    drivername="mysql+pymysql",
    username=os.getenv("MYSQL_USER"),
    password=os.getenv("MYSQL_PASSWORD"),
    host=os.getenv("MYSQL_HOST"),
    port=int(os.getenv("MYSQL_PORT")),
    database=os.getenv("MYSQL_DATABASE")
)

app.config["SQLALCHEMY_DATABASE_URI"] = db_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


db.init_app(app)


# ==========================================
# BLUEPRINTS
# ==========================================

app.register_blueprint(
    auth_bp,
    url_prefix="/api/auth"
)

app.register_blueprint(
    tickets_bp,
    url_prefix="/api/tickets"
)




# ==========================================
# HOME
# ==========================================

@app.route("/")
def home():
    return {
        "message": "AI IT Support System Backend is running!",
        "database": "ai_support_db"
    }


# ==========================================
# HEALTH CHECK
# ==========================================

@app.route("/health")
def health():
    try:
        db.session.execute(text("SELECT 1"))

        return {
            "status": "healthy",
            "database": "connected"
        }

    except Exception as e:

        return {
            "status": "error",
            "database": "disconnected",
            "message": str(e)
        }, 500


# ==========================================
# START SERVER
# ==========================================


if __name__ == "__main__":
    debug_mode = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    app.run(debug=debug_mode)
