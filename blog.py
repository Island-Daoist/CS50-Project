"""
The file that calls the application factory function.
Has some shell context setup as well, but not fully implemented.
"""

from app import create_app, db
from app.models import Users


app = create_app()


# Started implementing, but needs to be revised at a later date
@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Users': Users}
