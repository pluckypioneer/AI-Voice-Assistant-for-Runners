# Import necessary modules
from flask import Flask
from app.api.v1.routes import v1
from app.config.config import Config
from flask_compress import Compress
from flask_jwt_extended import JWTManager
from flask_caching import Cache

# Create a Flask application instance
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = Config.MAX_CONTENT_LENGTH
app.config['JWT_SECRET_KEY'] = Config.JWT_SECRET_KEY
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = Config.JWT_ACCESS_TOKEN_EXPIRES
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = Config.JWT_REFRESH_TOKEN_EXPIRES
app.config['COMPRESS_MIN_SIZE'] = Config.COMPRESS_MIN_SIZE

# Initialize extensions
Compress(app)
jwt = JWTManager(app)
cache = Cache(app, config={'CACHE_TYPE': 'SimpleCache', 'CACHE_DEFAULT_TIMEOUT': 300})

# Register the v1 blueprint with a URL prefix
app.register_blueprint(v1, url_prefix='/api/v1')

# Run the application if this script is executed directly
if __name__ == '__main__':
    # Run the Flask development server with debug mode and port from the configuration
    app.run(debug=Config.DEBUG, port=Config.PORT)