from flask import render_template, request
from products import bp
from models import Product, Category

@bp.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    category_id = request.args.get('category', type=int)
    search = request.args.get('search', '')
    
    query = Product.query.filter_by(active=True)
    
    if category_id:
        query = query.filter_by(category_id=category_id)
    
    if search:
        query = query.filter(Product.name.contains(search) | Product.description.contains(search))
    
    products = query.paginate(
        page=page, per_page=12, error_out=False
    )
    
    categories = Category.query.all()
    selected_category = Category.query.get(category_id) if category_id else None
    
    return render_template('products/index.html', 
                         products=products,
                         categories=categories,
                         selected_category=selected_category,
                         search=search)

@bp.route('/category/<int:category_id>')
def category(category_id):
    category = Category.query.get_or_404(category_id)
    page = request.args.get('page', 1, type=int)
    
    products = Product.query.filter_by(category_id=category_id, active=True).paginate(
        page=page, per_page=12, error_out=False
    )
    
    categories = Category.query.all()
    
    return render_template('products/category.html',
                         category=category,
                         products=products,
                         categories=categories)
