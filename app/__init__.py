from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from config import config
import datetime

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

def create_app(config_name='default'):
    """Application factory function"""
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    
    # Add template context processor for datetime
    @app.context_processor
    def inject_now():
        return {'now': datetime.datetime.now()}

    # Register blueprints
    from app.routes.main import main_bp
    app.register_blueprint(main_bp)

    from app.routes.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.routes.cars import cars_bp
    app.register_blueprint(cars_bp, url_prefix='/cars')

    from app.routes.repairs import repairs_bp
    app.register_blueprint(repairs_bp, url_prefix='/repairs')

    from app.routes.parts import parts_bp
    app.register_blueprint(parts_bp, url_prefix='/parts')

    from app.routes.providers import providers_bp
    app.register_blueprint(providers_bp, url_prefix='/providers')

    from app.routes.stands import stands_bp
    app.register_blueprint(stands_bp, url_prefix='/stands')

    from app.routes.dealers import dealers_bp
    app.register_blueprint(dealers_bp, url_prefix='/dealers')

    from app.routes.reports import reports_bp
    app.register_blueprint(reports_bp, url_prefix='/reports')

    return app 