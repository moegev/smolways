from time_utils import find_min_max_dates

def calculate_emissions_and_costs(va, vehicle_mpg=24.4, vehicle_kerb_w=3500, miles_driven_correction=1.0):
    passenger_va = [entry for entry in va if entry.get('topCandidateType') == 'IN_PASSENGER_VEHICLE']

    kms_driven = sum([item['distanceMeters'] for item in passenger_va]) / 1000
    miles_driven = kms_driven / 1.6 * miles_driven_correction

    min_date, max_date = find_min_max_dates(va)
    fraction_of_year_equivalent = (max_date - min_date).days / 365

    # Emission constants
    kCO2 = 11.14  # Well to pump CO2 in kg per gallon
    break_particulates = 25.85  # Sum of PM2.5 and PM10 light duty vehicle per mile MOVES
    tire_particulates = 11.5  # Based on MOVES 2014 light duty truck
    total_particulates = tire_particulates + break_particulates

    # Calculate emissions for actual miles driven
    gallons_burned = miles_driven / vehicle_mpg
    CO2kgs_released = gallons_burned * kCO2
    mgs_released = miles_driven * total_particulates

    # Calculate emissions for Bay Area average miles driven in same period of time
    bay_area_miles = 10000 * fraction_of_year_equivalent
    bay_area_gallons_burned = bay_area_miles / vehicle_mpg
    bay_area_CO2kgs_released = bay_area_gallons_burned * kCO2
    bay_area_mgs_released = bay_area_miles * total_particulates

    # Calculate wear costs
    wear_cost = determine_wear_costs(miles_driven, vehicle_mpg, "CA")

    results = {
        "miles_driven": round(miles_driven, 0),
        "gallons_burned": round(gallons_burned, 2),
        "CO2_tons_released": round(CO2kgs_released * 0.001, 2),
        "dust_pounds_released": round(mgs_released * 0.000001 / 2.2, 2),
        "wear_cost": round(wear_cost, 2),
        "bay_area_miles": round(bay_area_miles, 0),
        "bay_area_gallons_burned": round(bay_area_gallons_burned, 2),
        "bay_area_CO2_tons_released": round(bay_area_CO2kgs_released * 0.001, 2),
        "bay_area_dust_pounds_released": round(bay_area_mgs_released * 0.000001 / 2.2, 2),
    }

    return results

def determine_wear_costs(miles_driven, vehicle_mpg, state):
    # Constants
    cost_of_maint_year = 400  # dollars per year for 10,000 miles
    cost_of_tire = 400  # dollars per change
    cost_of_brake_change = 1000  # dollars per change
    brake_rate = 60000  # longevity in miles
    tire_rate = 60000  # longevity in miles
    cost_to_park = 80  # dollars a month for 10,000 miles per year

    maintenance_cost = (miles_driven / 10000) * cost_of_maint_year
    tire_wear_cost = (miles_driven / tire_rate) * cost_of_tire
    brake_wear_cost = (miles_driven / brake_rate) * cost_of_brake_change
    fuel_cost = (miles_driven / vehicle_mpg) * state_based_calc(state)
    parking_cost = (miles_driven / 10000) * (cost_to_park * 12)

    total_cost = maintenance_cost + tire_wear_cost + brake_wear_cost + fuel_cost + parking_cost

    return total_cost

def state_based_calc(state):
    # This function should be implemented to return the correct fuel cost based on the state
    # For now, we'll use a placeholder value
    return 4.50  # dollars per gallon