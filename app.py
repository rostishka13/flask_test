from flask import Flask, render_template
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config["FLASK_ADMIN_SWATHC"] = "cerulean"


db = SQLAlchemy(app)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SECRET_KEY"] = "thisismykey"


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


admin = Admin(app, name="Rozetka Test", template_mode="bootstrap3")
admin.add_view(ModelView(Product, db.session))
admin.add_view(ModelView(Category, db.session))

if __name__ == "__main__":
    app.run(debug=True)
