import sqlite3


# Connect to SQLite database (it will create the file if it doesn't exist)
def create_connection(db_file='immoprojectcalculator.db'):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print("Connected to SQLite database")
    except sqlite3.Error as e:
        print(e)
    return conn


# Create tables for rental properties
def create_tables(conn):
    create_rental_properties_table = '''
    CREATE TABLE IF NOT EXISTS rental_properties (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        area_sqm REAL, 
        beds INTEGER, 
        rent_per_month REAL, 
        furnishing_costs REAL, 
        average_stay_duration REAL,
        cleaning_charged_per_booking REAL, 
        base_room_rate REAL,
        UNIQUE(area_sqm, beds, rent_per_month)  -- Ensure unique entries
    );
    '''
    try:
        cursor = conn.cursor()
        cursor.execute(create_rental_properties_table)
        conn.commit()
        print("Tables created successfully")
    except sqlite3.Error as e:
        print(e)


# Insert data into rental_properties table if it doesn't already exist
def insert_rental_property(conn, rental_property):
    sql = '''
    INSERT OR IGNORE INTO rental_properties (area_sqm, beds, rent_per_month, furnishing_costs, 
                                             average_stay_duration, cleaning_charged_per_booking, base_room_rate)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    '''
    cursor = conn.cursor()
    cursor.execute(sql, rental_property)
    conn.commit()
    return cursor.lastrowid


# Fetch all rental properties
def fetch_rental_properties(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM rental_properties")
    rows = cursor.fetchall()
    return rows


# View all properties in a formatted manner
def view_all_properties(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM rental_properties")
    rows = cursor.fetchall()

    if len(rows) == 0:
        print("No rental properties found.")
    else:
        print(
            f"\n{'ID':<5}{'Area (sqm)':<12}{'Beds':<6}{'Rent (€/month)':<16}{'Furnishing (€)':<16}{'Avg Stay (days)':<14}{'Cleaning (€/booking)':<22}{'Base Room Rate (€/night)':<22}")
        print("-" * 100)
        for row in rows:
            print(
                f"{row[0]:<5}{row[1]:<12.2f}{row[2]:<6}{row[3]:<16.2f}{row[4]:<16.2f}{row[5]:<14.2f}{row[6]:<22.2f}{row[7]:<22.2f}")


# Delete a property by ID
def delete_rental_property(conn, property_id):
    sql = 'DELETE FROM rental_properties WHERE id = ?'
    cursor = conn.cursor()
    cursor.execute(sql, (property_id,))
    conn.commit()
