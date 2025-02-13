from flask import *
from flask_socketio import *
import os
from bs4 import BeautifulSoup
def strip_html(html):
    # Создаем объект BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")
    # Получаем текст без HTML-разметки
    return soup.get_text()

app = Flask("app")
app.secret_key = os.urandom(128)
sio = SocketIO(app, async_mode = "eventlet", cors_allowed_origins="*")
config = json.load(open("config.json", "r"))
chats = config['initialrooms']
users = {}
phones = ["android", "iphone"]

@app.route("/")
async def main():
    return render_template("index.html", title = config['title'])

@app.route("/login", methods = ["GET", "POST"])
async def login():
    if request.method == "GET":
        return render_template("login.html", title = config['title'])
    else:
        name = request.form.get("name")
        if name != None:
            if len(name) >= 2 and len(name) <= 10:
                session['name'] = name
                return redirect("/chat")
        return redirect("/login")

@app.route("/chat")
async def chat():
    if session.get('name') != None:
        useragent = request.headers.get("User-Agent").lower()
        #Temporary disabled
        #if any(x in useragent for x in phones):
        #    return render_template("mobilechat.html", title = config['title'])
        #else:
        return render_template("chat.html", title = config['title'])
    else:
        return redirect("/login")
@sio.on("connect")
def connect(sid):
    if session.get('name') != None:
        users[session['name']] = request.sid
        emit("connected", {'name': session['name']}, broadcast = True)
        emit("yourdata", {'name': session['name']})
    else:
        emit("error", {"text": "AUTHERROR"})

@sio.on("disconnect")
def disconnect():
    if session.get('name') != None:
        users.pop(session['name'])
        emit("disconnected", {'name': session['name']}, broadcast = True)

@sio.on("send")
def send(data):
    if session.get('name') != None:
        chatid = data['chatid']
        if chatid in chats:
            text = strip_html(data['text'])
            if text != "":
                chats[chatid]['messages'].append({
                    "name": session['name'],
                    "text": text,
                    "type": "user"
                })
                emit("msgstatus", {"status": "sended"})
                emit("message", {"text": text, "name": session['name'], "chat": chatid}, broadcast = True)
    else:
        emit("error", {"text": "AUTHERROR"})

@sio.on("getchat")
def getchat(data):
    if session.get('name') != None:
        chatid = data['chatid']
        if chatid in chats:
            emit('chat', {'chat': chats[chatid], "chatid": chatid})
        else:
            emit('chat', {'chat': 'notfound'})
    else:
        emit("error", {"text": "AUTHERROR"})

@sio.on("listchats")
def listchats():
    if session.get('name') != None:
        emit('chats', {"chatids": [chat for chat in chats], "chats": chats})
    else:
        emit("error", {"text": "AUTHERROR"})
sio.run(app, port = 5000)