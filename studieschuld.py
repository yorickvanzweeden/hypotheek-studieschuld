import math

def calculate_monthly_rate(annual_rate, compounding_periods=12):
    return math.pow(1 + annual_rate / 100, 1 / compounding_periods) - 1

def calculate_monthly_payment(principal, annual_rate, num_payments):
    monthly_rate = calculate_monthly_rate(annual_rate)
    if annual_rate == 0:
        return principal / num_payments
    else:
        return principal * (monthly_rate / (1 - math.pow(1 + monthly_rate, -num_payments)))

def calculate_draagkracht(income, partner=False):
    draagkrachtvrije_voet = 22356.00  # 2022 value for single person without children
    if partner:
        draagkrachtvrije_voet = round(draagkrachtvrije_voet * 1.43, 2) # 143% of minimumloon
    if income <= draagkrachtvrije_voet:
        return 0
    else:
        return (income - draagkrachtvrije_voet) * 0.04 / 12  # 4% of income above threshold, divided by 12 for monthly

def calculate_duo_monthly_fee(principal, annual_interest_rate, num_months, income, partner=False):
    # Calculate monthly payment without considering income
    monthly_payment_without_income = calculate_monthly_payment(principal, annual_interest_rate, num_months)

    # Calculate draagkracht
    monthly_draagkracht = calculate_draagkracht(income, partner)

    # Determine actual monthly payment
    actual_monthly_payment = min(monthly_payment_without_income, monthly_draagkracht)

    return actual_monthly_payment
