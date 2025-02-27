from flask import Flask, redirect, render_template, request, jsonify
import pandas as pd
import os
from cs50 import SQL
import csv


app = Flask(__name__)

db = SQL("sqlite:///sales.db")

# Biến lưu trữ dữ liệu CSV
sales_data = None

@app.route('/upload/', methods=['POST'])
def upload_csv():
    global sales_data

    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    df = pd.read_csv(file)

    # Chuẩn hóa tên cột
    df.columns = df.columns.str.strip().str.lower()

    # Kiểm tra cột cần thiết
    required_columns = {"date", "region", "product", "quantity", "price"}
    if not required_columns.issubset(df.columns):
        return jsonify({"error": "CSV missing required columns"}), 400

    # Chuyển đổi kiểu dữ liệu
    df["date"] = pd.to_datetime(df["date"])
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce").fillna(0)
    df["price"] = pd.to_numeric(df["price"], errors="coerce").fillna(0)

    # Thêm cột sales = quantity * price
    df["sales"] = df["quantity"] * df["price"]
    sales_data = df
    
    # save in database
    try:
        db.execute("CREATE TABLE IF NOT EXISTS sales (date TEXT, region TEXT, product TEXT, quantity INTEGER, price REAL)")
        # Đọc file CSV và import dữ liệu
        with open('sales_data.csv', 'r', encoding='utf-8') as csv_file:
            csv_reader = csv.reader(csv_file)
            next(csv_reader)
            for row in csv_reader:
                db.execute("INSERT INTO sales VALUES (?, ?, ?, ?, ?)", row[0], row[1], row[2], row[3], row[4])
    except:
        return jsonify({"message": "File uploaded successfully, database upload fail", "rows": len(df)})

    return jsonify({"message": "File uploaded successfully and uploaded database successfully", "rows": len(df)})



@app.route('/sales/', methods=['GET'])
def get_sales():
    global sales_data
    if sales_data is None:
        return jsonify({"error": "No data available"}), 400

    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    region = request.args.get('region')
    product = request.args.get('product')

    if start_date:
        start_date = pd.to_datetime(start_date)
    if end_date:
        end_date = pd.to_datetime(end_date)

    # Lọc dữ liệu
    df_filtered = sales_data.copy()
    if start_date:
        df_filtered = df_filtered[df_filtered["date"] >= start_date]
    if end_date:
        df_filtered = df_filtered[df_filtered["date"] <= end_date]
    if region:
        df_filtered = df_filtered[df_filtered["region"] == region]
    if product:
        df_filtered = df_filtered[df_filtered["product"] == product]

    try:
        total_sales = df_filtered["sales"].sum()
        avg_price = df_filtered["price"].mean()
        avg_quantity = df_filtered["quantity"].mean()
        count_transactions = df_filtered.shape[0]
        
        return jsonify({
            "total_sales" : total_sales,
            "avg_price": avg_price,
            "avg_quantity": avg_quantity,
            "count_transactions": count_transactions
        })
    except:
        avg_price = df_filtered["price"].mean()
        avg_quantity = df_filtered["quantity"].mean()
        count_transactions = df_filtered.shape[0]
        
        return jsonify({
            "avg_price": avg_price,
            "avg_quantity": avg_quantity,
            "count_transactions": count_transactions
        })



if __name__ == '__main__':
    app.run(debug=True)
