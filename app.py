from flask import Flask, render_template, request, redirect, url_for
import oracledb

app = Flask(__name__)

# List of allowed tables
ALLOWED_TABLES = [
    'CAR_SALES_TRANSACTIONS', 'CITY_MASTER', 'POSTAL_CODE_MASTER', 'REGION_MASTER', 'REGION_STATE_MAPPING',
    'SALES_STATUS', 'STATE_MASTER'
]

def get_db_connection():
    # Update these values with your actual database credentials
    dsn = oracledb.makedsn("localhost", "1521", service_name="xepdb1")
    conn = oracledb.connect(user=u"dbuser1", password="dbuser1", dsn=dsn)
    return conn

@app.route('/')
def index():
    return render_template('index1.html', tables=ALLOWED_TABLES)

@app.route('/show_table', methods=['GET','POST'])
def show_table():
    if request.method == 'POST':
        selected_table = request.form.get('table_name')
    else:  # GET request
        selected_table = request.args.get('table_name')
    print(f"Selected table: {selected_table}")# Debugging line
    if selected_table not in ALLOWED_TABLES:
        print("Invalid table selection")  # Debugging line
        return "Invalid table selection", 400
    
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch the data from the selected table
    cursor.execute(f"SELECT * FROM {selected_table}")
    columns = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('table1.html', columns=columns, rows=rows, table_name=selected_table)


@app.route('/firstOwner', methods=['GET','POST'])
def firstOwner():
    
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch the data from the selected table
    cursor.execute("""
        SELECT *
        FROM car_sales_transactions
        WHERE Owner = 'First Owner'
        AND Year BETWEEN 2016 AND 2020
        AND km_Driven < 80000
    """)
    columns = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('table1.html', columns=columns, rows=rows, table_name='First Owner Driven Less Than 80000')

@app.route('/fuelDeasel', methods=['GET','POST'])
def fuelDeasel():
    
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch the data from the selected table
    cursor.execute("""
       SELECT *
        FROM car_sales_transactions
        WHERE TO_NUMBER(REGEXP_SUBSTR(Mileage,'^[0-9]+(\.[0-9]+)?')) BETWEEN 24 AND 26
        AND Year BETWEEN 2018 AND 2020
        AND Seats IN (4, 5)
        AND Fuel = 'Diesel'
    """)
    columns = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('table1.html', columns=columns, rows=rows, table_name=' 4 Or 5 Seater Diesel Car')

@app.route('/salesStatus', methods=['GET','POST'])
def salesStatus():
    
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch the data from the selected table
    cursor.execute("""
       SELECT ct.*,ss.Sold
        FROM car_sales_transactions ct
        JOIN sales_status ss ON ct.Sales_ID = ss.Sales_ID
        WHERE ss.Sold = 'N'
        AND ct.Seller_Type IN ('Individual', 'Dealer')
        AND ct.km_Driven < 60000
        AND ct.Year BETWEEN 2014 AND 2020
    """)
    columns = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('table1.html', columns=columns, rows=rows, table_name='60000 Driven Car Sold In 2014 And 2020')

@app.route('/accordingCity', methods=['GET','POST'])
def accordingCity():
    
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch the data from the selected table
    cursor.execute("""
       SELECT ct.*,cm.city_name
        FROM car_sales_transactions ct
        JOIN city_master cm ON ct.City_Code = cm.City_Code
        WHERE ct.Transmission IN ('Manual', 'Automatic')
        AND TO_NUMBER(REGEXP_SUBSTR(ct.Mileage,'^[0-9]+(\.[0-9]+)?')) BETWEEN 20 AND 25
        AND cm.City_Name IN ('Mumbai', 'Hydrabad', 'Surat', 'Kanpur')
    """)
    columns = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('table1.html', columns=columns, rows=rows, table_name='According To Given City')

@app.route('/hondaPetrolSales', methods=['GET','POST'])
def hondaPetrolSales():
    
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch the data from the selected table
    cursor.execute("""
       SELECT ct.*,ss.Sold
        FROM car_sales_transactions ct
        JOIN sales_status ss ON ct.Sales_ID = ss.Sales_ID
        WHERE ct.Name LIKE 'Honda%'
        AND ct.Owner IN ('First Owner', 'Second Owner')
        AND ct.Fuel = 'Petrol'
        AND TO_NUMBER(REGEXP_SUBSTR(ct.Mileage,'^[0-9]+(\.[0-9]+)?')) = 17.0
        AND ss.Sold = 'Y'
        AND ct.Seats >= 4
    """)
    columns = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('table1.html', columns=columns, rows=rows, table_name='Honda Petrol Sold Car First Owner & Second Owner')
@app.route('/search_car', methods=['GET', 'POST'])
def search_car():
    if request.method == 'POST':
        car_id = request.form.get('car_id')
        return redirect(url_for('show_car_details', car_id=car_id))
    return render_template('search_car.html')

@app.route('/car_details/<car_id>', methods=['GET'])
def show_car_details(car_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""SELECT 
                cst.*, 
                cm.city_name, 
                sm.state_name,
                ss.sold
            FROM 
                car_sales_transactions cst
            JOIN 
                city_master cm ON cst.city_code = cm.city_code
            JOIN 
                state_master sm ON cst.state_code = sm.state_code
            JOIN 
                sales_status ss ON cst.sales_id = ss.sales_id
            WHERE 
                cst.sales_id = :car_id"""
                   , car_id=car_id)
    car = cursor.fetchone()
    print(f"car details :{car}")

    # Fetch column names before closing the cursor
    columns = [desc[0] for desc in cursor.description]

    cursor.close()
    conn.close()

    if not car:
        return "<h3 style='margin-left:40%;'>Car Not Found With This Id</h3>", 404

    car_details = dict(zip(columns, car))
    print(f"car details2  :{car_details}")
    return render_template('car_details.html', car=car_details)



if __name__ == '__main__':
    app.run(debug=True)
