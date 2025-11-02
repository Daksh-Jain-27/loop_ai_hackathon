from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    PatientRegisterView, 
    DoctorRegisterView, 
    MyTokenObtainPairView, 
    PatientSearchView, 
    PatientProfileView, 
    CreatePrescriptionView,
    PatientReportListView, 
    MyReportListView, 
    DownloadReportView
)

urlpatterns = [
    # --- NEW Register URLs ---
    path('register/patient/', PatientRegisterView.as_view(), name='patient_register'),
    path('register/doctor/', DoctorRegisterView.as_view(), name='doctor_register'),
    
    # --- Login ---
    path('token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # --- Other APIs ---
    path('search-patient/', PatientSearchView.as_view(), name='patient_search'),
    path('my-profile/', PatientProfileView.as_view(), name='my_profile'),
    path('create-prescription/', CreatePrescriptionView.as_view(), name='create_prescription'),
    path('patient-reports/<str:patient_unique_id>/', PatientReportListView.as_view(), name='patient_report_list'),
    path('my-reports/', MyReportListView.as_view(), name='my_report_list'),
    path('download-report/<int:report_id>/', DownloadReportView.as_view(), name='download_report'),
]