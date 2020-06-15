"""
Implement here.
"""
from flask import Blueprint


bp = Blueprint('auth', __name__)


# Module import located at bottom to avoid circular reference issues.
from app.auth import routes
