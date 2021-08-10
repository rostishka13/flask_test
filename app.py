from flask import Flask, render_template, redirect, url_for
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, current_user

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError


# config
app = Flask(__name__)
login = LoginManager(app)
db = SQLAlchemy(app)
app.config["FLASK_ADMIN_SWATHC"] = "cerulean"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SECRET_KEY"] = "thisismykey"


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


@login.user_loader
def load_user(user_id):
    return User.query.get(user_id)


# route
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login")
def login():
    form = LoginForm()
    return render_template("login.html", form=form)


@app.route("/register")
def register():
    form = RegisterForm()
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
