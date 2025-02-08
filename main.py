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
sio = SocketIO(app, async_mode = "eventlet")
chats = {
    "main": {
        "title": "Main room",
        "description": "Hang out!",
        "messages": []
    },
    "second": {
        "title": "Second room",
        "description": "If main was too small.",
        "messages": []
    },
    "third": {
        "title": "Test zone",
        "description": "Scary things...",
        "messages": []
    }
}
users = []

@app.route("/")
async def main():
    return render_template("index.html")

@app.route("/login", methods = ["GET", "POST"])
async def login():
    if request.method == "GET":
        return render_template("login.html")
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
        return render_template("chat.html")
    else:
        return redirect("/login")
@sio.on("connect")
def connect():
    if session.get('name') != None:
        print("Someone was connected")
        users.append(session['name'])
        emit("yourdata", {'name': session['name']})
    else:
        emit("error", {"text": "AUTHERROR"})

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