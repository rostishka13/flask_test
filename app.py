from flask import Flask, render_template, redirect, url_for
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_sqlalchemy import SQLAlchemy

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt
from flask_login import (
    UserMixin,
    login_user,
    LoginManager,
    login_required,
    logout_user,
    current_user,
)


# config
app = Flask(__name__)
bcrypt = Bcrypt(app)
login = LoginManager(app)
db = SQLAlchemy(app)
app.config["FLASK_ADMIN_SWATHC"] = "cerulean"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SECRET_KEY"] = "thisismykey"
# login config
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# authentication
class RegisterForm(FlaskForm):
    username = StringField(
        validators=[InputRequired(), Length(min=4, max=20)],
        render_kw={"placeholder": "username"},
    )
    password = PasswordField(
        validators=[InputRequired(), Length(min=4, max=20)],
        render_kw={"placeholder": "password"},
    )
    submit = SubmitField("Register")

    def validate_username(self, username):
        existing_user_username = User.query.filter_by(username=username.data).first()

        if existing_user_username:
            raise ValidationError(
                "That usernmae already exist. Please choose a different one"
            )


class LoginForm(FlaskForm):
    username = StringField(
        validators=[InputRequired(), Length(min=4, max=20)],
        render_kw={"placeholder": "username"},
    )
    password = PasswordField(
        validators=[InputRequired(), Length(min=4, max=20)],
        render_kw={"placeholder": "password"},
    )
    submit = SubmitField("Login")


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# route
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for("admin.index"))

    return render_template("login.html", form=form)


@app.route("/logout", methods=["POST", "GET"])
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for("login"))
    return render_template("register.html", form=form)


# model
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, unique=True)
    username = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(80), nullable=False)


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(50), nullable=False)
    product = db.relationship("Product", backref="category", lazy=True)

    def __repr__(self):
        return f"{self.category_name}"


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    color = db.Column(db.String(10))
    weigth = db.Column(db.Integer)
    category_id = db.Column(db.Integer, db.ForeignKey("category.id"), nullable=False)

    def __repr__(self):
        return f"product {self.title}"


# admin settings
class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for("index"))


admin = Admin(
    app, name="Rozetka Test", template_mode="bootstrap3", index_view=MyAdminIndexView()
)
admin.add_view(ModelView(Product, db.session))
admin.add_view(ModelView(Category, db.session))

if __name__ == "__main__":
    app.run(debug=True)
