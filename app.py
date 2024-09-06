from flask import Flask, render_template, request, redirect, url_for
from database import create_connection, create_tables, insert_rental_property, fetch_rental_properties, \
    delete_rental_property
from rental_profit_visualization import generate_heatmap_for_property
from rental_property import RentalProperty

app = Flask(__name__)


# Home route: View all properties
@app.route('/')
def index():
    conn = create_connection()
    properties = fetch_rental_properties(conn)
    conn.close()
    return render_template('index.html', properties=properties)


# Add new property form
@app.route('/add', methods=['GET', 'POST'])
def add_property():
    if request.method == 'POST':
        # Capture form data
        area_sqm = request.form['area_sqm']
        beds = request.form['beds']
        rent_per_month = request.form['rent_per_month']
        furnishing_costs = request.form['furnishing_costs']
        average_stay_duration = request.form['average_stay_duration']
        cleaning_charged_per_booking = request.form['cleaning_charged_per_booking']
        base_room_rate = request.form['base_room_rate']

        # Insert property into the database
        conn = create_connection()
        insert_rental_property(conn, (
            area_sqm, beds, rent_per_month, furnishing_costs,
            average_stay_duration, cleaning_charged_per_booking, base_room_rate
        ))
        conn.close()

        return redirect(url_for('index'))

    return render_template('add_property.html')



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


if __name__ == '__main__':
    app.run(debug=True)
