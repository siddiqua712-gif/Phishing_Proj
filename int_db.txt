from appp import db, app, User
from werkzeug.security import generate_password_hash

with app.app_context():
    # Create all tables
    db.create_all()

    # --- Admin user ---
    if not User.query.filter_by(username="admin").first():
        admin_user = User(
            username="admin",
            password=generate_password_hash("admin123"),
            role="admin"
        )
        db.session.add(admin_user)
        print("Admin user created!")

    # --- Normal user ---
    if not User.query.filter_by(username="user1").first():
        normal_user = User(
            username="user1",
            password=generate_password_hash("user123"),
            role="user"
        )
        db.session.add(normal_user)
        print("Normal user created!")

    # Save changes
    db.session.commit()
    print("Database initialized successfully!")