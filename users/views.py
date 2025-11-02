from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import MedicalReportSerializer
from .permissions import IsDoctor
from .models import User, PatientProfile
from .serializers import PatientRegisterSerializer, DoctorRegisterSerializer
from .serializers import PatientProfileSerializer, PatientProfileCreateSerializer
from .serializers import MyTokenObtainPairSerializer
from .permissions import IsDoctor
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
import datetime
# Imports for our new view
from .models import Prescription, MedicalReport, DoctorProfile
from .serializers import PrescriptionCreateSerializer
from django.http import HttpResponse

# --- NEW: Patient Register View ---
class PatientRegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = PatientRegisterSerializer

# --- NEW: Doctor Register View ---
class DoctorRegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = DoctorRegisterSerializer

# This is the view for /api/token/ (our login endpoint)
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

class PatientSearchView(APIView):
    permission_classes = [IsAuthenticated, IsDoctor] # Must be logged in AND be a doctor

    def get(self, request):
        # Get the 'unique_id' from the query parameters (e.g., /?unique_id=PATIENT-001)
        patient_id = request.query_params.get('unique_id', None)

        if not patient_id:
            return Response(
                {"error": "A 'unique_id' query parameter is required."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Find the patient
            profile = PatientProfile.objects.get(unique_patient_id=patient_id)
            serializer = PatientProfileSerializer(profile)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except PatientProfile.DoesNotExist:
            # Patient not found
            return Response(
                {"error": "Patient not found with this ID."}, 
                status=status.HTTP_404_NOT_FOUND
            )

class PatientProfileView(APIView):
    permission_classes = [IsAuthenticated]

    # GET: Fetches the profile
    def get(self, request):
        try:
            profile = PatientProfile.objects.get(user=request.user)
            
            # --- NEW COMPLETENESS CHECK ---
            # 'age' is a field that is only filled in by the form.
            # If it's missing, we know the profile is incomplete.
            if not profile.age: 
                # Intentionally raise this error to trigger the 404
                raise PatientProfile.DoesNotExist
                
            serializer = PatientProfileSerializer(profile)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except PatientProfile.DoesNotExist:
            # This 404 will tell the frontend to show the "Create Profile" form
            return Response(
                {"error": "Patient profile is incomplete. Please create one."}, 
                status=status.HTTP_404_NOT_FOUND
            )

    # POST: Creates/Updates the profile
    def post(self, request):
        # We are UPDATING the profile that was auto-created at registration
        try:
            # Get the existing, empty profile
            profile = PatientProfile.objects.get(user=request.user)
        except PatientProfile.DoesNotExist:
             return Response({"error": "Profile not found."}, status=status.HTTP_404_NOT_FOUND)
        
        # We use the 'instance=profile' argument to UPDATE the existing row
        serializer = PatientProfileCreateSerializer(instance=profile, data=request.data)
        
        if serializer.is_valid():
            # --- Auto-generate the Unique ID ---
            if not profile.unique_patient_id:
                profile.unique_patient_id = f"PAT-{request.user.id:06d}"
            
            serializer.save() # This will update the instance
            
            # Return the *full* profile data so the dashboard can update
            full_profile_serializer = PatientProfileSerializer(profile)
            return Response(full_profile_serializer.data, status=status.HTTP_200_OK)
        
        # If form is invalid
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CreatePrescriptionView(APIView):
    permission_classes = [IsAuthenticated, IsDoctor]

    def post(self, request, *args, **kwargs):
        
        # --- 1. Find Patient and Doctor profiles ---
        patient_unique_id = request.data.get('patient_unique_id')
        try:
            patient_profile = PatientProfile.objects.get(unique_patient_id=patient_unique_id)
            doctor_profile = DoctorProfile.objects.get(user=request.user)
        except PatientProfile.DoesNotExist:
            return Response({"error": "Patient not found."}, status=status.HTTP_404_NOT_FOUND)
        except DoctorProfile.DoesNotExist:
            return Response({"error": "Doctor profile not found."}, status=status.HTTP_404_NOT_FOUND)

        # 2. Validate and Save data
        # We pass the profiles in the 'context' to the serializer
        serializer_context = {
            'doctor': doctor_profile,
            'patient': patient_profile,
        }
        serializer = PrescriptionCreateSerializer(data=request.data, context=serializer_context)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # .save() will now call our custom .create() method
        prescription = serializer.save() 
        data = serializer.validated_data # This has all the clean data

        # --- 3. Generate the PDF ---
        pdf_buffer = io.BytesIO()
        p = canvas.Canvas(pdf_buffer, pagesize=letter)
        width, height = letter
        margin = 1 * inch
        
        # --- Helper function ---
        def draw_wrapped_text(y_pos, label, text):
            p.setFont("Helvetica-Bold", 12)
            p.drawString(margin, y_pos, label)
            p.setFont("Helvetica", 12)
            
            text_lines = []
            max_width = width - (2 * margin) - 70
            current_line = ""
            for word in text.split():
                if p.stringWidth(current_line + word) < max_width:
                    current_line += word + " "
                else:
                    text_lines.append(current_line)
                    current_line = word + " "
            text_lines.append(current_line)
            
            line_height = 14
            for line in text_lines:
                p.drawString(margin + 70, y_pos, line)
                y_pos -= line_height
            return y_pos - (0.25 * inch)
        # --- End Helper ---

        p.setFont("Helvetica-Bold", 18)
        p.drawCentredString(width / 2.0, height - 1*inch, "Medical Prescription")
        
        y = height - 1.5*inch
        p.setFont("Helvetica", 12)
        p.drawString(margin, y, f"Patient: {patient_profile.full_name}")
        p.drawString(margin, y - 20, f"Patient ID: {patient_profile.unique_patient_id}")
        
        p.drawRightString(width - margin, y, f"Doctor: {doctor_profile.full_name}")
        p.drawRightString(width - margin, y - 20, f"Specialization: {doctor_profile.specialization}")

        p.line(margin, y - 40, width - margin, y - 40)
        y = y - 70
        
        y = draw_wrapped_text(y, "Problem:", data['current_problem'])

        # --- NEW MEDICATION LOOP ---
        for i, med in enumerate(prescription.medication_items.all()):
            p.setFont("Helvetica-Bold", 14)
            p.drawString(margin, y, f"Rx #{i + 1}:")
            y -= 30

            p.setFont("Helvetica-Bold", 12)
            p.drawString(margin, y, f"{med.medication_name} {med.strength} ({med.dosage_form})")
            y -= 25

            p.setFont("Helvetica", 12)
            p.drawString(margin + 20, y, f"Dose: {med.dose}")
            p.drawString(margin + 150, y, f"Route: {med.route}")
            p.drawString(margin + 300, y, f"Frequency: {med.frequency}")
            y -= 20
            p.drawString(margin + 20, y, f"Duration: {med.duration}")
            p.drawString(margin + 150, y, f"Indication: {med.indication}")
            y -= (0.5 * inch)
            
            # (Add a page break if 'y' gets too low)
            if y < 2*inch:
                p.showPage()
                y = height - 1*inch
        # --- END LOOP ---
        
        y = draw_wrapped_text(y, "Notes:", data['warning_comments'])
        y = draw_wrapped_text(y, "Follow-up:", data['follow_up'])
        
        date_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        p.setFont("Helvetica", 10)
        p.drawString(margin, 1*inch, f"Generated on: {date_str}")
        p.drawString(width - (margin + 2.5*inch), 1*inch, "Doctor's Signature: ____________________")

        p.showPage()
        p.save()

        pdf_data = pdf_buffer.getvalue()
        pdf_buffer.close()

        # --- 4. Save the PDF to MedicalReport table ---
        report_name = f"Prescription-{patient_profile.unique_patient_id}-{datetime.date.today()}.pdf"
        
        MedicalReport.objects.create(
            patient=patient_profile,
            doctor=doctor_profile,
            report_name=report_name,
            file_data=pdf_data
        )

        return Response(
            {"message": "Prescription created and PDF saved successfully."}, 
            status=status.HTTP_201_CREATED
        )
    
class PatientReportListView(APIView):
    permission_classes = [IsAuthenticated, IsDoctor] # Only doctors

    def get(self, request, patient_unique_id, *args, **kwargs):
        try:
            # Find the patient by their unique ID
            patient = PatientProfile.objects.get(unique_patient_id=patient_unique_id)
            
            # Get all reports for that patient, ordered by newest first
            reports = MedicalReport.objects.filter(patient=patient).order_by('-created_at')
            
            # Serialize the list of reports
            serializer = MedicalReportSerializer(reports, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except PatientProfile.DoesNotExist:
            return Response({"error": "Patient not found."}, status=status.HTTP_404_NOT_FOUND)

# --- API for PATIENT to get their own reports ---
class MyReportListView(APIView):
    permission_classes = [IsAuthenticated] # Any logged-in user

    def get(self, request, *args, **kwargs):
        try:
            # Find the patient profile linked to the currently logged-in user
            patient = PatientProfile.objects.get(user=request.user)
            
            # Get all reports for that patient
            reports = MedicalReport.objects.filter(patient=patient).order_by('-created_at')
            
            # Serialize the list
            serializer = MedicalReportSerializer(reports, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except PatientProfile.DoesNotExist:
            # This will fire if a doctor tries to use this endpoint
            return Response({"error": "Patient profile not found for this user."}, status=status.HTTP_404_NOT_FOUND)
        
class DownloadReportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, report_id, *args, **kwargs):
        try:
            # 1. Find the report by its ID
            report = MedicalReport.objects.get(id=report_id)
        except MedicalReport.DoesNotExist:
            return Response({"error": "Report not found."}, status=status.HTTP_404_NOT_FOUND)

        # 2. Security Check: Is the user allowed to see this?
        # We check if the user is the patient on the report OR the doctor on the report.
        
        is_patient = hasattr(request.user, 'patient_profile') and request.user.patient_profile == report.patient
        is_doctor = hasattr(request.user, 'doctor_profile') and request.user.doctor_profile == report.doctor

        if not (is_patient or is_doctor):
            return Response(
                {"error": "You do not have permission to access this report."}, 
                status=status.HTTP_403_FORBIDDEN
            )

        # 3. Return the file
        # We use HttpResponse instead of Response
        response = HttpResponse(report.file_data, content_type='application/pdf')
        
        # This tells the browser to download the file with its original name
        response['Content-Disposition'] = f'attachment; filename="{report.report_name}"'
        
        return response