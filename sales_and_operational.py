from flask import Flask, jsonify
import random
from datetime import datetime, timedelta

app = Flask(__name__)

def generate_dummy_sales_data():
    return {
        "total_sales": round(random.uniform(10000, 50000), 2),
        "units_sold": random.randint(100, 500),
        "average_order_value": round(random.uniform(50, 200), 2)
    }

def generate_dummy_operational_data():
    return {
        "inventory_level": random.randint(500, 2000),
        "employees_on_shift": random.randint(5, 20),
        "customer_satisfaction": round(random.uniform(3.5, 5.0), 1)
    }

@app.route('/api/sales', methods=['GET'])
def get_sales_data():
    return jsonify({
        "timestamp": datetime.now().isoformat(),
        "data": generate_dummy_sales_data()
    })

@app.route('/api/operations', methods=['GET'])
def get_operational_data():
    return jsonify({
        "timestamp": datetime.now().isoformat(),
        "data": generate_dummy_operational_data()
    })

@app.route('/api/dashboard', methods=['GET'])
def get_dashboard_data():
    return jsonify({
        "timestamp": datetime.now().isoformat(),
        "sales_data": generate_dummy_sales_data(),
        "operational_data": generate_dummy_operational_data()
    })

if __name__ == '__main__':
    app.run(debug=True)