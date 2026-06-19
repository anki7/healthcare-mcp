import os
from mcp.server.fastmcp import FastMCP
from starlette.applications import Starlette
from starlette.routing import Route
from mcp.server.sse import SseServerTransport

from fhir_client import HealthcareAPI

mcp = FastMCP("healthcare-mcp")
api = HealthcareAPI()

# ---------------- Tools ----------------
@mcp.tool()
async def search_patients(name: str, birthdate: str | None = None) -> str:
    results = await api.search_patients(name, birthdate)
    summary = [
        {
            "id": p.get("id"),
            "name": " ".join(
                (p.get("name", [{}])[0].get("given", []) +
                 [p.get("name", [{}])[0].get("family", "")])
            ),
            "birthDate": p.get("birthDate")
        } for p in results[:10]
    ]
    return str(summary)

@mcp.tool()
async def get_patient_lab_results(patient_id: str, code: str | None = None,
                                  date_from: str | None = None) -> str:
    results = await api.get_patient_lab_results(patient_id, code, date_from)
    parsed = []
    for obs in results[:10]:
        value = obs.get("valueQuantity", {}).get("value") or obs.get("valueString")
        parsed.append({
            "id": obs["id"],
            "code": obs.get("code", {}).get("coding", [{}])[0].get("display"),
            "value": value,
            "unit": obs.get("valueQuantity", {}).get("unit"),
            "effective": obs.get("effectiveDateTime")
        })
    return str(parsed)

@mcp.tool()
async def get_patient_appointments(patient_id: str, date_from: str | None = None,
                                   date_to: str | None = None) -> str:
    results = await api.get_patient_appointments(patient_id, date_from, date_to)
    parsed = [{
        "id": a["id"],
        "status": a["status"],
        "start": a.get("start"),
        "type": a.get("serviceType", [{}])[0].get("text", "N/A")
    } for a in results[:10]]
    return str(parsed)

@mcp.tool()
async def get_patient_prescriptions(patient_id: str, status: str = "active") -> str:
    results = await api.get_patient_prescriptions(patient_id, status)
    parsed = [{
        "id": r["id"],
        "medication": r.get("medicationCodeableConcept", {}).get("text", "Unknown"),
        "status": r["status"],
        "authoredOn": r.get("authoredOn")
    } for r in results[:10]]
    return str(parsed)

# ---------- SSE transport ----------
async def handle_sse(request):
    async with SseServerTransport("/messages") as transport:
        await mcp.run(
            transport.read_stream,
            transport.write_stream,
            mcp._create_initialization_capabilities()
        )

starlette_app = Starlette(routes=[Route("/sse", endpoint=handle_sse)])

# ---------- Main runner ----------
if __name__ == "__main__":
    if os.environ.get("TRANSPORT", "stdio") == "sse":
        import uvicorn
        uvicorn.run(starlette_app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
    else:
        mcp.run()
