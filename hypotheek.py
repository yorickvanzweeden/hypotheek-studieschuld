import pandas as pd

df_flp = pd.read_csv("financieringslasttabellen.csv", index_col="Inkomen")
# https://www.nibud.nl/onderzoeksrapporten/rapport-advies-hypotheeknormen-2024/

def calculate_financieringslastpercentage(toetsingsinkomen: float, interest: float):
    # Get index of the row with the highest toetsingsinkomen that is lower than the input toetsingsinkomen
    index = df_flp.index[df_flp.index <= toetsingsinkomen].max()

    # Get interest rate column
    columns = [(col, float(col.replace(",", "."))) for col in df_flp.columns]
    column = [col for col, col_interest in columns if col_interest <= interest][-1]

    return df_flp.loc[index, str(column)]

def calculate_annuity(interest: float):
    ipm = interest / 100 / 12
    annuity = ipm * (ipm + 1) ** 360 / ((ipm + 1) ** 360 - 1)
    return annuity

def calculate_house_energy_label_addition(house_energy_label: str):
    if house_energy_label in ["E", "F", "G"]:
        return 0
    elif house_energy_label in ["C", "D"]:
        return 5000
    elif house_energy_label in ["A", "B"]:
        return 10000
    elif house_energy_label in ["A+", "A++"]:
        return 20000
    elif house_energy_label == "A+++":
        return 30000
    elif house_energy_label == "A++++":
        return 40000
    elif house_energy_label == "A++++ met garantie":
        return 50000
    else:
        return 0

def calculate_bruteringsfactor(interest):
    if interest <= 2.0:
        return 1.05
    elif interest <= 2.5:
        return 1.10
    elif interest <= 3.0:
        return 1.15
    elif interest <= 4.0:
        return 1.20
    elif interest <= 4.5:
        return 1.25
    elif interest <= 5.5:
        return 1.30
    elif interest <= 6.0:
        return 1.35
    else:
        return 1.40

def calculate_max_mortgage(income_1: float, income_2: float, duo_monthly_fee: float, interest: float,
                           fixed_interest_rate_period: int, house_energy_label: str | None = None):
    toetsingsinkomen = income_1 + income_2

    toetsrente = 5 if fixed_interest_rate_period < 10 else interest

    financieringslastpercentage = calculate_financieringslastpercentage(toetsingsinkomen, toetsrente)

    maximale_woonlast = toetsingsinkomen * financieringslastpercentage / 12

    # Studieschuld
    gebruteerde_studieschuld = duo_monthly_fee * calculate_bruteringsfactor(interest)

    annuïteitenfactor = calculate_annuity(toetsrente)

    verhoging_energie = calculate_house_energy_label_addition(house_energy_label)

    maximale_hypotheek = round((maximale_woonlast - gebruteerde_studieschuld) / annuïteitenfactor) + verhoging_energie

    # Extra info: studieschuld impact
    studieschuld_impact = round(gebruteerde_studieschuld / annuïteitenfactor)
    maandbedrag = maximale_woonlast - gebruteerde_studieschuld

    return maximale_hypotheek, studieschuld_impact, verhoging_energie, maandbedrag
