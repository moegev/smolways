import json
from data_processing import load_json_data, process_data, add_duration_to_va
from car_cost_calculator import determine_car_payment, determine_fees_insurance
from emissions_calculator import calculate_emissions_and_costs
from analysis import analyze_activity_sequences, filter_passenger_vehicle_entries
from time_utils import find_min_max_dates

def main():
    # Load and process data
    data = load_json_data("data/location-history.json")
    va, timelinePaths = process_data(data)
    va = add_duration_to_va(va)
    passenger_va = filter_passenger_vehicle_entries(va)

    # Analyze activity sequences
    sequence_analysis = analyze_activity_sequences(va)
    # print("\nActivity Sequence Analysis:")
    # for key, value in sequence_analysis.items():
    #     print(f"  {key.replace('_', ' ').title()}: {value}")

    # Calculate emissions and costs
    emissions_costs = calculate_emissions_and_costs(va, vehicle_mpg=24.4, vehicle_kerb_w=3500)
    print_emissions_costs(emissions_costs)

    # Car payment calculation
    car_params = {
    'model_year': 2017,
    'used_flag': False,
    'car_paid_off': True,
    'purchase_price': 23500,
    'years_owned': 7,
    'interest_rate': 0.00,
    'financed': True,
    'loan_term': 5,  # Adding loan term (in years)
    'purchase_year': 2017,  # Adding purchase year
    'payment_provided': 325,  # Adding payment_provided (set to None if not provided)
    'has_monthly_payment': False  # Adding has_monthly_payment flag
    }

    total_cost, monthly_payment, monthly_amortized_cost = determine_car_payment(**car_params)

    # Print car payment details
    print_car_payment_details(car_params, total_cost, monthly_payment, monthly_amortized_cost)

    # Calculate insurance costs
    insurance_cost = determine_fees_insurance(
        insurance_monthly=182,
        insurance_type='max',
        people_split=2
    )

    # Calculate total costs
    calculate_total_costs(emissions_costs, monthly_amortized_cost, va, car_params['years_owned'], insurance_cost)

def print_emissions_costs(emissions_costs):
    print("\nEmissions and Costs Data:")
    print(f"  Miles Driven: {emissions_costs['miles_driven']:.0f}")
    print(f"  Gallons of Fuel Burned: {emissions_costs['gallons_burned']:.2f}")
    print(f"  CO2 Emissions: {emissions_costs['CO2_tons_released']:.2f} metric tons")
    print(f"  Particulate Matter Released: {emissions_costs['dust_pounds_released']:.2f} pounds")
    
    print("\nComparison to Bay Area Average:")
    print(f"  Average Miles: {emissions_costs['bay_area_miles']:.0f}")
    print(f"  Average Gallons Burned: {emissions_costs['bay_area_gallons_burned']:.2f}")
    print(f"  Average CO2 Emissions: {emissions_costs['bay_area_CO2_tons_released']:.2f} metric tons")
    print(f"  Average Particulate Matter: {emissions_costs['bay_area_dust_pounds_released']:.2f} pounds")

def print_car_payment_details(params, total_cost, monthly_payment, monthly_amortized_cost):
    print(f"\nCar Payment Details:")
    print(f"  Model Year: {params['model_year']}")
    print(f"  Car Type: {'Used' if params['used_flag'] else 'New'}")
    print(f"  Payment Status: {'Paid off' if params['car_paid_off'] else 'Financed'}")
    print(f"  Years Owned: {params['years_owned']}")
    print(f"  Total Cost: ${total_cost:,.2f}")
    print(f"  Monthly Payment: ${monthly_payment:,.2f}")
    print(f"  Monthly Amortized Cost: ${monthly_amortized_cost:,.2f}")

    if params['car_paid_off']:
        print(f"\nNote: This car is paid off. The monthly payment shown is the equivalent cost spread over the ownership period.")

def calculate_total_costs(costs, monthly_amortized_cost, va, years_owned, insurance_cost):
    min_date, max_date = find_min_max_dates(va)
    days_used = (max_date - min_date).days
    miles_driven = costs["miles_driven"]
    
    annual_miles_driven = miles_driven / (days_used / 365.0)
    annual_wear_cost = costs["wear_cost"] / (days_used / 365.0)
    
    wear_cost_mile = annual_wear_cost / annual_miles_driven
    ownership_cost_mile = (monthly_amortized_cost * 12 * years_owned) / (annual_miles_driven * years_owned)
    
    annual_insurance_cost = insurance_cost['annual_insurance_cost']
    registration_fee = insurance_cost['registration_fee']
    fees_cost_mile = (annual_insurance_cost + registration_fee) / annual_miles_driven
    
    per_mile_cost = wear_cost_mile + ownership_cost_mile + fees_cost_mile
    
    print(f"\nTotal Costs:")
    print(f"  Days Used: {days_used}")
    print(f"  Annual Miles Driven: {annual_miles_driven:.2f}")
    print(f"  Annual Wear Cost: ${annual_wear_cost:.2f}")
    print(f"  Per Mile Cost: ${per_mile_cost:.2f}")

if __name__ == '__main__':
    main()