from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)  # Flask 변수

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lostitems.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class LostItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    location = db.Column(db.String(100))
    contact = db.Column(db.String(100))
    date = db.Column(db.DateTime, default=datetime.now)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        item_name = request.form["name"]
        item_location = request.form["location"]
        item_contact = request.form["contact"]
        if item_name and item_location and item_contact:
            new_item = LostItem(name=item_name, location=item_location, contact=item_contact)
            db.session.add(new_item)
            db.session.commit()
    items = LostItem.query.all()
    return render_template("index.html", items=items)

if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)
