from flask import Flask, render_template, redirect, url_for
from config import Config
from extensions import db, login_manager
from routes.tanks import tanks
from extensions import migrate

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.register_blueprint(tanks)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    with app.app_context():
        import models

        from routes.auth import auth
        app.register_blueprint(auth)

    return app

app = create_app()

@app.route("/")
def index():
    return redirect(url_for("tanks.list_tanks"))

if __name__ == "__main__":
    app.run(debug=True)