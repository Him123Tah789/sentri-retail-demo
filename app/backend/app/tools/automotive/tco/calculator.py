from app.schemas.automotive import VehicleNormalized, TcoAssumptions, TcoResult, TcoBreakdown
from .depreciation import depreciation_curve

def financing_cost(purchase_price: float, down_payment: float, apr: float, term_months: int) -> float:
    if term_months <= 0 or apr <= 0:
        return 0.0
    principal = max(0.0, purchase_price - down_payment)
    r = apr / 12.0
    n = term_months
    # monthly payment (amortized)
    pmt = (principal * r * (1 + r) ** n) / ((1 + r) ** n - 1)
    total_paid = pmt * n
    return max(0.0, total_paid - principal)

def fuel_energy_cost(vehicle: VehicleNormalized, a: TcoAssumptions) -> float:
    km = a.annual_km * a.years
    if vehicle.efficiency_unit == "L_PER_100KM":
        liters = (vehicle.efficiency_value / 100.0) * km
        return liters * a.fuel_price_per_liter
    else:
        kwh = (vehicle.efficiency_value / 100.0) * km
        return kwh * a.electricity_price_per_kwh

def tires_cost(a: TcoAssumptions) -> float:
    km = a.annual_km * a.years
    if a.tires_replace_km <= 0:
        return 0.0
    sets = int(km // a.tires_replace_km)
    return sets * a.tires_cost_per_set

def calculate_tco(vehicle: VehicleNormalized, a: TcoAssumptions) -> TcoResult:
    dep = depreciation_curve(a.purchase_price, a.years)
    fin = financing_cost(a.purchase_price, a.down_payment, a.interest_rate_apr, a.loan_term_months)
    energy = fuel_energy_cost(vehicle, a)
    ins = a.insurance_per_year * a.years
    tax = a.tax_per_year * a.years
    maint = a.maintenance_per_year * a.years
    tires = tires_cost(a)
    fees = a.fees_one_time

    total = dep + fin + energy + ins + tax + maint + tires + fees
    per_year = total / a.years
    per_month = total / (a.years * 12)

    return TcoResult(
        total=round(total, 2),
        per_year=round(per_year, 2),
        per_month=round(per_month, 2),
        breakdown=TcoBreakdown(
            depreciation=round(dep, 2),
            financing=round(fin, 2),
            fuel_or_energy=round(energy, 2),
            insurance=round(ins, 2),
            tax=round(tax, 2),
            maintenance=round(maint, 2),
            tires=round(tires, 2),
            fees=round(fees, 2),
        ),
        assumptions=a
    )
