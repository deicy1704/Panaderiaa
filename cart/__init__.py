from flask import Blueprint

bp = Blueprint('cart', __name__)

from cart import routes
