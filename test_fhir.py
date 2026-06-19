import asyncio
from fhir_client import HealthcareAPI

async def main():
    api = HealthcareAPI()
    patients = await api.search_patients("Smith")
    print("Patients found:", len(patients))
    if patients:
        p = patients[0]
        pid = p.get("id")
        print("First patient ID:", pid)
        labs = await api.get_patient_lab_results(pid)
        print("Lab results:", len(labs))
    await api.fhir.close()

asyncio.run(main())
