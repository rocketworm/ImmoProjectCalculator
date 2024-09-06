import math


class RentalProperty:
    # Shared class variables
    laundry_cost_per_kg = 7.5
    laundry_per_person = 1600
    cleaning_hourly_rate = 15.00
    cleaning_effort_per_sqm = 3
    maintenance_reserve_per_sqm = 0.50
    electricity_price_per_kwh = 0.24
    fees_percentage = 0.03
    overhead_costs_percentage = 20
    depreciation_years = 10

    def __init__(self, area_sqm, beds, rent_per_month, furnishing_costs, average_stay_duration,
                 cleaning_charged_per_booking, base_room_rate, rental_complex_id):
        self.area_sqm = area_sqm
        self.beds = beds
        self.rent_per_month = rent_per_month
        self.furnishing_costs = furnishing_costs
        self.average_stay_duration = average_stay_duration
        self.cleaning_charged_per_booking = cleaning_charged_per_booking
        self.base_room_rate = base_room_rate
        self.rental_complex_id = rental_complex_id

    @classmethod
    def from_db_row(cls, db_row):
        if len(db_row) == 8:
            # Handle case where rental_complex_id is missing (old schema)
            return cls(db_row[1], db_row[2], db_row[3], db_row[4], db_row[5], db_row[6], db_row[7], None)
        return cls(db_row[1], db_row[2], db_row[3], db_row[4], db_row[5], db_row[6], db_row[7], db_row[8])

    def calculate_yearly_profit(self, calculated_occupancy, current_room_rate):
        nights_rented_per_month = round(30 * calculated_occupancy, 1)
        people_per_booking = 2 * self.beds
        bookings_per_month = max(1, math.ceil(nights_rented_per_month / self.average_stay_duration))
        monthly_laundry_cost = ((people_per_booking * RentalProperty.laundry_per_person *
                                 RentalProperty.laundry_cost_per_kg) * bookings_per_month / 1000)
        cleaning_cost_per_booking = round(self.area_sqm * RentalProperty.cleaning_effort_per_sqm / 60 *
                                          RentalProperty.cleaning_hourly_rate, 2)
        monthly_cleaning_cost = cleaning_cost_per_booking * bookings_per_month
        monthly_maintenance_cost = self.area_sqm * RentalProperty.maintenance_reserve_per_sqm
        annual_electricity_cost = round(((self.area_sqm * 9) + (people_per_booking * 200)) *
                                        RentalProperty.electricity_price_per_kwh, 2)
        monthly_fees = round((((self.average_stay_duration * current_room_rate) + cleaning_cost_per_booking) *
                              RentalProperty.fees_percentage) * bookings_per_month, 2)
        monthly_revenue = (nights_rented_per_month * current_room_rate) + (self.cleaning_charged_per_booking *
                                                                           bookings_per_month)

        annual_rent_cost = 12 * self.rent_per_month
        annual_cleaning_cost = 12 * monthly_cleaning_cost
        annual_laundry_cost = 12 * monthly_laundry_cost
        annual_maintenance_cost = 12 * monthly_maintenance_cost
        annual_fees = round(12 * monthly_fees, 2)
        annual_depreciation = self.furnishing_costs / RentalProperty.depreciation_years
        annual_costs = (annual_rent_cost + annual_cleaning_cost + annual_laundry_cost + annual_maintenance_cost +
                        annual_depreciation + annual_fees + annual_electricity_cost)
        annual_revenue = 12 * monthly_revenue
        annual_profit = round(annual_revenue - annual_costs, 2)

        return annual_profit
