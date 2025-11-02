from rest_framework import serializers
from .models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import PatientProfile, DoctorProfile
from .models import Prescription, MedicationItem
from .models import MedicalReport

class PatientRegisterSerializer(serializers.ModelSerializer):
    # We add 'full_name' which isn't on the User model
    full_name = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('full_name', 'username', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        full_name = validated_data.pop('full_name')

        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            role='patient' # Set role automatically
        )

        PatientProfile.objects.create(user=user, full_name=full_name)
        return user

# --- NEW: Doctor Registration ---
class DoctorRegisterSerializer(serializers.ModelSerializer):
    # Add all the doctor-specific fields
    full_name = serializers.CharField(write_only=True, required=True)
    hospital_name = serializers.CharField(write_only=True, required=True)
    hospital_id = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        # The 'email' field will be used for 'work_email'
        fields = ('full_name', 'hospital_name', 'hospital_id', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        full_name = validated_data.pop('full_name')
        hospital_name = validated_data.pop('hospital_name')
        hospital_id = validated_data.pop('hospital_id')

        # Auto-generate a username from the email
        username = validated_data['email'].split('@')[0]

        user = User.objects.create_user(
            username=username,
            email=validated_data['email'],
            password=validated_data['password'],
            role='doctor' # Set role automatically
        )

        DoctorProfile.objects.create(
            user=user, 
            full_name=full_name,
            hospital_name=hospital_name,
            hospital_id=hospital_id
        )
        return user

# This customizes the login token to include the user's role
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['email'] = user.email
        token['username'] = user.username
        token['role'] = user.role

        # --- NEW: Add full_name to token ---
        token['full_name'] = user.username # default
        if user.role == 'patient':
            try:
                token['full_name'] = user.patient_profile.full_name
            except PatientProfile.DoesNotExist:
                pass
        elif user.role == 'doctor':
            try:
                token['full_name'] = user.doctor_profile.full_name
            except DoctorProfile.DoesNotExist:
                pass

        return token
    
class PatientProfileSerializer(serializers.ModelSerializer):
    # Get email from the related User model
    email = serializers.EmailField(source='user.email', read_only=True)
    # Format the 'member_since' date to be a readable string
    member_since = serializers.DateField(format="%Y-%m-%d", read_only=True)

    class Meta:
        model = PatientProfile
        # All the fields to include in the API response
        fields = (
            'unique_patient_id',
            'email',
            'full_name',
            'date_of_birth',
            'age',
            'gender',
            'blood_group',
            'height',
            'weight',
            'member_since',
            'emergency_contact',
            'phone_no',
            'allergies',
        )
# This serializer is for the items in the medication list
class MedicationItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicationItem
        # List all fields from the MedicationItem model
        fields = (
            'medication_name', 'strength', 'dosage_form', 'indication',
            'route', 'dose', 'frequency', 'duration'
        )

# --- REPLACED SERIALIZER ---
# This serializer now accepts a NESTED LIST of medications
class PrescriptionCreateSerializer(serializers.ModelSerializer):
    # This matches the frontend: a list of medication objects
    medication_items = MedicationItemSerializer(many=True) 
    patient_unique_id = serializers.CharField(write_only=True)

    class Meta:
        model = Prescription
        # These are the "header" fields
        fields = (
            'patient_unique_id',
            'current_problem',
            'warning_comments',
            'follow_up',
            'medication_items', # The nested list
        )

    def create(self, validated_data):
        # We need to handle the nested creation manually
        
        # 1. Get the patient and doctor
        patient_unique_id = validated_data.pop('patient_unique_id')
        medication_items_data = validated_data.pop('medication_items')
        
        # Get doctor from the request context (we'll pass this in the view)
        doctor_profile = self.context['doctor']
        patient_profile = self.context['patient']
        
        # 2. Create the main Prescription "header"
        prescription = Prescription.objects.create(
            doctor=doctor_profile,
            patient=patient_profile,
            **validated_data
        )

        # 3. Loop and create each MedicationItem
        for item_data in medication_items_data:
            MedicationItem.objects.create(prescription=prescription, **item_data)
            
        return prescription

class MedicalReportSerializer(serializers.ModelSerializer):
    # Get the doctor's full name from the related profile
    doctor_name = serializers.CharField(source='doctor.full_name', read_only=True)
    
    class Meta:
        model = MedicalReport
        # We only need to send the ID, name, date, and doctor
        # We don't send the 'file_data' here, that's too large for a list
        fields = ('id', 'report_name', 'created_at', 'doctor_name')

class PatientProfileCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatientProfile
        # These are all the fields from your list
        fields = (
            'full_name',
            'date_of_birth',
            'age',
            'gender',
            'blood_group',
            'height',
            'weight',
            'emergency_contact',
            'phone_no',
            'allergies',
        )