from pydantic import BaseModel
from typing import Literal, Optional, Dict, Any, List

FuelType = Literal["petrol", "diesel", "hybrid", "ev"]

class RawVehicle(BaseModel):
    source: str
    payload: Dict[str, Any]

class VehicleNormalized(BaseModel):
    vehicle_id: str
    make: str
    model: str
    year: int
    fuel_type: FuelType
    msrp: float
    efficiency_value: float   # L/100km for ICE/hybrid, kWh/100km for EV
    efficiency_unit: Literal["L_PER_100KM", "KWH_PER_100KM"]
    notes: Optional[str] = None

class TcoAssumptions(BaseModel):
    purchase_price: float
    down_payment: float = 0.0
    interest_rate_apr: float = 0.0  # e.g., 0.12 for 12%
    loan_term_months: int = 0       # 0 means cash
    annual_km: float = 15000
    fuel_price_per_liter: float = 1.2
    electricity_price_per_kwh: float = 0.20
    insurance_per_year: float = 700
    tax_per_year: float = 250
    maintenance_per_year: float = 400
    fees_one_time: float = 200
    tires_cost_per_set: float = 350
    tires_replace_km: float = 40000
    years: int = 5

class TcoBreakdown(BaseModel):
    depreciation: float
    financing: float
    fuel_or_energy: float
    insurance: float
    tax: float
    maintenance: float
    tires: float
    fees: float

class TcoResult(BaseModel):
    total: float
    per_year: float
    per_month: float
    breakdown: TcoBreakdown
    assumptions: TcoAssumptions

class SensitivityRequest(BaseModel):
    vehicle: VehicleNormalized
    assumptions: TcoAssumptions
    slider: Literal["fuel_price", "annual_km", "interest_rate"]
    points: int = 7
    range_min: float
    range_max: float

class SensitivityPoint(BaseModel):
    x: float
    total: float
    per_month: float

class SensitivityResult(BaseModel):
    slider: str
    points: List[SensitivityPoint]
