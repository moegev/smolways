import csv
import os
from datetime import datetime

def load_inflation_data():
    inflation_data = {}
    csv_path = os.path.join('data', 'inflation_rate_year.csv')
    
    try:
        with open(csv_path, 'r') as file:
            csv_reader = csv.reader(file)
            next(csv_reader)  # Skip header
            for row in csv_reader:
                inflation_data[int(row[0])] = float(row[1])
        return inflation_data
    except FileNotFoundError:
        print(f"Error: The file 'inflation_rate_year.csv' was not found in the 'data' directory.")
    except ValueError:
        print("Error: Invalid data in the CSV file.")
    return None

def calculate_car_cost(year, used_flag, inflation_data):
    current_year = datetime.now().year
    
    base_cost = 25571 if used_flag else 48644  # Used or new car average for 2024

    if year < 1929 or year > current_year:
        print(f"Error: Year {year} is out of range.")
        return None

    cost = base_cost
    for y in range(current_year - 1, year - 1, -1):
        if y in inflation_data:
            cost /= (1 + inflation_data[y])

    return round(cost, 2)

def determine_car_payment(
    model_year=None,
    used_flag=True,
    payment_provided=None,
    has_monthly_payment=None,
    car_paid_off=False,
    purchase_price=None,
    years_owned=5,
    interest_rate=0.05,
    financed=True,
    loan_term=5,
    purchase_year=None
):
    inflation_data = load_inflation_data()
    if inflation_data is None:
        return None, None, None

    current_year = datetime.now().year
    avg_car_pay_used, avg_car_pay_new = 523, 735  # US AVG 2024 per month for used/new cars

    # Determine if the car is currently paid off based on purchase year and loan term
    if purchase_year and loan_term:
        car_paid_off = (current_year - purchase_year) >= loan_term

    if car_paid_off:
        if purchase_price is not None:
            total_cost = purchase_price
            monthly_payment = purchase_price / (loan_term * 12)  # This is the actual monthly payment during the loan term
            monthly_amortized_cost = purchase_price / (years_owned * 12)  # This is the cost spread over the entire ownership period
        elif payment_provided is not None:
            monthly_payment = payment_provided
            total_cost = monthly_payment * loan_term * 12
            monthly_amortized_cost = total_cost / (years_owned * 12)
        else:
            # If neither purchase price nor payment is provided, estimate based on model year
            total_cost = calculate_car_cost(model_year, used_flag, inflation_data)
            monthly_payment = total_cost / (loan_term * 12)
            monthly_amortized_cost = total_cost / (years_owned * 12)
    elif payment_provided is not None:
        monthly_payment = payment_provided
        total_cost = monthly_payment * loan_term * 12
        monthly_amortized_cost = total_cost / (years_owned * 12)
    elif has_monthly_payment:
        monthly_payment = avg_car_pay_used if used_flag else avg_car_pay_new
        total_cost = monthly_payment * loan_term * 12
        monthly_amortized_cost = total_cost / (years_owned * 12)
    elif purchase_price is not None and model_year is not None:
        if financed:
            monthly_payment = calculate_monthly_payment(purchase_price, interest_rate, loan_term)
            total_cost = monthly_payment * loan_term * 12
        else:
            total_cost = purchase_price
            monthly_payment = total_cost / (loan_term * 12)
        monthly_amortized_cost = total_cost / (years_owned * 12)
    else:
        monthly_payment = 0.8 * (avg_car_pay_used if used_flag else avg_car_pay_new)
        total_cost = monthly_payment * loan_term * 12
        monthly_amortized_cost = total_cost / (years_owned * 12)

    # Handle discrepancies between provided values
    if purchase_price and payment_provided and interest_rate:
        calculated_payment = calculate_monthly_payment(purchase_price, interest_rate, loan_term)
        if abs(calculated_payment - payment_provided) > 1:  # Allow for small rounding differences
            print("Warning: Provided monthly payment doesn't match calculated payment.")
            monthly_payment = max(calculated_payment, payment_provided)
            total_cost = monthly_payment * loan_term * 12
            monthly_amortized_cost = total_cost / (years_owned * 12)

    return round(total_cost, 2), round(monthly_payment, 2), round(monthly_amortized_cost, 2)

def calculate_paid_off_costs(purchase_price, payment_provided, model_year, used_flag, years_owned, inflation_data, financed, interest_rate, loan_term, purchase_year):
    current_year = datetime.now().year
    if purchase_price is not None:
        if financed and purchase_year and (current_year - purchase_year) < loan_term:
            total_cost, monthly_payment = calculate_financed_costs(purchase_price, financed, interest_rate, loan_term, years_owned)
        else:
            total_cost = purchase_price
            monthly_payment = total_cost / (years_owned * 12)
    elif payment_provided is not None:
        monthly_payment = payment_provided
        total_cost = monthly_payment * loan_term * 12
    else:
        model_year = model_year or (purchase_year if purchase_year else current_year - 7)
        total_cost = calculate_car_cost(model_year, used_flag, inflation_data)
        monthly_payment = total_cost / (years_owned * 12)

    if total_cost is None:
        return None, None

    return total_cost, monthly_payment

def calculate_financed_costs(purchase_price, financed, interest_rate, loan_term, years_owned):
    if financed:
        monthly_payment = calculate_monthly_payment(purchase_price, interest_rate, loan_term)
        total_cost = monthly_payment * loan_term * 12
    else:
        total_cost = purchase_price
        monthly_payment = total_cost / (years_owned * 12)
    return total_cost, monthly_payment

def calculate_monthly_payment(principal, annual_interest_rate, loan_term_years):
    monthly_rate = annual_interest_rate / 12
    num_payments = loan_term_years * 12
    return (principal * monthly_rate * (1 + monthly_rate) ** num_payments) / ((1 + monthly_rate) ** num_payments - 1)

def determine_fees_insurance(insurance_monthly=None, insurance_type='min', people_split=1, registration_fee=None):
    cost_of_registration = 289  # dollars per year
    min_car_ins_cal, avg_ful_ins_cal = 50, 190  # dollars per month for minimum/full coverage

    if insurance_monthly is None:
        insurance_monthly = avg_ful_ins_cal if insurance_type == 'max' else min_car_ins_cal

    insurance_monthly_split = insurance_monthly / people_split
    annual_insurance_cost = insurance_monthly_split * 12

    registration_fee = registration_fee or cost_of_registration

    return {
        'annual_insurance_cost': round(annual_insurance_cost, 2),
        'registration_fee': round(registration_fee, 2)
    }