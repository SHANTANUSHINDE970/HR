import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import pandas as pd
import json
import time
import secrets
import string
import os
import traceback
import ssl
from email.utils import formataddr
import socket
import uuid
import hashlib
import io
import mimetypes

try:
    from google.oauth2.service_account import Credentials as GoogleAuthCredentials
    from googleapiclient.discovery import build as build_drive_service
    from googleapiclient.http import MediaIoBaseUpload
    DRIVE_UPLOAD_LIBS_AVAILABLE = True
except ImportError:
    DRIVE_UPLOAD_LIBS_AVAILABLE = False

# Page configuration
st.set_page_config(
    page_title="VOLAR FASHION - Leave Management",
    page_icon="\u2728",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Beautiful Elegant CSS with Premium Design - DARK MODE COMPATIBLE
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Playfair+Display:wght@400;500;600&display=swap');

    :root {
        --primary-color: #673ab7;
        --secondary-color: #9c27b0;
        --accent-color: #2196f3;
        --success-color: #28a745;
        --warning-color: #ff9800;
        --danger-color: #dc3545;
        --text-primary: #1a1a1a;
        --text-secondary: #4a5568;
        --text-light: #718096;
        --bg-primary: #ffffff;
        --bg-secondary: #f8f9ff;
        --bg-tertiary: #f5f7fa;
        --border-color: #e2e8f0;
        --card-bg: #ffffff;
        --input-bg: #fafbfc;
        --shadow-color: rgba(103, 58, 183, 0.08);
    }

    @media (prefers-color-scheme: dark) {
        :root {
            --primary-color: #9c6bff;
            --secondary-color: #d179ff;
            --accent-color: #64b5f6;
            --success-color: #4caf50;
            --warning-color: #ffb74d;
            --danger-color: #f44336;
            --text-primary: #ffffff;
            --text-secondary: #cbd5e0;
            --text-light: #a0aec0;
            --bg-primary: #1a202c;
            --bg-secondary: #2d3748;
            --bg-tertiary: #4a5568;
            --border-color: #4a5568;
            --card-bg: #2d3748;
            --input-bg: #4a5568;
            --shadow-color: rgba(0, 0, 0, 0.3);
        }
    }

    @media (prefers-color-scheme: dark) {
        .stApp { background-color: var(--bg-primary) !important; }
        .main { background-color: var(--bg-primary) !important; }
        .stTextInput input,
        .stSelectbox select,
        .stTextArea textarea,
        .stDateInput input,
        .stNumberInput input {
            color: var(--text-primary) !important;
            background-color: var(--input-bg) !important;
            border-color: var(--border-color) !important;
        }
        .stTextInput label,
        .stSelectbox label,
        .stTextArea label,
        .stDateInput label,
        .stNumberInput label { color: var(--text-secondary) !important; }
        .stTextInput input::placeholder,
        .stSelectbox select::placeholder,
        .stTextArea textarea::placeholder,
        .stDateInput input::placeholder {
            color: var(--text-light) !important;
            opacity: 0.7;
        }
    }

    * { font-family: 'Inter', sans-serif; color: var(--text-primary); }

    .main {
        background: linear-gradient(135deg, var(--bg-secondary) 0%, var(--bg-tertiary) 100%);
        min-height: 100vh;
    }

    .stApp {
        background: linear-gradient(135deg, var(--bg-secondary) 0%, var(--bg-tertiary) 100%);
        background-attachment: fixed;
    }

    .form-container {
        background: var(--card-bg);
        padding: 3.5rem;
        border-radius: 24px;
        box-shadow: 0 20px 60px var(--shadow-color);
        margin: 2rem auto;
        max-width: 1000px;
        border: 1px solid rgba(103, 58, 183, 0.1);
        position: relative;
        overflow: hidden;
    }

    .form-container:before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 4px;
        background: linear-gradient(90deg, var(--primary-color), var(--secondary-color), var(--accent-color));
    }

    h1 {
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--accent-color) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        font-size: 3.2rem;
        margin-bottom: 0.5rem;
        font-weight: 700;
        font-family: 'Playfair Display', serif;
        letter-spacing: -0.5px;
    }

    h2 {
        color: var(--text-light);
        text-align: center;
        font-size: 1.6rem;
        margin-bottom: 3rem;
        font-weight: 400;
        font-family: 'Inter', sans-serif;
        opacity: 0.9;
    }

    h3 {
        color: var(--text-secondary);
        font-size: 1.4rem;
        margin-top: 2.5rem;
        margin-bottom: 1.5rem;
        font-weight: 600;
        position: relative;
        padding-bottom: 10px;
    }

    h3:after {
        content: '';
        position: absolute;
        bottom: 0; left: 0;
        width: 60px; height: 3px;
        background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
        border-radius: 2px;
    }

    .stButton>button {
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
        color: white;
        border: none;
        padding: 1rem 3rem;
        font-size: 1.1rem;
        border-radius: 12px;
        font-weight: 600;
        width: 100%;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 8px 25px rgba(103, 58, 183, 0.25);
        cursor: pointer;
        position: relative;
        overflow: hidden;
    }

    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 35px rgba(103, 58, 183, 0.35);
    }

    .stTextInput>div>div>input {
        color: var(--text-primary) !important;
        background-color: var(--input-bg) !important;
        border: 2px solid var(--border-color) !important;
        border-radius: 12px;
        padding: 0.875rem 1rem !important;
        font-size: 1rem;
        transition: all 0.3s ease;
    }

    .stSelectbox>div>div>select {
        color: var(--text-primary) !important;
        background-color: var(--input-bg) !important;
        border: 2px solid var(--border-color) !important;
        border-radius: 12px;
        padding: 0.875rem 1rem !important;
        font-size: 1rem;
    }

    .stTextArea>div>div>textarea {
        color: var(--text-primary) !important;
        background-color: var(--input-bg) !important;
        border: 2px solid var(--border-color) !important;
        border-radius: 12px;
        padding: 0.875rem 1rem !important;
        font-size: 1rem;
    }

    .stDateInput>div>div>input {
        color: var(--text-primary) !important;
        background-color: var(--input-bg) !important;
        border: 2px solid var(--border-color) !important;
        border-radius: 12px;
        padding: 0.875rem 1rem !important;
        font-size: 1rem;
    }

    .stTextInput>div>div>input:focus,
    .stSelectbox>div>div>select:focus,
    .stTextArea>div>div>textarea:focus,
    .stDateInput>div>div>input:focus {
        border-color: var(--primary-color) !important;
        box-shadow: 0 0 0 4px rgba(103, 58, 183, 0.1) !important;
        background: var(--card-bg) !important;
        outline: none !important;
    }

    .stTextInput>div>label,
    .stSelectbox>div>label,
    .stTextArea>div>label,
    .stDateInput>div>label {
        color: var(--text-secondary) !important;
        font-weight: 600 !important;
    }

    p, span, div, li { color: var(--text-primary); }

    .success-message {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        border-left: 4px solid var(--success-color);
        color: #155724;
        padding: 1.75rem;
        border-radius: 16px;
        text-align: center;
        font-weight: 500;
        margin: 2rem 0;
        box-shadow: 0 10px 30px rgba(40, 167, 69, 0.1);
        animation: slideIn 0.5s ease-out;
    }

    @keyframes slideIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .error-message {
        background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
        border-left: 4px solid var(--danger-color);
        color: #721c24;
        padding: 1.75rem;
        border-radius: 16px;
        text-align: center;
        font-weight: 500;
        margin: 2rem 0;
        box-shadow: 0 10px 30px rgba(220, 53, 69, 0.1);
    }

    .info-box {
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
        border-left: 4px solid var(--accent-color);
        color: #0d47a1;
        padding: 1.75rem;
        border-radius: 16px;
        margin: 2rem 0;
        box-shadow: 0 10px 30px rgba(33, 150, 243, 0.1);
    }

    .thumbsup-box {
        background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
        border-left: 4px solid #4caf50;
        color: #2e7d32;
        padding: 1.75rem;
        border-radius: 16px;
        margin: 2rem 0;
        box-shadow: 0 10px 30px rgba(76, 175, 80, 0.1);
        text-align: center;
    }

    .metric-card {
        background: linear-gradient(135deg, #f3e5f5 0%, #e1bee7 100%);
        padding: 1.5rem;
        border-radius: 16px;
        text-align: center;
        box-shadow: 0 8px 20px rgba(156, 39, 176, 0.1);
        border: 1px solid rgba(156, 39, 176, 0.1);
    }

    .approval-card {
        background: var(--card-bg);
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.05);
        margin: 1rem 0;
        border: 1px solid var(--border-color);
    }

    .status-pending {
        background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
        color: #856404;
        padding: 0.5rem 1.25rem;
        border-radius: 20px;
        font-size: 0.875rem;
        font-weight: 600;
        border: 1px solid rgba(255, 193, 7, 0.3);
    }

    .status-approved {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        color: #155724;
        padding: 0.5rem 1.25rem;
        border-radius: 20px;
        font-size: 0.875rem;
        font-weight: 600;
        border: 1px solid rgba(40, 167, 69, 0.3);
    }

    .status-rejected {
        background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
        color: #721c24;
        padding: 0.5rem 1.25rem;
        border-radius: 20px;
        font-size: 0.875rem;
        font-weight: 600;
        border: 1px solid rgba(220, 53, 69, 0.3);
    }

    label {
        font-weight: 600 !important;
        color: var(--text-secondary) !important;
        font-size: 0.95rem !important;
        margin-bottom: 0.5rem !important;
        display: block;
    }

    .footer {
        text-align: center;
        color: var(--text-light);
        padding: 3rem 2rem;
        margin-top: 4rem;
        position: relative;
    }

    .footer:before {
        content: '';
        position: absolute;
        top: 0; left: 50%;
        transform: translateX(-50%);
        width: 200px; height: 2px;
        background: linear-gradient(90deg, transparent, var(--primary-color), transparent);
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        background: var(--card-bg);
        padding: 12px;
        border-radius: 16px;
        border: 1px solid rgba(103, 58, 183, 0.1);
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }

    .stTabs [data-baseweb="tab"] {
        background: var(--card-bg);
        border-radius: 12px;
        color: var(--text-light);
        font-weight: 500;
        padding: 12px 28px;
        border: 1px solid var(--border-color);
        transition: all 0.3s ease;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
        color: white;
        border-color: var(--primary-color);
        box-shadow: 0 4px 12px rgba(103, 58, 183, 0.2);
    }

    .company-header {
        text-align: center;
        margin-bottom: 3rem;
        padding: 2rem;
        background: var(--card-bg);
        border-radius: 24px;
        box-shadow: 0 15px 40px rgba(103, 58, 183, 0.08);
        border: 1px solid rgba(103, 58, 183, 0.1);
        position: relative;
        overflow: hidden;
    }

    .company-header:before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 4px;
        background: linear-gradient(90deg, var(--primary-color), var(--secondary-color), var(--accent-color));
    }

    .icon-badge {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 40px; height: 40px;
        border-radius: 12px;
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
        color: white;
        margin-right: 12px;
        font-size: 1.2rem;
    }

    .section-header {
        display: flex;
        align-items: center;
        margin-bottom: 2rem;
        padding-bottom: 1rem;
        border-bottom: 2px solid var(--border-color);
    }

    .floating-element { animation: float 6s ease-in-out infinite; }

    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
    }

    ::-webkit-scrollbar { width: 8px; }
    ::-webkit-scrollbar-track { background: var(--bg-tertiary); border-radius: 4px; }
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
        border-radius: 4px;
    }

    .thumbsup-emoji {
        font-size: 3rem;
        animation: thumbsupAnimation 2s ease-in-out infinite;
    }

    @keyframes thumbsupAnimation {
        0%, 100% { transform: scale(1) rotate(0deg); }
        25% { transform: scale(1.1) rotate(-5deg); }
        50% { transform: scale(1.2) rotate(5deg); }
        75% { transform: scale(1.1) rotate(-5deg); }
    }

    .cluster-section {
        background: linear-gradient(135deg, #1e3a8a 0%, #1e40af 100%);
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1.5rem 0;
        border: 2px solid #3b82f6;
        box-shadow: 0 8px 25px rgba(59, 130, 246, 0.2);
    }

    .cluster-header h3 { color: #ffffff !important; margin: 0; }
    .cluster-header p { color: #dbeafe !important; margin: 5px 0 0 0; font-size: 0.95rem; }

    .holidays-table-wrapper {
        display: flex;
        justify-content: center;
        width: 100%;
        margin: 2rem 0;
    }

    .holidays-table-wrapper table {
        border-collapse: collapse;
        border: 1px solid var(--border-color);
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        max-width: 800px;
        background-color: var(--card-bg);
    }

    .holidays-table-wrapper th {
        background: linear-gradient(135deg, #673ab7 0%, #9c27b0 100%);
        color: white;
        font-weight: 600;
        padding: 1rem 1.5rem;
        text-align: left;
        font-size: 1rem;
    }

    .holidays-table-wrapper td {
        padding: 1rem 1.5rem;
        font-size: 0.95rem;
        border-bottom: 1px solid var(--border-color);
        color: var(--text-primary);
    }

    .holidays-table-wrapper tr:last-child td { border-bottom: none; }
    .holidays-table-wrapper tr:nth-child(even) { background-color: rgba(103, 58, 183, 0.05); }
    .holidays-table-wrapper tr:hover { background-color: rgba(103, 58, 183, 0.1); }

    .day-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.85rem;
        font-weight: 500;
    }
    .day-saturday { background: rgba(33, 150, 243, 0.1); color: #2196f3; border: 1px solid rgba(33, 150, 243, 0.2); }
    .day-sunday { background: rgba(244, 67, 54, 0.1); color: #f44336; border: 1px solid rgba(244, 67, 54, 0.2); }
    .day-weekday { background: rgba(76, 175, 80, 0.1); color: #4caf50; border: 1px solid rgba(76, 175, 80, 0.2); }

    .debug-log {
        background: var(--bg-tertiary);
        border: 1px solid var(--border-color);
        border-radius: 6px;
        padding: 10px;
        margin: 10px 0;
        font-family: 'Courier New', monospace;
        font-size: 12px;
        max-height: 200px;
        overflow-y: auto;
    }

    @media (prefers-color-scheme: dark) {
        section[data-testid="stSidebar"] { background-color: var(--bg-secondary) !important; }
        section[data-testid="stSidebar"] * { color: var(--text-primary) !important; }
    }
    </style>
""", unsafe_allow_html=True)

# ============================================================
# CONSTANTS
# ============================================================
SUPERIORS = {
    "Jaya Tahilramani": "hrvolarfashion@gmail.com",
    "Sandip Gawankar": "sandip@ragunited.com",
    "Tariq Patel": "dn1@vfemails.com",
    "Sarath Kumar": "Sarath@vfemails.com",
    "Rajeev Thakur": "Rajeev@vfemails.com",
    "Ayushi Jain": "ayushi@volarfashion.in",
    "Akshaya Shinde": "Akshaya@vfemails.com",
    "Vitika Mehta": "vitika@vfemails.com",
    "Mohammed Tahir": "tahir@vfemails.com",
    "Hr": "hrvolarfashion@gmail.com",
    "Krishna Yadav": "Krishna@vfemails.com",
    "Manish Gupta": "Manish@vfemails.com",
    "Shantanu Shinde": "s37@vfemails.com"
}

DEPARTMENTS = [
    "Accounts and Finance", "Administration", "Business Development", "Content",
    "E-Commerce", "Factory & Production", "Graphics", "Human Resources", "IT",
    "Social Media", "Bandra Store", "Support Staff", "Warehouse", "SEO"
]

# WFH approvals: requests are sent to Sandip + HR; HR approves via portal
WFH_APPROVAL_RECIPIENTS = {
    
    "HR": "hrvolarfashion@gmail.com"
}
HR_EMAIL = "hrvolarfashion@gmail.com"

# Google Drive folder ID where medical certificates / prescriptions are uploaded.
# Get this from the folder's URL: drive.google.com/drive/folders/THIS_PART
# (this must be the ID, not the folder's display name - see get_drive_folder_id() below)
# Leave as "" to instead read it from Streamlit secrets under [DRIVE] folder_id = "..."
DRIVE_FOLDER_ID = "1BtcoTsjXaZRwWBMSQjnLX4tF_bfECmSu"


HOLIDAYS_2026 = [
    {"date": "01-Jan", "day": "Thursday",  "holiday": "New Year"},
    {"date": "26-Jan", "day": "Monday",    "holiday": "Republic Day"},
    {"date": "03-Mar", "day": "Tuesday",   "holiday": "Holi"},
    {"date": "21-Mar", "day": "Saturday",  "holiday": "Ramzan Eid"},
    {"date": "01-May", "day": "Friday",    "holiday": "Maharashtra Day"},
    {"date": "15-Aug", "day": "Saturday",  "holiday": "Independence Day"},
    {"date": "14-Sep", "day": "Monday",    "holiday": "Ganesh Chaturthi"},
    {"date": "02-Oct", "day": "Friday",    "holiday": "Gandhi Jayanti"},
    {"date": "21-Oct", "day": "Wednesday", "holiday": "Vijaydashmi"},
    {"date": "08-Nov", "day": "Sunday",    "holiday": "Diwali"},
    {"date": "11-Nov", "day": "Wednesday", "holiday": "Bhai Dooj"},
    {"date": "25-Dec", "day": "Friday",    "holiday": "Christmas"}
]

# ============================================================
# SESSION STATE INITIALISATION
# ============================================================
if 'clusters' not in st.session_state:
    st.session_state.clusters = [{
        'cluster_number': 1, 'leave_type': 'Select Type',
        'from_date': datetime.now().date(), 'till_date': datetime.now().date(), 'approval_code': ''
    }]
if 'reset_form_tab1' not in st.session_state: st.session_state.reset_form_tab1 = False
if 'reset_form_tab2' not in st.session_state: st.session_state.reset_form_tab2 = False
if 'reset_form_tab4' not in st.session_state: st.session_state.reset_form_tab4 = False
if 'reset_form_tab5' not in st.session_state: st.session_state.reset_form_tab5 = False

if 'form_data_tab1' not in st.session_state:
    st.session_state.form_data_tab1 = {
        'employee_name': '', 'employee_code': '', 'employee_email': '',
        'department': 'Select Department', 'purpose': '',
        'superior_name': 'Select Manager', 'is_cluster': False
    }
if 'form_data_tab2' not in st.session_state:
    st.session_state.form_data_tab2 = {'approval_password': '', 'action': 'Select Decision'}

# Tab 4: WFH — no approval_from, now includes employee_email
if 'form_data_tab4' not in st.session_state:
    st.session_state.form_data_tab4 = {
        'employee_name': '', 'employee_code': '', 'employee_email': '',
        'request_type': 'Select Type',
        'start_date': datetime.now().date(), 'end_date': datetime.now().date(),
        'reason': ''
    }

# Tab 5: WFH Approval Portal (HR only)
if 'form_data_tab5' not in st.session_state:
    st.session_state.form_data_tab5 = {'wfh_approval_password': '', 'wfh_action': 'Select Decision'}

if 'cluster_codes' not in st.session_state: st.session_state.cluster_codes = {}
if 'show_copy_section' not in st.session_state: st.session_state.show_copy_section = False
if 'test_email_result' not in st.session_state: st.session_state.test_email_result = None
if 'email_config_status' not in st.session_state: st.session_state.email_config_status = "Not Tested"
if 'debug_logs' not in st.session_state: st.session_state.debug_logs = []
if 'generated_codes' not in st.session_state: st.session_state.generated_codes = set()
if 'generated_wfh_codes' not in st.session_state: st.session_state.generated_wfh_codes = set()
if 'submission_in_progress' not in st.session_state: st.session_state.submission_in_progress = False
if 'submission_completed' not in st.session_state: st.session_state.submission_completed = False
if 'last_submission_hash' not in st.session_state: st.session_state.last_submission_hash = None
if 'submission_timestamp' not in st.session_state: st.session_state.submission_timestamp = None
if 'last_wfh_submission_hash' not in st.session_state: st.session_state.last_wfh_submission_hash = None
if 'wfh_submission_timestamp' not in st.session_state: st.session_state.wfh_submission_timestamp = None
if 'leave_file_uploader_key' not in st.session_state: st.session_state.leave_file_uploader_key = 0
if 'wfh_file_uploader_key' not in st.session_state: st.session_state.wfh_file_uploader_key = 0


# ============================================================
# UTILITY / LOGGING
# ============================================================
def add_debug_log(message, level="INFO"):
    timestamp = datetime.now().strftime('%H:%M:%S')
    log_entry = f"[{timestamp}] [{level}] {message}"
    st.session_state.debug_logs.append(log_entry)
    if len(st.session_state.debug_logs) > 50:
        st.session_state.debug_logs.pop(0)
    print(f"[{level}] {message}")


def log_debug(message):
    add_debug_log(message, "DEBUG")
    st.sidebar.text(f"{datetime.now().strftime('%H:%M:%S')}: {message}")


# ============================================================
# GOOGLE CREDENTIALS
# ============================================================
def get_google_credentials():
    try:
        log_debug("Loading Google credentials from Streamlit secrets...")
        possible_keys = ["google_credentials", "google", "gcp_service_account", "gcp", "GOOGLE", "GCP"]
        secrets_key = None
        for k in possible_keys:
            if k in st.secrets:
                secrets_key = k
                log_debug(f"Found Google credentials section: [{secrets_key}]")
                break
        if secrets_key is None:
            available = list(st.secrets.keys()) if st.secrets else []
            log_debug(f"Google credentials section NOT found. Available keys: {available}")
            st.error(f"Google credentials not found. Available keys: {available}. Please add a section named one of: {possible_keys}")
            return None
        try:
            creds_dict = {
                "type": st.secrets[secrets_key]["type"],
                "project_id": st.secrets[secrets_key]["project_id"],
                "private_key_id": st.secrets[secrets_key]["private_key_id"],
                "private_key": st.secrets[secrets_key]["private_key"],
                "client_email": st.secrets[secrets_key]["client_email"],
                "client_id": st.secrets[secrets_key]["client_id"],
                "auth_uri": st.secrets[secrets_key]["auth_uri"],
                "token_uri": st.secrets[secrets_key]["token_uri"],
                "auth_provider_x509_cert_url": st.secrets[secrets_key]["auth_provider_x509_cert_url"],
                "client_x509_cert_url": st.secrets[secrets_key]["client_x509_cert_url"],
            }
        except KeyError as e:
            log_debug(f"Missing key in [{secrets_key}]: {str(e)}")
            st.error(f"Missing field in [{secrets_key}] section: {str(e)}")
            return None
        required_fields = ["type", "project_id", "private_key_id", "private_key", "client_email"]
        missing_fields = [f for f in required_fields if not creds_dict.get(f)]
        if missing_fields:
            log_debug(f"Missing Google credential fields: {missing_fields}")
            st.error(f"Missing Google credential fields: {', '.join(missing_fields)}")
            return None
        private_key = creds_dict.get("private_key", "")
        if private_key:
            if "-----BEGIN PRIVATE KEY-----" not in private_key:
                if "\\n" in private_key:
                    private_key = private_key.replace("\\n", "\n")
                elif "MII" in private_key[:100]:
                    private_key = f"-----BEGIN PRIVATE KEY-----\n{private_key}\n-----END PRIVATE KEY-----"
            if "\n" not in private_key and "\\n" in private_key:
                private_key = private_key.replace("\\n", "\n")
            creds_dict["private_key"] = private_key
            log_debug("Processed private key formatting")
        log_debug(f"Google credentials loaded successfully for: {creds_dict['client_email']}")
        return creds_dict
    except Exception as e:
        log_debug(f"Error getting Google credentials: {traceback.format_exc()}")
        st.error(f"Error loading Google credentials: {str(e)}")
        return None


# ============================================================
# GOOGLE SHEETS SETUP
# ============================================================
def setup_google_sheets():
    try:
        log_debug("Setting up Google Sheets connection...")
        SCOPES = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds_dict = get_google_credentials()
        if not creds_dict:
            st.error("No Google credentials found")
            return None
        if not creds_dict.get("private_key"):
            st.error("Google private key not found in credentials")
            return None
        try:
            creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, SCOPES)
            log_debug("Successfully created ServiceAccountCredentials")
        except Exception as cred_error:
            log_debug(f"Error creating credentials: {str(cred_error)}")
            raise cred_error
        client = gspread.authorize(creds)
        SHEET_NAME = "Leave_Applications"
        try:
            spreadsheet = client.open(SHEET_NAME)
            sheet = spreadsheet.sheet1
            log_debug(f"Successfully connected to sheet: {SHEET_NAME}")
            try:
                if sheet.row_count == 0 or not sheet.row_values(1):
                    headers = [
                        "Submission Date", "Employee Code", "Employee Name", "Department",
                        "Type of Leave", "No of Days", "Purpose of Leave", "From Date",
                        "To Date", "Superior or Team leader Name", "Superior or Team leader Email",
                        "Status", "Approval Date", "Approval Password", "Cluster (Yes/No)",
                        "Cluster leave Number", "Employee email"
                    ]
                    sheet.append_row(headers)
                    log_debug("Added headers to sheet")
            except Exception as e:
                log_debug(f"Warning: Could not check/add headers: {str(e)}")
            return sheet
        except gspread.SpreadsheetNotFound:
            st.error(f"Google Sheet '{SHEET_NAME}' not found!")
            st.info(f"Please create a sheet named '{SHEET_NAME}' and share it with: {creds_dict.get('client_email', 'service account email')}")
            return None
        except Exception as e:
            st.error(f"Error accessing sheet: {str(e)}")
            return None
    except Exception as e:
        st.error(f"Error in setup_google_sheets: {str(e)}")
        log_debug(f"setup_google_sheets error: {traceback.format_exc()}")
        return None


def setup_wfh_sheet():
    """
    Connects to Sheet2 in Leave_Applications.

    Sheet2 columns (updated):
      1  Submission Date
      2  Employee Name
      3  Employee Code
      4  Employee Email
      5  Request Type
      6  Start Date
      7  End Date
      8  Reason
      9  Status
      10 Approval Date
      11 Approval Code
    """
    try:
        log_debug("Setting up WFH Google Sheets connection...")
        SCOPES = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds_dict = get_google_credentials()
        if not creds_dict:
            log_debug("No Google credentials found")
            return None
        if not creds_dict.get("private_key"):
            log_debug("Google private key not found in credentials")
            return None
        try:
            creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, SCOPES)
            log_debug("Successfully created ServiceAccountCredentials for WFH")
        except Exception as cred_error:
            log_debug(f"Error creating credentials for WFH: {str(cred_error)}")
            raise cred_error
        client = gspread.authorize(creds)
        SHEET_NAME = "Leave_Applications"
        try:
            spreadsheet = client.open(SHEET_NAME)
            try:
                sheet = spreadsheet.worksheet("Sheet2")
                log_debug(f"Successfully connected to Sheet2 in: {SHEET_NAME}")
            except gspread.exceptions.WorksheetNotFound:
                log_debug("Sheet2 not found, creating new sheet...")
                sheet = spreadsheet.add_worksheet(title="Sheet2", rows=100, cols=20)
                log_debug("Created Sheet2 successfully")
            try:
                if sheet.row_count == 0 or not sheet.row_values(1):
                    headers = [
                        "Submission Date", "Employee Name", "Employee Code", "Employee Email",
                        "Request Type", "Start Date", "End Date", "Reason",
                        "Status", "Approval Date", "Approval Code"
                    ]
                    sheet.append_row(headers)
                    log_debug("Added headers to WFH sheet (Sheet2)")
            except Exception as e:
                log_debug(f"Warning: Could not check/add headers to WFH sheet: {str(e)}")
            return sheet
        except gspread.SpreadsheetNotFound:
            log_debug(f"Google Sheet '{SHEET_NAME}' not found!")
            st.error(f"Google Sheet '{SHEET_NAME}' not found!")
            return None
        except Exception as e:
            log_debug(f"Error accessing WFH sheet: {str(e)}")
            st.error(f"Error accessing WFH sheet: {str(e)}")
            return None
    except Exception as e:
        log_debug(f"setup_wfh_sheet error: {traceback.format_exc()}")
        st.error(f"Error in setup_wfh_sheet: {str(e)}")
        return None


# ============================================================
# GOOGLE DRIVE FILE UPLOAD (Medical Certificate / Prescription)
# ============================================================
def get_drive_folder_id():
    """Reads the target Google Drive folder ID - checks the DRIVE_FOLDER_ID constant
    above first, then falls back to Streamlit secrets."""
    if DRIVE_FOLDER_ID:
        return DRIVE_FOLDER_ID.strip()
    try:
        possible_sections = ["DRIVE", "drive", "GDRIVE", "gdrive"]
        possible_keys = ["folder_id", "FOLDER_ID", "drive_folder_id"]
        for section in possible_sections:
            if section in st.secrets:
                sec = st.secrets[section]
                for k in possible_keys:
                    try:
                        val = sec[k]
                        if val:
                            return str(val).strip()
                    except (KeyError, TypeError):
                        continue
        # Fallback: direct top-level key
        for k in ["DRIVE_FOLDER_ID", "drive_folder_id"]:
            try:
                val = st.secrets[k]
                if val:
                    return str(val).strip()
            except (KeyError, TypeError):
                continue
        return ""
    except Exception as e:
        log_debug(f"Error reading Drive folder ID: {str(e)}")
        return ""


def get_drive_service():
    """Builds an authenticated Google Drive v3 service using the same service account as Sheets."""
    if not DRIVE_UPLOAD_LIBS_AVAILABLE:
        log_debug("google-api-python-client / google-auth not installed; cannot upload to Drive")
        return None
    try:
        creds_dict = get_google_credentials()
        if not creds_dict:
            return None
        drive_scopes = ['https://www.googleapis.com/auth/drive']
        creds = GoogleAuthCredentials.from_service_account_info(creds_dict, scopes=drive_scopes)
        service = build_drive_service('drive', 'v3', credentials=creds, cache_discovery=False)
        return service
    except Exception as e:
        log_debug(f"Error building Google Drive service: {traceback.format_exc()}")
        return None


def generate_attachment_filename(employee_name, day_count, start_date):
    """
    Builds the attachment filename as Employee_DayCount_StartDate
    e.g. Shantanu_15_14-08-2026
    (original file extension is appended separately by upload_file_to_drive)
    """
    safe_name = "".join(ch for ch in str(employee_name).strip() if ch.isalnum())
    if not safe_name:
        safe_name = "Employee"
    start_str = start_date.strftime("%d-%m-%Y")
    return f"{safe_name}_{day_count}_{start_str}"


def upload_file_to_drive(uploaded_file, new_filename):
    """
    Uploads a Streamlit UploadedFile object to the configured Google Drive folder,
    saving it under new_filename (original extension preserved).
    Returns (success: bool, result: str) — result is a webViewLink on success,
    or an error message on failure.
    """
    try:
        if uploaded_file is None:
            return True, ""
        folder_id = get_drive_folder_id()
        if not folder_id:
            log_debug("Drive folder ID not configured in secrets; skipping upload")
            return False, "Drive folder not configured. Add [DRIVE] folder_id to Streamlit secrets."
        service = get_drive_service()
        if not service:
            return False, "Could not authenticate with Google Drive"

        original_name = uploaded_file.name or ""
        ext = ""
        if "." in original_name:
            ext = "." + original_name.rsplit(".", 1)[-1].lower()
        final_filename = f"{new_filename}{ext}"

        mime_type = uploaded_file.type or mimetypes.guess_type(original_name)[0] or "application/octet-stream"
        file_bytes = uploaded_file.getvalue()

        file_metadata = {"name": final_filename, "parents": [folder_id]}
        media = MediaIoBaseUpload(io.BytesIO(file_bytes), mimetype=mime_type, resumable=False)
        created = service.files().create(
            body=file_metadata, media_body=media, fields="id, webViewLink"
        ).execute()
        log_debug(f"Uploaded attachment to Drive: {final_filename} (ID: {created.get('id')})")
        return True, created.get("webViewLink", "")
    except Exception as e:
        log_debug(f"Error uploading file to Drive: {traceback.format_exc()}")
        return False, str(e)


# ============================================================
# EMAIL CREDENTIALS
# ============================================================
def get_email_credentials():
    try:
        log_debug("Getting email credentials from secrets...")
        sender_email = None
        sender_password = None
        source = ""
        email_sections = ['EMAIL', 'email', 'gmail', 'GMAIL', 'SMTP', 'smtp']
        email_keys = ['sender_email', 'email', 'EMAIL', 'user', 'USER', 'username', 'USERNAME']
        password_keys = ['sender_password', 'password', 'PASSWORD', 'app_password', 'APP_PASSWORD', 'pass', 'PASS']
        for section in email_sections:
            if section in st.secrets:
                log_debug(f"Found email section: [{section}]")
                sec = st.secrets[section]
                for ek in email_keys:
                    try:
                        val = sec[ek]
                        if val and "@" in str(val):
                            sender_email = str(val).strip()
                            break
                    except (KeyError, TypeError):
                        continue
                for pk in password_keys:
                    try:
                        val = sec[pk]
                        if val:
                            sender_password = str(val).strip()
                            break
                    except (KeyError, TypeError):
                        continue
                if sender_email and sender_password:
                    source = f"[{section}]"
                    break
        if not sender_email or not sender_password:
            direct_email_keys = ['EMAIL_SENDER', 'sender_email', 'email', 'EMAIL', 'GMAIL_USER', 'SMTP_USER']
            direct_pass_keys = ['EMAIL_PASSWORD', 'sender_password', 'password', 'PASSWORD', 'GMAIL_PASSWORD', 'SMTP_PASSWORD', 'APP_PASSWORD']
            for ek in direct_email_keys:
                try:
                    val = st.secrets[ek]
                    if val and "@" in str(val):
                        sender_email = str(val).strip()
                        break
                except (KeyError, TypeError):
                    continue
            for pk in direct_pass_keys:
                try:
                    val = st.secrets[pk]
                    if val:
                        sender_password = str(val).strip()
                        break
                except (KeyError, TypeError):
                    continue
            if sender_email and sender_password:
                source = "Direct top-level keys"
        if sender_email and sender_password:
            clean_password = sender_password.replace(" ", "")
            if len(clean_password) == 16 and len(sender_password) != 16:
                sender_password = clean_password
            log_debug(f"Email credentials loaded. Email={sender_email}, PasswordLen={len(sender_password)}, Source={source}")
            return sender_email, sender_password, source
        else:
            available = list(st.secrets.keys()) if st.secrets else []
            log_debug(f"Email credentials NOT found. Available keys: {available}")
            return "", "", f"Not Found (available keys: {available})"
    except Exception as e:
        log_debug(f"Error getting email credentials: {traceback.format_exc()}")
        return "", "", f"Error: {str(e)}"


def check_email_configuration():
    sender_email, sender_password, source = get_email_credentials()
    if not sender_email or not sender_password:
        return {"configured": False, "message": "Email credentials not found",
                "details": f"Source info: {source}. Please add [EMAIL] section with sender_email and sender_password.",
                "source": source}
    if "@" not in sender_email or "." not in sender_email:
        return {"configured": False, "message": "Invalid email format",
                "details": f"Email '{sender_email}' doesn't look valid", "source": source}
    if len(sender_password) == 16 and ' ' not in sender_password:
        password_type = "App Password (16 chars)"
    elif len(sender_password) > 0:
        password_type = f"Password ({len(sender_password)} chars)"
    else:
        password_type = "Unknown"
    return {"configured": True, "sender_email": sender_email, "source": source,
            "password_type": password_type, "password_length": len(sender_password),
            "message": f"Email credentials found ({password_type})",
            "details": f"Loaded from: {source}"}


# ============================================================
# SMTP CONNECTION
# ============================================================
def create_smtp_connection(sender_email, sender_password):
    server = None
    connection_method = ""
    error_messages = []
    try:
        log_debug("Trying SMTP_SSL on port 465...")
        context = ssl.create_default_context()
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=10, context=context)
        server.login(sender_email, sender_password)
        connection_method = "SMTP_SSL (Port 465)"
        log_debug(f"Connection successful via {connection_method}")
        return server, connection_method
    except Exception as e1:
        error_messages.append(f"Port 465 failed: {str(e1)}")
        log_debug(f"Port 465 failed: {str(e1)}")
        if server:
            try: server.quit()
            except: pass
    try:
        log_debug("Trying STARTTLS on port 587...")
        server = smtplib.SMTP('smtp.gmail.com', 587, timeout=10)
        server.ehlo()
        server.starttls(context=ssl.create_default_context())
        server.ehlo()
        server.login(sender_email, sender_password)
        connection_method = "STARTTLS (Port 587)"
        log_debug(f"Connection successful via {connection_method}")
        return server, connection_method
    except Exception as e2:
        error_messages.append(f"Port 587 failed: {str(e2)}")
        log_debug(f"Port 587 failed: {str(e2)}")
        if server:
            try: server.quit()
            except: pass
    for port in [25, 2525]:
        try:
            log_debug(f"Trying port {port}...")
            server = smtplib.SMTP('smtp.gmail.com', port, timeout=10)
            server.starttls(context=ssl.create_default_context())
            server.login(sender_email, sender_password)
            connection_method = f"Port {port}"
            return server, connection_method
        except Exception as e:
            error_messages.append(f"Port {port} failed: {str(e)}")
            if server:
                try: server.quit()
                except: pass
    return None, f"All methods failed: {' | '.join(error_messages)}"


def test_email_connection(test_recipient=None):
    try:
        log_debug("Starting email connection test...")
        sender_email, sender_password, source = get_email_credentials()
        if not sender_email or not sender_password:
            return {"success": False, "message": "Email credentials not configured",
                    "details": "Please check your Streamlit secrets",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        recipient = test_recipient or sender_email
        msg = MIMEMultipart()
        msg['From'] = formataddr(("VOLAR FASHION HR", sender_email))
        msg['To'] = recipient
        msg['Subject'] = "VOLAR FASHION - Email Configuration Test"
        test_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        body = f"""This is a test email from VOLAR FASHION Leave and WFH / Out of office request.

Test Details:
- Time: {test_time}
- Sender: {sender_email}
- Recipient: {recipient}
- Source: {source}

If you received this email, your email configuration is working correctly!

--
VOLAR FASHION HR Department
"""
        msg.attach(MIMEText(body, 'plain'))
        server, method = create_smtp_connection(sender_email, sender_password)
        if server:
            try:
                server.sendmail(sender_email, recipient, msg.as_string())
                server.quit()
                return {"success": True, "message": f"Email sent successfully via {method}",
                        "details": f"Test email sent to {recipient} at {test_time}",
                        "method": method, "sender": sender_email, "timestamp": test_time}
            except Exception as e:
                try: server.quit()
                except: pass
                return {"success": False, "message": "Failed to send email",
                        "details": f"Error: {str(e)}", "sender": sender_email, "timestamp": test_time}
        else:
            return {"success": False, "message": "SMTP Connection Failed",
                    "details": f"Error: {method}", "sender": sender_email, "timestamp": test_time}
    except Exception as e:
        log_debug(f"Unexpected error in test_email_connection: {traceback.format_exc()}")
        return {"success": False, "message": "Unexpected Error",
                "details": f"Error: {str(e)}",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}


# ============================================================
# APPROVAL CODE GENERATION (Sheet1 - Leave)
# ============================================================
def get_existing_codes_from_sheet(sheet):
    try:
        if not sheet:
            return set()
        all_records = sheet.get_all_values()
        existing_codes = set()
        for idx, row in enumerate(all_records):
            if idx == 0:
                continue
            if len(row) > 13 and row[13]:
                existing_codes.add(row[13])
        log_debug(f"Found {len(existing_codes)} existing leave codes in sheet")
        return existing_codes
    except Exception as e:
        log_debug(f"Error getting existing leave codes: {str(e)}")
        return set()


def generate_approval_password(sheet=None):
    alphabet = string.ascii_uppercase + string.digits
    alphabet = alphabet.replace('0', '').replace('O', '').replace('1', '').replace('I', '').replace('L', '')
    existing_codes = set()
    if sheet:
        existing_codes = get_existing_codes_from_sheet(sheet)
    existing_codes.update(st.session_state.generated_codes)
    max_attempts = 20
    for attempt in range(max_attempts):
        password = ''.join(secrets.choice(alphabet) for _ in range(5))
        if password not in existing_codes:
            st.session_state.generated_codes.add(password)
            log_debug(f"Generated unique leave approval password: {password} (attempt {attempt + 1})")
            return password
    log_debug(f"Could not generate unique random code after {max_attempts} attempts, using fallback")
    timestamp = int(time.time() * 1000)
    base36 = "23456789ABCDEFGHJKMNPQRSTUVWXYZ"
    code = ""
    temp_timestamp = timestamp
    while temp_timestamp > 0 and len(code) < 3:
        temp_timestamp, remainder = divmod(temp_timestamp, 36)
        code = base36[remainder] + code
    while len(code) < 5:
        code = code + secrets.choice(base36)
    if code not in existing_codes:
        st.session_state.generated_codes.add(code)
        return code
    for i in range(1, 100):
        fallback_code = f"{code[:4]}{i}"
        if fallback_code not in existing_codes:
            st.session_state.generated_codes.add(fallback_code)
            return fallback_code
    final_code = str(uuid.uuid4().int)[:5].upper()
    final_code = ''.join([c for c in final_code if c in alphabet])
    while len(final_code) < 5:
        final_code += secrets.choice(alphabet)
    st.session_state.generated_codes.add(final_code)
    return final_code


# ============================================================
# WFH APPROVAL CODE GENERATION (Sheet2)
# ============================================================
def get_existing_wfh_codes_from_sheet(sheet):
    """Read existing WFH approval codes from Sheet2 column 11 (index 10)."""
    try:
        if not sheet:
            return set()
        all_records = sheet.get_all_values()
        existing_codes = set()
        for idx, row in enumerate(all_records):
            if idx == 0:
                continue
            # Column 11 (0-indexed: 10) = Approval Code
            if len(row) > 10 and row[10]:
                existing_codes.add(row[10])
        log_debug(f"Found {len(existing_codes)} existing WFH codes in Sheet2")
        return existing_codes
    except Exception as e:
        log_debug(f"Error getting existing WFH codes: {str(e)}")
        return set()


def generate_wfh_approval_code(sheet=None):
    """Generate a unique 5-char code for WFH approval, checking Sheet2."""
    alphabet = string.ascii_uppercase + string.digits
    alphabet = alphabet.replace('0', '').replace('O', '').replace('1', '').replace('I', '').replace('L', '')
    existing_codes = set()
    if sheet:
        existing_codes = get_existing_wfh_codes_from_sheet(sheet)
    existing_codes.update(st.session_state.generated_wfh_codes)
    max_attempts = 20
    for attempt in range(max_attempts):
        code = ''.join(secrets.choice(alphabet) for _ in range(5))
        if code not in existing_codes:
            st.session_state.generated_wfh_codes.add(code)
            log_debug(f"Generated unique WFH approval code: {code} (attempt {attempt + 1})")
            return code
    # Fallback
    base36 = "23456789ABCDEFGHJKMNPQRSTUVWXYZ"
    timestamp = int(time.time() * 1000)
    code = ""
    temp = timestamp
    while temp > 0 and len(code) < 3:
        temp, r = divmod(temp, 36)
        code = base36[r] + code
    while len(code) < 5:
        code += secrets.choice(base36)
    if code not in existing_codes:
        st.session_state.generated_wfh_codes.add(code)
        return code
    for i in range(1, 100):
        fc = f"{code[:4]}{i}"
        if fc not in existing_codes:
            st.session_state.generated_wfh_codes.add(fc)
            return fc
    final = str(uuid.uuid4().int)[:5].upper()
    final = ''.join([c for c in final if c in alphabet])
    while len(final) < 5:
        final += secrets.choice(alphabet)
    st.session_state.generated_wfh_codes.add(final)
    return final


# ============================================================
# CALCULATIONS
# ============================================================
def calculate_working_days(from_date, till_date):
    return (till_date - from_date).days + 1


def calculate_days(from_date, till_date, leave_type):
    if leave_type == "Half Day":
        return 0.5
    elif leave_type == "Early Exit":
        return ""
    else:
        return calculate_working_days(from_date, till_date)


# ============================================================
# SHEET INSERT HELPERS
# ============================================================
def add_data_to_sheet1(sheet, row_data):
    try:
        all_records = sheet.get_all_values()
        next_row = 2
        found_empty_row = False
        if len(all_records) > 1:
            for i in range(1, len(all_records)):
                row = all_records[i]
                if not any(cell.strip() for cell in row):
                    next_row = i + 1
                    found_empty_row = True
                    break
            if not found_empty_row:
                next_row = len(all_records) + 1
        else:
            next_row = 2
        sheet.insert_row(row_data, index=next_row)
        log_debug(f"Sheet1 data inserted at row {next_row}")
        return True
    except Exception as e:
        log_debug(f"Error adding data to Sheet1: {str(e)}\n{traceback.format_exc()}")
        return False


def add_data_to_sheet2(sheet, row_data):
    try:
        all_records = sheet.get_all_values()
        next_row = 2
        found_empty_row = False
        if len(all_records) > 1:
            for i in range(1, len(all_records)):
                row = all_records[i]
                if not any(cell.strip() for cell in row):
                    next_row = i + 1
                    found_empty_row = True
                    break
            if not found_empty_row:
                next_row = len(all_records) + 1
        else:
            next_row = 2
        sheet.insert_row(row_data, index=next_row)
        log_debug(f"Sheet2 data inserted at row {next_row}")
        return True
    except Exception as e:
        log_debug(f"Error adding data to Sheet2: {str(e)}\n{traceback.format_exc()}")
        return False


# ============================================================
# LEAVE EMAILS
# ============================================================
def send_approval_email(employee_name, superior_name, superior_email, employee_email, clusters_data, cluster_codes):
    try:
        log_debug(f"Preparing to send leave approval email to {superior_email}")
        sender_email, sender_password, source = get_email_credentials()
        if not sender_email or not sender_password:
            st.warning("Email credentials not configured")
            return False
        if "@" not in superior_email or "." not in superior_email:
            st.warning(f"Invalid superior email format: {superior_email}")
            return False
        try:
            app_url = st.secrets.get("APP_URL", "https://9yq6u8fklhfba8uggnjr7h.streamlit.app/")
        except:
            app_url = "https://9yq6u8fklhfba8uggnjr7h.streamlit.app/"

        clusters_html = ""
        for i, cluster in enumerate(clusters_data):
            days = calculate_days(cluster['from_date'], cluster['till_date'], cluster['leave_type'])
            days_display = "N/A" if cluster['leave_type'] == "Early Exit" else (f"{days} days" if cluster['leave_type'] == "Full Day" else "0.5 day")
            clusters_html += f"""
            <div style="background: {'#f8f9ff' if i % 2 == 0 else '#f0f2ff'}; padding: 15px; border-radius: 8px; margin: 10px 0; border-left: 4px solid #4dabf7;">
                <h4 style="margin-top: 0; color: #339af0;">Period {i+1}</h4>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr><td style="padding: 5px; width: 40%;"><strong>Leave Type:</strong></td><td style="padding: 5px;">{cluster['leave_type']}</td></tr>
                    <tr><td style="padding: 5px;"><strong>From Date:</strong></td><td style="padding: 5px;">{cluster['from_date'].strftime('%Y-%m-%d')}</td></tr>
                    <tr><td style="padding: 5px;"><strong>Till Date:</strong></td><td style="padding: 5px;">{cluster['till_date'].strftime('%Y-%m-%d')}</td></tr>
                    <tr><td style="padding: 5px;"><strong>Duration:</strong></td><td style="padding: 5px;">{days_display}</td></tr>
                    <tr><td style="padding: 5px;"><strong>Approval Code:</strong></td>
                        <td style="padding: 5px;"><span style="background: #fff3cd; padding: 5px 10px; border-radius: 4px; font-family: 'Courier New', monospace; font-weight: bold; letter-spacing: 2px;">{cluster_codes.get(i, 'CODE MISSING')}</span></td>
                    </tr>
                </table>
            </div>
            """

        msg_superior = MIMEMultipart('alternative')
        msg_superior['From'] = formataddr(("VOLAR FASHION HR", sender_email))
        msg_superior['To'] = superior_email
        msg_superior['Subject'] = (f"CLUSTER LEAVE: {employee_name} - {len(clusters_data)} periods"
                                   if len(clusters_data) > 1 else f"Leave Approval Required: {employee_name}")

        html_body_superior = f"""
        <html><head><style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
        .container {{ max-width: 700px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #673ab7 0%, #9c27b0 100%); color: white; padding: 20px; border-radius: 10px; text-align: center; }}
        .info-box {{ background: #f8f9ff; padding: 20px; border-radius: 10px; margin: 20px 0; border: 1px solid #e2e8f0; }}
        .instructions {{ background: #e8f5e9; padding: 15px; border-radius: 8px; margin: 15px 0; border-left: 4px solid #4caf50; }}
        .footer {{ color: #666; font-size: 12px; margin-top: 30px; padding-top: 15px; border-top: 1px solid #eee; }}
        </style></head><body>
        <div class="container">
            <div class="header"><h2 style="margin: 0;">Leave Approval Required</h2><p style="margin: 5px 0 0 0; opacity: 0.9;">VOLAR FASHION HR System</p></div>
            <p>Dear {superior_name},</p>
            <div class="info-box">
                <h3 style="margin-top: 0; color: #673ab7;">Employee Information</h3>
                <p><strong>Employee Name:</strong> {employee_name}</p>
                <p><strong>Employee Email:</strong> {employee_email if employee_email else 'Not provided'}</p>
                <p><strong>Employee Code:</strong> {clusters_data[0].get('employee_code', 'N/A')}</p>
                <p><strong>Department:</strong> {clusters_data[0].get('department', 'N/A')}</p>
                <p><strong>Total Periods:</strong> {len(clusters_data)}</p>
                <p><strong>Purpose:</strong> {clusters_data[0].get('purpose', 'N/A')}</p>
            </div>
            <h3 style="color: #339af0;">Leave Periods Details</h3>
            {clusters_html}
            <div class="instructions">
                <h4 style="margin-top: 0; color: #2e7d32;">How to Approve/Reject:</h4>
                <ol>
                    <li>Visit: <a href="{app_url}">{app_url}</a></li>
                    <li>Click on "Approval Portal" tab</li>
                    <li>For each period: Enter the specific approval code</li>
                    <li>Select Approve or Reject for that period</li>
                    <li>Click Submit Decision</li>
                </ol>
                <p><strong>Note:</strong> Each code can only be used once.</p>
            </div>
            <div class="footer">VOLAR FASHION PVT LTD - HR Department<br>hrvolarfashion@gmail.com</div>
        </div></body></html>
        """
        msg_superior.attach(MIMEText(html_body_superior, 'html'))

        # Employee confirmation email
        msg_employee = None
        if employee_email and "@" in employee_email:
            msg_employee = MIMEMultipart('alternative')
            msg_employee['From'] = formataddr(("VOLAR FASHION HR", sender_email))
            msg_employee['To'] = employee_email
            msg_employee['Subject'] = (f"Leave Application Submitted: {len(clusters_data)} periods"
                                       if len(clusters_data) > 1 else "Leave Application Submitted Successfully")
            employee_clusters_html = ""
            for i, cluster in enumerate(clusters_data):
                days = calculate_days(cluster['from_date'], cluster['till_date'], cluster['leave_type'])
                days_display = "N/A" if cluster['leave_type'] == "Early Exit" else (f"{days} days" if cluster['leave_type'] == "Full Day" else "0.5 day")
                employee_clusters_html += f"""
                <div style="background: {'#f8f9ff' if i % 2 == 0 else '#f0f2ff'}; padding: 15px; border-radius: 8px; margin: 10px 0; border-left: 4px solid #4dabf7;">
                    <h4 style="margin-top: 0; color: #339af0;">Period {i+1}</h4>
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr><td style="padding: 5px; width: 40%;"><strong>Leave Type:</strong></td><td style="padding: 5px;">{cluster['leave_type']}</td></tr>
                        <tr><td style="padding: 5px;"><strong>From:</strong></td><td style="padding: 5px;">{cluster['from_date'].strftime('%Y-%m-%d')}</td></tr>
                        <tr><td style="padding: 5px;"><strong>To:</strong></td><td style="padding: 5px;">{cluster['till_date'].strftime('%Y-%m-%d')}</td></tr>
                        <tr><td style="padding: 5px;"><strong>Duration:</strong></td><td style="padding: 5px;">{days_display}</td></tr>
                    </table>
                </div>
                """
            html_body_employee = f"""
            <html><head><style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
            .container {{ max-width: 700px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #4caf50 0%, #2e7d32 100%); color: white; padding: 20px; border-radius: 10px; text-align: center; }}
            .info-box {{ background: #f8f9ff; padding: 20px; border-radius: 10px; margin: 20px 0; border: 1px solid #e2e8f0; }}
            .footer {{ color: #666; font-size: 12px; margin-top: 30px; padding-top: 15px; border-top: 1px solid #eee; }}
            </style></head><body>
            <div class="container">
                <div class="header"><h2 style="margin: 0;">Leave Application Confirmation</h2></div>
                <p>Dear {employee_name},</p>
                <div class="info-box">
                    <h3 style="margin-top: 0; color: #4caf50;">Application Submitted Successfully</h3>
                    <p>Your leave application has been submitted and sent to your manager for approval.</p>
                    <p><strong>Reporting Manager:</strong> {superior_name}</p>
                    <p><strong>Purpose:</strong> {clusters_data[0].get('purpose', 'N/A')}</p>
                    <p><strong>Total Periods:</strong> {len(clusters_data)}</p>
                </div>
                <h3 style="color: #339af0;">Your Leave Periods</h3>
                {employee_clusters_html}
                <div class="footer">VOLAR FASHION PVT LTD - HR Department<br>hrvolarfashion@gmail.com</div>
            </div></body></html>
            """
            msg_employee.attach(MIMEText(html_body_employee, 'html'))

        server, method = create_smtp_connection(sender_email, sender_password)
        if server:
            try:
                server.sendmail(sender_email, superior_email, msg_superior.as_string())
                log_debug(f"Leave approval email sent to {superior_email}")
                if msg_employee and employee_email and "@" in employee_email:
                    try:
                        server.sendmail(sender_email, employee_email, msg_employee.as_string())
                        log_debug(f"Leave confirmation email sent to {employee_email}")
                    except Exception as e:
                        log_debug(f"Could not send confirmation to employee: {str(e)}")
                server.quit()
                return True
            except Exception as e:
                try: server.quit()
                except: pass
                log_debug(f"Failed to send leave emails: {str(e)}")
                st.error(f"Failed to send emails: {str(e)}")
                return False
        else:
            log_debug(f"Could not establish SMTP connection: {method}")
            st.error(f"Could not establish SMTP connection: {method}")
            return False
    except Exception as e:
        log_debug(f"Error in send_approval_email: {traceback.format_exc()}")
        st.error(f"Email sending error: {str(e)}")
        return False


def send_decision_email_to_employee(employee_name, employee_email, superior_name, status,
                                    cluster_info=None, cluster_number=None, total_clusters=None):
    try:
        sender_email, sender_password, source = get_email_credentials()
        if not sender_email or not sender_password: return False
        if not employee_email or "@" not in employee_email: return False
        msg = MIMEMultipart('alternative')
        msg['From'] = formataddr(("VOLAR FASHION HR", sender_email))
        msg['To'] = employee_email
        if cluster_number and total_clusters and total_clusters > 1:
            msg['Subject'] = f"Leave Period {cluster_number}/{total_clusters} {status} - {employee_name}"
        else:
            msg['Subject'] = f"Leave Application {status} - {employee_name}"
        status_color = "#4caf50" if status == "Approved" else "#f44336"
        status_bg = "#e8f5e9" if status == "Approved" else "#ffebee"
        cluster_details = ""
        if cluster_info:
            days = calculate_days(
                datetime.strptime(cluster_info['from_date'], "%Y-%m-%d").date() if isinstance(cluster_info['from_date'], str) else cluster_info['from_date'],
                datetime.strptime(cluster_info['till_date'], "%Y-%m-%d").date() if isinstance(cluster_info['till_date'], str) else cluster_info['till_date'],
                cluster_info['leave_type']
            )
            days_display = "N/A" if cluster_info['leave_type'] == "Early Exit" else (f"{days} days" if cluster_info['leave_type'] == "Full Day" else "0.5 day")
            from_date_str = cluster_info['from_date'].strftime('%Y-%m-%d') if hasattr(cluster_info['from_date'], 'strftime') else cluster_info['from_date']
            till_date_str = cluster_info['till_date'].strftime('%Y-%m-%d') if hasattr(cluster_info['till_date'], 'strftime') else cluster_info['till_date']
            cluster_label = f"Period {cluster_number}" if cluster_number and total_clusters and total_clusters > 1 else "Leave Period"
            cluster_details = f"""
            <div style="background: #f8f9ff; padding: 15px; border-radius: 8px; margin: 15px 0; border-left: 4px solid #4dabf7;">
                <h4 style="margin-top: 0; color: #339af0;">{cluster_label} Details</h4>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr><td style="padding: 5px; width: 40%;"><strong>Leave Type:</strong></td><td style="padding: 5px;">{cluster_info['leave_type']}</td></tr>
                    <tr><td style="padding: 5px;"><strong>From:</strong></td><td style="padding: 5px;">{from_date_str}</td></tr>
                    <tr><td style="padding: 5px;"><strong>To:</strong></td><td style="padding: 5px;">{till_date_str}</td></tr>
                    <tr><td style="padding: 5px;"><strong>Duration:</strong></td><td style="padding: 5px;">{days_display}</td></tr>
                </table>
            </div>
            """
        status_message = ("""<div style="background: #e8f5e9; padding: 15px; border-radius: 8px; margin: 15px 0; border-left: 4px solid #4caf50;">
            <h4 style="margin-top: 0; color: #2e7d32;">Approval Confirmation</h4>
            <p>Your leave request has been approved. You can proceed with your leave plans.</p></div>"""
            if status == "Approved" else
            f"""<div style="background: #ffebee; padding: 15px; border-radius: 8px; margin: 15px 0; border-left: 4px solid #f44336;">
            <h4 style="margin-top: 0; color: #c62828;">Rejection Notification</h4>
            <p>Your leave request has been rejected. Please contact <strong>{superior_name}</strong> for more information.</p></div>""")
        html_body = f"""
        <html><head><style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
        .container {{ max-width: 700px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, {status_color} 0%, {status_color}80 100%); color: white; padding: 20px; border-radius: 10px; text-align: center; }}
        .info-box {{ background: {status_bg}; padding: 20px; border-radius: 10px; margin: 20px 0; }}
        .footer {{ color: #666; font-size: 12px; margin-top: 30px; padding-top: 15px; border-top: 1px solid #eee; }}
        </style></head><body>
        <div class="container">
            <div class="header"><h2 style="margin: 0;">Leave Application {status}</h2></div>
            <p>Dear {employee_name},</p>
            <div class="info-box">
                <h3 style="margin-top: 0; color: {status_color};">Your leave request has been {status.lower()}</h3>
                <p><strong>Decision by:</strong> {superior_name}</p>
                <p><strong>Decision Date:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                {cluster_details}
                {status_message}
            </div>
            <div class="footer">VOLAR FASHION PVT LTD - HR Department<br>hrvolarfashion@gmail.com</div>
        </div></body></html>
        """
        msg.attach(MIMEText(html_body, 'html'))
        server, method = create_smtp_connection(sender_email, sender_password)
        if server:
            try:
                server.sendmail(sender_email, employee_email, msg.as_string())
                server.quit()
                log_debug(f"Leave decision email sent to employee: {employee_email}")
                return True
            except Exception as e:
                try: server.quit()
                except: pass
                log_debug(f"Failed to send leave decision email: {str(e)}")
                return False
        return False
    except Exception as e:
        log_debug(f"Error in send_decision_email_to_employee: {traceback.format_exc()}")
        return False


def send_decision_email_to_superior(employee_name, employee_email, superior_name, superior_email, status, approval_password):
    try:
        sender_email, sender_password, source = get_email_credentials()
        if not sender_email or not sender_password: return False
        msg = MIMEMultipart('alternative')
        msg['From'] = formataddr(("VOLAR FASHION HR", sender_email))
        msg['To'] = superior_email
        msg['Subject'] = f"Leave Decision Recorded: {employee_name} - {status}"
        html_body = f"""
        <html><head><style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
        .container {{ max-width: 700px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #673ab7 0%, #9c27b0 100%); color: white; padding: 20px; border-radius: 10px; text-align: center; }}
        .success-box {{ background: #e8f5e9; padding: 15px; border-radius: 8px; margin: 15px 0; border-left: 4px solid #4caf50; }}
        .info-box {{ background: #f8f9ff; padding: 20px; border-radius: 10px; margin: 20px 0; border: 1px solid #e2e8f0; }}
        .footer {{ color: #666; font-size: 12px; margin-top: 30px; padding-top: 15px; border-top: 1px solid #eee; }}
        </style></head><body>
        <div class="container">
            <div class="header"><h2 style="margin: 0;">Decision Confirmation</h2></div>
            <p>Dear {superior_name},</p>
            <div class="success-box">
                <p>You have successfully <strong>{status.lower()}</strong> the leave request for <strong>{employee_name}</strong>.</p>
            </div>
            <div class="info-box">
                <p><strong>Employee:</strong> {employee_name}</p>
                <p><strong>Decision:</strong> <span style="color: {'#4caf50' if status == 'Approved' else '#f44336'}; font-weight: bold;">{status}</span></p>
                <p><strong>Code Used:</strong> {approval_password}</p>
                <p><strong>Decision Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            <div class="footer">VOLAR FASHION PVT LTD - HR Department<br>hrvolarfashion@gmail.com</div>
        </div></body></html>
        """
        msg.attach(MIMEText(html_body, 'html'))
        server, method = create_smtp_connection(sender_email, sender_password)
        if server:
            try:
                server.sendmail(sender_email, superior_email, msg.as_string())
                server.quit()
                log_debug(f"Leave decision confirmation sent to superior: {superior_email}")
                return True
            except Exception as e:
                try: server.quit()
                except: pass
                return False
        return False
    except Exception as e:
        log_debug(f"Error in send_decision_email_to_superior: {traceback.format_exc()}")
        return False


def update_leave_status(sheet, approval_password, status):
    try:
        all_records = sheet.get_all_values()
        for idx, row in enumerate(all_records):
            if idx == 0:
                continue
            if len(row) > 13 and row[13] == approval_password:
                sheet.update_cell(idx + 1, 12, status)
                sheet.update_cell(idx + 1, 13, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                employee_name = row[2] if len(row) > 2 else ""
                employee_email = row[16] if len(row) > 16 else ""
                superior_name = row[9] if len(row) > 9 else ""
                superior_email = row[10] if len(row) > 10 else ""
                cluster_info = None
                if len(row) > 4:
                    cluster_info = {
                        'leave_type': row[4] if len(row) > 4 else "",
                        'from_date': row[7] if len(row) > 7 else "",
                        'till_date': row[8] if len(row) > 8 else ""
                    }
                is_cluster = row[14] if len(row) > 14 else "No"
                cluster_number = None
                if is_cluster == "Yes" and len(row) > 15:
                    cluster_number = row[15] if row[15] else None
                total_clusters = None
                if is_cluster == "Yes" and employee_name:
                    total_clusters = sum(
                        1 for record in all_records[1:]
                        if len(record) > 2 and record[2] == employee_name and len(record) > 14 and record[14] == "Yes"
                    )
                log_debug(f"Updated leave row {idx + 1} to status: {status}")
                if employee_email and "@" in employee_email:
                    send_decision_email_to_employee(employee_name, employee_email, superior_name, status,
                                                    cluster_info, cluster_number, total_clusters)
                if superior_email and "@" in superior_email:
                    send_decision_email_to_superior(employee_name, employee_email, superior_name,
                                                    superior_email, status, approval_password)
                return True
        log_debug("No matching leave record found for approval code")
        return False
    except Exception as e:
        st.error(f"Error updating leave status: {str(e)}")
        log_debug(f"Update leave error: {traceback.format_exc()}")
        return False


# ============================================================
# WFH EMAILS
# ============================================================
def send_wfh_approval_email(employee_name, employee_code, employee_email,
                             request_type, start_date, end_date, reason, approval_code):
    """
    Send WFH/Out-of-Office approval request to BOTH Sandip and HR,
    containing the 5-char approval code for use in Tab 5.
    """
    try:
        log_debug(f"Sending WFH approval email to HR and Sandip for {employee_name}")
        sender_email, sender_password, source = get_email_credentials()
        if not sender_email or not sender_password:
            log_debug("Email credentials not configured for WFH email")
            return False
        try:
            app_url = st.secrets.get("APP_URL", "https://9yq6u8fklhfba8uggnjr7h.streamlit.app/")
        except:
            app_url = "https://9yq6u8fklhfba8uggnjr7h.streamlit.app/"
        duration = (end_date - start_date).days + 1
        start_str = start_date.strftime('%Y-%m-%d')
        end_str = end_date.strftime('%Y-%m-%d')

        html_body = f"""
        <html><head><style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
        .container {{ max-width: 700px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #20c997 0%, #0ca678 100%); color: white; padding: 20px; border-radius: 10px; text-align: center; }}
        .info-box {{ background: #f8f9ff; padding: 20px; border-radius: 10px; margin: 20px 0; border: 1px solid #e2e8f0; }}
        .code-box {{ background: #fff3cd; padding: 20px; border-radius: 10px; margin: 20px 0; text-align: center; border: 2px solid #ffc107; }}
        .instructions {{ background: #e8f5e9; padding: 15px; border-radius: 8px; margin: 15px 0; border-left: 4px solid #4caf50; }}
        .footer {{ color: #666; font-size: 12px; margin-top: 30px; padding-top: 15px; border-top: 1px solid #eee; }}
        </style></head><body>
        <div class="container">
            <div class="header">
                <h2 style="margin: 0;">{'WFH' if request_type == 'Work From Home' else 'Out of Office'} Request - Approval Required</h2>
                <p style="margin: 5px 0 0 0; opacity: 0.9;">VOLAR FASHION HR System</p>
            </div>
            <p>Dear HR / Sandip Sir,</p>
            <div class="info-box">
                <h3 style="margin-top: 0; color: #20c997;">Employee Request Details</h3>
                <p><strong>Employee Name:</strong> {employee_name}</p>
                <p><strong>Employee Code:</strong> {employee_code}</p>
                <p><strong>Employee Email:</strong> {employee_email if employee_email else 'Not provided'}</p>
                <p><strong>Request Type:</strong> {request_type}</p>
                <p><strong>Start Date:</strong> {start_str}</p>
                <p><strong>End Date:</strong> {end_str}</p>
                <p><strong>Duration:</strong> {duration} day(s)</p>
                <p><strong>Reason:</strong> {reason}</p>
            </div>
            <div class="code-box">
                <div style="font-size: 0.95rem; color: #856404; font-weight: 600; margin-bottom: 10px;">
                    WFH Approval Code (HR Use Only)
                </div>
                <div style="font-size: 2.5rem; font-weight: 700; color: #553c9a; letter-spacing: 6px;
                            font-family: 'Courier New', monospace; background: white; padding: 15px;
                            border-radius: 8px; display: inline-block; margin: 10px 0;">
                    {approval_code}
                </div>
                <div style="font-size: 0.85rem; color: #856404; margin-top: 8px;">
                    Use this code in the WFH Approval Portal to approve or reject this request.
                </div>
            </div>
            <div class="instructions">
                <h4 style="margin-top: 0; color: #2e7d32;">How to Approve / Reject:</h4>
                <ol>
                    <li>Visit: <a href="{app_url}">{app_url}</a></li>
                    <li>Click on the <strong>"WFH / OOO Approval"</strong> tab (Tab 5)</li>
                    <li>Enter the 5-character code: <strong style="font-family: monospace; letter-spacing: 2px;">{approval_code}</strong></li>
                    <li>Select <strong>Approve</strong> or <strong>Reject</strong></li>
                    <li>Click <strong>Submit Decision</strong></li>
                </ol>
                <p style="font-size: 0.9rem;"><strong>Note:</strong> Only HR can approve/reject via this code. The employee will be notified automatically.</p>
            </div>
            <div class="footer">VOLAR FASHION PVT LTD - HR Department<br>hrvolarfashion@gmail.com<br>This is an automated message.</div>
        </div></body></html>
        """

        server, method = create_smtp_connection(sender_email, sender_password)
        if not server:
            log_debug(f"SMTP connection failed for WFH approval email: {method}")
            return False
        try:
            # Send to HR
            msg_hr = MIMEMultipart('alternative')
            msg_hr['From'] = formataddr(("VOLAR FASHION HR", sender_email))
            msg_hr['To'] = HR_EMAIL
            msg_hr['Subject'] = f"WFH/OOO Approval Required: {employee_name} [{approval_code}]"
            msg_hr.attach(MIMEText(html_body, 'html'))
            server.sendmail(sender_email, HR_EMAIL, msg_hr.as_string())
            log_debug(f"WFH approval email sent to HR: {HR_EMAIL}")

            

            server.quit()
            return True
        except Exception as e:
            try: server.quit()
            except: pass
            log_debug(f"Failed to send WFH approval emails: {str(e)}")
            return False
    except Exception as e:
        log_debug(f"Error in send_wfh_approval_email: {traceback.format_exc()}")
        return False


def send_wfh_employee_confirmation_email(employee_name, employee_email, request_type,
                                          start_date, end_date, reason):
    """Send confirmation email to employee after WFH/OOO request submission."""
    try:
        if not employee_email or "@" not in employee_email:
            return False
        sender_email, sender_password, source = get_email_credentials()
        if not sender_email or not sender_password:
            return False
        duration = (end_date - start_date).days + 1
        msg = MIMEMultipart('alternative')
        msg['From'] = formataddr(("VOLAR FASHION HR", sender_email))
        msg['To'] = employee_email
        msg['Subject'] = f"{'WFH' if request_type == 'Work From Home' else 'Out of Office'} Request Submitted - {employee_name}"
        html_body = f"""
        <html><head><style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
        .container {{ max-width: 700px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #4caf50 0%, #2e7d32 100%); color: white; padding: 20px; border-radius: 10px; text-align: center; }}
        .info-box {{ background: #f8f9ff; padding: 20px; border-radius: 10px; margin: 20px 0; border: 1px solid #e2e8f0; }}
        .footer {{ color: #666; font-size: 12px; margin-top: 30px; padding-top: 15px; border-top: 1px solid #eee; }}
        </style></head><body>
        <div class="container">
            <div class="header"><h2 style="margin: 0;">Request Submitted Successfully</h2><p style="margin: 5px 0 0 0; opacity: 0.9;">VOLAR FASHION HR System</p></div>
            <p>Dear {employee_name},</p>
            <div class="info-box">
                <h3 style="margin-top: 0; color: #4caf50;">Your {request_type} request has been submitted.</h3>
                <p><strong>Request Type:</strong> {request_type}</p>
                <p><strong>Start Date:</strong> {start_date.strftime('%Y-%m-%d')}</p>
                <p><strong>End Date:</strong> {end_date.strftime('%Y-%m-%d')}</p>
                <p><strong>Duration:</strong> {duration} day(s)</p>
                <p><strong>Reason:</strong> {reason}</p>
            </div>
            <div style="background: #e3f2fd; padding: 15px; border-radius: 8px; margin: 15px 0; border-left: 4px solid #2196f3;">
                <h4 style="margin-top: 0; color: #0d47a1;">What Happens Next:</h4>
                <ol>
                    <li>Your request has been sent to HR and Sandip Sir for review.</li>
                    <li>HR will approve or reject your request.</li>
                    <li>You will receive an email once a decision is made.</li>
                    <li>Please check your inbox regularly for updates.</li>
                </ol>
            </div>
            <div class="footer">VOLAR FASHION PVT LTD - HR Department<br>hrvolarfashion@gmail.com<br>This is an automated confirmation email.</div>
        </div></body></html>
        """
        msg.attach(MIMEText(html_body, 'html'))
        server, method = create_smtp_connection(sender_email, sender_password)
        if server:
            try:
                server.sendmail(sender_email, employee_email, msg.as_string())
                server.quit()
                log_debug(f"WFH confirmation email sent to employee: {employee_email}")
                return True
            except Exception as e:
                try: server.quit()
                except: pass
                log_debug(f"Failed to send WFH confirmation to employee: {str(e)}")
                return False
        return False
    except Exception as e:
        log_debug(f"Error in send_wfh_employee_confirmation_email: {traceback.format_exc()}")
        return False


def send_wfh_decision_email_to_employee(employee_name, employee_email, status,
                                         request_type, start_date_str, end_date_str, reason):
    """Notify employee of WFH/OOO approval or rejection decision by HR."""
    try:
        if not employee_email or "@" not in employee_email:
            log_debug(f"No valid employee email for WFH decision notification")
            return False
        sender_email, sender_password, source = get_email_credentials()
        if not sender_email or not sender_password:
            return False
        msg = MIMEMultipart('alternative')
        msg['From'] = formataddr(("VOLAR FASHION HR", sender_email))
        msg['To'] = employee_email
        msg['Subject'] = f"{'WFH' if 'Home' in request_type else 'Out of Office'} Request {status} - {employee_name}"
        status_color = "#4caf50" if status == "Approved" else "#f44336"
        status_bg = "#e8f5e9" if status == "Approved" else "#ffebee"
        status_icon = "✅" if status == "Approved" else "❌"
        action_note = (
            "<p>Your request has been approved. Please ensure you stay reachable during your WFH/OOO period.</p>"
            if status == "Approved"
            else "<p>Your request has been rejected. Please contact HR or Sandip Sir for more details.</p>"
        )
        html_body = f"""
        <html><head><style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
        .container {{ max-width: 700px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, {status_color} 0%, {status_color}80 100%); color: white; padding: 20px; border-radius: 10px; text-align: center; }}
        .info-box {{ background: {status_bg}; padding: 20px; border-radius: 10px; margin: 20px 0; }}
        .footer {{ color: #666; font-size: 12px; margin-top: 30px; padding-top: 15px; border-top: 1px solid #eee; }}
        </style></head><body>
        <div class="container">
            <div class="header">
                <h2 style="margin: 0;">{request_type} Request {status}</h2>
                <p style="margin: 5px 0 0 0; opacity: 0.9;">VOLAR FASHION HR System</p>
            </div>
            <p>Dear {employee_name},</p>
            <div class="info-box">
                <h3 style="margin-top: 0; color: {status_color};">
                    {status_icon} Your {request_type} request has been <strong>{status.lower()}</strong> by HR.
                </h3>
                <p><strong>Request Type:</strong> {request_type}</p>
                <p><strong>Start Date:</strong> {start_date_str}</p>
                <p><strong>End Date:</strong> {end_date_str}</p>
                <p><strong>Reason Submitted:</strong> {reason}</p>
                <p><strong>Decision By:</strong> HR - VOLAR FASHION</p>
                <p><strong>Decision Date:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <div style="margin-top: 15px; padding: 12px; background: white; border-radius: 8px; border-left: 3px solid {status_color};">
                    {action_note}
                </div>
            </div>
            <div class="footer">VOLAR FASHION PVT LTD - HR Department<br>hrvolarfashion@gmail.com<br>This is an automated notification.</div>
        </div></body></html>
        """
        msg.attach(MIMEText(html_body, 'html'))
        server, method = create_smtp_connection(sender_email, sender_password)
        if server:
            try:
                server.sendmail(sender_email, employee_email, msg.as_string())
                server.quit()
                log_debug(f"WFH decision email sent to employee: {employee_email}")
                return True
            except Exception as e:
                try: server.quit()
                except: pass
                log_debug(f"Failed to send WFH decision to employee: {str(e)}")
                return False
        return False
    except Exception as e:
        log_debug(f"Error in send_wfh_decision_email_to_employee: {traceback.format_exc()}")
        return False


def send_wfh_decision_confirmation_to_hr(employee_name, employee_email, status,
                                          request_type, approval_code):
    """Send decision confirmation back to HR after they approve/reject WFH."""
    try:
        sender_email, sender_password, source = get_email_credentials()
        if not sender_email or not sender_password:
            return False
        msg = MIMEMultipart('alternative')
        msg['From'] = formataddr(("VOLAR FASHION HR", sender_email))
        msg['To'] = HR_EMAIL
        msg['Subject'] = f"WFH Decision Recorded: {employee_name} - {status}"
        html_body = f"""
        <html><head><style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
        .container {{ max-width: 700px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #20c997 0%, #0ca678 100%); color: white; padding: 20px; border-radius: 10px; text-align: center; }}
        .success-box {{ background: #e8f5e9; padding: 15px; border-radius: 8px; margin: 15px 0; border-left: 4px solid #4caf50; }}
        .info-box {{ background: #f8f9ff; padding: 20px; border-radius: 10px; margin: 20px 0; border: 1px solid #e2e8f0; }}
        .footer {{ color: #666; font-size: 12px; margin-top: 30px; padding-top: 15px; border-top: 1px solid #eee; }}
        </style></head><body>
        <div class="container">
            <div class="header"><h2 style="margin: 0;">WFH/OOO Decision Confirmed</h2></div>
            <p>Dear HR Team,</p>
            <div class="success-box">
                <p>The WFH/OOO request for <strong>{employee_name}</strong> has been <strong>{status.lower()}</strong> successfully.</p>
            </div>
            <div class="info-box">
                <p><strong>Employee:</strong> {employee_name}</p>
                <p><strong>Employee Email:</strong> {employee_email if employee_email else 'N/A'}</p>
                <p><strong>Request Type:</strong> {request_type}</p>
                <p><strong>Decision:</strong> <span style="color: {'#4caf50' if status == 'Approved' else '#f44336'}; font-weight: bold;">{status}</span></p>
                <p><strong>Code Used:</strong> {approval_code}</p>
                <p><strong>Decision Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            <div class="footer">VOLAR FASHION PVT LTD - HR Department<br>hrvolarfashion@gmail.com</div>
        </div></body></html>
        """
        msg.attach(MIMEText(html_body, 'html'))
        server, method = create_smtp_connection(sender_email, sender_password)
        if server:
            try:
                server.sendmail(sender_email, HR_EMAIL, msg.as_string())
                server.quit()
                log_debug(f"WFH decision confirmation sent to HR")
                return True
            except Exception as e:
                try: server.quit()
                except: pass
                return False
        return False
    except Exception as e:
        log_debug(f"Error in send_wfh_decision_confirmation_to_hr: {traceback.format_exc()}")
        return False


def update_wfh_status(sheet, approval_code, status):
    """
    Find the row in Sheet2 matching approval_code (column 11 = index 10),
    update Status (col 9) and Approval Date (col 10), then send emails.
    """
    try:
        all_records = sheet.get_all_values()
        for idx, row in enumerate(all_records):
            if idx == 0:
                continue
            # Column 11 (1-indexed) = index 10 (0-indexed) = Approval Code
            if len(row) > 10 and row[10] == approval_code:
                # Update Status (col 9) and Approval Date (col 10)
                sheet.update_cell(idx + 1, 9, status)
                sheet.update_cell(idx + 1, 10, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

                # Extract info from row
                employee_name   = row[1] if len(row) > 1 else ""
                employee_code   = row[2] if len(row) > 2 else ""
                employee_email  = row[3] if len(row) > 3 else ""
                request_type    = row[4] if len(row) > 4 else ""
                start_date_str  = row[5] if len(row) > 5 else ""
                end_date_str    = row[6] if len(row) > 6 else ""
                reason          = row[7] if len(row) > 7 else ""

                log_debug(f"Updated WFH row {idx + 1} → status: {status} for {employee_name}")

                # Notify employee
                if employee_email and "@" in employee_email:
                    send_wfh_decision_email_to_employee(
                        employee_name, employee_email, status,
                        request_type, start_date_str, end_date_str, reason
                    )

                # Confirm to HR
                send_wfh_decision_confirmation_to_hr(
                    employee_name, employee_email, status, request_type, approval_code
                )
                return True

        log_debug("No matching WFH record found for approval code")
        return False
    except Exception as e:
        st.error(f"Error updating WFH status: {str(e)}")
        log_debug(f"Update WFH error: {traceback.format_exc()}")
        return False


# ============================================================
# WFH SUBMISSION
# ============================================================
def submit_wfh_request(employee_name, employee_code, employee_email,
                        request_type, start_date, end_date, reason, medical_doc=None):
    """
    Save WFH/OOO request to Sheet2 with a generated approval code,
    then email HR + Sandip and confirm to the employee.
    """
    try:
        log_debug(f"Submitting WFH/OOO request for: {employee_name}")
        sheet = setup_wfh_sheet()
        if not sheet:
            return False, "Database connection failed. Please check your Google Sheets setup."

        # Generate unique approval code
        approval_code = generate_wfh_approval_code(sheet)
        log_debug(f"Generated WFH approval code: {approval_code} for {employee_name}")

        submission_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        row_data = [
            submission_date,
            employee_name.strip(),
            employee_code.strip(),
            employee_email.strip(),
            request_type.strip(),
            start_date.strftime("%Y-%m-%d"),
            end_date.strftime("%Y-%m-%d"),
            reason.strip(),
            "Pending",
            "",           # Approval Date (blank until decided)
            approval_code
        ]

        write_success = add_data_to_sheet2(sheet, row_data)
        if not write_success:
            return False, "Error submitting request to database."

        log_debug(f"WFH request written to Sheet2 for {employee_name}")

        # Upload supporting document (if provided) to Google Drive
        if medical_doc is not None:
            try:
                attachment_day_count = (end_date - start_date).days + 1
                attachment_filename = generate_attachment_filename(employee_name, attachment_day_count, start_date)
                upload_ok, upload_result = upload_file_to_drive(medical_doc, attachment_filename)
                if upload_ok:
                    log_debug(f"WFH attachment uploaded to Drive as {attachment_filename}")
                else:
                    log_debug(f"WFH attachment upload failed: {upload_result}")
                    st.warning("The attached document could not be uploaded automatically. Please share it with HR directly.")
            except Exception as att_err:
                log_debug(f"WFH attachment upload exception: {traceback.format_exc()}")
                st.warning("The attached document could not be uploaded automatically. Please share it with HR directly.")

        # Email HR + Sandip with approval code
        email_sent = False
        try:
            email_sent = send_wfh_approval_email(
                employee_name, employee_code, employee_email,
                request_type, start_date, end_date, reason, approval_code
            )
        except Exception as email_err:
            log_debug(f"WFH approval email error: {str(email_err)}")

        # Confirm submission to employee (best-effort)
        try:
            if employee_email and "@" in employee_email:
                send_wfh_employee_confirmation_email(
                    employee_name, employee_email,
                    request_type, start_date, end_date, reason
                )
        except Exception as conf_err:
            log_debug(f"WFH confirmation email error: {str(conf_err)}")

        if email_sent:
            return True, "Request submitted and approval email sent to HR successfully!"
        else:
            return True, (f"Request saved to database. However, the email notification could not be sent automatically. "
                          f"Please inform HR manually. Approval Code: {approval_code}")

    except Exception as e:
        log_debug(f"Error in submit_wfh_request: {traceback.format_exc()}")
        return False, f"Error: {str(e)}"


# ============================================================
# DUPLICATE SUBMISSION GUARDS
# ============================================================
def generate_submission_hash(form_data):
    data_string = f"{form_data['employee_name']}_{form_data['employee_code']}_{form_data['purpose']}_{datetime.now().strftime('%Y%m%d')}"
    return hashlib.md5(data_string.encode()).hexdigest()


def check_duplicate_submission(form_data):
    current_hash = generate_submission_hash(form_data)
    if st.session_state.last_submission_hash == current_hash:
        if st.session_state.submission_timestamp:
            time_diff = (datetime.now() - st.session_state.submission_timestamp).total_seconds()
            if time_diff < 30:
                return True, "You have already submitted this form. Please wait before submitting again."
    return False, ""


def generate_wfh_hash(form_data):
    data_string = (f"{form_data['employee_name']}_{form_data['employee_code']}_"
                   f"{form_data['request_type']}_{form_data['start_date']}_{form_data['end_date']}_"
                   f"{form_data['reason']}_{datetime.now().strftime('%Y%m%d')}")
    return hashlib.md5(data_string.encode()).hexdigest()


def check_duplicate_wfh_submission(form_data):
    current_hash = generate_wfh_hash(form_data)
    if st.session_state.get('last_wfh_submission_hash') == current_hash:
        if st.session_state.get('wfh_submission_timestamp'):
            time_diff = (datetime.now() - st.session_state.wfh_submission_timestamp).total_seconds()
            if time_diff < 30:
                return True, "You have already submitted this WFH/Out of Office form. Please wait before submitting again."
    return False, ""


# ============================================================
# SIDEBAR
# ============================================================
st.sidebar.title("Configuration Panel")
email_config = check_email_configuration()

st.sidebar.markdown("### Secrets Diagnostic")
try:
    all_secret_keys = list(st.secrets.keys())
    st.sidebar.info(f"Top-level secret keys found:\n`{all_secret_keys}`")
except Exception:
    st.sidebar.error("Could not read st.secrets — check your Streamlit Cloud secrets setup")

st.sidebar.markdown("### Email Configuration")
if email_config["configured"]:
    st.sidebar.success(f"Email ready: {email_config['sender_email']}")
    st.sidebar.info(f"**Source:** {email_config['source']}")
    if 'password_type' in email_config:
        st.sidebar.info(f"**Password Type:** {email_config['password_type']}  ({email_config.get('password_length', '?')} chars)")
else:
    st.sidebar.error("Email credentials NOT found")
    st.sidebar.warning(
        "Add to Streamlit Secrets:\n\n"
        "```toml\n[EMAIL]\nsender_email = \"you@gmail.com\"\nsender_password = \"abcd efgh ijkl mnop\"\n```"
    )
    st.sidebar.caption(f"Details: {email_config.get('details', email_config.get('message', ''))}")

st.sidebar.markdown("---")
if st.sidebar.button("Test Google Sheets Connection"):
    with st.sidebar:
        with st.spinner("Testing connection..."):
            sheet = setup_google_sheets()
            if sheet:
                st.success("Connected successfully!")
                st.info(f"Sheet: Leave_Applications | Rows: {sheet.row_count}")
            else:
                st.error("Connection failed")

st.sidebar.markdown("---")
if st.sidebar.button("Test Google Drive Connection"):
    with st.sidebar:
        with st.spinner("Testing Drive connection..."):
            drive_folder_id = get_drive_folder_id()
            if not drive_folder_id:
                st.error("Drive folder ID not set. Add [DRIVE] folder_id to secrets.")
            elif not DRIVE_UPLOAD_LIBS_AVAILABLE:
                st.error("google-api-python-client / google-auth not installed. See requirements.txt.")
            else:
                drive_service = get_drive_service()
                if not drive_service:
                    st.error("Could not authenticate with Google Drive. Check credentials.")
                else:
                    try:
                        folder_info = drive_service.files().get(fileId=drive_folder_id, fields="id, name").execute()
                        st.success(f"Connected! Folder: {folder_info.get('name')}")
                    except Exception as drive_test_error:
                        st.error(f"Could not access folder: {str(drive_test_error)}")

st.sidebar.markdown("---")
st.sidebar.markdown("### Test Email Configuration")
test_recipient = st.sidebar.text_input("Test Recipient Email", value="", placeholder="Leave blank to send to yourself")
col1, col2 = st.sidebar.columns(2)
with col1:
    if st.button("Send Test Email", key="test_email_btn", use_container_width=True):
        with st.spinner("Sending test email..."):
            result = test_email_connection(test_recipient)
            st.session_state.test_email_result = result
            if result["success"]:
                st.session_state.email_config_status = "Working"
                st.sidebar.success("Test email sent successfully!")
            else:
                st.session_state.email_config_status = "Failed"
                st.sidebar.error("Test email failed")
with col2:
    if st.button("Clear Logs", key="clear_logs", use_container_width=True):
        st.session_state.debug_logs = []

if st.session_state.test_email_result:
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Last Test Result")
    if st.session_state.test_email_result["success"]:
        st.sidebar.success("Last test: SUCCESS")
        st.sidebar.info(f"**Method:** {st.session_state.test_email_result.get('method', 'Unknown')}")
    else:
        st.sidebar.error("Last test: FAILED")
        with st.sidebar.expander("View Error Details"):
            st.error(st.session_state.test_email_result.get('message', 'No error message'))
            st.info(st.session_state.test_email_result.get('details', 'No details'))

st.sidebar.markdown("---")
st.sidebar.markdown("### Debug Logs")
if st.sidebar.checkbox("Show Debug Logs", value=False):
    if st.session_state.debug_logs:
        debug_logs_html = "<div class='debug-log'>"
        for log in reversed(st.session_state.debug_logs[-10:]):
            if "ERROR" in log:
                debug_logs_html += f"<div style='color: #dc3545;'>{log}</div>"
            elif "SUCCESS" in log or "INFO" in log:
                debug_logs_html += f"<div style='color: #28a745;'>{log}</div>"
            elif "WARNING" in log:
                debug_logs_html += f"<div style='color: #ffc107;'>{log}</div>"
            else:
                debug_logs_html += f"<div>{log}</div>"
        debug_logs_html += "</div>"
        st.sidebar.markdown(debug_logs_html, unsafe_allow_html=True)
    else:
        st.sidebar.info("No debug logs yet")

st.sidebar.markdown("---")
with st.sidebar.expander("Email Setup Guide"):
    st.markdown("""
    **Step-by-Step Gmail Configuration:**

    1. Enable 2-Step Verification: https://myaccount.google.com/security

    2. Generate App Password: https://myaccount.google.com/apppasswords
       - Select Mail → Other (Custom name)
       - Name it "VOLAR FASHION Streamlit"
       - Copy the 16-character password

    3. Update Streamlit Secrets:
    ```toml
    [EMAIL]
    sender_email = "hrvolarfashion@gmail.com"
    sender_password = "your-16-character-app-password"
    ```
    4. Click "Send Test Email" to verify.
    """)


# ============================================================
# MAIN APPLICATION HEADER
# ============================================================
st.markdown("""
    <div class="company-header floating-element">
        <h1>VOLAR FASHION</h1>
        <h2>Leave and WFH / Out of office request</h2>
    </div>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "\U0001f4dd Submit Leave Application",
    "\u2705 Approval Portal",
    "\U0001f4c5 Company Holidays",
    "\U0001f3e0 WFH / Out of Office",
    "\U0001f4f2 WFH / OOO Approval"
])


# ============================================================
# TAB 1: SUBMIT LEAVE APPLICATION
# ============================================================
with tab1:
    if not email_config["configured"] or st.session_state.email_config_status == "Failed":
        st.markdown("""
            <div style="background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
                        border-left: 4px solid #ff9800; color: #856404;
                        padding: 1.5rem; border-radius: 12px; margin-bottom: 2rem;">
                <div style="display: flex; align-items: center;">
                    <div style="font-size: 1.5rem; margin-right: 15px;">&#x26A0;&#xFE0F;</div>
                    <div>
                        <strong>Email Configuration Issue Detected</strong><br>
                        <span style="font-size: 0.95rem;">
                            Emails may not be sent automatically. Please use the manual approval process below if email fails.
                            Test your email configuration in the sidebar.
                        </span>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    elif st.session_state.email_config_status == "Working":
        st.markdown("""
            <div style="background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
                        border-left: 4px solid #28a745; color: #155724;
                        padding: 1.5rem; border-radius: 12px; margin-bottom: 2rem;">
                <div style="display: flex; align-items: center;">
                    <div style="font-size: 1.5rem; margin-right: 15px;">&#x2705;</div>
                    <div>
                        <strong>Email Configuration Working</strong><br>
                        <span style="font-size: 0.95rem;">
                            Email notifications will be sent automatically to managers and employees.
                        </span>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("""
        <div class="section-header">
            <div class="icon-badge">&#x1F4CB;</div>
            <div>
                <h3 style="margin: 0;">Leave Application Form</h3>
                <p style="margin: 5px 0 0 0; color: #718096; font-size: 0.95rem;">
                    Complete all fields below to submit your leave request
                </p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    if st.session_state.reset_form_tab1:
        st.session_state.form_data_tab1 = {
            'employee_name': '', 'employee_code': '', 'employee_email': '',
            'department': 'Select Department', 'purpose': '',
            'superior_name': 'Select Manager', 'is_cluster': False
        }
        st.session_state.clusters = [{
            'cluster_number': 1, 'leave_type': 'Select Type',
            'from_date': datetime.now().date(), 'till_date': datetime.now().date(), 'approval_code': ''
        }]
        st.session_state.cluster_codes = {}
        st.session_state.reset_form_tab1 = False
        st.session_state.submission_in_progress = False
        st.session_state.submission_completed = True
        st.session_state.leave_file_uploader_key += 1

    col1, col2, col3 = st.columns([1, 1, 1], gap="large")
    with col1:
        employee_name = st.text_input(
            "Full Name", value=st.session_state.form_data_tab1['employee_name'],
            placeholder="Enter your full name", key="employee_name_input"
        )
    with col2:
        employee_code = st.text_input(
            "Employee ID", value=st.session_state.form_data_tab1['employee_code'],
            placeholder="e.g., VF-EMP-001", key="employee_code_input"
        )
    with col3:
        employee_email = st.text_input(
            "Employee Email", value=st.session_state.form_data_tab1['employee_email'],
            placeholder="your.email@company.com", key="employee_email_input"
        )

    col4, col5 = st.columns([1, 1], gap="large")
    with col4:
        department = st.selectbox(
            "Department", ["Select Department"] + DEPARTMENTS, index=0,
            help="Select your department from the list", key="department_select"
        )
    with col5:
        is_cluster = st.checkbox(
            "Is this a Cluster Holiday? (Multiple leave periods)",
            value=st.session_state.form_data_tab1['is_cluster'],
            help="Check this if you need to apply for multiple separate leave periods",
            key="is_cluster_checkbox"
        )

    if is_cluster:
        st.markdown("""
            <div class="cluster-section">
                <div class="cluster-header">
                    <div class="icon-badge" style="background: linear-gradient(135deg, #4dabf7 0%, #339af0 100%);">&#x1F4C5;</div>
                    <div>
                        <h3 style="margin: 0; color: #ffffff !important;">Cluster Holiday Periods</h3>
                        <p style="margin: 5px 0 0 0; color: #4dabf7; font-size: 0.95rem;">
                            Add multiple leave periods below (each will have separate approval code)
                        </p>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        total_clusters = len(st.session_state.clusters)
        for i, cluster in enumerate(st.session_state.clusters):
            st.markdown(f"<h4 style='color: #339af0;'>Period {i+1}</h4>", unsafe_allow_html=True)
            col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
            with col1:
                leave_type = st.selectbox(
                    f"Leave Type - Period {i+1}",
                    ["Select Type", "Full Day", "Half Day", "Early Exit"],
                    index=0 if cluster['leave_type'] == 'Select Type' else ["Select Type", "Full Day", "Half Day", "Early Exit"].index(cluster['leave_type']),
                    key=f"leave_type_cluster_{i}"
                )
                st.session_state.clusters[i]['leave_type'] = leave_type
            with col2:
                if leave_type in ["Half Day", "Early Exit"]:
                    selected_date = st.date_input(
                        f"Date - Period {i+1}", value=cluster['from_date'],
                        min_value=datetime.now().date() - timedelta(days=60), key=f"date_cluster_{i}"
                    )
                    st.session_state.clusters[i]['from_date'] = selected_date
                    st.session_state.clusters[i]['till_date'] = selected_date
                else:
                    col_a, col_b = st.columns(2)
                    with col_a:
                        from_date = st.date_input(
                            f"From - Period {i+1}", value=cluster['from_date'],
                            min_value=datetime.now().date() - timedelta(days=60), key=f"from_date_cluster_{i}"
                        )
                        st.session_state.clusters[i]['from_date'] = from_date
                    with col_b:
                        till_date = st.date_input(
                            f"To - Period {i+1}", value=cluster['till_date'],
                            min_value=datetime.now().date() - timedelta(days=60), key=f"till_date_cluster_{i}"
                        )
                        st.session_state.clusters[i]['till_date'] = till_date
            with col3:
                if leave_type != "Select Type":
                    no_of_days = calculate_days(
                        st.session_state.clusters[i]['from_date'],
                        st.session_state.clusters[i]['till_date'], leave_type
                    )
                    days_display = "N/A" if leave_type == "Early Exit" else ("0.5" if leave_type == "Half Day" else str(no_of_days))
                    st.markdown(f"""
                        <div style="background: #e3f2fd; padding: 10px; border-radius: 8px; text-align: center;">
                            <div style="font-size: 0.8rem; color: #1976d2;">Days</div>
                            <div style="font-size: 1.2rem; font-weight: bold; color: #0d47a1;">{days_display}</div>
                        </div>
                    """, unsafe_allow_html=True)
            with col4:
                if total_clusters > 1:
                    if st.button("Remove", key=f"remove_cluster_{i}"):
                        st.session_state.clusters.pop(i)
                        st.rerun()

        if st.button("Add Another Period", key="add_cluster"):
            new_cluster_number = len(st.session_state.clusters) + 1
            st.session_state.clusters.append({
                'cluster_number': new_cluster_number, 'leave_type': 'Select Type',
                'from_date': datetime.now().date(), 'till_date': datetime.now().date(), 'approval_code': ''
            })
            st.rerun()

        total_days = sum(
            (calculate_working_days(c['from_date'], c['till_date']) if c['leave_type'] == "Full Day"
             else 0.5 if c['leave_type'] == "Half Day" else 0)
            for c in st.session_state.clusters
        )
        st.markdown(f"""
            <div style="background: linear-gradient(135deg, #4dabf7 0%, #339af0 100%);
                        color: white; padding: 1rem; border-radius: 12px; text-align: center; margin: 1rem 0;">
                <div style="font-size: 0.9rem;">Total Working Days</div>
                <div style="font-size: 2rem; font-weight: bold;">{total_days}</div>
                <div style="font-size: 0.8rem;">across {len(st.session_state.clusters)} period(s)</div>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <div style="margin-top: 2rem;">
                <div style="display: flex; align-items: center; margin-bottom: 1rem;">
                    <div class="icon-badge" style="background: linear-gradient(135deg, #2196f3 0%, #03a9f4 100%);">&#x1F4C5;</div>
                    <div>
                        <h3 style="margin: 0;">Leave Details</h3>
                        <p style="margin: 5px 0 0 0; color: #718096; font-size: 0.95rem;">Enter your leave period details</p>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns([1, 1], gap="large")
        with col1:
            leave_type = st.selectbox(
                "Leave Type", ["Select Type", "Full Day", "Half Day", "Early Exit"],
                index=0, help="Select the type of leave you are requesting", key="leave_type_single"
            )
        with col2:
            if leave_type in ["Half Day", "Early Exit"]:
                selected_date = st.date_input(
                    "Date", value=st.session_state.clusters[0]['from_date'],
                    min_value=datetime.now().date() - timedelta(days=60),
                    help="Select the date for your leave", key="date_single"
                )
                from_date = selected_date
                till_date = selected_date
            else:
                col_a, col_b = st.columns(2)
                with col_a:
                    from_date = st.date_input(
                        "Start Date", value=st.session_state.clusters[0]['from_date'],
                        min_value=datetime.now().date() - timedelta(days=60),
                        help="Select the first day of your leave", key="from_date_single"
                    )
                with col_b:
                    till_date = st.date_input(
                        "End Date", value=st.session_state.clusters[0]['till_date'],
                        min_value=datetime.now().date() - timedelta(days=60),
                        help="Select the last day of your leave", key="till_date_single"
                    )

        st.session_state.clusters[0]['leave_type'] = leave_type
        st.session_state.clusters[0]['from_date'] = from_date
        st.session_state.clusters[0]['till_date'] = till_date

        if leave_type != "Select Type":
            no_of_days = calculate_days(from_date, till_date, leave_type)
            if leave_type == "Early Exit":
                st.markdown("""
                    <div class="thumbsup-box floating-element">
                        <div class="thumbsup-emoji">&#x1F44D;</div>
                        <div style="font-size: 1.1rem; font-weight: 600; margin-bottom: 8px;">Early Exit Request</div>
                        <div style="font-size: 0.95rem;">
                            You are requesting to leave early. Only 1 Early Leave is permitted per month.
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            elif leave_type == "Half Day":
                st.markdown("""
                    <div class="metric-card floating-element">
                        <div style="font-size: 0.9rem; color: #6b46c1; font-weight: 500;">Leave Duration</div>
                        <div style="font-size: 2.5rem; font-weight: 700; color: #553c9a; margin: 10px 0;">0.5</div>
                        <div style="font-size: 0.9rem; color: #805ad5;">half day</div>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                    <div class="metric-card floating-element">
                        <div style="font-size: 0.9rem; color: #6b46c1; font-weight: 500;">Leave Duration</div>
                        <div style="font-size: 2.5rem; font-weight: 700; color: #553c9a; margin: 10px 0;">{no_of_days}</div>
                        <div style="font-size: 0.9rem; color: #805ad5;">working days</div>
                    </div>
                """, unsafe_allow_html=True)

    st.markdown("""
        <div style="margin-top: 2.5rem;">
            <div style="display: flex; align-items: center; margin-bottom: 1rem;">
                <div class="icon-badge" style="background: linear-gradient(135deg, #2196f3 0%, #03a9f4 100%);">&#x1F4DD;</div>
                <div>
                    <h3 style="margin: 0;">Additional Details</h3>
                    <p style="margin: 5px 0 0 0; color: #718096; font-size: 0.95rem;">
                        Provide detailed information about your leave request
                    </p>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    purpose = st.text_area(
        "Purpose of Leave", value=st.session_state.form_data_tab1['purpose'],
        placeholder="Please provide a clear and detailed explanation for your leave request...",
        height=120, help="Be specific about the reason for your leave", key="purpose_textarea"
    )

    leave_medical_doc = st.file_uploader(
        "Medical Certificate / Prescription",
        type=["pdf", "jpg", "jpeg", "png"],
        help="Upload a scanned copy or photo of the medical certificate or doctor's prescription",
        key=f"leave_medical_doc_uploader_{st.session_state.leave_file_uploader_key}"
    )

    superior_name = st.selectbox(
        "Reporting Manager or Team Leader",
        ["Select Manager"] + list(SUPERIORS.keys()), index=0,
        help="Select your direct reporting manager", key="superior_select"
    )

    submit_col1, submit_col2, submit_col3 = st.columns([1, 2, 1])
    with submit_col2:
        submit_button_disabled = st.session_state.get('submission_in_progress', False)
        if submit_button_disabled:
            st.info("Processing your submission... Please wait.")
        submit_button = st.button(
            "Submit Leave Request", type="primary", use_container_width=True,
            key="submit_leave_request", disabled=submit_button_disabled
        )

        if submit_button and not submit_button_disabled:
            st.session_state.submission_in_progress = True
            st.session_state.submission_completed = False
            form_data_for_check = {
                'employee_name': employee_name, 'employee_code': employee_code, 'purpose': purpose
            }
            is_duplicate, duplicate_message = check_duplicate_submission(form_data_for_check)
            if is_duplicate:
                st.session_state.submission_in_progress = False
                st.markdown(f"""
                    <div class="error-message">
                        <strong>Duplicate Submission Detected</strong><br>{duplicate_message}
                    </div>
                """, unsafe_allow_html=True)
            else:
                validation_passed = True
                error_messages = []
                if not all([employee_name, employee_code, employee_email,
                            department != "Select Department", purpose, superior_name != "Select Manager"]):
                    validation_passed = False
                    error_messages.append("Please complete all required fields")
                if employee_email and ("@" not in employee_email or "." not in employee_email):
                    validation_passed = False
                    error_messages.append("Please enter a valid email address")
                for i, cluster in enumerate(st.session_state.clusters):
                    if cluster['leave_type'] == "Select Type":
                        validation_passed = False
                        error_messages.append(f"Please select leave type for Period {i+1}")
                        break
                    if cluster['leave_type'] == "Full Day" and cluster['from_date'] > cluster['till_date']:
                        validation_passed = False
                        error_messages.append(f"End date must be after or equal to start date for Period {i+1}")
                        break
                if not validation_passed:
                    st.session_state.submission_in_progress = False
                    error_html = "<div class='error-message'><strong>Validation Error</strong><br>"
                    for error in error_messages:
                        error_html += f"{error}<br>"
                    error_html += "</div>"
                    st.markdown(error_html, unsafe_allow_html=True)
                else:
                    with st.spinner('Submitting your application...'):
                        submission_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        superior_email = SUPERIORS[superior_name]
                        sheet = setup_google_sheets()
                        if sheet:
                            try:
                                cluster_codes = {}
                                for i in range(len(st.session_state.clusters)):
                                    code = generate_approval_password(sheet)
                                    cluster_codes[i] = code
                                    log_debug(f"Generated unique code for period {i+1}: {code}")
                                for i, cluster in enumerate(st.session_state.clusters):
                                    no_of_days = calculate_days(cluster['from_date'], cluster['till_date'], cluster['leave_type'])
                                    row_data = [
                                        submission_date, employee_code.strip(), employee_name.strip(),
                                        department.strip(), cluster['leave_type'].strip(),
                                        str(no_of_days) if no_of_days is not None else "",
                                        purpose.strip(), cluster['from_date'].strftime("%Y-%m-%d"),
                                        cluster['till_date'].strftime("%Y-%m-%d"), superior_name.strip(),
                                        superior_email.strip(), "Pending", "", cluster_codes[i],
                                        "Yes" if is_cluster else "No",
                                        str(i+1) if is_cluster else "", employee_email.strip()
                                    ]
                                    while len(row_data) < 17: row_data.append("")
                                    row_data = row_data[:17]
                                    for j, item in enumerate(row_data):
                                        if not isinstance(item, str):
                                            row_data[j] = str(item) if item is not None else ""
                                    write_success = add_data_to_sheet1(sheet, row_data)
                                    if not write_success:
                                        log_debug(f"Error writing to Google Sheets for period {i+1}")
                                        st.error(f"Error writing to Google Sheets for period {i+1}")
                                        raise Exception(f"Failed to write to Google Sheets for period {i+1}")

                                if leave_medical_doc is not None:
                                    try:
                                        first_cluster = st.session_state.clusters[0]
                                        attachment_day_count = calculate_working_days(
                                            first_cluster['from_date'], first_cluster['till_date']
                                        )
                                        attachment_filename = generate_attachment_filename(
                                            employee_name, attachment_day_count, first_cluster['from_date']
                                        )
                                        upload_ok, upload_result = upload_file_to_drive(leave_medical_doc, attachment_filename)
                                        if upload_ok:
                                            log_debug(f"Leave attachment uploaded to Drive as {attachment_filename}")
                                        else:
                                            log_debug(f"Leave attachment upload failed: {upload_result}")
                                            st.warning("The attached document could not be uploaded automatically. Please share it with HR directly.")
                                    except Exception as att_err:
                                        log_debug(f"Leave attachment upload exception: {traceback.format_exc()}")
                                        st.warning("The attached document could not be uploaded automatically. Please share it with HR directly.")

                                email_sent = False
                                email_error = ""
                                if email_config["configured"]:
                                    try:
                                        clusters_for_email = []
                                        for cluster in st.session_state.clusters:
                                            cluster_copy = cluster.copy()
                                            cluster_copy['employee_code'] = employee_code
                                            cluster_copy['department'] = department
                                            cluster_copy['purpose'] = purpose
                                            clusters_for_email.append(cluster_copy)
                                        email_sent = send_approval_email(
                                            employee_name, superior_name, superior_email,
                                            employee_email, clusters_for_email, cluster_codes
                                        )
                                        if not email_sent:
                                            email_error = "Email sending failed - check debug logs"
                                    except Exception as e:
                                        email_error = f"Email exception: {str(e)}"
                                        log_debug(f"Email exception: {traceback.format_exc()}")

                                st.session_state.last_submission_hash = generate_submission_hash(form_data_for_check)
                                st.session_state.submission_timestamp = datetime.now()
                                st.session_state.submission_in_progress = False
                                st.session_state.submission_completed = True

                                if email_sent:
                                    st.markdown("""
                                        <div class="success-message">
                                            <div style="font-size: 3rem; margin-bottom: 1rem;">&#x2728;</div>
                                            <div style="font-size: 1.5rem; font-weight: 600; margin-bottom: 10px;">
                                                Application Submitted Successfully!
                                            </div>
                                            <div style="margin-bottom: 15px;">
                                                Your leave request has been sent to your manager for approval.
                                            </div>
                                            <div style="font-size: 0.95rem; opacity: 0.9;">
                                                Confirmation email sent to your email address.
                                            </div>
                                        </div>
                                    """, unsafe_allow_html=True)
                                    st.balloons()
                                    st.session_state.generated_codes.clear()
                                    st.session_state.reset_form_tab1 = True
                                    time.sleep(2)
                                    st.rerun()
                                else:
                                    st.session_state.cluster_codes = cluster_codes
                                    st.session_state.show_copy_section = True
                                    st.markdown(f"""
                                        <div class="info-box">
                                            <strong style="color: #ff9800;">&#x1F4E7; Email Notification Issue</strong><br>
                                            Your application was saved to the database successfully!<br>
                                            However, we could not send the email notification automatically.<br>
                                            <small>{email_error}</small>
                                        </div>
                                    """, unsafe_allow_html=True)
                                    st.markdown(f"""
                                        <div style="text-align: center; margin: 2rem 0;">
                                            <div style="font-size: 1.3rem; font-weight: 600; color: #673ab7; margin-bottom: 1rem;">
                                                Manual Approval Process
                                            </div>
                                            <p style="color: #718096; margin-bottom: 1.5rem;">
                                                Please share these approval codes with your manager <strong>{superior_name}</strong>:
                                            </p>
                                        </div>
                                    """, unsafe_allow_html=True)
                                    for i, cluster in enumerate(st.session_state.clusters):
                                        code = cluster_codes[i]
                                        days = calculate_days(cluster['from_date'], cluster['till_date'], cluster['leave_type'])
                                        days_display = "N/A" if cluster['leave_type'] == "Early Exit" else (f"{days} days" if cluster['leave_type'] == "Full Day" else "0.5 day")
                                        st.markdown(f"""
                                            <div style="background: {'#f8f9ff' if i % 2 == 0 else '#f0f2ff'}; padding: 1.5rem; border-radius: 12px; margin: 1rem 0; border-left: 4px solid #4dabf7;">
                                                <div style="display: flex; justify-content: space-between; align-items: center;">
                                                    <div>
                                                        <div style="font-size: 1.1rem; font-weight: 600; color: #339af0;">Period {i+1}</div>
                                                        <div style="font-size: 0.9rem; color: #718096;">
                                                            {cluster['from_date'].strftime('%Y-%m-%d')} to {cluster['till_date'].strftime('%Y-%m-%d')} &bull; {cluster['leave_type']} &bull; {days_display}
                                                        </div>
                                                    </div>
                                                    <div style="text-align: center;">
                                                        <div style="font-size: 0.9rem; color: #6b46c1; font-weight: 500;">Approval Code</div>
                                                        <div style="font-size: 2rem; font-weight: 700; color: #553c9a; letter-spacing: 4px; font-family: 'Courier New', monospace;">
                                                            {code}
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>
                                        """, unsafe_allow_html=True)
                                    st.balloons()
                                    st.session_state.generated_codes.clear()
                                    st.session_state.reset_form_tab1 = True
                                    time.sleep(2)
                                    st.rerun()

                            except Exception as e:
                                st.session_state.submission_in_progress = False
                                st.markdown(f"""
                                    <div class="error-message">
                                        <strong>Submission Error</strong><br>
                                        Please try again or contact HR<br>Error: {str(e)}
                                    </div>
                                """, unsafe_allow_html=True)
                                log_debug(f"Submission error: {traceback.format_exc()}")
                        else:
                            st.session_state.submission_in_progress = False
                            st.markdown("""
                                <div class="error-message">
                                    <strong>&#x1F4CA; Database Connection Error</strong><br>
                                    Could not connect to database. Please try again later.
                                </div>
                            """, unsafe_allow_html=True)


# ============================================================
# TAB 2: LEAVE APPROVAL PORTAL (Manager / Team Leader)
# ============================================================
with tab2:
    st.markdown("""
        <div class="section-header">
            <div class="icon-badge" style="background: linear-gradient(135deg, #2196f3 0%, #03a9f4 100%);">&#x2705;</div>
            <div>
                <h3 style="margin: 0;">Manager or Team Leader Approval Portal</h3>
                <p style="margin: 5px 0 0 0; color: #718096; font-size: 0.95rem;">
                    Securely approve or reject leave requests using the approval code
                </p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div style="background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
                    padding: 1.5rem; border-radius: 12px; margin-bottom: 2rem;
                    border: 1px solid rgba(33, 150, 243, 0.2);">
            <div style="display: flex; align-items: center;">
                <div style="font-size: 1.5rem; margin-right: 15px; color: #2196f3;">&#x1F512;</div>
                <div>
                    <strong style="color: #0d47a1;">Secure Authentication Required</strong><br>
                    <span style="color: #1565c0; font-size: 0.95rem;">
                        Use the unique 5-character approval code sent via email for authentication
                    </span>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    if st.session_state.reset_form_tab2:
        st.session_state.form_data_tab2 = {'approval_password': '', 'action': 'Select Decision'}
        st.session_state.reset_form_tab2 = False
        st.session_state.submission_in_progress = False

    approval_password_input = st.text_input(
        "Approval Code", value=st.session_state.form_data_tab2['approval_password'],
        type="password", placeholder="Enter 5-character code",
        help="Enter the unique code from the approval email", key="approval_code_input"
    )

    st.markdown("---")
    action_options = ["Select Decision", "Approve", "Reject"]
    action = st.selectbox(
        "Select Action", action_options, index=0,
        label_visibility="collapsed", key="action_select"
    )

    submit_decision_disabled = st.session_state.get('submission_in_progress', False)
    if submit_decision_disabled:
        st.info("Processing your decision... Please wait.")
    submit_decision_button = st.button(
        "Submit Decision", type="primary", use_container_width=True,
        key="submit_decision_button", disabled=submit_decision_disabled
    )

    if submit_decision_button and not submit_decision_disabled:
        st.session_state.submission_in_progress = True
        if not all([approval_password_input, action != "Select Decision"]):
            st.session_state.submission_in_progress = False
            st.markdown("""
                <div class="error-message">
                    <strong>Missing Information</strong><br>
                    Please enter approval code and select a decision
                </div>
            """, unsafe_allow_html=True)
        elif len(approval_password_input) != 5:
            st.session_state.submission_in_progress = False
            st.markdown("""
                <div class="error-message">
                    <strong>&#x1F511; Invalid Code Format</strong><br>
                    Please enter the exact 5-character code from the approval email
                </div>
            """, unsafe_allow_html=True)
        else:
            with st.spinner("Processing your decision..."):
                sheet = setup_google_sheets()
                if sheet:
                    status = "Approved" if action == "Approve" else "Rejected"
                    success = update_leave_status(sheet, approval_password_input, status)
                    if success:
                        st.session_state.submission_in_progress = False
                        status_color = "#155724" if status == "Approved" else "#721c24"
                        status_bg = "#d4edda" if status == "Approved" else "#f8d7da"
                        status_icon = "&#x2705;" if status == "Approved" else "&#x274C;"
                        st.markdown(f"""
                            <div style="background: {status_bg}; border-left: 4px solid {status_color};
                                      color: {status_color}; padding: 2rem; border-radius: 16px;
                                      margin: 2rem 0; text-align: center;">
                                <div style="font-size: 3rem; margin-bottom: 1rem;">{status_icon}</div>
                                <div style="font-size: 1.5rem; font-weight: 600; margin-bottom: 10px;">
                                    Decision Submitted Successfully!
                                </div>
                                <div style="margin-bottom: 15px;">
                                    The leave request has been <strong>{status.lower()}</strong>.
                                </div>
                                <div style="font-size: 0.95rem; opacity: 0.9;">
                                    Status email sent to employee &bull; Confirmation email sent to you
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                        st.balloons()
                        st.session_state.reset_form_tab2 = True
                        time.sleep(2)
                        st.rerun()
                    else:
                        st.session_state.submission_in_progress = False
                        st.markdown("""
                            <div class="error-message">
                                <strong>&#x1F510; Authentication Failed</strong><br>
                                Invalid code or code already used.<br>
                                Please check your approval code or contact HR for assistance.
                            </div>
                        """, unsafe_allow_html=True)
                else:
                    st.session_state.submission_in_progress = False
                    st.markdown("""
                        <div class="error-message">
                            <strong>&#x1F4CA; Database Connection Error</strong><br>
                            Could not connect to database. Please try again later.
                        </div>
                    """, unsafe_allow_html=True)


# ============================================================
# TAB 3: COMPANY HOLIDAYS
# ============================================================
with tab3:
    st.markdown("""
        <div class="section-header">
            <div class="icon-badge" style="background: linear-gradient(135deg, #2196f3 0%, #03a9f4 100%);">&#x1F4C5;</div>
            <div>
                <h3 style="margin: 0;">Company Holidays 2026</h3>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
        <div style="text-align: center; margin: 2rem 0; padding: 1.5rem;
                    background: var(--card-bg); border-radius: 16px;
                    border: 1px solid var(--border-color); box-shadow: 0 4px 12px var(--shadow-color);">
            <div style="font-size: 3rem; font-weight: 700; background: linear-gradient(135deg, #673ab7 0%, #9c27b0 100%);
                        -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                {len(HOLIDAYS_2026)}
            </div>
            <div style="font-size: 1.2rem; font-weight: 600; color: var(--text-primary); margin-top: 0.5rem;">
                Official Holidays in 2026
            </div>
        </div>
    """, unsafe_allow_html=True)

    holidays_data = []
    for holiday in HOLIDAYS_2026:
        day_month = holiday["date"].split("-")
        date_str = f"{day_month[0]} {day_month[1]} 2026"
        holidays_data.append({"Date": date_str, "Day": holiday["day"], "Holiday": holiday["holiday"]})

    df = pd.DataFrame(holidays_data)

    def style_day(val):
        if val == "Saturday":
            return f'<span class="day-badge day-saturday">{val}</span>'
        elif val == "Sunday":
            return f'<span class="day-badge day-sunday">{val}</span>'
        else:
            return f'<span class="day-badge day-weekday">{val}</span>'

    df["Day"] = df["Day"].apply(style_day)
    html_table = df.to_html(escape=False, index=False)
    st.markdown(f'<div class="holidays-table-wrapper">{html_table}</div>', unsafe_allow_html=True)


# ============================================================
# TAB 4: WFH / OUT OF OFFICE REQUEST (Submit)
# ============================================================
with tab4:
    st.markdown("""
        <div class="section-header">
            <div class="icon-badge" style="background: linear-gradient(135deg, #38d9a9 0%, #20c997 100%);">&#x1F3E0;</div>
            <div>
                <h3 style="margin: 0;">Work From Home / Out of Office Request</h3>
                <p style="margin: 5px 0 0 0; color: #718096; font-size: 0.95rem;">
                    Submit requests for remote work or official out-of-office assignments
                </p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div style="background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
                    padding: 1.5rem; border-radius: 12px; margin-bottom: 2rem;
                    border: 1px solid rgba(33, 150, 243, 0.2);">
            <div style="display: flex; align-items: center;">
                <div style="font-size: 1.5rem; margin-right: 15px; color: #2196f3;">&#x2139;&#xFE0F;</div>
                <div>
                    <strong style="color: #0d47a1;">How it works</strong><br>
                    <span style="color: #1565c0; font-size: 0.95rem;">
                        Your request will be sent to <strong>HR and Sandip Sir</strong> for review.
                        HR will approve or reject via the WFH Approval Portal, and you will be notified by email.
                    </span>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    if st.session_state.reset_form_tab4:
        st.session_state.form_data_tab4 = {
            'employee_name': '', 'employee_code': '', 'employee_email': '',
            'request_type': 'Select Type',
            'start_date': datetime.now().date(), 'end_date': datetime.now().date(),
            'reason': ''
        }
        st.session_state.reset_form_tab4 = False
        st.session_state.submission_in_progress = False
        st.session_state.wfh_file_uploader_key += 1

    col1, col2, col3 = st.columns([1, 1, 1], gap="large")
    with col1:
        wfh_employee_name = st.text_input(
            "Employee Name", value=st.session_state.form_data_tab4['employee_name'],
            placeholder="Enter your full name", key="wfh_employee_name"
        )
    with col2:
        wfh_employee_code = st.text_input(
            "Employee Code", value=st.session_state.form_data_tab4['employee_code'],
            placeholder="e.g., VF-EMP-001", key="wfh_employee_code"
        )
    with col3:
        wfh_employee_email = st.text_input(
            "Employee Email", value=st.session_state.form_data_tab4['employee_email'],
            placeholder="your.email@company.com", key="wfh_employee_email"
        )

    st.markdown("---")
    st.markdown("""
        <div style="margin-bottom: 1.5rem;">
            <div style="display: flex; align-items: center; margin-bottom: 1rem;">
                <div class="icon-badge" style="background: linear-gradient(135deg, #4dabf7 0%, #339af0 100%);">&#x1F4CB;</div>
                <div>
                    <h4 style="margin: 0;">Request Type</h4>
                    <p style="margin: 5px 0 0 0; color: #718096; font-size: 0.9rem;">
                        Select the type of request you are submitting
                    </p>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    wfh_request_type = st.selectbox(
        "Select Request Type",
        ["Select Type", "Work From Home", "Out of Office for Official Work"],
        index=0, key="wfh_request_type"
    )

    st.markdown("---")
    st.markdown("""
        <div style="margin-bottom: 1.5rem;">
            <div style="display: flex; align-items: center; margin-bottom: 1rem;">
                <div class="icon-badge" style="background: linear-gradient(135deg, #4caf50 0%, #388e3c 100%);">&#x1F4C5;</div>
                <div>
                    <h4 style="margin: 0;">Date Range</h4>
                    <p style="margin: 5px 0 0 0; color: #718096; font-size: 0.9rem;">
                        Select the start and end dates for your request
                    </p>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    col3, col4 = st.columns([1, 1], gap="large")
    with col3:
        wfh_start_date = st.date_input(
            "Start Date", value=st.session_state.form_data_tab4['start_date'],
            min_value=datetime.now().date() - timedelta(days=60), key="wfh_start_date"
        )
    with col4:
        wfh_end_date = st.date_input(
            "End Date", value=st.session_state.form_data_tab4['end_date'],
            min_value=datetime.now().date() - timedelta(days=60), key="wfh_end_date"
        )

    if wfh_start_date and wfh_end_date:
        if wfh_end_date < wfh_start_date:
            st.error("End date cannot be before start date")
        else:
            total_days_wfh = (wfh_end_date - wfh_start_date).days + 1
            st.markdown(f"""
                <div style="background: linear-gradient(135deg, #4dabf7 0%, #339af0 100%);
                            color: white; padding: 1rem; border-radius: 12px; text-align: center; margin: 1rem 0;">
                    <div style="font-size: 0.9rem;">Total Duration</div>
                    <div style="font-size: 2rem; font-weight: bold;">{total_days_wfh}</div>
                    <div style="font-size: 0.8rem;">day(s)</div>
                </div>
            """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
        <div style="margin-bottom: 1.5rem;">
            <div style="display: flex; align-items: center; margin-bottom: 1rem;">
                <div class="icon-badge" style="background: linear-gradient(135deg, #ff9800 0%, #f57c00 100%);">&#x1F4DD;</div>
                <div>
                    <h4 style="margin: 0;">Reason for Request</h4>
                    <p style="margin: 5px 0 0 0; color: #718096; font-size: 0.9rem;">
                        Provide a detailed explanation for your request
                    </p>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    wfh_reason = st.text_area(
        "Reason / Purpose", value=st.session_state.form_data_tab4['reason'],
        placeholder="Please provide a clear and detailed explanation for your request...",
        height=150, key="wfh_reason"
    )

    wfh_medical_doc = st.file_uploader(
        "Medical Certificate / Prescription",
        type=["pdf", "jpg", "jpeg", "png"],
        help="Upload a scanned copy or photo of the medical certificate or doctor's prescription",
        key=f"wfh_medical_doc_uploader_{st.session_state.wfh_file_uploader_key}"
    )

    st.markdown("---")
    submit_col1, submit_col2, submit_col3 = st.columns([1, 2, 1])
    with submit_col2:
        wfh_submit_disabled = st.session_state.get('submission_in_progress', False)
        if wfh_submit_disabled:
            st.info("Processing your submission... Please wait.")
        wfh_submit_button = st.button(
            "Submit Request", type="primary", use_container_width=True,
            key="submit_wfh_request", disabled=wfh_submit_disabled
        )

        if wfh_submit_button and not wfh_submit_disabled:
            st.session_state.submission_in_progress = True
            wfh_form_data = {
                'employee_name': wfh_employee_name,
                'employee_code': wfh_employee_code,
                'request_type': wfh_request_type,
                'start_date': wfh_start_date,
                'end_date': wfh_end_date,
                'reason': wfh_reason
            }
            is_duplicate, duplicate_message = check_duplicate_wfh_submission(wfh_form_data)
            if is_duplicate:
                st.session_state.submission_in_progress = False
                st.markdown(f"""
                    <div class="error-message">
                        <strong>Duplicate Submission Detected</strong><br>{duplicate_message}
                    </div>
                """, unsafe_allow_html=True)
            else:
                validation_passed = True
                error_messages = []
                if not all([wfh_employee_name, wfh_employee_code,
                            wfh_request_type != "Select Type", wfh_reason]):
                    validation_passed = False
                    error_messages.append("Please complete all required fields (Name, Code, Request Type, Reason)")
                if wfh_employee_email and ("@" not in wfh_employee_email or "." not in wfh_employee_email):
                    validation_passed = False
                    error_messages.append("Please enter a valid employee email address")
                if wfh_end_date < wfh_start_date:
                    validation_passed = False
                    error_messages.append("End date cannot be before start date")
                if not validation_passed:
                    st.session_state.submission_in_progress = False
                    error_html = "<div class='error-message'><strong>Validation Error</strong><br>"
                    for error in error_messages:
                        error_html += f"{error}<br>"
                    error_html += "</div>"
                    st.markdown(error_html, unsafe_allow_html=True)
                else:
                    with st.spinner('Submitting your request...'):
                        success, message = submit_wfh_request(
                            wfh_employee_name, wfh_employee_code, wfh_employee_email,
                            wfh_request_type, wfh_start_date, wfh_end_date, wfh_reason,
                            medical_doc=wfh_medical_doc
                        )
                        if success:
                            st.session_state.last_wfh_submission_hash = generate_wfh_hash(wfh_form_data)
                            st.session_state.wfh_submission_timestamp = datetime.now()
                            st.session_state.submission_in_progress = False
                            duration_wfh = (wfh_end_date - wfh_start_date).days + 1
                            st.markdown(f"""
                                <div class="success-message">
                                    <div style="font-size: 3rem; margin-bottom: 1rem;">&#x2728;</div>
                                    <div style="font-size: 1.5rem; font-weight: 600; margin-bottom: 10px;">
                                        Request Submitted Successfully!
                                    </div>
                                    <div style="margin-bottom: 15px;">
                                        Your {wfh_request_type.lower()} request has been submitted.
                                        HR and Sandip Sir have been notified.
                                    </div>
                                    <div style="font-size: 0.95rem; opacity: 0.9;">
                                        Request Type: {wfh_request_type}<br>
                                        Duration: {duration_wfh} day(s)<br>
                                        You will receive an email once a decision is made.
                                    </div>
                                </div>
                            """, unsafe_allow_html=True)
                            st.balloons()
                            st.session_state.reset_form_tab4 = True
                            time.sleep(2)
                            st.rerun()
                        else:
                            st.session_state.submission_in_progress = False
                            st.markdown(f"""
                                <div class="error-message">
                                    <strong>&#x274C; Submission Error</strong><br>
                                    {message}<br>
                                    Please try again or contact HR for assistance.
                                </div>
                            """, unsafe_allow_html=True)


# ============================================================
# TAB 5: WFH / OOO APPROVAL PORTAL (HR Only)
# ============================================================
with tab5:
    st.markdown("""
        <div class="section-header">
            <div class="icon-badge" style="background: linear-gradient(135deg, #20c997 0%, #0ca678 100%);">&#x1F4F2;</div>
            <div>
                <h3 style="margin: 0;">WFH / Out of Office Approval Portal</h3>
                <p style="margin: 5px 0 0 0; color: #718096; font-size: 0.95rem;">
                    For HR use only — Approve or reject WFH / Out of Office requests
                </p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div style="background: linear-gradient(135deg, #e0f7f4 0%, #b2dfdb 100%);
                    padding: 1.5rem; border-radius: 12px; margin-bottom: 2rem;
                    border: 1px solid rgba(32, 201, 151, 0.3);">
            <div style="display: flex; align-items: center;">
                <div style="font-size: 1.5rem; margin-right: 15px; color: #0ca678;">&#x1F512;</div>
                <div>
                    <strong style="color: #065f46;">HR Authentication Required</strong><br>
                    <span style="color: #047857; font-size: 0.95rem;">
                        Enter the 5-character WFH approval code received in the email from HR System.
                        This portal is for <strong>HR use only</strong>. Employees will be notified automatically once a decision is submitted.
                    </span>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    if st.session_state.reset_form_tab5:
        st.session_state.form_data_tab5 = {'wfh_approval_password': '', 'wfh_action': 'Select Decision'}
        st.session_state.reset_form_tab5 = False
        st.session_state.submission_in_progress = False

    st.markdown("""
        <div style="margin-bottom: 1.5rem;">
            <div style="display: flex; align-items: center; margin-bottom: 1rem;">
                <div class="icon-badge" style="background: linear-gradient(135deg, #20c997 0%, #0ca678 100%);">&#x1F511;</div>
                <div>
                    <h4 style="margin: 0;">Enter WFH Approval Code</h4>
                    <p style="margin: 5px 0 0 0; color: #718096; font-size: 0.9rem;">
                        The 5-character code was sent to HR email when the employee submitted the request
                    </p>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    wfh_code_input = st.text_input(
        "WFH Approval Code",
        value=st.session_state.form_data_tab5['wfh_approval_password'],
        type="password",
        placeholder="Enter 5-character WFH approval code",
        help="Enter the unique code from the WFH approval email sent to HR",
        key="wfh_approval_code_input"
    )

    st.markdown("---")
    st.markdown("""
        <div style="margin-bottom: 1.5rem;">
            <div style="display: flex; align-items: center; margin-bottom: 1rem;">
                <div class="icon-badge" style="background: linear-gradient(135deg, #4caf50 0%, #388e3c 100%);">&#x1F4CB;</div>
                <div>
                    <h4 style="margin: 0;">HR Decision</h4>
                    <p style="margin: 5px 0 0 0; color: #718096; font-size: 0.9rem;">
                        Select your decision for this WFH / Out of Office request
                    </p>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    wfh_action = st.selectbox(
        "Select Decision",
        ["Select Decision", "Approve", "Reject"],
        index=0,
        label_visibility="collapsed",
        key="wfh_action_select"
    )

    st.markdown("---")
    submit_col1, submit_col2, submit_col3 = st.columns([1, 2, 1])
    with submit_col2:
        wfh_decision_disabled = st.session_state.get('submission_in_progress', False)
        if wfh_decision_disabled:
            st.info("Processing your decision... Please wait.")
        wfh_decision_button = st.button(
            "Submit WFH Decision", type="primary", use_container_width=True,
            key="submit_wfh_decision_button", disabled=wfh_decision_disabled
        )

        if wfh_decision_button and not wfh_decision_disabled:
            st.session_state.submission_in_progress = True

            # Validation
            if not wfh_code_input or wfh_action == "Select Decision":
                st.session_state.submission_in_progress = False
                st.markdown("""
                    <div class="error-message">
                        <strong>&#x26A0;&#xFE0F; Missing Information</strong><br>
                        Please enter the WFH approval code and select a decision.
                    </div>
                """, unsafe_allow_html=True)
            elif len(wfh_code_input) != 5:
                st.session_state.submission_in_progress = False
                st.markdown("""
                    <div class="error-message">
                        <strong>&#x1F511; Invalid Code Format</strong><br>
                        Please enter the exact 5-character WFH approval code from the email.
                    </div>
                """, unsafe_allow_html=True)
            else:
                with st.spinner("Processing your WFH decision..."):
                    wfh_sheet = setup_wfh_sheet()
                    if wfh_sheet:
                        wfh_status = "Approved" if wfh_action == "Approve" else "Rejected"
                        wfh_success = update_wfh_status(wfh_sheet, wfh_code_input, wfh_status)
                        if wfh_success:
                            st.session_state.submission_in_progress = False
                            status_color = "#155724" if wfh_status == "Approved" else "#721c24"
                            status_bg = "#d4edda" if wfh_status == "Approved" else "#f8d7da"
                            status_icon = "&#x2705;" if wfh_status == "Approved" else "&#x274C;"
                            st.markdown(f"""
                                <div style="background: {status_bg}; border-left: 4px solid {status_color};
                                          color: {status_color}; padding: 2rem; border-radius: 16px;
                                          margin: 2rem 0; text-align: center;">
                                    <div style="font-size: 3rem; margin-bottom: 1rem;">{status_icon}</div>
                                    <div style="font-size: 1.5rem; font-weight: 600; margin-bottom: 10px;">
                                        WFH Decision Submitted Successfully!
                                    </div>
                                    <div style="margin-bottom: 15px;">
                                        The WFH / Out of Office request has been <strong>{wfh_status.lower()}</strong>.
                                    </div>
                                    <div style="font-size: 0.95rem; opacity: 0.9;">
                                        &#x2709;&#xFE0F; The employee has been notified by email.<br>
                                        A confirmation has been sent to HR.
                                    </div>
                                </div>
                            """, unsafe_allow_html=True)
                            st.balloons()
                            st.session_state.reset_form_tab5 = True
                            time.sleep(2)
                            st.rerun()
                        else:
                            st.session_state.submission_in_progress = False
                            st.markdown("""
                                <div class="error-message">
                                    <strong>&#x1F510; Authentication Failed</strong><br>
                                    Invalid WFH code or code has already been used.<br>
                                    Please check the code from the HR email or contact the system administrator.
                                </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.session_state.submission_in_progress = False
                        st.markdown("""
                            <div class="error-message">
                                <strong>&#x1F4CA; Database Connection Error</strong><br>
                                Could not connect to the WFH database. Please try again later.
                            </div>
                        """, unsafe_allow_html=True)


# ============================================================
# FOOTER
# ============================================================
st.markdown("""
    <div class="footer">
        <div style="margin-bottom: 1rem;">
            <strong style="color: #673ab7;">VOLAR FASHION PVT LTD</strong><br>
            Human Resources Management System
        </div>
        <div style="font-size: 0.9rem;">
            hrvolarfashion@gmail.com<br>
            &copy; 2026 VOLAR FASHION.
        </div>
    </div>
""", unsafe_allow_html=True)
