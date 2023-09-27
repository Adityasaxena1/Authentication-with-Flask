from flask import Flask, render_template, request, url_for, redirect, flash, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret-key-goes-here'

# CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy()
db.init_app(app)
login_manager = LoginManager(app)
login_manager.init_app(app)




# CREATE TABLE IN DB
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
 
 
with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def home():
    return render_template("index.html")


@app.route('/register', methods=["POST", "GET"])
def register():
    if request.method == "POST":
        email = request.form.get("email")
        result = db.session.execute(db.select(User).where(User.email == email))
        user = result.scalar()
        if user:
            flash("You've already signed up with that email, login instead!")
            return redirect(url_for('login'))

        new_user = User(
            name=request.form.get("name"),
            email=request.form.get("email"),
            password=generate_password_hash(request.form.get("password"), method='pbkdf2:sha256', salt_length=8)
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return render_template("secrets.html", name=request.form.get("name"))
    return render_template("register.html")


@app.route('/login', methods=["POST", "GET"])
def login():
    if request.method=="POST":
        email=request.form.get("email")
        password=request.form.get("password")
        result = db.session.execute(db.select(User).where(User.email==email))
        user = result.scalar()
        if not user:
            flash("email doesn't exist try again.")
            return redirect(url_for('login'))
        elif  not check_password_hash(user.password, password):
            flash("Password incorrect. Try again!")
            return redirect(url_for('login'))
        else:
            login_user(user)
            return redirect(url_for('secrets'))


    return render_template("login.html")


@app.route('/secrets')
@login_required
def secrets():
    return render_template("secrets.html", name=current_user.name)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/download')
@login_required
def download():
    return send_from_directory(
       "static", path="files/cheat_sheet.pdf"
    )


if __name__ == "__main__":
    app.run(debug=True)
