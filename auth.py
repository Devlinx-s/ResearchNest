from functools import wraps
from flask import request, redirect, url_for, flash, session, render_template
from flask_login import LoginManager, login_user, logout_user, current_user
from app import app, db
from models import User

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

def require_login(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def require_admin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
        if not current_user.is_admin:
            flash('Admin access required.', 'error')
            return render_template('403.html'), 403
        return f(*args, **kwargs)
    return decorated_function