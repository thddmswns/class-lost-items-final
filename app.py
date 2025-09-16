from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os
from werkzeug.utils import secure_filename
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

# 업로드 폴더
UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

db = SQLAlchemy(app)

# 모델 정의
class LostItem(db.Model):
    __tablename__ = "lost_item"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    place = db.Column(db.String(100), nullable=False)
    contact = db.Column(db.String(100), nullable=False)
    date = db.Column(db.String(20), nullable=False)
    image = db.Column(db.String(200))  # 이미지 파일명 저장

with app.app_context():
    db.create_all()

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/", methods=["GET", "POST"])
def index():
    message = ""
    items = None

    if request.method == "POST":
        # 등록
        if "register" in request.form:
            name = request.form["name"]
            place = request.form["place"]
            contact = request.form["contact"]
            date = datetime.now().strftime("%Y-%m-%d")

            file = request.files.get("image")
            filename = None
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

            new_item = LostItem(name=name, place=place, contact=contact, date=date, image=filename)
            db.session.add(new_item)
            db.session.commit()
            return redirect("/")

        # 검색
        if "search" in request.form:
            keyword = request.form["search"]
            items = LostItem.query.filter(
                (LostItem.name.ilike(f"%{keyword}%")) |
                (LostItem.place.ilike(f"%{keyword}%")) |
                (LostItem.contact.ilike(f"%{keyword}%"))
            ).all()
            if not items:
                message = "검색 결과가 없습니다."
            return render_template("index.html", items=items, all_items=LostItem.query.all(), message=message)

    items = LostItem.query.all()
    return render_template("index.html", all_items=items, message=message)

@app.route("/delete/<int:item_id>", methods=["POST"])
def delete(item_id):
    item = LostItem.query.get(item_id)
    if item:
        if item.image:
            path = os.path.join(app.config["UPLOAD_FOLDER"], item.image)
            if os.path.exists(path):
                os.remove(path)
        db.session.delete(item)
        db.session.commit()
    return redirect("/")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
