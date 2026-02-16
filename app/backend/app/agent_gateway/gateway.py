import json
import datetime
from typing import Dict, Any, Optional
from app.agent_gateway.intent_router import detect_intent
from app.agent_gateway.response_builder import build_reply
from app.llm.llm_router import llm_explain
from app.llm.prompts import AUTO_EXPLAIN, SEC_EXPLAIN

# Automotive tools
from app.tools.automotive.dataset import DEMO_VEHICLES
from app.tools.automotive.tco.calculator import calculate_tco
from app.tools.automotive.tco.sensitivity import sensitivity

# Security stub (keep your existing engines here)
from app.tools.security.stub import security_stub_scan

# Simple in-memory conversations for hackathon (replace with DB later)
_CONV: Dict[str, list[dict]] = {}

def _get_conv(cid: str) -> list[dict]:
    return _CONV.setdefault(cid, [])

def list_conversations() -> list[dict]:
    """List all conversations with preview."""
    out = []
    for cid, msgs in _CONV.items():
        if not msgs:
            continue
        first = msgs[0]
        last = msgs[-1]
        out.append({
            "id": cid,
            "mode": first.get("mode", "security"),
            "preview": first.get("content", "")[:60],
            "timestamp": last.get("timestamp", datetime.datetime.now().isoformat()),
            "message_count": len(msgs)
        })
    # Sort by timestamp desc
    return sorted(out, key=lambda x: x["timestamp"], reverse=True)

def get_conversation(cid: str) -> list[dict]:
    """Get full conversation history."""
    return _CONV.get(cid, [])

def handle_chat(conversation_id: str, mode: str, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    intent = detect_intent(mode, message)
    tool_result = None
    ts = datetime.datetime.now().isoformat()

    # Save message
    _get_conv(conversation_id).append({
        "role": "user", 
        "content": message, 
        "mode": mode,
        "timestamp": ts
    })

    if mode == "security":
        if intent in ("scan_link", "scan_email", "scan_logs"):
            tool_result = security_stub_scan(intent=intent, text=message)

        system_extra = SEC_EXPLAIN
        llm_reply = llm_explain(
            user_message=message if tool_result is None else "Explain the scan result and next steps.",
            system_extra=system_extra,
            context_json=json.dumps(tool_result or {}, ensure_ascii=False)
        )
        _get_conv(conversation_id).append({
            "role": "assistant", 
            "content": llm_reply, 
            "mode": mode,
            "timestamp": datetime.datetime.now().isoformat()
        })
        return build_reply(intent, tool_result, llm_reply)

    if mode == "automotive":
        # Default: pick a demo vehicle if not provided
        vehicle_id = (context or {}).get("vehicle_id", DEMO_VEHICLES[0]["vehicle_id"])
        vehicle = next(v for v in DEMO_VEHICLES if v["vehicle_id"] == vehicle_id)

        # Default assumptions from context (frontend sends)
        assumptions = (context or {}).get("assumptions", {})
        # Minimal defaults if missing
        a = {
            "purchase_price": assumptions.get("purchase_price", vehicle["msrp"]),
            "down_payment": assumptions.get("down_payment", 0.0),
            "interest_rate_apr": assumptions.get("interest_rate_apr", 0.10),
            "loan_term_months": assumptions.get("loan_term_months", 48),
            "annual_km": assumptions.get("annual_km", 15000),
            "fuel_price_per_liter": assumptions.get("fuel_price_per_liter", 1.2),
            "electricity_price_per_kwh": assumptions.get("electricity_price_per_kwh", 0.2),
            "insurance_per_year": assumptions.get("insurance_per_year", 700),
            "tax_per_year": assumptions.get("tax_per_year", 250),
            "maintenance_per_year": assumptions.get("maintenance_per_year", 400),
            "fees_one_time": assumptions.get("fees_one_time", 200),
            "tires_cost_per_set": assumptions.get("tires_cost_per_set", 350),
            "tires_replace_km": assumptions.get("tires_replace_km", 40000),
            "years": assumptions.get("years", 5),
        }

        if intent in ("auto_tco", "auto_chat", "auto_compare"):
            # For hackathon: treat auto_chat as "compute TCO then explain"
            from app.schemas.automotive import VehicleNormalized, TcoAssumptions
            v = VehicleNormalized(**vehicle)
            ta = TcoAssumptions(**a)
            tco = calculate_tco(v, ta)
            tool_result = {
                "vehicle": vehicle,
                "tco": tco.model_dump()
            }

        if intent == "auto_sensitivity":
            from app.schemas.automotive import VehicleNormalized, TcoAssumptions, SensitivityRequest
            v = VehicleNormalized(**vehicle)
            ta = TcoAssumptions(**a)

            slider = (context or {}).get("slider", "fuel_price")
            rng = (context or {}).get("range", {"min": 0.9, "max": 1.8})
            req = SensitivityRequest(
                vehicle=v,
                assumptions=ta,
                slider=slider,
                points=int((context or {}).get("points", 7)),
                range_min=float(rng["min"]),
                range_max=float(rng["max"]),
            )
            s = sensitivity(req)
            tool_result = {
                "vehicle": vehicle,
                "sensitivity": s.model_dump()
            }

        system_extra = AUTO_EXPLAIN
        llm_reply = llm_explain(
            user_message=message if tool_result is None else "Explain the result and give a recommendation with tradeoffs.",
            system_extra=system_extra,
            context_json=json.dumps(tool_result or {}, ensure_ascii=False)
        )
        _get_conv(conversation_id).append({
            "role": "assistant", 
            "content": llm_reply, 
            "mode": mode,
            "timestamp": datetime.datetime.now().isoformat()
        })
        return build_reply(intent, tool_result, llm_reply)

    # fallback
    llm_reply = "Sentri: Unsupported mode."
    _get_conv(conversation_id).append({
        "role": "assistant", 
        "content": llm_reply, 
        "mode": mode,
        "timestamp": datetime.datetime.now().isoformat()
    })
    return build_reply(intent, tool_result, llm_reply)
