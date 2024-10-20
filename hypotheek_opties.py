from pydantic import BaseModel, Field
import requests_cache
from enum import Enum
from typing import Optional, List

class MortgageType(str, Enum):
    ANNUITY = "Annuiteitenhypotheek"
    LINEAR = "Lineaire_hypotheek"
    INTEREST_ONLY = "Aflossingsvrije_hypotheek"
    INVESTMENT = "Beleggershypotheek"
    LIFE = "Levenhypotheek"
    SAVINGS = "Spaarhypotheek"

class InterestTariff(str, Enum):
    NHG = "0"
    UPTO_50 = "50"
    UPTO_60 = "60"
    UPTO_70 = "70"
    UPTO_80 = "80"
    UPTO_90 = "90"
    UPTO_100 = "100"
    ABOVE_100 = "106"

class BuildingType(str, Enum):
    EXISTING = "Bestaande_bouw"
    NEW = "Nieuwbouw"

class EnergyLabel(str, Enum):
    APPPP_GUARANTEE = "APPPP"
    APPPP = "APPPP"
    APPP = "APPP"
    APP = "APP"
    AP = "AP"
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    E = "E"
    F = "F"
    G = "G"
    NONE = ""

class MortgageInput(BaseModel):
    mortgage_type: MortgageType = Field(..., alias="HypotheekVorm")
    mortgage_term: int = Field(..., alias="RentevastePeriode")
    interest_tariff: InterestTariff = Field(..., alias="RenteBasis")
    building_type: BuildingType = Field(..., alias="IsNieuwbouw")
    energy_label: Optional[EnergyLabel] = Field(None, alias="EnergyLabel")

class MortgageProduct(BaseModel):
    logoUrl: str
    hypotheekNaam: str
    aanbiederId: str
    aanbiederNaam: str
    rentestand: float
    hypotheekVorm: MortgageType
    trend: str
    uitgelicht: bool
    lookupId: str
    rentevastePeriode: int

class MortgageOutput(BaseModel):
    producten: List[MortgageProduct]

def get_interest_rates(input_data: MortgageInput) -> MortgageOutput:
    # Create a cached session
    session = requests_cache.CachedSession('mortgage_cache', backend='sqlite', expire_after=3600)

    # Prepare the URL and parameters
    url = 'https://api.hypotheker.nl/v2/interestrates/hypotheekaanbieders/'
    params = input_data.model_dump(by_alias=True)

    # Convert building_type to boolean
    params['IsNieuwbouw'] = params['IsNieuwbouw'] == BuildingType.NEW

    # Make the API request
    response = session.get(url, params=params)
    response.raise_for_status()  # Raise an exception for HTTP errors

    # Parse the response into the MortgageOutput model
    return MortgageOutput.model_validate(response.json())

def create_mortgage_input(
    ltv: int,
    fixed_interest_rate_period: int,
    build_type: str,
    house_energy_label: Optional[str]
) -> MortgageInput:
    # Convert LTV to InterestTariff
    if ltv <= 60:
        interest_tariff = InterestTariff.UPTO_60
    elif ltv <= 70:
        interest_tariff = InterestTariff.UPTO_70
    elif ltv <= 80:
        interest_tariff = InterestTariff.UPTO_80
    elif ltv <= 90:
        interest_tariff = InterestTariff.UPTO_90
    elif ltv <= 100:
        interest_tariff = InterestTariff.UPTO_100
    else:
        interest_tariff = InterestTariff.ABOVE_100

    # Convert build_type
    building_type = BuildingType.NEW if build_type == "Nieuwbouw" else BuildingType.EXISTING

    # Convert energy_label
    energy_label_map = {
        None: None,
        "A++++ met garantie": EnergyLabel.APPPP_GUARANTEE,
        "A++++": EnergyLabel.APPPP,
        "A+++": EnergyLabel.APPP,
        "A++": EnergyLabel.APP,
        "A+": EnergyLabel.AP,
        "A": EnergyLabel.A,
        "B": EnergyLabel.B,
        "C": EnergyLabel.C,
        "D": EnergyLabel.D,
        "E": EnergyLabel.E,
        "F": EnergyLabel.F,
        "G": EnergyLabel.G
    }
    energy_label = energy_label_map.get(house_energy_label, None)

    return MortgageInput(
        HypotheekVorm=MortgageType.ANNUITY,  # Assuming Annuity as default
        RentevastePeriode=fixed_interest_rate_period,
        RenteBasis=interest_tariff,
        IsNieuwbouw=building_type,
        EnergyLabel=energy_label
    )

def get_options(ltv: int,
    fixed_interest_rate_period: int,
    build_type: str,
    house_energy_label: Optional[str]) -> List[MortgageProduct]:
    input_data = create_mortgage_input(ltv, fixed_interest_rate_period, build_type, house_energy_label)
    return get_interest_rates(input_data).producten
