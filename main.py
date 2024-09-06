from database import create_connection, create_tables, insert_rental_property, view_all_properties

# Connect to SQLite database
conn = create_connection()

# Create tables if they don't exist
create_tables(conn)

# Example properties
rental_properties_data = [
    (110.83, 3, 1500, 18000, 2, 70, 240),
    (59.49, 1, 800, 12000, 2, 50, 115),
    (48.85, 1, 800, 12000, 2, 50, 100),
    (61.71, 1, 800, 12000, 2, 50, 115)
]

# Insert properties into the database (only if they don't already exist)
for property_data in rental_properties_data:
    insert_rental_property(conn, property_data)

# View all property entries in the database
view_all_properties(conn)

# Close the database connection
conn.close()
