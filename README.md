README FILE

# Medispeak

Medical Records, Demystified.

Your health. Your data. Your language.

Medispeak is a secure, intelligent portal designed to break down the language barrier in healthcare. It provides a simple, smart, and secure platform for both healthcare providers and patients to manage and understand complex medical data.

* *For Patients:* The Patient Portal is a personal health dashboard. You can see all your reports, but with one key difference: the "Chat With Your Report" feature. Using a powerful AI pipeline, we instantly translate any complex PDF report (past or new) into simple, easy-to-understand layman's terms. No more guessing. Just clear answers.
* *For Doctors:* The Doctor Portal is a force multiplier. Instead of searching for a needle in a haystack, doctors can search for a patient by their unique ID and see their entire relevant history in one place. They can generate new, multi-medication prescriptions that are instantly saved as structured data and as a PDF, which is then available to the patient.

---

## ✨ Features

* *Role-Based Authentication:* Secure, separate workflows for Patients and Doctors using JWT.
* *Self-Service Registration:* No admin needed. Doctors and Patients can register themselves from dedicated, role-specific pages.
* *Dynamic Profile Creation:* Users fill out their own profile information after their first login.
* *Doctor Dashboard:* Securely search for patients by their Unique Patient ID.
* *Patient Dashboard:* View and manage personal details, and see your unique, shareable Patient ID.
* *PDF Prescription Generation:* Doctors can fill out a multi-meditation form, which the backend saves to the database and generates as a legal PDF file using reportlab.
* *Binary File Storage:* All generated PDFs are stored directly in the SQLite database (BYTEA/BLOB) for security and integrity.
* *Report Management:* Both doctors and patients can view a list of all past reports and download them on-demand.
* *AI Chatbot Integration:*
    * Drag-and-drop any PDF (or an existing past report) into the chat window.
    * Select from pre-defined prompts ("Summarize this," "What is my diagnosis?").
    * The frontend sends the PDF and the prompt to an external ML pipeline to get a real-time, simple-language summary.

---

## 🚀 Technology Stack

* *Frontend:*
    * React.js
    * Tailwind CSS
    * React Router
    * Axios
* *Backend:*
    * Python 3
    * Django & Django Rest Framework
    * SQLite3 (for hackathon speed!)
    * djangorestframework-simplejwt (for JWT)
    * reportlab (for PDF generation)
    * django-cors-headers

---

## 🏁 Getting Started

Follow these instructions to get the project running locally on your Windows machine.

### Prerequisites

* Python
* Node.js (which includes npm)

### 1. Backend Setup (Django)

First, let's get the server running.

PowerShell
# 1. Go into the backend folder
cd backend

# 2. Create and activate a Python virtual environment
python -m venv venv
.\venv\Scripts\activate

# 3. Install all required packages
pip install django djangorestframework djangorestframework-simplejwt django-cors-headers reportlab

# 4. Create the database
# (This will create a new db.sqlite3 file based on our models)
python manage.py makemigrations users
python manage.py migrate

# 5. Run the server!
python manage.py runserver

# Your backend is now running at http://127.0.0.1:8000

### 2. Frontend Setup (React)
PowerShell
# 1. Go into the frontend folder
cd frontend

# 2. Install all node modules
npm install

# 3. Install Tailwind CSS
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
# (Make sure your tailwind.config.js and index.css are configured)

# 4. Run the app!
npm start

# Your frontend is now running at http://localhost:3000 and is connected to your backend.

## 💡 How to Use the App

The admin panel is not required for any part of this workflow.

1.  *Doctor Registration:*
    * Go to http://localhost:3000.
    * Click "Doctor Sign Up" (or go to /register/doctor).
    * Fill out the form (Full Name, Hospital Name, etc.).
2.  *Patient Registration:*
    * Go to http://localhost:3000.
    * Click "Patient Sign Up" (or go to /register/patient).
    * Fill out the form (Full Name, Username, etc.).
3.  *Patient Flow (First Time):*
    * Log in as the new patient.
    * You will be shown the "Complete Your Profile" form.
    * Fill it out and click "Save Profile."
    * You will now see your full dashboard, including your Unique Patient ID (e.g., PAT-000002). Note this down.
4.  *Doctor Flow:*
    * Log in as the doctor.
    * You will see the patient search dashboard.
    * Enter the patient's ID (PAT-000002).
    * The patient's profile and (empty) report list will appear.
    * Click "Generate New Prescription."
    * Fill out the multi-medication form and click "Save."
5.  *Patient Flow (Second Time):*
    * Log out as the doctor and log back in as the patient.
    * You will now see the new PDF prescription in your "Past Reports" list.
6.  *AI Chatbot Flow:*
    * Drag the new prescription from the "Past Reports" list and drop it into the "Chat With Your Report" box.
    * Click one of the prompts (e.g., "Summarize this...").
    * The app will send the PDF to the NGROK endpoint and display the AI-generated summary in the chat window.

## ⚙ API Endpoints

All endpoints are prefixed with /api/.

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| POST | /register/patient/ | Creates a new patient user and profile. |
| POST | /register/doctor/ | Creates a new doctor user and profile. |
| POST | /token/ | Login. Returns JWT access/refresh tokens. |
| GET | /my-profile/ | Patient: Gets their own profile. (Returns 404 if incomplete). |
| POST | /my-profile/ | Patient: Creates/updates their profile details. |
| GET | /my-doctor-profile/ | Doctor: Gets their own profile. |
| GET | /search-patient/ | Doctor: Searches for a patient by ?unique_id=.... |
| POST | /create-prescription/ | Doctor: Creates a new prescription (and PDF). |
| GET | /my-reports/ | Patient: Gets a list of their own reports. |
| GET | /patient-reports/<id>/ | Doctor: Gets a list of a patient's reports. |
| GET | /download-report/<id>/ | Downloads the raw PDF file for a specific report. |
| POST | [NGROK_URL] | (External) Sends a PDF and prompt to the ML pipeline. |
