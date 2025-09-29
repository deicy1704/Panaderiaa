from flask import Blueprint

bp = Blueprint('products', __name__)

from products import routes
