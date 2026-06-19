from pydantic import BaseModel, Field

class PatientSearch(BaseModel):
    name: str = Field(description="Full or partial name of the patient")
    birthdate: str | None = Field(default=None, description="YYYY-MM-DD")

class PatientIdParam(BaseModel):
    patient_id: str = Field(description="FHIR Patient resource ID")

class LabResultsQuery(PatientIdParam):
    code: str | None = Field(default=None, description="LOINC code, e.g. 26474-7")
    date_from: str | None = None

class AppointmentQuery(PatientIdParam):
    date_from: str | None = None
    date_to: str | None = None

class PrescriptionQuery(PatientIdParam):
    status: str | None = "active"
