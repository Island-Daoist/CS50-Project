"""
Implement here.
"""
from flask import Blueprint


bp = Blueprint('main', __name__)


# Module import located at bottom to avoid circular reference issues.
from app.main import routes
