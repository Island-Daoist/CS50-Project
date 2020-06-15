"""
Implement here.
"""
from flask import Blueprint


bp = Blueprint('errors', __name__)


# Module import located at bottom to avoid circular reference issues.
from app.errors import handlers