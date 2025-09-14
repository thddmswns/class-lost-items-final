from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///lost_items.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# DB 모델 정의
class LostItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    place = db.Column(db.String(100), nullable=False)
    date = db.Column(db.String(50), nullable=False)
    contact = db.Column(db.String(50), nullable=False)

# DB 생성
if not os.path.exists("lost_items.db"):
    with app.app_context():
        db.create_all()

# 메인 페이지
@app.route("/", methods=["GET", "POST"])
def index():
    items = []
    message = ""
    all_items = LostItem.query.all()  # 전체 분실물 리스트
    if request.method == "POST":
        if "register" in request.form:
            # 등록
            name = request.form["name"].strip()
            place = request.form["place"].strip()
            contact = request.form["contact"].strip()
            date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if name and place and contact:
                item = LostItem(name=name, place=place, date=date, contact=contact)
                db.session.add(item)
                db.session.commit()
        elif "search" in request.form:
            # 검색
            query = request.form["search"].strip().lower()
            items = LostItem.query.filter(LostItem.name.ilike(f"%{query}%")).all()
            if not items:
                message = "⚠ 없는 물건입니다."

    return render_template("index.html", items=items, message=message, all_items=all_items)

# 삭제 기능
@app.route("/delete/<int:item_id>", methods=["POST"])
def delete(item_id):
    item = LostItem.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == "__main__":
    # host="0.0.0.0" → 같은 Wi-Fi 안 핸드폰에서도 접속 가능
    app.run(host="0.0.0.0", port=5000, debug=True)
