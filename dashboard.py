import streamlit as st

from hypotheek import calculate_max_mortgage
from hypotheek_opties import get_options
from studieschuld import calculate_duo_monthly_fee


def calculate_zzp_income(zzp_income_1, zzp_income_2, zzp_income_3):
    return (zzp_income_1 + zzp_income_2 + zzp_income_3) / 3


def main():
    st.set_page_config(layout="wide")
    st.title("Hypotheek Calculator")

    col_input, _, col_results = st.columns([2, 1, 2])

    with col_input:
        with st.sidebar:
            st.header("Inkomen")

            col_l, col_r = st.columns(2)

            with col_l:
                vast_inkomen = st.slider("Vast Inkomen", min_value=0, max_value=100000, step=5000, value=50000)

            with col_r:
                zzp_income_1 = st.number_input("ZZP Inkomen Jaar 1 (2021)", min_value=0, step=1000, value=50000)
                zzp_income_2 = st.number_input("ZZP Inkomen Jaar 2 (2022)", min_value=0, step=1000, value=50000)
                zzp_income_3 = st.number_input("ZZP Inkomen Jaar 3 (2023)", min_value=0, step=1000, value=50000)

            st.header("Studieschuld")
            col_l, col_r = st.columns(2)

            with col_l:
                studieschuld_1 = st.number_input("Studieschuld 1", min_value=0.0, step=1000.0, value=20000.00)
                interest_rate_1 = st.number_input("Jaarlijkse Rente 1 (%)", min_value=0.0, max_value=100.0,
                                                       step=0.01, value=0.0)
                num_months_1 = st.number_input("Aantal Maanden 1", min_value=0, step=1, value=420)

            with col_r:
                studieschuld_2 = st.number_input("Studieschuld 2", min_value=0.0, step=1000.0, value=10000.0)
                interest_rate_2 = st.number_input("Jaarlijkse Rente 2 (%)", min_value=0.0, max_value=100.0, step=0.1,
                                                     value=0.0)
                num_months_2 = st.number_input("Aantal Maanden 2", min_value=0, step=1, value=420)
            partnered = st.checkbox("Partnered")

        st.header("Input")
        house_price = st.number_input("Hoeveel kost het huis?", min_value=0, value=400000)
        ltv = st.slider("Hoeveel leg je zelf in?", min_value=60, max_value=100, step=1, value=100)
        if ltv < 100:
            st.warning(f"Je legt €{house_price * (100 - ltv) / 100:,.0f} eigen geld in. Rente daalt bij elke 10% eigen inleg (60%, 70%, 80%, 90%)")

        fixed_interest_rate_period = st.selectbox("Rentevaste periode", options=[5, 10, 20, 30], index=1)
        if fixed_interest_rate_period < 10:
            st.warning("Rente is vast voor minder dan 10 jaar, toetsrente is 5%")
        build_type = st.selectbox("Type bouw", options=["Bestaande bouw", "Nieuwbouw"], index=0)
        house_energy_label = st.selectbox("Energielabel",
                                          options=[None, "A++++ met garantie", "A++++", "A+++", "A++", "A+", "A", "B",
                                                   "C", "D", "E", "F", "G"], index=0)

        options = get_options(ltv, fixed_interest_rate_period, build_type, house_energy_label)

        interest_option = st.selectbox("Rente", options=[f"{p.rentestand:.2f} -- {p.aanbiederNaam}" for p in options], index=0)
        selected_interest = float(interest_option.split(" -- ")[0])
        interest_slider = st.slider("Rente", min_value=0.0, max_value=8.0, step=0.01, value=selected_interest)
        interest = interest_slider

    with col_results:
        result_zzp_income = calculate_zzp_income(zzp_income_1, zzp_income_2, zzp_income_3)
        total_income = vast_inkomen + result_zzp_income

        if partnered:
            duo_monthly_fee = calculate_duo_monthly_fee(
                principal=studieschuld_1 + studieschuld_2,
                annual_interest_rate=interest_rate_1,
                num_months=num_months_1,
                income=total_income,
                partner=partnered
            )
        else:
            duo_monthly_fee_1 = calculate_duo_monthly_fee(
                principal=studieschuld_1,
                annual_interest_rate=interest_rate_1,
                num_months=num_months_1,
                income=vast_inkomen + zzp_income_1,
                partner=partnered
            )
            duo_monthly_fee_2 = calculate_duo_monthly_fee(
                principal=studieschuld_2,
                annual_interest_rate=interest_rate_2,
                num_months=num_months_2,
                income=zzp_income_2 + zzp_income_3,
                partner=partnered
            )
            duo_monthly_fee = duo_monthly_fee_1 + duo_monthly_fee_2

        max_mortgage, loan_impact, energy_addition, monthly_payment = calculate_max_mortgage(
            vast_inkomen,
            result_zzp_income,
            duo_monthly_fee,
            interest,
            fixed_interest_rate_period,
            house_energy_label
        )

        st.header("Resultaten")
        col_l, col_r = st.columns(2)
        with col_l:
            st.metric(label="Maandbedrag DUO (gezamenlijk)", value=f"€{duo_monthly_fee:.2f}", delta=f"- €{loan_impact:,.0f} minder hypotheek")
        with col_r:
            st.metric(label="Totaal Inkomen", value=f"€{total_income:,.2f}", delta=f"€{vast_inkomen:,.0f} (Y) + €{result_zzp_income:,.0f} (A)")

        st.markdown("---")
        col_l, col_r = st.columns(2)
        with col_l:
            st.metric(label="Maximale Hypotheek", value=f"€{max_mortgage:,.0f}", delta=f"€{energy_addition:,.0f} (energielabel {house_energy_label})" if energy_addition > 0 else None)
        with col_r:
            st.metric(label="Kosten huis", value=f"€{house_price:,.0f}")
        st.markdown("---")

        if max_mortgage < ltv / 100 * house_price:
            st.warning("Hypotheek is hoger dan huiswaarde")
            return

        col_l, col_r = st.columns(2)
        with col_l:
            st.metric(label="Hypotheekbedrag", value=f"€{ltv / 100 * house_price:,.0f}")
        with col_r:
            st.metric(label="Maandbedrag hypotheek", value=f"€{monthly_payment:,.2f}")


        eigen_inleg = house_price - ltv / 100 * house_price
        overbieden = house_price * 0.12
        nhg_kosten = max_mortgage * 0.006 if house_price <= 435000 else 0
        taxatie_kosten = 800 if build_type == "Bestaande bouw" else 0
        totaal = eigen_inleg + overbieden + nhg_kosten + taxatie_kosten + 1600
        with st.expander(f"Eenmalige kosten: €{totaal:,.0f}"):
            st.markdown(f"""
    | Extra item                   | Kosten |
    |------------------------------|--------|
    | Eigen inleg                  | €{eigen_inleg:,.0f} |
    | Overbieden (12%)             | €{overbieden:,.0f} |
    | Nationale Hypotheek Garantie | €{nhg_kosten:,.0f} {'' if nhg_kosten else '_(Huis te duur)_'} |
    | Notaris + kadaster           | €1,600 |
    | Taxatie                      | €{taxatie_kosten} {'' if taxatie_kosten else '_(nieuwbouw)_'}|
    | **Totaal**                   | **€{eigen_inleg + overbieden + nhg_kosten + taxatie_kosten + 1600:,.0f}** |
    """)


if __name__ == "__main__":
    main()