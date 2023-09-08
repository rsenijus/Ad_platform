from flask import Flask, render_template, request, url_for, redirect, make_response, jsonify, send_from_directory
from math import ceil
import os
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from kodland_db import db

import bcrypt

def hashed_password(plain_text_password):
    return bcrypt.hashpw(plain_text_password.encode('utf-8'), bcrypt.gensalt()) 

def check_password(plain_text_password, hashed_password):
    return bcrypt.checkpw(plain_text_password.encode('utf-8'), hashed_password)

app = Flask(__name__)

app.config.update(
    SECRET_KEY = 'qwertars'
)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

class User(UserMixin):
    def __init__(self, id):
        self.id = id
        
@login_manager.user_loader
def load_user(login):
    return User(login)

app.config['MAX_CONTENT_LENGTH'] = 1024**3
app.config['UPLOAD_FOLDER'] = 'C:\\Users\\suhin\\OneDrive\\Рабочий стол\\Python\\Рекламная платформа\\static\\'

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'video' in request.files and 'image' in request.files:
        video = request.files['video']
        image = request.files['image']
        if video and image and allowed_file(video.filename, {"mp4", "mov", "avi"}) and allowed_file(image.filename, {"png", "jpg", "jpeg"}):
            filename = db.publicity.get_all()
            filename = str(int(filename[len(filename)-1].id)+1)
            videotype = video.filename.rsplit(".",1)[1].lower()
            imagetype = image.filename.rsplit(".",1)[1].lower()
            try:
                video.save(os.path.join(app.config['UPLOAD_FOLDER']+'videos\\', filename + "." + videotype))
                image.save(os.path.join(app.config['UPLOAD_FOLDER']+'images\\', filename + "." + imagetype))
                data = {"name": request.form["name"],
                        "description": request.form["description"],
                        "author": request.form["login"],
                        "videotype": videotype,
                        "imagetype": imagetype,
                        "moderated": 0,
                        "users": 10}
                db.publicity.put(data)
            except Exception as e:
                return f'Error код загрузки: {str(e)}', 500
            return redirect(url_for("index"))

    return 'Создание апликации невозможна'

ALLOWED_EXTENSIONS = {"mp4", "mov", "avi"}

def allowed_file(filename, extenstions):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in extenstions
           
@app.errorhandler(413)
def too_large(e):
    return make_response(jsonify(message="Файл слишком большой"), 413)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/publicity=<id>", methods=["GET", "POST"])
def publicity(id):
    pub = db.publicity.get("id", id)
    if pub.moderated:
        if request.method == "POST":
            login = db.login.get("login", request.form["login"])
            if not login:
                return render_template("publicity.html", pub=pub, message="Неправильный логин")
            if login.password != request.form["password"]:
                return render_template("publicity.html", pub=pub, message="Неправильный пароль")
            if login.coins < request.form["number"]:
                return render_template("publicity.html", pub=pub, message="Недостаточно coins")
            db.publicity.update("id", id, "users", pub.users+request.form["number"])
            db.login.update("login", request.form["login"], "coins", login.coins-2*int(request.form["number"]))
        return render_template("publicity.html", pub=pub)

@app.route("/page=<page>")
def page(page):
    content = db.publicity.get_all().reverse()
    con = 5
    page=int(page)
    maxpage = ceil(len(content)/con) 
    if page != maxpage:
        content = content[(page-1)*con:page*con]
    else:
        content = content[(page-1)*con:]
    return render_template("page.html", page=page, maxpage=maxpage, content=content)

@app.route("/search=<search>", methods=["GET","POST"])
def search(search):
    elem = db.publicity.get_all().reverse()
    if request.method == 'POST' and request.form['search'] != "":
        return redirect(url_for('search', search=request.form['search']))
    elems = []
    for el in elem:
        if search in el.description or search in el.name:
            elems.append(el)
    return render_template("search.html", search=search, elems=elems)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        for key in request.form:
            if request.form[key] == '':
                return render_template('register.html', message='Все поля должны быть заполнены!')
        row = db.login.get('login', request.form['login'])
        if row:
            return render_template('register.html', message='Такой логин уже есть')
        
        if request.form['password'] != request.form['password_check']:
            return render_template('register.html', message='Пароли не совпадают')
        
        data = dict(request.form)
        data['password'] = hashed_password(request.form['password'])
        data.pop('password_check')
        data["coins"] = 0
        db.login.put(data)
        return redirect(url_for('index'))
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        row = db.login.get('login', request.form['login'])
        if not row and not check_password(request.form['password'] , row.password):
            return render_template('login.html', message='Неправильный логин или пароль')
        user = User(row.login)
        login_user(user)
        return redirect(url_for('info'))
    return render_template('login.html')

@app.route("/moderation")
@login_required
def moderation():
    return render_template("moderation.html")

@app.route("/proof_moderation", methods=["GET", "POST"])
def proof_moderation():
    if request.method == "GET":
        return render_template("proofmoderation.html")
    if not db.publicity.get("id", request.form["id"]):
        return render_template("proofmoderation.html", message="Неправильный id")
    if not db.login.get("login", request.form["login"]):
        return render_template("proofmoderation.html", message="Неправильный логин")
    if not request.form["proof"]:
        return render_template("proofmoderation.html", message="Вы не ввели доказательство")
    data = {"pub_id": request.form["id"], "proof": request.form["proof"], "author": request.form["login"], "moderated": 0}
    db.proofs.put(data)
    return render_template("proofmoderation.html", message="Операция произошла успешно")

@app.route("/buycoins", methods=["GET", "POST"])
@login_required
def buycoins():
    if request.method == "POST":
        coins = db.login.get('login', request.form['login'])
        if not coins:
            return render_template("buycoins.html", message="Неправильный логин")
        db.login.update('login', request.form['login'], 'coins', coins.coins+int(request.form["coins"]))
        return redirect(url_for("index"))
    return render_template("buycoins.html")

@app.route("/info", methods=["GET", "POST"])
@login_required
def info():
    if request.method == "POST":
        return render_template("info.html", search=True, login=db.login.get("login", request.form["login"]), pub=db.publicity.get_all())
    return render_template("info.html", search=False)

@app.route("/file=<name>type=<type>")
def file(name, type):
    return send_from_directory(f"{app.config['UPLOAD_FOLDER']}{type}s\\", name, as_attachment=False)

app.run()