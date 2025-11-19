# create a simple flask app that returns a hello world message
from flask import Flask, render_template
import pymysql

app = Flask(__name__)


@app.route("/")
def hello_world():
    return "Hello, World!"


@app.route("/customers")
def customers():
    # connect to the database
    conn = pymysql.connect(
        host="localhost", user="root", password="12345678", database="chargerstore"
    )
    # Use dictionary cursor to access columns by name
    cur = conn.cursor(pymysql.cursors.DictCursor)
    cur.execute("SELECT * FROM customers")
    result = cur.fetchall()
    cur.close()
    conn.close()

    # Convert Decimal values to float for template rendering
    for customer in result:
        if customer.get("creditLimit") is not None:
            customer["creditLimit"] = float(customer["creditLimit"])

    return render_template("customers.html", customers=result)


if __name__ == "__main__":
    app.run(debug=True)
