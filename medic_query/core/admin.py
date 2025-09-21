from django.contrib import admin
from .models import Patient, Encounter, Consultation, Diagnosis, Prescription, Attachment

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ("id", "last_name", "first_name", "dni", "phone", "email", "created_at")
    search_fields = ("last_name", "first_name", "dni", "email")


@admin.register(Encounter)
class EncounterAdmin(admin.ModelAdmin):
    list_display = ("id", "patient", "date", "reason")
    list_filter = ("date",)


@admin.register(Consultation)
class ConsultationAdmin(admin.ModelAdmin):
    list_display = ("id", "encounter", "created_at")


@admin.register(Diagnosis)
class DiagnosisAdmin(admin.ModelAdmin):
    list_display = ("id", "encounter", "code", "icd10_code", "description")
    search_fields = ("code", "icd10_code", "description")


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ("id", "encounter", "medication", "dosage", "frequency", "duration")
    search_fields = ("medication",)


@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = ("id", "encounter", "file", "description", "created_at")
