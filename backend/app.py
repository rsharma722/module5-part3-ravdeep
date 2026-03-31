from flask import Flask, request, session, jsonify
from pymongo import MongoClient
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "pixelriversecret")

client = MongoClient(os.getenv("MONGO_URI", "mongodb://mongo:27017/"))
db = client["bank_app"]
users = db["users"]
transactions = db["transactions"]

@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json()
    if users.find_one({"username": data["username"]}):
        return jsonify({"success": False, "message": "User already exists"})
    users.insert_one({"username": data["username"], "password": data["password"], "balance": 0.0})
    return jsonify({"success": True, "message": "Registration successful"})

@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    user = users.find_one({"username": data["username"], "password": data["password"]})
    if not user:
        return jsonify({"success": False, "message": "Invalid credentials"})
    session["username"] = data["username"]
    return jsonify({"success": True})

@app.route("/api/dashboard")
def dashboard():
    if "username" not in session:
        return jsonify({"success": False})
    user = users.find_one({"username": session["username"]})
    return jsonify({"success": True, "balance": float(user["balance"])})

@app.route("/api/deposit", methods=["POST"])
def deposit():
    if "username" not in session:
        return jsonify({"success": False}), 401
    amount = float(request.get_json()["amount"])
    users.update_one({"username": session["username"]}, {"$inc": {"balance": amount}})
    transactions.insert_one({
        "username": session["username"],
        "type": "deposit",
        "amount": amount,
        "created_at": datetime.utcnow()
    })
    return jsonify({"success": True})

@app.route("/api/withdraw", methods=["POST"])
def withdraw():
    if "username" not in session:
        return jsonify({"success": False}), 401
    amount = float(request.get_json()["amount"])
    user = users.find_one({"username": session["username"]})
    if amount > float(user["balance"]):
        return jsonify({"success": False, "message": "Insufficient funds"})
    users.update_one({"username": session["username"]}, {"$inc": {"balance": -amount}})
    transactions.insert_one({
        "username": session["username"],
        "type": "withdraw",
        "amount": amount,
        "created_at": datetime.utcnow()
    })
    return jsonify({"success": True})

@app.route("/api/logout")
def logout():
    session.clear()
    return jsonify({"success": True})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)