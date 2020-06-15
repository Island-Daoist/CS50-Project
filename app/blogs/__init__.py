"""
Implement here.
"""
from flask import Blueprint


bp = Blueprint('blogs', __name__)


# Module import located at bottom to avoid circular reference issues.
from app.blogs import routes
