from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# Render 환경변수(DATABASE_URL) 사용, 없으면 로컬 sqlite로 fallback
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    "DATABASE_URL", "sqlite:///local.db"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# 모델 정의 (분실물)
class LostItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)   # 분실물 이름
    place = db.Column(db.String(100), nullable=False)  # 발견 장소
    date = db.Column(db.String(20), nullable=False)    # 발견 날짜

# DB 생성 (앱 컨텍스트 필요)
with app.app_context():
    db.create_all()

# 홈 화면 - 목록 보여주기
@app.route("/")
def index():
    items = LostItem.query.all()
    return render_template("index.html", items=items)

# 분실물 추가
@app.route("/add", methods=["POST"])
def add():
    name = request.form["name"]
    place = request.form["place"]
    date = request.form["date"]

    new_item = LostItem(name=name, place=place, date=date)
    db.session.add(new_item)
    db.session.commit()

    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
