import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
from fpdf  import FPDF  


# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    
    # Database configuration
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///bakery.db")
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    
    # Login manager configuration
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        from models import User
        return User.query.get(int(user_id))
    
    # Register blueprints
    from auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    from products import bp as products_bp
    app.register_blueprint(products_bp, url_prefix='/products')
    
    from cart import bp as cart_bp
    app.register_blueprint(cart_bp, url_prefix='/cart')
    
    from admin import bp as admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    # Main routes
    @app.route('/')
    def index():
        from flask import render_template
        from models import Product, Category
        
        featured_products = Product.query.filter_by(featured=True).limit(6).all()
        categories = Category.query.all()
        
        return render_template('index.html', 
                             featured_products=featured_products,
                             categories=categories)
    
    @app.route('/orders')
    def order_history():
        from flask import render_template
        from flask_login import login_required, current_user
        from models import Order
        
        if not current_user.is_authenticated:
            return login_manager.unauthorized()
            
        orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
        return render_template('orders/history.html', orders=orders)
    
    with app.app_context():
        import models
        db.create_all()
        
        # Create default admin user and sample data
        from werkzeug.security import generate_password_hash
        from models import User, Category, Product
        
        if not User.query.filter_by(email='admin@bakery.com').first():
            admin_user = User(
                username='admin',
                email='admin@bakery.com',
                password_hash=generate_password_hash('admin123'),
                is_admin=True
            )
            db.session.add(admin_user)
            
        # Create default categories
        if not Category.query.first():
            categories = [
                Category(name='Pan', description='Pan fresco recién horneado'),
                Category(name='Pasteles', description='Deliciosos pasteles para toda ocasión'),
                Category(name='Pastelería', description='Dulces y salados artesanales'),
                Category(name='Galletas', description='Galletas caseras tradicionales')
            ]
            for category in categories:
                db.session.add(category)
            
            db.session.commit()
            
            # Add sample products
            sample_products = [
                Product(name='Pan de Masa Madre', description='Pan artesanal tradicional con corteza crujiente y miga esponjosa', 
                       price=5.99, category_id=1, featured=True, active=True),
                Product(name='Croissant de Chocolate', description='Hojaldrado mantecoso relleno de chocolate belga', 
                       price=3.50, category_id=3, featured=True, active=True),
                Product(name='Pastel de Vainilla', description='Clásico pastel de vainilla con crema de mantequilla', 
                       price=25.00, category_id=2, featured=True, active=True),
                Product(name='Galletas Chispas Chocolate', description='Galletas recién horneadas con chispas de chocolate premium', 
                       price=2.99, category_id=4, featured=False, active=True),
                Product(name='Pan Integral', description='Pan saludable de trigo integral con semillas', 
                       price=4.99, category_id=1, featured=False, active=True),
                Product(name='Tarta de Fresa', description='Fresas frescas sobre crema pastelera de vainilla', 
                       price=4.75, category_id=3, featured=True, active=True),
                Product(name='Pastel Red Velvet', description='Delicioso pastel red velvet con frosting de queso crema', 
                       price=28.00, category_id=2, featured=False, active=True),
                Product(name='Galletas de Avena', description='Galletas saludables de avena con pasas', 
                       price=2.75, category_id=4, featured=False, active=True),
                Product(name='Baguette Francesa', description='Auténtica baguette crujiente estilo francés', 
                       price=3.25, category_id=1, featured=False, active=True),
                Product(name='Éclair de Chocolate', description='Hojaldre relleno de crema y cubierto de chocolate', 
                       price=4.50, category_id=3, featured=False, active=True),
                Product(name='Pastel de Zanahoria', description='Húmedo pastel de zanahoria con frosting de queso', 
                       price=26.00, category_id=2, featured=True, active=True),
                Product(name='Alfajores', description='Deliciosos alfajores rellenos de dulce de leche', 
                       price=3.99, category_id=4, featured=True, active=True)
            ]
            
            for product in sample_products:
                db.session.add(product)
                
        db.session.commit()
    
    return app

# Create app instance
app = create_app()
