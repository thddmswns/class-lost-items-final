from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime

app = Flask(__name__)

# PostgreSQL 환경변수
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

app.config["SQLALCHEMY_DATABASE_URI"] = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# 모델 정의
class LostItem(db.Model):
    __tablename__ = "lost_item"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    place = db.Column(db.String(100), nullable=False)
    contact = db.Column(db.String(50), nullable=False)
    date = db.Column(db.String(20), nullable=False, default=datetime.now().strftime("%Y-%m-%d"))

# 테이블 생성
with app.app_context():
    db.create_all()

@app.route("/", methods=["GET", "POST"])
def index():
    message = ""
    if request.method == "POST":
        if "register" in request.form:
            name = request.form["name"]
            place = request.form["place"]
            contact = request.form["contact"]
            new_item = LostItem(name=name, place=place, contact=contact)
            db.session.add(new_item)
            db.session.commit()
            return redirect("/")
        elif "search" in request.form:
            keyword = request.form["search"]
            items = LostItem.query.filter(
                (LostItem.name.ilike(f"%{keyword}%")) |
                (LostItem.place.ilike(f"%{keyword}%")) |
                (LostItem.contact.ilike(f"%{keyword}%"))
            ).all()
            if not items:
                message = "검색 결과가 없습니다."
            all_items = LostItem.query.all()
            return render_template("index.html", items=items, all_items=all_items, message=message)

    items = []
    all_items = LostItem.query.all()
    return render_template("index.html", items=items, all_items=all_items, message=message)

@app.route("/delete/<int:item_id>", methods=["POST"])
def delete(item_id):
    item = LostItem.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    return redirect("/")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
