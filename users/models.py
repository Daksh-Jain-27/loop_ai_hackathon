from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = (
        ('doctor', 'Doctor'),
        ('patient', 'Patient'),
    )
    # We use email as the unique identifier instead of username
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    # Tell Django to use 'email' as the login field
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username'] # 'username' is still required by AbstractUser

# This will store patient-specific info
class PatientProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name='patient_profile')
    unique_patient_id = models.CharField(max_length=20, unique=True, blank=True, null=True)

    # This will be set at registration
    full_name = models.CharField(max_length=255, blank=True)

    # These will be set by the patient after logging in
    date_of_birth = models.CharField(max_length=20, blank=True)
    age = models.PositiveIntegerField(null=True, blank=True)
    gender = models.CharField(max_length=20, blank=True)
    blood_group = models.CharField(max_length=5, blank=True)
    height = models.CharField(max_length=10, blank=True)
    weight = models.CharField(max_length=10, blank=True)
    member_since = models.DateField(auto_now_add=True)
    emergency_contact = models.CharField(max_length=255, blank=True)
    phone_no = models.CharField(max_length=20, blank=True)
    allergies = models.TextField(blank=True)

    def __str__(self):
        return self.user.email

# This will store doctor-specific info
class DoctorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name='doctor_profile')

    # These will be set at registration
    full_name = models.CharField(max_length=255, blank=True)
    hospital_name = models.CharField(max_length=255, blank=True)
    hospital_id = models.CharField(max_length=100, blank=True)

    # These were here before
    specialization = models.CharField(max_length=100, blank=True)
    license_number = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.user.email

# 4. Stores the PRESCRIPTION FORM DATA (This is the "TXT" part)
class Prescription(models.Model):
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='prescriptions')
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name='prescriptions')
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Fields from your new form
    current_problem = models.TextField()
    warning_comments = models.TextField(blank=True)
    follow_up = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"Prescription for {self.patient.user.email} on {self.created_at.date()}"

# 5. NEW MODEL: Stores the individual medications FOR a prescription
class MedicationItem(models.Model):
    # This links each medication back to its one prescription
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE, related_name='medication_items')
    
    medication_name = models.CharField(max_length=255)
    strength = models.CharField(max_length=100, blank=True)
    dosage_form = models.CharField(max_length=100, blank=True)
    indication = models.CharField(max_length=255, blank=True)
    route = models.CharField(max_length=100, blank=True)
    dose = models.CharField(max_length=100, blank=True)
    frequency = models.CharField(max_length=100, blank=True)
    duration = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.medication_name

# 5. Stores all PDF reports AND generated prescriptions
class MedicalReport(models.Model):
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='reports')
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name='reports')
    report_name = models.CharField(max_length=255) # e.g., "Prescription - 02-Nov-2025.pdf"
    file_data = models.BinaryField() # This is the BYTEA / BLOB field for PDF data
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.report_name} for {self.patient.user.email}"