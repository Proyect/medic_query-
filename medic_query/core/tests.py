from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from .models import Patient, Encounter, Consultation, Diagnosis, Prescription, Attachment
from datetime import datetime
from django.core.files.uploadedfile import SimpleUploadedFile


class ModelSmokeTests(TestCase):
    def test_create_patient_and_encounter(self):
        patient = Patient.objects.create(first_name="Ana", last_name="García", dni="12345678")
        self.assertIsNotNone(patient.id)
        enc = Encounter.objects.create(patient=patient, date=datetime(2024, 1, 1, 10, 0), reason="Control")
        self.assertEqual(enc.patient.id, patient.id)
        self.assertEqual(patient.encounters.count(), 1)


class APISmokeTests(TestCase):
    def setUp(self):
        self.User = get_user_model()
        self.user = self.User.objects.create_user(username="tester", email="t@example.com", password="Passw0rd!123")
        self.client = APIClient()

    def _obtain_token(self):
        url = reverse('token_obtain_pair')
        resp = self.client.post(url, {"username": "tester", "password": "Passw0rd!123"}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK, msg=resp.content)
        return resp.data['access']

    def test_patients_requires_auth(self):
        # List without auth should be 401 by default (settings require IsAuthenticated)
        resp = self.client.get('/api/v1/patients/')
        self.assertIn(resp.status_code, (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN))

    def test_patients_crud_with_jwt(self):
        token = self._obtain_token()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

        # Create
        payload = {"first_name": "Juan", "last_name": "Pérez", "dni": "99999999"}
        resp = self.client.post('/api/v1/patients/', payload, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED, msg=resp.content)
        pid = resp.data['id']

        # List
        resp = self.client.get('/api/v1/patients/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(resp.data.get('count', 1), 1)

        # Retrieve
        resp = self.client.get(f'/api/v1/patients/{pid}/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['dni'], '99999999')

    def _auth(self):
        token = self._obtain_token()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    def test_full_flow_encounter_clinical_records(self):
        self._auth()

        # Create patient
        p = self.client.post('/api/v1/patients/', {"first_name": "Eva", "last_name": "Lopez"}, format='json').data
        pid = p['id']

        # Create encounter
        enc_payload = {"patient": pid, "date": "2025-01-01T10:00:00Z", "reason": "Consulta"}
        enc = self.client.post('/api/v1/encounters/', enc_payload, format='json').data
        eid = enc['id']

        # Create consultation (SOAP)
        cons_payload = {
            "encounter": eid,
            "subjective": "dolor leve",
            "objective": "TA 120/80",
            "assessment": "cefalea tensional",
            "plan": "ibuprofeno PRN"
        }
        cons = self.client.post('/api/v1/consultations/', cons_payload, format='json').data
        self.assertIsNotNone(cons['id'])

        # Create diagnosis
        diag_payload = {"encounter": eid, "icd10_code": "R51", "description": "Cefalea"}
        diag = self.client.post('/api/v1/diagnoses/', diag_payload, format='json').data
        self.assertIsNotNone(diag['id'])

        # Create prescription
        rx_payload = {"encounter": eid, "medication": "Ibuprofeno 400 mg", "dosage": "1 comprimido", "frequency": "c/8h", "duration": "3 dias"}
        rx = self.client.post('/api/v1/prescriptions/', rx_payload, format='json').data
        self.assertIsNotNone(rx['id'])

        # Upload attachment (fake text file)
        file = SimpleUploadedFile("nota.txt", b"anexo de prueba", content_type="text/plain")
        resp = self.client.post('/api/v1/attachments/', {"encounter": eid, "file": file, "description": "nota"})
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED, msg=resp.content)

        # Basic lists
        for path in [
            '/api/v1/encounters/',
            '/api/v1/consultations/',
            '/api/v1/diagnoses/',
            '/api/v1/prescriptions/',
            '/api/v1/attachments/',
        ]:
            r = self.client.get(path)
            self.assertEqual(r.status_code, status.HTTP_200_OK, msg=f"List failed on {path}: {r.content}")

# Create your tests here.
