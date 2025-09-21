from rest_framework import routers
from .views import (
    PatientViewSet,
    EncounterViewSet,
    ConsultationViewSet,
    DiagnosisViewSet,
    PrescriptionViewSet,
    AttachmentViewSet,
)

router = routers.DefaultRouter()
router.register(r'patients', PatientViewSet)
router.register(r'encounters', EncounterViewSet)
router.register(r'consultations', ConsultationViewSet)
router.register(r'diagnoses', DiagnosisViewSet)
router.register(r'prescriptions', PrescriptionViewSet)
router.register(r'attachments', AttachmentViewSet)

urlpatterns = router.urls
