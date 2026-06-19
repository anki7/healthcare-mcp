import httpx
from typing import Any
from config import settings

class FHIRClient:
    def __init__(self):
        self.client = httpx.AsyncClient(
            base_url=settings.fhir_base_url,
            headers={"Accept": "application/fhir+json"}
        )

    async def search(self, resource_type: str, params: dict[str, Any]) -> list[dict]:
        """Generic FHIR search returning list of resource dicts."""
        response = await self.client.get(
            f"/{resource_type}", params=params
        )
        response.raise_for_status()
        bundle = response.json()
        entries = bundle.get("entry", [])
        return [entry["resource"] for entry in entries]

    async def get_resource(self, resource_type: str, resource_id: str) -> dict:
        response = await self.client.get(f"/{resource_type}/{resource_id}")
        response.raise_for_status()
        return response.json()

    async def close(self):
        await self.client.aclose()


# ===== Convenience methods =====
class HealthcareAPI:
    def __init__(self):
        self.fhir = FHIRClient()

    async def search_patients(self, name: str, birthdate: str | None = None) -> list[dict]:
        params = {"name": name}
        if birthdate:
            params["birthdate"] = birthdate
        return await self.fhir.search("Patient", params)

    async def get_patient_lab_results(self, patient_id: str, code: str | None = None,
                                      date_from: str | None = None) -> list[dict]:
        params = {
            "patient": patient_id,
            "category": "laboratory",
            "_sort": "-date"
        }
        if code:
            params["code"] = code
        if date_from:
            params["date"] = f"ge{date_from}"
        return await self.fhir.search("Observation", params)

    async def get_patient_appointments(self, patient_id: str,
                                       date_from: str | None = None,
                                       date_to: str | None = None) -> list[dict]:
        params = {
            "patient": patient_id,
            "_sort": "date"
        }
        if date_from and date_to:
            params["date"] = f"ge{date_from}&le{date_to}"
        elif date_from:
            params["date"] = f"ge{date_from}"
        elif date_to:
            params["date"] = f"le{date_to}"
        return await self.fhir.search("Appointment", params)

    async def get_patient_prescriptions(self, patient_id: str,
                                        status: str = "active") -> list[dict]:
        params = {
            "patient": patient_id,
            "status": status,
            "_sort": "-date"
        }
        return await self.fhir.search("MedicationRequest", params)
