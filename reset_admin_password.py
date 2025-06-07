from app import app, db
from models import User
from werkzeug.security import generate_password_hash

with app.app_context():
    # Find the admin user
    admin = User.query.filter_by(email='admin@researchnest.local').first()
    if admin:
        # Set a new password
        new_password = 'admin123'  # Using the same password as before
        admin.password_hash = generate_password_hash(new_password)
        db.session.commit()
        print("Admin password has been reset successfully!")
        print(f"Email: admin@researchnest.local")
        print(f"Password: {new_password}")
    else:
        print("Admin user not found. Creating a new admin user...")
        admin = User(
            email='admin@researchnest.local',
            first_name='Admin',
            last_name='User',
            is_admin=True
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print("Admin user created successfully!")
        print(f"Email: admin@researchnest.local")
        print("Password: admin123")
