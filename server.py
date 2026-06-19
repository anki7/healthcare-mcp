import os
from mcp.server.fastmcp import FastMCP
from fhir_client import HealthcareAPI

# Create the MCP server
mcp = FastMCP("healthcare-mcp")
api = HealthcareAPI()

# ---------- Tools (unchanged) ----------
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

# ---------- Main runner ----------
if __name__ == "__main__":
    if os.environ.get("TRANSPORT", "stdio") == "sse":
        import uvicorn
        # FastMCP provides an ASGI app for SSE / HTTP
        uvicorn.run(mcp.get_asgi_app(), host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
    else:
        mcp.run()   # stdio for Claude Desktop
