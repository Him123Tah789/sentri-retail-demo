from app.schemas.automotive import VehicleNormalized, RawVehicle

def normalize_vehicle(raw: RawVehicle) -> VehicleNormalized:
    """
    Hackathon normalization:
    - supports 2 fake source formats to prove capability
    - output always VehicleNormalized
    """
    src = raw.source.lower()
    p = raw.payload

    if src == "source_a":
        # Example source A fields
        return VehicleNormalized(
            vehicle_id=p["id"],
            make=p["make"],
            model=p["model"],
            year=int(p["year"]),
            fuel_type=p["fuel"],
            msrp=float(p["msrp"]),
            efficiency_value=float(p["efficiency_value"]),
            efficiency_unit=p["efficiency_unit"],
            notes=p.get("notes")
        )

    if src == "source_b":
        # Example source B fields
        fuel = p["powertrain"]["type"]
        eff = p["powertrain"]["eff"]
        unit = "KWH_PER_100KM" if fuel == "ev" else "L_PER_100KM"
        return VehicleNormalized(
            vehicle_id=p["vehicleKey"],
            make=p["brand"],
            model=p["name"],
            year=int(p["modelYear"]),
            fuel_type=fuel,
            msrp=float(p["pricing"]["msrp"]),
            efficiency_value=float(eff),
            efficiency_unit=unit,
            notes=p.get("description")
        )

    raise ValueError(f"Unsupported source: {raw.source}")
