from django.db import models

class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Patient(TimeStampedModel):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    dni = models.CharField(max_length=20, unique=True, blank=True, null=True)
    phone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    birth_date = models.DateField(blank=True, null=True)
    sex = models.CharField(max_length=20, blank=True)
    address = models.CharField(max_length=255, blank=True)

    def __str__(self) -> str:
        return f"{self.last_name}, {self.first_name}"


class Encounter(TimeStampedModel):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='encounters')
    date = models.DateTimeField()
    reason = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)

    def __str__(self) -> str:
        return f"Encounter {self.id} - {self.patient} - {self.date:%Y-%m-%d}"


class Consultation(TimeStampedModel):
    encounter = models.OneToOneField(Encounter, on_delete=models.CASCADE, related_name='consultation')
    subjective = models.TextField(blank=True)
    objective = models.TextField(blank=True)
    assessment = models.TextField(blank=True)
    plan = models.TextField(blank=True)

    def __str__(self) -> str:
        return f"Consultation for {self.encounter}"


class Diagnosis(TimeStampedModel):
    encounter = models.ForeignKey(Encounter, on_delete=models.CASCADE, related_name='diagnoses')
    code = models.CharField(max_length=50, blank=True)
    icd10_code = models.CharField(max_length=20, blank=True)
    description = models.CharField(max_length=255)

    def __str__(self) -> str:
        return f"{self.code or self.icd10_code} - {self.description}"


class Prescription(TimeStampedModel):
    encounter = models.ForeignKey(Encounter, on_delete=models.CASCADE, related_name='prescriptions')
    medication = models.CharField(max_length=255)
    dosage = models.CharField(max_length=255, blank=True)
    frequency = models.CharField(max_length=255, blank=True)
    duration = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)

    def __str__(self) -> str:
        return f"{self.medication} for {self.encounter.patient}"


class Attachment(TimeStampedModel):
    encounter = models.ForeignKey(Encounter, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='attachments/%Y/%m/%d/')
    description = models.CharField(max_length=255, blank=True)

    def __str__(self) -> str:
        return f"Attachment {self.id} for {self.encounter}"
