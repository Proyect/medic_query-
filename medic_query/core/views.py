from rest_framework import viewsets, permissions
from .models import Patient, Encounter, Consultation, Diagnosis, Prescription, Attachment
from .serializers import (
    PatientSerializer,
    EncounterSerializer,
    ConsultationSerializer,
    DiagnosisSerializer,
    PrescriptionSerializer,
    AttachmentSerializer,
)

# Create your views here.

class IsAuthenticatedOrReadOnly(permissions.IsAuthenticatedOrReadOnly):
    pass


class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all().order_by('-created_at')
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class EncounterViewSet(viewsets.ModelViewSet):
    queryset = Encounter.objects.select_related('patient').all().order_by('-date')
    serializer_class = EncounterSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class ConsultationViewSet(viewsets.ModelViewSet):
    queryset = Consultation.objects.select_related('encounter', 'encounter__patient').all().order_by('-created_at')
    serializer_class = ConsultationSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class DiagnosisViewSet(viewsets.ModelViewSet):
    queryset = Diagnosis.objects.select_related('encounter', 'encounter__patient').all().order_by('-created_at')
    serializer_class = DiagnosisSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class PrescriptionViewSet(viewsets.ModelViewSet):
    queryset = Prescription.objects.select_related('encounter', 'encounter__patient').all().order_by('-created_at')
    serializer_class = PrescriptionSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class AttachmentViewSet(viewsets.ModelViewSet):
    queryset = Attachment.objects.select_related('encounter', 'encounter__patient').all().order_by('-created_at')
    serializer_class = AttachmentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
