from flask import Flask, render_template
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, current_user

app = Flask(__name__)
login = LoginManager(app)


app.config["FLASK_ADMIN_SWATHC"] = "cerulean"


db = SQLAlchemy(app)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SECRET_KEY"] = "thisismykey"


@login.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.route("/")
def index():
    return render_template("index.html")


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)


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


class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated


admin = Admin(
    app, name="Rozetka Test", template_mode="bootstrap3", index_view=MyAdminIndexView()
)
admin.add_view(ModelView(Product, db.session))
admin.add_view(ModelView(Category, db.session))

if __name__ == "__main__":
    app.run(debug=True)
