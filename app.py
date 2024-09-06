from flask import Flask, render_template, request, redirect, url_for
from database import create_connection, create_tables, insert_rental_property, fetch_rental_properties, \
    delete_rental_property
from rental_profit_visualization import generate_heatmap_for_property
from profit_heatmap_generator import ProfitHeatmapGenerator
from rental_property import RentalProperty

app = Flask(__name__)


# Home route: View all properties
@app.route('/')
def index():
    # Fetch all properties from the database
    conn = create_connection()
    create_tables(conn)  # This will ensure tables exist on app startup
    properties_data = fetch_rental_properties(conn)
    conn.close()

    # Print properties_data for debugging
    print(f"Fetched properties data: {properties_data}")

    # Convert database rows to RentalProperty instances
    rental_properties = [RentalProperty.from_db_row(row) for row in properties_data]

    # Define occupancy rates and percentage changes for the heatmap
    occupancy_rates = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
    percentage_changes = [-0.4, -0.3, -0.2, -0.1, 0, 0.1, 0.2, 0.3, 0.4]

    # Debugging Output
    print(f"Properties: {rental_properties}")
    print(f"Occupancy Rates: {occupancy_rates}")
    print(f"Percentage Changes: {percentage_changes}")

    # Generate the cumulative profit heatmap for all properties
    if rental_properties:
        try:
            heatmap_generator = ProfitHeatmapGenerator(rental_properties, occupancy_rates, percentage_changes)
            df = heatmap_generator.calculate_profits()  # Get the data frame with profits
            heatmap_html = heatmap_generator.create_heatmap(df)  # Generate the heatmap HTML
            print("Heatmap generated successfully.")
        except Exception as e:
            print(f"Error generating heatmap: {e}")
            heatmap_html = "<p>Error generating heatmap.</p>"
    else:
        heatmap_html = "<p>No properties available for heatmap generation.</p>"

    # Render the index.html page with properties and heatmap
    return render_template('index.html', properties=properties_data, heatmap=heatmap_html)


# Add new property form
@app.route('/add', methods=['GET', 'POST'])
def add_property():
    conn = create_connection()

    # Fetch available rental complexes
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM rental_complex")
    complexes = cursor.fetchall()

    if request.method == 'POST':
        # Capture form data
        area_sqm = request.form['area_sqm']
        beds = request.form['beds']
        rent_per_month = request.form['rent_per_month']
        furnishing_costs = request.form['furnishing_costs']
        average_stay_duration = request.form['average_stay_duration']
        cleaning_charged_per_booking = request.form['cleaning_charged_per_booking']
        base_room_rate = request.form['base_room_rate']
        rental_complex_id = request.form['rental_complex_id']

        # Insert property into the database
        insert_rental_property(conn, (
            area_sqm, beds, rent_per_month, furnishing_costs,
            average_stay_duration, cleaning_charged_per_booking, base_room_rate, rental_complex_id
        ))
        conn.close()

        return redirect(url_for('index'))

    return render_template('add_property.html', complexes=complexes)


# Edit property
@app.route('/edit/<int:property_id>', methods=['GET', 'POST'])
def edit_property(property_id):
    if request.method == 'POST':
        area_sqm = request.form['area_sqm']
        beds = request.form['beds']
        rent_per_month = request.form['rent_per_month']
        furnishing_costs = request.form['furnishing_costs']
        average_stay_duration = request.form['average_stay_duration']
        cleaning_charged_per_booking = request.form['cleaning_charged_per_booking']
        base_room_rate = request.form['base_room_rate']

        # Update property in the database
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE rental_properties SET area_sqm = ?, beds = ?, rent_per_month = ?, 
                furnishing_costs = ?, average_stay_duration = ?, 
                cleaning_charged_per_booking = ?, base_room_rate = ?
            WHERE id = ?
        ''', (area_sqm, beds, rent_per_month, furnishing_costs, average_stay_duration,
              cleaning_charged_per_booking, base_room_rate, property_id))
        conn.commit()
        conn.close()

        return redirect(url_for('index'))

    # Fetch the property to pre-fill the form
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM rental_properties WHERE id = ?", (property_id,))
    property_data = cursor.fetchone()
    conn.close()

    return render_template('edit_property.html', property=property_data)


# View Property Details
@app.route('/view/<int:property_id>', methods=['GET'])
def view_property(property_id):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM rental_properties WHERE id = ?", (property_id,))
    property_data = cursor.fetchone()
    conn.close()

    if property_data:
        # Create a RentalProperty instance from the fetched data
        rental_property = RentalProperty.from_db_row(property_data)

        # Generate the heatmap for this property
        heatmap_html = generate_heatmap_for_property(rental_property)

        return render_template('view_property.html', property=property_data, heatmap=heatmap_html)
    else:
        return "Property not found", 404


# Delete a property
@app.route('/delete/<int:property_id>', methods=['POST'])
def delete_property(property_id):
    conn = create_connection()
    delete_rental_property(conn, property_id)
    conn.close()
    return redirect(url_for('index'))

# Add a property complex
@app.route('/add_complex', methods=['GET', 'POST'])
def add_complex():
    if request.method == 'POST':
        name = request.form['name']
        address = request.form['address']

        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO rental_complex (name, address) VALUES (?, ?)", (name, address))
        conn.commit()
        conn.close()

        return redirect(url_for('index'))

    return render_template('add_complex.html')

# Check Database Tables
@app.route('/check_table')
def check_table():
    conn = create_connection()
    cursor = conn.cursor()

    # Run the PRAGMA command to get table info
    cursor.execute("PRAGMA table_info(rental_properties);")
    table_info = cursor.fetchall()

    # Print the table structure
    print("Table structure of rental_properties:")
    for row in table_info:
        print(row)

    conn.close()

    return "Check the console for table info."

if __name__ == '__main__':
    app.run(debug=True)
