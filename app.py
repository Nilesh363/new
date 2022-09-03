import os

from flask import (Flask, jsonify, redirect, render_template, request, session,
                   url_for)
from flask_migrate import Migrate
from flask_socketio import SocketIO, send
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
socketio = SocketIO(app)
db = SQLAlchemy(app, session_options={"autoflush": False})
migrate = Migrate(app, db)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["SECRET_KEY"] = os.urandom(128)
app.config["SQLALCHEMY_DATABASE_URI"] = 'postgresql://postgres:123456@localhost:5432/chat_app'
app.config["SQLALCHEMY_POOL_TIMEOUT"] = 86400
app.config["SQLALCHEMY_POOL_SIZE"] = 200
app.config["SQLALCHEMY_POOL_RECYCLE"] = 100
app.config["ENV"] = "development"


class Message(db.Model):


    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(24), nullable=False)
    message = db.Column(db.String(2000), nullable=False)
    date = db.Column(db.String(2000))

@app.route("/chat_room")
def chat_room():
    print("Session: ", session)
    if "logged" in session and "username" in session:
        messages = Message.query.all()
        return render_template("chat_room.html", messages=messages)
    else:
        return redirect(url_for("register"))


@app.route("/", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        session["logged"] = True
        session["username"] = request.form.get("username")
        return redirect(url_for("chat_room"))
    if request.method == "GET":
        if "logged" in session and "username" in session:
            return redirect(url_for("chat_room"))
        else:
            return render_template("register.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("register"))

@app.route("/snooze")
def snooze():
    print("Session: ", session)
    messages = Message.query.all()
    return render_template("snooze.html", messages=messages)


def save_message(sender, message, date):

    add_message = Message(username=sender, message=message, date=date)
    db.session.add(add_message)
    db.session.commit()


@socketio.on('message')
def handleMessage(msg):
    import json

    response = json.loads(msg)
    print(msg)
    save_message(response["sender"], response["msg"], response["date"])
    send(msg, broadcast=True)


if __name__ == '__main__':
    socketio.run(app, debug=True, port=8000)
