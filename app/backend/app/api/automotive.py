from fastapi import APIRouter
from app.tools.automotive.dataset import DEMO_VEHICLES

router = APIRouter()

@router.get("/auto/vehicles")
def list_demo_vehicles():
    return {"vehicles": DEMO_VEHICLES}
