from flask import Flask, jsonify, request
import json, datetime
import os
from flask_cors import CORS
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)
CORS(app)
client = MongoClient("mongodb+srv://admin:admin@muebles-troncoso.kqxfz.mongodb.net/?retryWrites=true&w=majority&appName=muebles-troncoso")
db = client['bazar']

# Obtener la ruta absoluta de products.json en relación al archivo app.py
base_dir = os.path.dirname(os.path.abspath(__file__))
json_path = os.path.join(base_dir, 'products.json')

# Cargar productos desde el archivo JSON usando la ruta absoluta
with open(json_path, 'r') as file:
    data = json.load(file)
    products = data["products"]

@app.route("/api/items")
def get_items():
    query = request.args.get("q", "").lower()
    filtered_items = [
        {**item, "id": str(item["id"])} for item in products
        if query in item["title"].lower()
    ]
    return jsonify(filtered_items)

@app.route("/api/items/<id>")
def get_item(id):
    item = next((item for item in products if str(item["id"]) == id), None)
    if item:
        return jsonify(item)
    return jsonify({"error": "Item not found"}), 404

@app.route('/api/addSale', methods=['POST'])
def add_sale():
    data = request.json
    product_id = data.get('productId')
    product_title = data.get('productTitle')
    product_price = data.get('productPrice')
    product_thumbnail = data.get('productThumbnail')
    
    if product_id and product_title and product_price and product_thumbnail:
        db.sales.insert_one({
            "productId": product_id,
            "title": product_title,
            "price": product_price,
            "thumbnail": product_thumbnail,
            "purchaseDate": datetime.datetime.utcnow()
        })
        return jsonify({"success": True})
    return jsonify({"success": False}), 400

@app.route('/api/sales', methods=['GET'])
def get_sales():
    sales = list(db.sales.find({}))
    for sale in sales:
        sale["_id"] = str(sale["_id"])
    return jsonify(sales)

if __name__ == "__main__":
    app.run(debug=True)