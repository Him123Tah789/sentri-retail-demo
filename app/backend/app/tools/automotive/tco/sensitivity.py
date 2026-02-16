from app.schemas.automotive import VehicleNormalized, TcoAssumptions, SensitivityRequest, SensitivityResult, SensitivityPoint
from .calculator import calculate_tco

def sensitivity(req: SensitivityRequest) -> SensitivityResult:
    pts = []
    if req.points < 3:
        req.points = 3
    step = (req.range_max - req.range_min) / (req.points - 1)

    for i in range(req.points):
        x = req.range_min + step * i
        a = req.assumptions.model_copy(deep=True)

        if req.slider == "fuel_price":
            a.fuel_price_per_liter = float(x)
        elif req.slider == "annual_km":
            a.annual_km = float(x)
        elif req.slider == "interest_rate":
            a.interest_rate_apr = float(x)
        else:
            raise ValueError("Unsupported slider")

        t = calculate_tco(req.vehicle, a)
        pts.append(SensitivityPoint(x=round(x, 4), total=t.total, per_month=t.per_month))

    return SensitivityResult(slider=req.slider, points=pts)
