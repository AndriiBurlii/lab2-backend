
from flask import Flask, request, jsonify
from datetime import datetime
from threading import Lock

app = Flask(__name__)

# In-memory "database"
db = {
    "users": {},           # id -> {"id": int, "name": str}
    "categories": {},      # id -> {"id": int, "name": str}
    "records": {}          # id -> {"id": int, "user_id": int, "category_id": int, "created_at": iso, "amount": float}
}

counters = {"users": 0, "categories": 0, "records": 0}
lock = Lock()

def _next_id(kind: str) -> int:
    with lock:
        counters[kind] += 1
        return counters[kind]

def _get_or_404(store: str, _id: int, entity: str):
    try:
        _id = int(_id)
    except (TypeError, ValueError):
        return None, (jsonify({"error": f"Invalid {entity}_id"}), 400)
    obj = db[store].get(_id)
    if not obj:
        return None, (jsonify({"error": f"{entity.capitalize()} not found"}), 404)
    return obj, None

@app.get("/")
def root():
    return jsonify({"service": "Expenses REST API (Lab2)", "status": "ok"}), 200

# ---------- USERS ----------
@app.post("/user")
def create_user():
    payload = request.get_json(silent=True) or {}
    name = (payload.get("name") or "").strip()
    if not name:
        return jsonify({"error": "Field 'name' is required"}), 400
    uid = _next_id("users")
    user = {"id": uid, "name": name}
    db["users"][uid] = user
    return jsonify(user), 201

@app.get("/user/<user_id>")
def get_user(user_id):
    user, err = _get_or_404("users", user_id, "user")
    return err if err else (jsonify(user), 200)

@app.delete("/user/<user_id>")
def delete_user(user_id):
    user, err = _get_or_404("users", user_id, "user")
    if err:
        return err
    # Optional cascade delete records of this user
    to_delete = [rid for rid, r in db["records"].items() if r["user_id"] == user["id"]]
    for rid in to_delete:
        db["records"].pop(rid, None)
    db["users"].pop(user["id"], None)
    return jsonify({"deleted": user["id"], "cascade_deleted_records": to_delete}), 200

@app.get("/users")
def list_users():
    return jsonify(list(db["users"].values())), 200

# ---------- CATEGORIES ----------
@app.get("/category")
def list_categories():
    return jsonify(list(db["categories"].values())), 200

@app.post("/category")
def create_category():
    payload = request.get_json(silent=True) or {}
    name = (payload.get("name") or "").strip()
    if not name:
        return jsonify({"error": "Field 'name' is required"}), 400
    cid = _next_id("categories")
    cat = {"id": cid, "name": name}
    db["categories"][cid] = cat
    return jsonify(cat), 201

@app.delete("/category")
def delete_category():
    # Spec shows DELETE /category without path param -> accept ?id= or JSON {"id": ...}
    cat_id = request.args.get("id")
    if cat_id is None:
        payload = request.get_json(silent=True) or {}
        cat_id = payload.get("id")
    cat, err = _get_or_404("categories", cat_id, "category")
    if err:
        return err
    # Optional cascade delete records of this category
    to_delete = [rid for rid, r in db["records"].items() if r["category_id"] == cat["id"]]
    for rid in to_delete:
        db["records"].pop(rid, None)
    db["categories"].pop(cat["id"], None)
    return jsonify({"deleted": cat["id"], "cascade_deleted_records": to_delete}), 200

# ---------- RECORDS ----------
@app.post("/record")
def create_record():
    payload = request.get_json(silent=True) or {}
    try:
        user_id = int(payload.get("user_id"))
        category_id = int(payload.get("category_id"))
        amount = float(payload.get("amount"))
    except (TypeError, ValueError):
        return jsonify({"error": "Fields 'user_id', 'category_id' (ints) and 'amount' (number) are required"}), 400

    # Check foreign keys
    if user_id not in db["users"]:
        return jsonify({"error": "User does not exist"}), 400
    if category_id not in db["categories"]:
        return jsonify({"error": "Category does not exist"}), 400

    rid = _next_id("records")
    rec = {
        "id": rid,
        "user_id": user_id,
        "category_id": category_id,
        "created_at": datetime.utcnow().isoformat() + "Z",
        "amount": amount
    }
    db["records"][rid] = rec
    return jsonify(rec), 201

@app.get("/record/<record_id>")
def get_record(record_id):
    rec, err = _get_or_404("records", record_id, "record")
    return err if err else (jsonify(rec), 200)

@app.delete("/record/<record_id>")
def delete_record(record_id):
    rec, err = _get_or_404("records", record_id, "record")
    if err:
        return err
    db["records"].pop(rec["id"], None)
    return jsonify({"deleted": rec["id"]}), 200

@app.get("/record")
def filter_records():
    # Must accept user_id and/or category_id; without params -> error (per spec)
    user_id = request.args.get("user_id")
    category_id = request.args.get("category_id")

    if user_id is None and category_id is None:
        return jsonify({"error": "At least one of 'user_id' or 'category_id' query params is required"}), 400

    def match(r):
        ok_user = True if user_id is None else r["user_id"] == int(user_id)
        ok_cat = True if category_id is None else r["category_id"] == int(category_id)
        return ok_user and ok_cat

    out = [r for r in db["records"].values() if match(r)]
    return jsonify(out), 200

if __name__ == "__main__":
    # For local dev
    app.run(host="0.0.0.0", port=5000, debug=True)
