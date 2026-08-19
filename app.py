from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import Config
from models import db
from routes import register_routes

app = Flask(__name__)
app.config.from_object(Config)

CORS(app)
jwt = JWTManager(app)

db.init_app(app)
register_routes(app)

with app.app_context():
    db.create_all()
    print("✅ پایگاه داده آماده شد")
if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)