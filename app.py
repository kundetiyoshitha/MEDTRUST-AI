from flask import Flask, render_template

from routes.analysis import analysis_bp
from routes.history import history_bp


app = Flask(__name__)


# ============================================================
# BLUEPRINTS
# ============================================================

app.register_blueprint(analysis_bp)
app.register_blueprint(history_bp)


# ============================================================
# PUBLIC PAGES
# ============================================================

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/access")
def access():
    return render_template("access.html")


@app.route("/user-login")
def user_login():
    return render_template("user-login.html")


@app.route("/admin-login")
def admin_login():
    return render_template("admin-login.html")


# ============================================================
# USER MODULE
# ============================================================

@app.route("/user-dashboard")
def user_dashboard():
    return render_template(
        "user-dashboard.html",
        active_page="dashboard"
    )


@app.route("/analyze")
def analyze():
    return render_template(
        "analyze.html",
        active_page="analyze"
    )


@app.route("/evidence")
def evidence():
    return render_template(
        "evidence.html",
        active_page="evidence"
    )


@app.route("/learning")
def learning():
    return render_template(
        "learning.html",
        active_page="learning"
    )


@app.route("/settings")
def settings():
    return render_template(
        "settings.html",
        active_page="settings"
    )


# ============================================================
# HISTORY
# ============================================================

@app.route("/history")
def history():
    return render_template(
        "history.html",
        active_page="history"
    )


@app.route("/history/<int:analysis_id>")
def history_detail(analysis_id):
    return render_template(
        "history-detail.html",
        analysis_id=analysis_id,
        active_page="history"
    )


# ============================================================
# ADMIN MODULE
# ============================================================

@app.route("/admin-dashboard")
def admin_dashboard():
    return render_template(
        "admin-dashboard.html",
        active_page="admin-dashboard"
    )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    app.run(debug=True)