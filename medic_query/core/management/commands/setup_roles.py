from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from core.models import Patient, Encounter, Consultation, Diagnosis, Prescription, Attachment


class Command(BaseCommand):
    help = "Create default roles (Admin, Medico, Asistente) with scoped permissions"

    def handle(self, *args, **options):
        # Ensure groups
        admin_group, _ = Group.objects.get_or_create(name="Admin")
        medico_group, _ = Group.objects.get_or_create(name="Medico")
        asistente_group, _ = Group.objects.get_or_create(name="Asistente")

        # Content types
        ct_patient = ContentType.objects.get_for_model(Patient)
        ct_encounter = ContentType.objects.get_for_model(Encounter)
        ct_consultation = ContentType.objects.get_for_model(Consultation)
        ct_diagnosis = ContentType.objects.get_for_model(Diagnosis)
        ct_prescription = ContentType.objects.get_for_model(Prescription)
        ct_attachment = ContentType.objects.get_for_model(Attachment)

        # Helper to get perms
        def perms(ct, codenames):
            return list(Permission.objects.filter(content_type=ct, codename__in=codenames))

        # Default Django model perms: add, change, delete, view
        admin_all_perms = []
        for ct in [ct_patient, ct_encounter, ct_consultation, ct_diagnosis, ct_prescription, ct_attachment]:
            admin_all_perms += perms(ct, [
                f"add_{ct.model}", f"change_{ct.model}", f"delete_{ct.model}", f"view_{ct.model}"
            ])
        admin_group.permissions.set(admin_all_perms)

        # Medico: full on clinical records, view on patients, add/change on patients
        medico_perms = []
        medico_perms += perms(ct_patient, ["view_patient", "add_patient", "change_patient"])  # no delete
        for ct in [ct_encounter, ct_consultation, ct_diagnosis, ct_prescription, ct_attachment]:
            medico_perms += perms(ct, [
                f"add_{ct.model}", f"change_{ct.model}", f"delete_{ct.model}", f"view_{ct.model}"
            ])
        medico_group.permissions.set(medico_perms)

        # Asistente: gestionar pacientes y turnos/encounters, ver todo, sin borrar clínico
        asistente_perms = []
        asistente_perms += perms(ct_patient, ["add_patient", "change_patient", "view_patient"])  # no delete
        asistente_perms += perms(ct_encounter, ["add_encounter", "change_encounter", "view_encounter"])  # no delete
        # Read-only for the rest
        for ct in [ct_consultation, ct_diagnosis, ct_prescription, ct_attachment]:
            asistente_perms += perms(ct, [f"view_{ct.model}"])
        asistente_group.permissions.set(asistente_perms)

        self.stdout.write(self.style.SUCCESS("Roles y permisos creados/actualizados."))
