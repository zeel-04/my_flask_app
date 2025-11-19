# create a simple flask app that returns a hello world message
from flask import Flask, render_template, request, redirect, url_for, flash
import pymysql

app = Flask(__name__)
app.secret_key = "your-secret-key-here"  # Required for flash messages


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

    # Get search query parameter
    search_query = request.args.get("search", "").strip()

    if search_query:
        # Filter by customer name (case-insensitive partial match)
        cur.execute(
            "SELECT * FROM customers WHERE LOWER(customerName) LIKE LOWER(%s)",
            (f"%{search_query}%",),
        )
    else:
        cur.execute("SELECT * FROM customers")

    result = cur.fetchall()
    cur.close()
    conn.close()

    # Convert Decimal values to float for template rendering
    for customer in result:
        if customer.get("creditLimit") is not None:
            customer["creditLimit"] = float(customer["creditLimit"])

    return render_template(
        "customers.html", customers=result, search_query=search_query
    )


@app.route("/customers/add", methods=["GET", "POST"])
def add_customer():
    conn = pymysql.connect(
        host="localhost", user="root", password="12345678", database="chargerstore"
    )
    cur = conn.cursor(pymysql.cursors.DictCursor)

    if request.method == "POST":
        try:
            # Get form data
            customer_name = request.form.get("customerName")
            contact_last_name = request.form.get("contactLastName")
            contact_first_name = request.form.get("contactFirstName")
            phone = request.form.get("phone")
            city = request.form.get("city")
            state = request.form.get("state") or None
            country = request.form.get("country")
            sales_rep = request.form.get("salesRepEmployeeNumber")
            sales_rep = int(sales_rep) if sales_rep else None
            credit_limit = request.form.get("creditLimit")
            credit_limit = float(credit_limit) if credit_limit else None

            # Get the next customer number
            cur.execute("SELECT MAX(customerNumber) as max_num FROM customers")
            result = cur.fetchone()
            next_customer_number = (result["max_num"] or 0) + 1

            # Insert new customer
            insert_query = """
                INSERT INTO customers 
                (customerNumber, customerName, contactLastName, contactFirstName,
                 phone, city, state, country, salesRepEmployeeNumber, creditLimit)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cur.execute(
                insert_query,
                (
                    next_customer_number,
                    customer_name,
                    contact_last_name,
                    contact_first_name,
                    phone,
                    city,
                    state,
                    country,
                    sales_rep,
                    credit_limit,
                ),
            )
            conn.commit()
            flash("Customer added successfully!", "success")
            cur.close()
            conn.close()
            return redirect(url_for("customers"))
        except Exception as e:
            conn.rollback()
            flash(f"Error adding customer: {str(e)}", "error")
            cur.close()
            conn.close()
            return redirect(url_for("add_customer"))
    else:
        # GET request - show add form
        cur.close()
        conn.close()
        return render_template("add_customer.html")


@app.route("/customers/<int:customer_number>/edit", methods=["GET", "POST"])
def edit_customer(customer_number):
    conn = pymysql.connect(
        host="localhost", user="root", password="12345678", database="chargerstore"
    )
    cur = conn.cursor(pymysql.cursors.DictCursor)

    if request.method == "POST":
        try:
            # Get form data
            customer_name = request.form.get("customerName")
            contact_last_name = request.form.get("contactLastName")
            contact_first_name = request.form.get("contactFirstName")
            phone = request.form.get("phone")
            city = request.form.get("city")
            state = request.form.get("state") or None
            country = request.form.get("country")
            sales_rep = request.form.get("salesRepEmployeeNumber")
            sales_rep = int(sales_rep) if sales_rep else None
            credit_limit = request.form.get("creditLimit")
            credit_limit = float(credit_limit) if credit_limit else None

            # Update customer
            update_query = """
                UPDATE customers 
                SET customerName = %s, contactLastName = %s, contactFirstName = %s,
                    phone = %s, city = %s, state = %s, country = %s,
                    salesRepEmployeeNumber = %s, creditLimit = %s
                WHERE customerNumber = %s
            """
            cur.execute(
                update_query,
                (
                    customer_name,
                    contact_last_name,
                    contact_first_name,
                    phone,
                    city,
                    state,
                    country,
                    sales_rep,
                    credit_limit,
                    customer_number,
                ),
            )
            conn.commit()
            flash("Customer updated successfully!", "success")
            cur.close()
            conn.close()
            return redirect(url_for("customers"))
        except Exception as e:
            conn.rollback()
            flash(f"Error updating customer: {str(e)}", "error")
            cur.close()
            conn.close()
            return redirect(url_for("edit_customer", customer_number=customer_number))
    else:
        # GET request - show edit form
        cur.execute(
            "SELECT * FROM customers WHERE customerNumber = %s", (customer_number,)
        )
        customer = cur.fetchone()
        cur.close()
        conn.close()

        if not customer:
            flash("Customer not found!", "error")
            return redirect(url_for("customers"))

        # Convert Decimal to float for template
        if customer.get("creditLimit") is not None:
            customer["creditLimit"] = float(customer["creditLimit"])

        return render_template("edit_customer.html", customer=customer)


@app.route("/customers/<int:customer_number>/delete", methods=["POST"])
def delete_customer(customer_number):
    conn = pymysql.connect(
        host="localhost", user="root", password="12345678", database="chargerstore"
    )
    cur = conn.cursor(pymysql.cursors.DictCursor)

    try:
        # Check if customer exists
        cur.execute(
            "SELECT customerName FROM customers WHERE customerNumber = %s",
            (customer_number,),
        )
        customer = cur.fetchone()

        if not customer:
            flash("Customer not found!", "error")
            cur.close()
            conn.close()
            return redirect(url_for("customers"))

        # Delete customer
        cur.execute(
            "DELETE FROM customers WHERE customerNumber = %s", (customer_number,)
        )
        conn.commit()
        flash(f"Customer '{customer['customerName']}' deleted successfully!", "success")
        cur.close()
        conn.close()
        return redirect(url_for("customers"))
    except Exception as e:
        conn.rollback()
        flash(f"Error deleting customer: {str(e)}", "error")
        cur.close()
        conn.close()
        return redirect(url_for("customers"))


if __name__ == "__main__":
    app.run(debug=True)
