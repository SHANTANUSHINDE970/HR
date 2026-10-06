import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import time
import secrets
import string
import traceback
import ssl
from email.utils import formataddr
import uuid
import hashlib
from html import escape as html_escape

# ============================================================
# PAGE CONFIGURATION
# ============================================================
st.set_page_config(
    page_title="ANULACH FASHION - Leave Management",
    page_icon="\u2728",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================
# CSS
# ============================================================
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
        .main  { background-color: var(--bg-primary) !important; }
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
        .stTextArea textarea::placeholder {
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
        to   { opacity: 1; transform: translateY(0); }
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

    .metric-card {
        background: linear-gradient(135deg, #f3e5f5 0%, #e1bee7 100%);
        padding: 1.5rem;
        border-radius: 16px;
        text-align: center;
        box-shadow: 0 8px 20px rgba(156, 39, 176, 0.1);
        border: 1px solid rgba(156, 39, 176, 0.1);
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
    .cluster-header p  { color: #dbeafe !important; margin: 5px 0 0 0; font-size: 0.95rem; }

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
    footer      {visibility: hidden;}
    header      {visibility: hidden;}

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
        50%       { transform: translateY(-10px); }
    }

    ::-webkit-scrollbar { width: 8px; }
    ::-webkit-scrollbar-track { background: var(--bg-tertiary); border-radius: 4px; }
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
        border-radius: 4px;
    }

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
# All leave approvals go directly to HR
HR_NAME  = "Hr"
HR_EMAIL = "hr@anulachfashion.com"

# Leave types available in the leave application form
LEAVE_TYPES = ["Select Type", "Full Day", "Half Day"]

# ---------- Out-of-Office (OOO) settings ----------
# The workbook is the same one used for leave ("Leave_Applications").
# OOO requests are stored in their OWN worksheet (tab) inside that workbook.
# The worksheet is created automatically the first time it is needed.
# (The worksheet name is unchanged so that existing OOO data stays in the same tab.)
WFH_WORKSHEET_NAME = "anulach OOO and WFH"

# The only request type available in the OOO form
OOO_REQUEST_TYPE = "Out of Office for Official Work"

WFH_HEADERS = [
    "Submission Date", "Employee Name", "Employee Code", "Employee Email",
    "Request Type", "Start Date", "End Date", "Reason",
    "Status", "Approval Date", "Approval Code",
]

# Everyone listed here receives the OOO approval request (with the approval code).
# HR then approves / rejects it from the "OOO Approval" tab.
# Same recipient as the Volar app: HR at hrvolarfashion@gmail.com.
# (Leave approvals above still go to HR_EMAIL; only OOO uses this list.)
WFH_APPROVAL_RECIPIENTS = {
    "HR": "hrvolarfashion@gmail.com",
    "Sandip": "sandip@ragunited.com",   # <- remove the leading # to also send to Sandip
}

# ============================================================
# SESSION STATE INITIALISATION
# ============================================================
if "clusters" not in st.session_state:
    st.session_state.clusters = [{
        "cluster_number": 1, "leave_type": "Select Type",
        "from_date": datetime.now().date(), "till_date": datetime.now().date(),
        "approval_code": "",
    }]
if "reset_form_tab1" not in st.session_state: st.session_state.reset_form_tab1 = False
if "reset_form_tab2" not in st.session_state: st.session_state.reset_form_tab2 = False
if "reset_form_tab4" not in st.session_state: st.session_state.reset_form_tab4 = False
if "reset_form_tab5" not in st.session_state: st.session_state.reset_form_tab5 = False

if "form_data_tab1" not in st.session_state:
    st.session_state.form_data_tab1 = {
        "employee_name": "", "employee_code": "",
        "purpose": "", "is_cluster": False,
    }
if "form_data_tab2" not in st.session_state:
    st.session_state.form_data_tab2 = {"approval_password": "", "action": "Select Decision"}

if "cluster_codes"          not in st.session_state: st.session_state.cluster_codes          = {}
if "show_copy_section"      not in st.session_state: st.session_state.show_copy_section      = False
if "test_email_result"      not in st.session_state: st.session_state.test_email_result      = None
if "email_config_status"    not in st.session_state: st.session_state.email_config_status    = "Not Tested"
if "debug_logs"             not in st.session_state: st.session_state.debug_logs             = []
if "generated_codes"        not in st.session_state: st.session_state.generated_codes        = set()
if "submission_in_progress" not in st.session_state: st.session_state.submission_in_progress = False
if "submission_completed"   not in st.session_state: st.session_state.submission_completed   = False
if "last_submission_hash"   not in st.session_state: st.session_state.last_submission_hash   = None
if "submission_timestamp"   not in st.session_state: st.session_state.submission_timestamp   = None

# OOO state (kept separate from the leave flags so the tabs never block each other)
if "generated_wfh_codes"         not in st.session_state: st.session_state.generated_wfh_codes         = set()
if "wfh_submission_in_progress"  not in st.session_state: st.session_state.wfh_submission_in_progress  = False
if "wfh_decision_in_progress"    not in st.session_state: st.session_state.wfh_decision_in_progress    = False
if "last_wfh_submission_hash"    not in st.session_state: st.session_state.last_wfh_submission_hash    = None
if "wfh_submission_timestamp"    not in st.session_state: st.session_state.wfh_submission_timestamp    = None

# ============================================================
# UTILITY / LOGGING
# ============================================================
def add_debug_log(message, level="INFO"):
    timestamp = datetime.now().strftime("%H:%M:%S")
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
            log_debug(f"Google credentials NOT found. Available keys: {available}")
            st.error(f"Google credentials not found. Available keys: {available}.")
            return None
        try:
            creds_dict = {
                "type":                        st.secrets[secrets_key]["type"],
                "project_id":                  st.secrets[secrets_key]["project_id"],
                "private_key_id":              st.secrets[secrets_key]["private_key_id"],
                "private_key":                 st.secrets[secrets_key]["private_key"],
                "client_email":                st.secrets[secrets_key]["client_email"],
                "client_id":                   st.secrets[secrets_key]["client_id"],
                "auth_uri":                    st.secrets[secrets_key]["auth_uri"],
                "token_uri":                   st.secrets[secrets_key]["token_uri"],
                "auth_provider_x509_cert_url": st.secrets[secrets_key]["auth_provider_x509_cert_url"],
                "client_x509_cert_url":        st.secrets[secrets_key]["client_x509_cert_url"],
            }
        except KeyError as e:
            log_debug(f"Missing key in [{secrets_key}]: {str(e)}")
            st.error(f"Missing field in [{secrets_key}] section: {str(e)}")
            return None
        required_fields = ["type", "project_id", "private_key_id", "private_key", "client_email"]
        missing_fields  = [f for f in required_fields if not creds_dict.get(f)]
        if missing_fields:
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
        log_debug(f"Google credentials loaded for: {creds_dict['client_email']}")
        return creds_dict
    except Exception as e:
        log_debug(f"Error getting Google credentials: {traceback.format_exc()}")
        st.error(f"Error loading Google credentials: {str(e)}")
        return None


# ============================================================
# GOOGLE SHEETS SETUP
# ============================================================
def setup_google_sheets():
    """Connect to the 'Anulach' worksheet inside the Leave_Applications workbook."""
    try:
        log_debug("Setting up Google Sheets connection...")
        SCOPES = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds_dict = get_google_credentials()
        if not creds_dict:
            st.error("No Google credentials found")
            return None
        try:
            creds  = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, SCOPES)
            client = gspread.authorize(creds)
        except Exception as e:
            log_debug(f"Error creating credentials: {str(e)}")
            raise e
        SHEET_NAME      = "Leave_Applications"    # workbook name
        WORKSHEET_NAME  = "Anulach"               # tab name inside the workbook
        try:
            spreadsheet = client.open(SHEET_NAME)
            sheet       = spreadsheet.worksheet(WORKSHEET_NAME)
            log_debug(f"Connected to worksheet '{WORKSHEET_NAME}' in workbook '{SHEET_NAME}'")
            try:
                if sheet.row_count == 0 or not sheet.row_values(1):
                    headers = [
                        "Submission Date", "Employee Code", "Employee Name",
                        "Type of Leave", "No of Days", "Purpose of Leave", "From Date",
                        "To Date", "Superior or Team leader Name", "Superior or Team leader Email",
                        "Status", "Approval Date", "Approval Password", "Cluster (Yes/No)",
                        "Cluster leave Number",
                    ]
                    sheet.append_row(headers)
                    log_debug("Added headers to sheet")
            except Exception as e:
                log_debug(f"Warning: Could not check/add headers: {str(e)}")
            return sheet
        except gspread.SpreadsheetNotFound:
            st.error(f"Google Workbook '{SHEET_NAME}' not found!")
            st.info(f"Make sure the workbook is named '{SHEET_NAME}' and shared with: {creds_dict.get('client_email', '')}")
            return None
        except Exception as e:
            st.error(f"Error accessing sheet: {str(e)}")
            return None
    except Exception as e:
        log_debug(f"setup_google_sheets error: {traceback.format_exc()}")
        st.error(f"Error in setup_google_sheets: {str(e)}")
        return None


def setup_wfh_sheet():
    """
    Connect to the 'anulach OOO and WFH' worksheet inside the SAME workbook
    ('Leave_Applications'). The worksheet is created automatically if it does not exist.
    This worksheet stores the Out-of-Office (OOO) requests.

    Columns:
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
        log_debug("Setting up OOO Google Sheets connection...")
        SCOPES = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds_dict = get_google_credentials()
        if not creds_dict:
            st.error("No Google credentials found")
            return None
        try:
            creds  = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, SCOPES)
            client = gspread.authorize(creds)
        except Exception as e:
            log_debug(f"Error creating credentials for OOO sheet: {str(e)}")
            raise e
        WORKBOOK_NAME = "Leave_Applications"
        try:
            spreadsheet = client.open(WORKBOOK_NAME)
        except gspread.SpreadsheetNotFound:
            st.error(f"Google Workbook '{WORKBOOK_NAME}' not found!")
            st.info(f"Make sure the workbook is named '{WORKBOOK_NAME}' and shared with: {creds_dict.get('client_email', '')}")
            return None

        try:
            sheet = spreadsheet.worksheet(WFH_WORKSHEET_NAME)
            log_debug(f"Connected to worksheet '{WFH_WORKSHEET_NAME}'")
        except gspread.exceptions.WorksheetNotFound:
            log_debug(f"Worksheet '{WFH_WORKSHEET_NAME}' not found - creating it...")
            sheet = spreadsheet.add_worksheet(title=WFH_WORKSHEET_NAME, rows=1000, cols=len(WFH_HEADERS))
            log_debug(f"Created worksheet '{WFH_WORKSHEET_NAME}'")

        try:
            if not sheet.row_values(1):
                sheet.insert_row(WFH_HEADERS, index=1)
                log_debug("Added headers to OOO worksheet")
        except Exception as e:
            log_debug(f"Warning: Could not check/add headers on OOO worksheet: {str(e)}")
        return sheet
    except Exception as e:
        log_debug(f"setup_wfh_sheet error: {traceback.format_exc()}")
        st.error(f"Error in setup_wfh_sheet: {str(e)}")
        return None


# ============================================================
# EMAIL CREDENTIALS
# ============================================================
def get_email_credentials():
    try:
        log_debug("Getting email credentials from secrets...")
        sender_email    = None
        sender_password = None
        source          = ""
        email_sections  = ["EMAIL", "email", "gmail", "GMAIL", "SMTP", "smtp"]
        email_keys      = ["sender_email", "email", "EMAIL", "user", "USER", "username", "USERNAME"]
        password_keys   = ["sender_password", "password", "PASSWORD", "app_password", "APP_PASSWORD", "pass", "PASS"]
        for section in email_sections:
            if section in st.secrets:
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
            direct_email_keys = ["EMAIL_SENDER", "sender_email", "email", "EMAIL", "GMAIL_USER"]
            direct_pass_keys  = ["EMAIL_PASSWORD", "sender_password", "password", "PASSWORD", "GMAIL_PASSWORD", "APP_PASSWORD"]
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
            log_debug(f"Email credentials loaded. Email={sender_email}, Source={source}")
            return sender_email, sender_password, source
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
                "details": f"Source info: {source}.", "source": source}
    if "@" not in sender_email or "." not in sender_email:
        return {"configured": False, "message": "Invalid email format",
                "details": f"Email '{sender_email}' doesn't look valid", "source": source}
    password_type = "App Password (16 chars)" if len(sender_password) == 16 else f"Password ({len(sender_password)} chars)"
    return {"configured": True, "sender_email": sender_email, "source": source,
            "password_type": password_type, "password_length": len(sender_password),
            "message": f"Email credentials found ({password_type})", "details": f"Loaded from: {source}"}


# ============================================================
# SMTP CONNECTION
# ============================================================
def create_smtp_connection(sender_email, sender_password):
    server             = None
    error_messages     = []
    try:
        log_debug("Trying SMTP_SSL on port 465...")
        context = ssl.create_default_context()
        server  = smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=10, context=context)
        server.login(sender_email, sender_password)
        return server, "SMTP_SSL (Port 465)"
    except Exception as e1:
        error_messages.append(f"Port 465 failed: {str(e1)}")
        if server:
            try: server.quit()
            except: pass
    try:
        log_debug("Trying STARTTLS on port 587...")
        server = smtplib.SMTP("smtp.gmail.com", 587, timeout=10)
        server.ehlo()
        server.starttls(context=ssl.create_default_context())
        server.ehlo()
        server.login(sender_email, sender_password)
        return server, "STARTTLS (Port 587)"
    except Exception as e2:
        error_messages.append(f"Port 587 failed: {str(e2)}")
        if server:
            try: server.quit()
            except: pass
    for port in [25, 2525]:
        try:
            server = smtplib.SMTP("smtp.gmail.com", port, timeout=10)
            server.starttls(context=ssl.create_default_context())
            server.login(sender_email, sender_password)
            return server, f"Port {port}"
        except Exception as e:
            error_messages.append(f"Port {port} failed: {str(e)}")
            if server:
                try: server.quit()
                except: pass
    return None, f"All methods failed: {' | '.join(error_messages)}"


def test_email_connection(test_recipient=None):
    try:
        sender_email, sender_password, source = get_email_credentials()
        if not sender_email or not sender_password:
            return {"success": False, "message": "Email credentials not configured",
                    "details": "Please check your Streamlit secrets",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        recipient  = test_recipient or sender_email
        msg        = MIMEMultipart()
        msg["From"]    = formataddr(("ANULACH FASHION HR", sender_email))
        msg["To"]      = recipient
        msg["Subject"] = "ANULACH FASHION - Email Configuration Test"
        test_time  = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        body = (f"This is a test email from ANULACH FASHION Leave Management System.\n\n"
                f"Time: {test_time}\nSender: {sender_email}\nRecipient: {recipient}\nSource: {source}\n\n"
                f"Email configuration is working correctly!\n\n-- ANULACH FASHION HR Department")
        msg.attach(MIMEText(body, "plain"))
        server, method = create_smtp_connection(sender_email, sender_password)
        if server:
            try:
                server.sendmail(sender_email, recipient, msg.as_string())
                server.quit()
                return {"success": True, "message": f"Email sent via {method}",
                        "details": f"Test email sent to {recipient} at {test_time}",
                        "method": method, "sender": sender_email, "timestamp": test_time}
            except Exception as e:
                try: server.quit()
                except: pass
                return {"success": False, "message": "Failed to send email",
                        "details": f"Error: {str(e)}", "sender": sender_email, "timestamp": test_time}
        return {"success": False, "message": "SMTP Connection Failed",
                "details": f"Error: {method}", "sender": sender_email, "timestamp": test_time}
    except Exception as e:
        return {"success": False, "message": "Unexpected Error",
                "details": f"Error: {str(e)}",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}


# ============================================================
# APPROVAL CODE GENERATION (Leave)
# ============================================================
def get_existing_codes_from_sheet(sheet):
    try:
        if not sheet:
            return set()
        all_records    = sheet.get_all_values()
        existing_codes = set()
        for idx, row in enumerate(all_records):
            if idx == 0:
                continue
            if len(row) > 12 and row[12]:
                existing_codes.add(row[12])
        log_debug(f"Found {len(existing_codes)} existing codes in sheet")
        return existing_codes
    except Exception as e:
        log_debug(f"Error getting existing codes: {str(e)}")
        return set()


def generate_approval_password(sheet=None):
    alphabet = string.ascii_uppercase + string.digits
    alphabet = alphabet.replace("0","").replace("O","").replace("1","").replace("I","").replace("L","")
    existing_codes = set()
    if sheet:
        existing_codes = get_existing_codes_from_sheet(sheet)
    existing_codes.update(st.session_state.generated_codes)
    for attempt in range(20):
        password = "".join(secrets.choice(alphabet) for _ in range(5))
        if password not in existing_codes:
            st.session_state.generated_codes.add(password)
            log_debug(f"Generated unique approval code: {password} (attempt {attempt+1})")
            return password
    # Fallback
    base36     = "23456789ABCDEFGHJKMNPQRSTUVWXYZ"
    timestamp  = int(time.time() * 1000)
    code       = ""
    temp       = timestamp
    while temp > 0 and len(code) < 3:
        temp, r = divmod(temp, 36)
        code    = base36[r] + code
    while len(code) < 5:
        code += secrets.choice(base36)
    if code not in existing_codes:
        st.session_state.generated_codes.add(code)
        return code
    for i in range(1, 100):
        fc = f"{code[:4]}{i}"
        if fc not in existing_codes:
            st.session_state.generated_codes.add(fc)
            return fc
    final = "".join([c for c in str(uuid.uuid4().int)[:5].upper() if c in alphabet])
    while len(final) < 5:
        final += secrets.choice(alphabet)
    st.session_state.generated_codes.add(final)
    return final


# ============================================================
# CALCULATIONS
# ============================================================
def calculate_working_days(from_date, till_date):
    return (till_date - from_date).days + 1


def calculate_days(from_date, till_date, leave_type):
    if leave_type == "Half Day":
        return 0.5
    return calculate_working_days(from_date, till_date)


# ============================================================
# SHEET INSERT HELPER (used for both the leave sheet and the OOO sheet)
# ============================================================
def add_data_to_sheet(sheet, row_data):
    try:
        all_records   = sheet.get_all_values()
        next_row      = 2
        found_empty   = False
        if len(all_records) > 1:
            for i in range(1, len(all_records)):
                if not any(cell.strip() for cell in all_records[i]):
                    next_row  = i + 1
                    found_empty = True
                    break
            if not found_empty:
                next_row = len(all_records) + 1
        sheet.insert_row(row_data, index=next_row)
        log_debug(f"Data inserted at row {next_row}")
        return True
    except Exception as e:
        log_debug(f"Error adding data to sheet: {str(e)}\n{traceback.format_exc()}")
        return False


# ============================================================
# LEAVE EMAILS
# ============================================================
def send_approval_email(employee_name, superior_name, superior_email,
                        clusters_data, cluster_codes):
    try:
        log_debug(f"Sending leave approval email to {superior_email}")
        sender_email, sender_password, _ = get_email_credentials()
        if not sender_email or not sender_password:
            st.warning("Email credentials not configured")
            return False
        if "@" not in superior_email or "." not in superior_email:
            st.warning(f"Invalid superior email: {superior_email}")
            return False
        try:
            app_url = st.secrets.get("APP_URL", "https://your-anulach-leave-app.streamlit.app/")
        except:
            app_url = "https://your-anulach-leave-app.streamlit.app/"

        clusters_html = ""
        for i, cluster in enumerate(clusters_data):
            days         = calculate_days(cluster["from_date"], cluster["till_date"], cluster["leave_type"])
            days_display = "0.5 day" if cluster["leave_type"] == "Half Day" else f"{days} days"
            clusters_html += f"""
            <div style="background:{'#f8f9ff' if i%2==0 else '#f0f2ff'};padding:15px;border-radius:8px;
                        margin:10px 0;border-left:4px solid #4dabf7;">
                <h4 style="margin-top:0;color:#339af0;">Period {i+1}</h4>
                <table style="width:100%;border-collapse:collapse;">
                    <tr><td style="padding:5px;width:40%;"><strong>Leave Type:</strong></td>
                        <td style="padding:5px;">{cluster["leave_type"]}</td></tr>
                    <tr><td style="padding:5px;"><strong>From Date:</strong></td>
                        <td style="padding:5px;">{cluster["from_date"].strftime("%Y-%m-%d")}</td></tr>
                    <tr><td style="padding:5px;"><strong>Till Date:</strong></td>
                        <td style="padding:5px;">{cluster["till_date"].strftime("%Y-%m-%d")}</td></tr>
                    <tr><td style="padding:5px;"><strong>Duration:</strong></td>
                        <td style="padding:5px;">{days_display}</td></tr>
                    <tr><td style="padding:5px;"><strong>Approval Code:</strong></td>
                        <td style="padding:5px;">
                            <span style="background:#fff3cd;padding:5px 10px;border-radius:4px;
                                         font-family:'Courier New',monospace;font-weight:bold;
                                         letter-spacing:2px;">{cluster_codes.get(i, "CODE MISSING")}</span>
                        </td></tr>
                </table>
            </div>"""

        msg = MIMEMultipart("alternative")
        msg["From"]    = formataddr(("ANULACH FASHION HR", sender_email))
        msg["To"]      = superior_email
        msg["Subject"] = (f"CLUSTER LEAVE: {employee_name} - {len(clusters_data)} periods"
                          if len(clusters_data) > 1 else f"Leave Approval Required: {employee_name}")
        html_body = f"""
        <html><head><style>
        body{{font-family:Arial,sans-serif;line-height:1.6;}}
        .container{{max-width:700px;margin:0 auto;padding:20px;}}
        .header{{background:linear-gradient(135deg,#673ab7 0%,#9c27b0 100%);color:white;padding:20px;
                 border-radius:10px;text-align:center;}}
        .info-box{{background:#f8f9ff;padding:20px;border-radius:10px;margin:20px 0;border:1px solid #e2e8f0;}}
        .instructions{{background:#e8f5e9;padding:15px;border-radius:8px;margin:15px 0;border-left:4px solid #4caf50;}}
        .footer{{color:#666;font-size:12px;margin-top:30px;padding-top:15px;border-top:1px solid #eee;}}
        </style></head><body>
        <div class="container">
            <div class="header">
                <h2 style="margin:0;">Leave Approval Required</h2>
                <p style="margin:5px 0 0 0;opacity:0.9;">ANULACH FASHION HR System</p>
            </div>
            <p>Dear {superior_name},</p>
            <div class="info-box">
                <h3 style="margin-top:0;color:#673ab7;">Employee Information</h3>
                <p><strong>Employee Name:</strong> {employee_name}</p>
                <p><strong>Employee Code:</strong> {clusters_data[0].get("employee_code","N/A")}</p>
                <p><strong>Total Periods:</strong> {len(clusters_data)}</p>
                <p><strong>Purpose:</strong> {clusters_data[0].get("purpose","N/A")}</p>
            </div>
            <h3 style="color:#339af0;">Leave Periods Details</h3>
            {clusters_html}
            <div class="instructions">
                <h4 style="margin-top:0;color:#2e7d32;">How to Approve / Reject:</h4>
                <ol>
                    <li>Visit: <a href="{app_url}">{app_url}</a></li>
                    <li>Click on the <strong>"Approval Portal"</strong> tab</li>
                    <li>Enter the specific approval code for the period</li>
                    <li>Select <strong>Approve</strong> or <strong>Reject</strong></li>
                    <li>Click <strong>Submit Decision</strong></li>
                </ol>
                <p><strong>Note:</strong> Each code can only be used once.</p>
            </div>
            <div class="footer">
                ANULACH FASHION PVT LTD - HR Department<br>{sender_email}
            </div>
        </div></body></html>"""
        msg.attach(MIMEText(html_body, "html"))

        server, method = create_smtp_connection(sender_email, sender_password)
        if server:
            try:
                server.sendmail(sender_email, superior_email, msg.as_string())
                log_debug(f"Approval email sent to {superior_email}")
                server.quit()
                return True
            except Exception as e:
                try: server.quit()
                except: pass
                log_debug(f"Failed to send emails: {str(e)}")
                st.error(f"Failed to send emails: {str(e)}")
                return False
        st.error(f"Could not establish SMTP connection: {method}")
        return False
    except Exception as e:
        log_debug(f"Error in send_approval_email: {traceback.format_exc()}")
        st.error(f"Email sending error: {str(e)}")
        return False


def send_decision_email_to_superior(employee_name, superior_name,
                                    superior_email, status, approval_password):
    try:
        sender_email, sender_password, _ = get_email_credentials()
        if not sender_email or not sender_password: return False
        msg = MIMEMultipart("alternative")
        msg["From"]    = formataddr(("ANULACH FASHION HR", sender_email))
        msg["To"]      = superior_email
        msg["Subject"] = f"Leave Decision Recorded: {employee_name} - {status}"
        html_body = f"""
        <html><head><style>
        body{{font-family:Arial,sans-serif;line-height:1.6;}}
        .container{{max-width:700px;margin:0 auto;padding:20px;}}
        .header{{background:linear-gradient(135deg,#673ab7 0%,#9c27b0 100%);color:white;
                 padding:20px;border-radius:10px;text-align:center;}}
        .success-box{{background:#e8f5e9;padding:15px;border-radius:8px;margin:15px 0;border-left:4px solid #4caf50;}}
        .info-box{{background:#f8f9ff;padding:20px;border-radius:10px;margin:20px 0;border:1px solid #e2e8f0;}}
        .footer{{color:#666;font-size:12px;margin-top:30px;padding-top:15px;border-top:1px solid #eee;}}
        </style></head><body>
        <div class="container">
            <div class="header"><h2 style="margin:0;">Decision Confirmation</h2></div>
            <p>Dear {superior_name},</p>
            <div class="success-box">
                <p>You have successfully <strong>{status.lower()}</strong> the leave request
                   for <strong>{employee_name}</strong>.</p>
            </div>
            <div class="info-box">
                <p><strong>Employee:</strong> {employee_name}</p>
                <p><strong>Decision:</strong>
                    <span style="color:{'#4caf50' if status=='Approved' else '#f44336'};
                                 font-weight:bold;">{status}</span></p>
                <p><strong>Code Used:</strong> {approval_password}</p>
                <p><strong>Decision Time:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
            </div>
            <div class="footer">
                ANULACH FASHION PVT LTD - HR Department<br>{sender_email}
            </div>
        </div></body></html>"""
        msg.attach(MIMEText(html_body, "html"))
        server, method = create_smtp_connection(sender_email, sender_password)
        if server:
            try:
                server.sendmail(sender_email, superior_email, msg.as_string())
                server.quit()
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
            # Approval Password is now column 13 (index 12)
            if len(row) > 12 and row[12] == approval_password:
                sheet.update_cell(idx + 1, 11, status)
                sheet.update_cell(idx + 1, 12, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                employee_name  = row[2]  if len(row) > 2  else ""
                superior_name  = row[8]  if len(row) > 8  else ""
                superior_email = row[9]  if len(row) > 9  else ""
                log_debug(f"Updated row {idx+1} to status: {status}")
                if superior_email and "@" in superior_email:
                    send_decision_email_to_superior(employee_name, superior_name,
                                                    superior_email, status, approval_password)
                return True
        log_debug("No matching record found for approval code")
        return False
    except Exception as e:
        st.error(f"Error updating leave status: {str(e)}")
        log_debug(f"Update leave error: {traceback.format_exc()}")
        return False


# ============================================================
# DUPLICATE SUBMISSION GUARD (Leave)
# ============================================================
def generate_submission_hash(form_data):
    data_string = (f"{form_data['employee_name']}_{form_data['employee_code']}_"
                   f"{form_data['purpose']}_{datetime.now().strftime('%Y%m%d')}")
    return hashlib.md5(data_string.encode()).hexdigest()


def check_duplicate_submission(form_data):
    current_hash = generate_submission_hash(form_data)
    if st.session_state.last_submission_hash == current_hash:
        if st.session_state.submission_timestamp:
            time_diff = (datetime.now() - st.session_state.submission_timestamp).total_seconds()
            if time_diff < 30:
                return True, "You have already submitted this form. Please wait before submitting again."
    return False, ""


# ============================================================
# OOO — APPROVAL CODES (worksheet: "anulach OOO and WFH")
# ============================================================
def get_existing_wfh_codes_from_sheet(sheet):
    """Read existing OOO approval codes from column 11 (index 10)."""
    try:
        if not sheet:
            return set()
        existing_codes = set()
        for idx, row in enumerate(sheet.get_all_values()):
            if idx == 0:
                continue
            if len(row) > 10 and row[10]:
                existing_codes.add(row[10])
        log_debug(f"Found {len(existing_codes)} existing OOO codes")
        return existing_codes
    except Exception as e:
        log_debug(f"Error getting existing OOO codes: {str(e)}")
        return set()


def generate_wfh_approval_code(sheet=None):
    """Generate a unique 5-character approval code for an OOO request."""
    alphabet = string.ascii_uppercase + string.digits
    alphabet = alphabet.replace("0", "").replace("O", "").replace("1", "").replace("I", "").replace("L", "")
    existing_codes = set()
    if sheet:
        existing_codes = get_existing_wfh_codes_from_sheet(sheet)
    existing_codes.update(st.session_state.generated_wfh_codes)
    for attempt in range(200):
        code = "".join(secrets.choice(alphabet) for _ in range(5))
        if code not in existing_codes:
            st.session_state.generated_wfh_codes.add(code)
            log_debug(f"Generated unique OOO approval code: {code} (attempt {attempt+1})")
            return code
    raise RuntimeError("Could not generate a unique OOO approval code")


# ============================================================
# OOO — EMAIL HELPERS
# ============================================================
def _wfh_label(request_type):
    return "Out of Office"


def send_html_email_to_many(recipients, subject, html_body):
    """Send the same HTML email separately to each address. Returns how many were sent."""
    sender_email, sender_password, _ = get_email_credentials()
    if not sender_email or not sender_password:
        log_debug("Email credentials not configured")
        return 0
    valid = [r for r in recipients if r and "@" in r]
    if not valid:
        log_debug("No valid recipient addresses")
        return 0
    server, method = create_smtp_connection(sender_email, sender_password)
    if not server:
        log_debug(f"SMTP connection failed: {method}")
        return 0
    sent = 0
    try:
        for addr in valid:
            try:
                msg = MIMEMultipart("alternative")
                msg["From"]    = formataddr(("ANULACH FASHION HR", sender_email))
                msg["To"]      = addr
                msg["Subject"] = subject
                msg.attach(MIMEText(html_body, "html"))
                server.sendmail(sender_email, addr, msg.as_string())
                sent += 1
                log_debug(f"Email sent to {addr}: {subject}")
            except Exception as e:
                log_debug(f"Failed to send email to {addr}: {str(e)}")
    finally:
        try: server.quit()
        except: pass
    return sent


def _wfh_email_html(header_title, header_gradient, inner_html, sender_email):
    return f"""
    <html><head><style>
    body{{font-family:Arial,sans-serif;line-height:1.6;}}
    .container{{max-width:700px;margin:0 auto;padding:20px;}}
    .header{{background:{header_gradient};color:white;padding:20px;border-radius:10px;text-align:center;}}
    .info-box{{background:#f8f9ff;padding:20px;border-radius:10px;margin:20px 0;border:1px solid #e2e8f0;}}
    .code-box{{background:#fff3cd;padding:20px;border-radius:10px;margin:20px 0;text-align:center;border:2px solid #ffc107;}}
    .instructions{{background:#e8f5e9;padding:15px;border-radius:8px;margin:15px 0;border-left:4px solid #4caf50;}}
    .footer{{color:#666;font-size:12px;margin-top:30px;padding-top:15px;border-top:1px solid #eee;}}
    </style></head><body>
    <div class="container">
        <div class="header">
            <h2 style="margin:0;">{header_title}</h2>
            <p style="margin:5px 0 0 0;opacity:0.9;">ANULACH FASHION HR System</p>
        </div>
        {inner_html}
        <div class="footer">
            ANULACH FASHION PVT LTD - HR Department<br>{sender_email}<br>This is an automated message.
        </div>
    </div></body></html>"""


# ============================================================
# OOO — EMAILS
# ============================================================
def send_wfh_approval_email(employee_name, employee_code, employee_email,
                            request_type, start_date, end_date, reason, approval_code):
    """Send the approval request (with the 5-character code) to everyone in WFH_APPROVAL_RECIPIENTS."""
    try:
        sender_email, sender_password, _ = get_email_credentials()
        if not sender_email or not sender_password:
            log_debug("Email credentials not configured for OOO approval email")
            return False
        try:
            app_url = st.secrets.get("APP_URL", "https://your-anulach-leave-app.streamlit.app/")
        except Exception:
            app_url = "https://your-anulach-leave-app.streamlit.app/"

        duration = (end_date - start_date).days + 1
        label    = _wfh_label(request_type)
        inner = f"""
        <p>Dear HR Team,</p>
        <div class="info-box">
            <h3 style="margin-top:0;color:#20c997;">Employee Request Details</h3>
            <p><strong>Employee Name:</strong> {html_escape(employee_name)}</p>
            <p><strong>Employee Code:</strong> {html_escape(employee_code)}</p>
            <p><strong>Employee Email:</strong> {html_escape(employee_email) if employee_email else 'Not provided'}</p>
            <p><strong>Request Type:</strong> {html_escape(request_type)}</p>
            <p><strong>Start Date:</strong> {start_date.strftime('%Y-%m-%d')}</p>
            <p><strong>End Date:</strong> {end_date.strftime('%Y-%m-%d')}</p>
            <p><strong>Duration:</strong> {duration} day(s)</p>
            <p><strong>Reason:</strong> {html_escape(reason)}</p>
        </div>
        <div class="code-box">
            <div style="font-size:0.95rem;color:#856404;font-weight:600;margin-bottom:10px;">
                {label} Approval Code (HR Use Only)
            </div>
            <div style="font-size:2.5rem;font-weight:700;color:#553c9a;letter-spacing:6px;
                        font-family:'Courier New',monospace;background:white;padding:15px;
                        border-radius:8px;display:inline-block;margin:10px 0;">
                {approval_code}
            </div>
            <div style="font-size:0.85rem;color:#856404;margin-top:8px;">
                Use this code in the OOO Approval tab to approve or reject this request.
            </div>
        </div>
        <div class="instructions">
            <h4 style="margin-top:0;color:#2e7d32;">How to Approve / Reject:</h4>
            <ol>
                <li>Visit: <a href="{app_url}">{app_url}</a></li>
                <li>Click on the <strong>"OOO Approval"</strong> tab</li>
                <li>Enter the 5-character code:
                    <strong style="font-family:monospace;letter-spacing:2px;">{approval_code}</strong></li>
                <li>Select <strong>Approve</strong> or <strong>Reject</strong></li>
                <li>Click <strong>Submit OOO Decision</strong></li>
            </ol>
            <p style="font-size:0.9rem;"><strong>Note:</strong> The employee will be notified automatically.</p>
        </div>"""
        html_body = _wfh_email_html(f"{label} Request - Approval Required",
                                    "linear-gradient(135deg,#20c997 0%,#0ca678 100%)",
                                    inner, sender_email)
        subject = f"Out of Office Approval Required: {employee_name} [{approval_code}]"
        sent = send_html_email_to_many(list(WFH_APPROVAL_RECIPIENTS.values()), subject, html_body)
        log_debug(f"OOO approval email sent to {sent} recipient(s)")
        return sent > 0
    except Exception:
        log_debug(f"Error in send_wfh_approval_email: {traceback.format_exc()}")
        return False


def send_wfh_employee_confirmation_email(employee_name, employee_email, request_type,
                                         start_date, end_date, reason):
    """Confirmation to the employee right after they submit an OOO request."""
    try:
        if not employee_email or "@" not in employee_email:
            return False
        sender_email, sender_password, _ = get_email_credentials()
        if not sender_email or not sender_password:
            return False
        duration = (end_date - start_date).days + 1
        label    = _wfh_label(request_type)
        inner = f"""
        <p>Dear {html_escape(employee_name)},</p>
        <div class="info-box">
            <h3 style="margin-top:0;color:#4caf50;">Your {html_escape(request_type)} request has been submitted.</h3>
            <p><strong>Request Type:</strong> {html_escape(request_type)}</p>
            <p><strong>Start Date:</strong> {start_date.strftime('%Y-%m-%d')}</p>
            <p><strong>End Date:</strong> {end_date.strftime('%Y-%m-%d')}</p>
            <p><strong>Duration:</strong> {duration} day(s)</p>
            <p><strong>Reason:</strong> {html_escape(reason)}</p>
        </div>
        <div style="background:#e3f2fd;padding:15px;border-radius:8px;margin:15px 0;border-left:4px solid #2196f3;">
            <h4 style="margin-top:0;color:#0d47a1;">What Happens Next:</h4>
            <ol>
                <li>Your request has been sent to HR for review.</li>
                <li>HR will approve or reject your request.</li>
                <li>You will receive an email once a decision is made.</li>
            </ol>
        </div>"""
        html_body = _wfh_email_html("Request Submitted Successfully",
                                    "linear-gradient(135deg,#4caf50 0%,#2e7d32 100%)",
                                    inner, sender_email)
        subject = f"{label} Request Submitted - {employee_name}"
        return send_html_email_to_many([employee_email], subject, html_body) > 0
    except Exception:
        log_debug(f"Error in send_wfh_employee_confirmation_email: {traceback.format_exc()}")
        return False


def send_wfh_decision_email_to_employee(employee_name, employee_email, status,
                                        request_type, start_date_str, end_date_str, reason):
    """Tell the employee whether HR approved or rejected the request."""
    try:
        if not employee_email or "@" not in employee_email:
            log_debug("No valid employee email for OOO decision notification")
            return False
        sender_email, sender_password, _ = get_email_credentials()
        if not sender_email or not sender_password:
            return False
        label        = _wfh_label(request_type)
        status_color = "#4caf50" if status == "Approved" else "#f44336"
        status_bg    = "#e8f5e9" if status == "Approved" else "#ffebee"
        status_icon  = "\u2705" if status == "Approved" else "\u274C"
        action_note  = (
            "<p>Your request has been approved. Please stay reachable during your Out of Office period.</p>"
            if status == "Approved"
            else "<p>Your request has been rejected. Please contact HR for more details.</p>"
        )
        inner = f"""
        <p>Dear {html_escape(employee_name)},</p>
        <div style="background:{status_bg};padding:20px;border-radius:10px;margin:20px 0;">
            <h3 style="margin-top:0;color:{status_color};">
                {status_icon} Your {html_escape(request_type)} request has been <strong>{status.lower()}</strong> by HR.
            </h3>
            <p><strong>Request Type:</strong> {html_escape(request_type)}</p>
            <p><strong>Start Date:</strong> {html_escape(start_date_str)}</p>
            <p><strong>End Date:</strong> {html_escape(end_date_str)}</p>
            <p><strong>Reason Submitted:</strong> {html_escape(reason)}</p>
            <p><strong>Decision By:</strong> HR - ANULACH FASHION</p>
            <p><strong>Decision Date:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <div style="margin-top:15px;padding:12px;background:white;border-radius:8px;
                        border-left:3px solid {status_color};">
                {action_note}
            </div>
        </div>"""
        html_body = _wfh_email_html(f"{html_escape(request_type)} Request {status}",
                                    f"linear-gradient(135deg,{status_color} 0%,{status_color}80 100%)",
                                    inner, sender_email)
        subject = f"{label} Request {status} - {employee_name}"
        return send_html_email_to_many([employee_email], subject, html_body) > 0
    except Exception:
        log_debug(f"Error in send_wfh_decision_email_to_employee: {traceback.format_exc()}")
        return False


def send_wfh_decision_confirmation_to_hr(employee_name, employee_email, status,
                                         request_type, approval_code):
    """Send a decision confirmation to everyone in WFH_APPROVAL_RECIPIENTS."""
    try:
        sender_email, sender_password, _ = get_email_credentials()
        if not sender_email or not sender_password:
            return False
        inner = f"""
        <p>Dear HR Team,</p>
        <div class="instructions">
            <p>The Out of Office request for <strong>{html_escape(employee_name)}</strong>
               has been <strong>{status.lower()}</strong> successfully.</p>
        </div>
        <div class="info-box">
            <p><strong>Employee:</strong> {html_escape(employee_name)}</p>
            <p><strong>Employee Email:</strong> {html_escape(employee_email) if employee_email else 'N/A'}</p>
            <p><strong>Request Type:</strong> {html_escape(request_type)}</p>
            <p><strong>Decision:</strong>
                <span style="color:{'#4caf50' if status == 'Approved' else '#f44336'};
                             font-weight:bold;">{status}</span></p>
            <p><strong>Code Used:</strong> {approval_code}</p>
            <p><strong>Decision Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>"""
        html_body = _wfh_email_html("Out of Office Decision Confirmed",
                                    "linear-gradient(135deg,#20c997 0%,#0ca678 100%)",
                                    inner, sender_email)
        subject = f"Out of Office Decision Recorded: {employee_name} - {status}"
        return send_html_email_to_many(list(WFH_APPROVAL_RECIPIENTS.values()), subject, html_body) > 0
    except Exception:
        log_debug(f"Error in send_wfh_decision_confirmation_to_hr: {traceback.format_exc()}")
        return False


# ============================================================
# OOO — STATUS UPDATE & SUBMISSION
# ============================================================
def update_wfh_status(sheet, approval_code, status):
    """
    Find the row whose Approval Code (column 11) matches, set Status (column 9) and
    Approval Date (column 10), then notify the employee and HR.
    """
    try:
        all_records = sheet.get_all_values()
        for idx, row in enumerate(all_records):
            if idx == 0:
                continue
            if len(row) > 10 and row[10] == approval_code:
                sheet.update_cell(idx + 1, 9, status)
                sheet.update_cell(idx + 1, 10, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

                employee_name  = row[1] if len(row) > 1 else ""
                employee_email = row[3] if len(row) > 3 else ""
                request_type   = row[4] if len(row) > 4 else ""
                start_date_str = row[5] if len(row) > 5 else ""
                end_date_str   = row[6] if len(row) > 6 else ""
                reason         = row[7] if len(row) > 7 else ""
                log_debug(f"Updated OOO row {idx+1} to status: {status} for {employee_name}")

                if employee_email and "@" in employee_email:
                    send_wfh_decision_email_to_employee(employee_name, employee_email, status,
                                                        request_type, start_date_str, end_date_str, reason)
                send_wfh_decision_confirmation_to_hr(employee_name, employee_email, status,
                                                     request_type, approval_code)
                return True
        log_debug("No matching OOO record found for approval code")
        return False
    except Exception as e:
        st.error(f"Error updating OOO status: {str(e)}")
        log_debug(f"Update OOO error: {traceback.format_exc()}")
        return False


def submit_wfh_request(employee_name, employee_code, employee_email,
                       request_type, start_date, end_date, reason):
    """
    Save the request to the 'anulach OOO and WFH' worksheet with a fresh approval code,
    email the approvers, and confirm to the employee.
    Returns (success, message, approval_email_sent, approval_code).
    """
    try:
        log_debug(f"Submitting OOO request for: {employee_name}")
        sheet = setup_wfh_sheet()
        if not sheet:
            return False, "Database connection failed. Please check your Google Sheets setup.", False, ""

        approval_code = generate_wfh_approval_code(sheet)
        row_data = [
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            employee_name.strip(),
            employee_code.strip(),
            employee_email.strip(),
            request_type.strip(),
            start_date.strftime("%Y-%m-%d"),
            end_date.strftime("%Y-%m-%d"),
            reason.strip(),
            "Pending",
            "",              # Approval Date (blank until HR decides)
            approval_code,
        ]
        if not add_data_to_sheet(sheet, row_data):
            return False, "Error submitting request to the database.", False, ""
        log_debug(f"OOO request written to '{WFH_WORKSHEET_NAME}' for {employee_name}")

        email_sent = False
        try:
            email_sent = send_wfh_approval_email(employee_name, employee_code, employee_email,
                                                 request_type, start_date, end_date, reason, approval_code)
        except Exception as e:
            log_debug(f"OOO approval email error: {str(e)}")

        try:
            if employee_email and "@" in employee_email:
                send_wfh_employee_confirmation_email(employee_name, employee_email,
                                                     request_type, start_date, end_date, reason)
        except Exception as e:
            log_debug(f"OOO confirmation email error: {str(e)}")

        if email_sent:
            return True, "Request submitted and approval email sent to HR.", True, approval_code
        return True, "Request saved, but the approval email could not be sent.", False, approval_code
    except Exception as e:
        log_debug(f"Error in submit_wfh_request: {traceback.format_exc()}")
        return False, f"Error: {str(e)}", False, ""


# ============================================================
# DUPLICATE SUBMISSION GUARD (OOO)
# ============================================================
def generate_wfh_hash(form_data):
    data_string = (f"{form_data['employee_name']}_{form_data['employee_code']}_"
                   f"{form_data['request_type']}_{form_data['start_date']}_{form_data['end_date']}_"
                   f"{form_data['reason']}_{datetime.now().strftime('%Y%m%d')}")
    return hashlib.md5(data_string.encode()).hexdigest()


def check_duplicate_wfh_submission(form_data):
    current_hash = generate_wfh_hash(form_data)
    if st.session_state.last_wfh_submission_hash == current_hash:
        if st.session_state.wfh_submission_timestamp:
            time_diff = (datetime.now() - st.session_state.wfh_submission_timestamp).total_seconds()
            if time_diff < 30:
                return True, "You have already submitted this Out of Office request. Please wait before submitting again."
    return False, ""


# ============================================================
# SIDEBAR
# ============================================================
st.sidebar.title("Configuration Panel")
email_config = check_email_configuration()

st.sidebar.markdown("### Secrets Diagnostic")
try:
    all_secret_keys = list(st.secrets.keys())
    st.sidebar.info(f"Top-level secret keys:\n`{all_secret_keys}`")
except Exception:
    st.sidebar.error("Could not read st.secrets")

st.sidebar.markdown("### Email Configuration")
if email_config["configured"]:
    st.sidebar.success(f"Email ready: {email_config['sender_email']}")
    st.sidebar.info(f"**Source:** {email_config['source']}")
    if "password_type" in email_config:
        st.sidebar.info(f"**Password Type:** {email_config['password_type']} ({email_config.get('password_length','?')} chars)")
else:
    st.sidebar.error("Email credentials NOT found")
    st.sidebar.warning(
        "Add to Streamlit Secrets:\n\n"
        "```toml\n[EMAIL]\nsender_email = \"you@gmail.com\"\n"
        "sender_password = \"abcd efgh ijkl mnop\"\n```"
    )
    st.sidebar.caption(f"Details: {email_config.get('details', email_config.get('message',''))}")

st.sidebar.markdown("---")
if st.sidebar.button("Test Google Sheets Connection"):
    with st.sidebar:
        with st.spinner("Testing..."):
            sheet = setup_google_sheets()
            if sheet:
                st.success("Connected!")
                st.info(f"Workbook: Leave_Applications | Worksheet: Anulach | Rows: {sheet.row_count}")
            else:
                st.error("Connection failed")

if st.sidebar.button("Test OOO Sheet Connection"):
    with st.sidebar:
        with st.spinner("Testing..."):
            wfh_test_sheet = setup_wfh_sheet()
            if wfh_test_sheet:
                st.success("Connected!")
                st.info(f"Workbook: Leave_Applications | Worksheet: {WFH_WORKSHEET_NAME} | Rows: {wfh_test_sheet.row_count}")
            else:
                st.error("Connection failed")

st.sidebar.markdown("---")
st.sidebar.markdown("### Test Email Configuration")
test_recipient = st.sidebar.text_input("Test Recipient Email", value="",
                                       placeholder="Leave blank to send to yourself")
col1, col2 = st.sidebar.columns(2)
with col1:
    if st.button("Send Test Email", key="test_email_btn", use_container_width=True):
        with st.spinner("Sending..."):
            result = test_email_connection(test_recipient)
            st.session_state.test_email_result = result
            if result["success"]:
                st.session_state.email_config_status = "Working"
                st.sidebar.success("Test email sent!")
            else:
                st.session_state.email_config_status = "Failed"
                st.sidebar.error("Test failed")
with col2:
    if st.button("Clear Logs", key="clear_logs", use_container_width=True):
        st.session_state.debug_logs = []

if st.session_state.test_email_result:
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Last Test Result")
    if st.session_state.test_email_result["success"]:
        st.sidebar.success("Last test: SUCCESS")
        st.sidebar.info(f"**Method:** {st.session_state.test_email_result.get('method','Unknown')}")
    else:
        st.sidebar.error("Last test: FAILED")
        with st.sidebar.expander("View Error Details"):
            st.error(st.session_state.test_email_result.get("message","No message"))
            st.info(st.session_state.test_email_result.get("details","No details"))

st.sidebar.markdown("---")
st.sidebar.markdown("### Debug Logs")
if st.sidebar.checkbox("Show Debug Logs", value=False):
    if st.session_state.debug_logs:
        html = "<div class='debug-log'>"
        for log in reversed(st.session_state.debug_logs[-10:]):
            color = ("#dc3545" if "ERROR" in log
                     else "#28a745" if "SUCCESS" in log or "INFO" in log
                     else "#ffc107" if "WARNING" in log else "inherit")
            html += f"<div style='color:{color};'>{log}</div>"
        html += "</div>"
        st.sidebar.markdown(html, unsafe_allow_html=True)
    else:
        st.sidebar.info("No debug logs yet")

st.sidebar.markdown("---")
with st.sidebar.expander("Email Setup Guide"):
    st.markdown("""
    **Step-by-Step Gmail Configuration:**

    1. Enable 2-Step Verification:
       https://myaccount.google.com/security

    2. Generate App Password:
       https://myaccount.google.com/apppasswords
       - Select Mail → Other (Custom name)
       - Name it "ANULACH FASHION Streamlit"
       - Copy the 16-character password

    3. Update Streamlit Secrets:
    ```toml
    [EMAIL]
    sender_email = "hr@anulachfashion.com"
    sender_password = "your-16-char-app-password"
    ```
    4. Click **Send Test Email** to verify.
    """)


# ============================================================
# MAIN HEADER
# ============================================================
st.markdown("""
    <div class="company-header floating-element">
        <h1>ANULACH FASHION</h1>
        <h2>Leave and Out of Office request</h2>
    </div>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs([
    "\U0001f4dd Submit Leave Application",
    "\u2705 Approval Portal",
    "\U0001f3e2 Out of Office",
    "\U0001f4f2 OOO Approval",
])


# ============================================================
# TAB 1 — SUBMIT LEAVE APPLICATION
# ============================================================
with tab1:
    # ── email status banner ──────────────────────────────────
    if not email_config["configured"] or st.session_state.email_config_status == "Failed":
        st.markdown("""
            <div style="background:linear-gradient(135deg,#fff3cd 0%,#ffeaa7 100%);
                        border-left:4px solid #ff9800;color:#856404;
                        padding:1.5rem;border-radius:12px;margin-bottom:2rem;">
                <strong>&#x26A0;&#xFE0F; Email Configuration Issue Detected</strong><br>
                <span style="font-size:0.95rem;">
                    Emails may not send automatically. Test your email config in the sidebar.
                </span>
            </div>
        """, unsafe_allow_html=True)
    elif st.session_state.email_config_status == "Working":
        st.markdown("""
            <div style="background:linear-gradient(135deg,#d4edda 0%,#c3e6cb 100%);
                        border-left:4px solid #28a745;color:#155724;
                        padding:1.5rem;border-radius:12px;margin-bottom:2rem;">
                <strong>&#x2705; Email Configuration Working</strong><br>
                <span style="font-size:0.95rem;">
                    Email notifications will be sent automatically to managers and employees.
                </span>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("""
        <div class="section-header">
            <div class="icon-badge">&#x1F4CB;</div>
            <div>
                <h3 style="margin:0;">Leave Application Form</h3>
                <p style="margin:5px 0 0 0;color:#718096;font-size:0.95rem;">
                    Complete all fields below to submit your leave request
                </p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # ── reset guard ──────────────────────────────────────────
    if st.session_state.reset_form_tab1:
        st.session_state.form_data_tab1 = {
            "employee_name": "", "employee_code": "",
            "purpose": "", "is_cluster": False,
        }
        st.session_state.clusters = [{
            "cluster_number": 1, "leave_type": "Select Type",
            "from_date": datetime.now().date(), "till_date": datetime.now().date(),
            "approval_code": "",
        }]
        st.session_state.cluster_codes          = {}
        st.session_state.reset_form_tab1        = False
        st.session_state.submission_in_progress = False
        st.session_state.submission_completed   = True

    # ── employee info ────────────────────────────────────────
    col1, col2 = st.columns([1, 1], gap="large")
    with col1:
        employee_name = st.text_input("Full Name", value=st.session_state.form_data_tab1["employee_name"],
                                      placeholder="Enter your full name", key="employee_name_input")
    with col2:
        employee_code = st.text_input("Employee ID", value=st.session_state.form_data_tab1["employee_code"],
                                      placeholder="e.g., AF-EMP-001", key="employee_code_input")

    is_cluster = st.checkbox(
        "Is this a Cluster Holiday? (Multiple leave periods)",
        value=st.session_state.form_data_tab1["is_cluster"],
        help="Check this if you need to apply for multiple separate leave periods",
        key="is_cluster_checkbox",
    )

    # ── cluster / single leave ───────────────────────────────
    if is_cluster:
        st.markdown("""
            <div class="cluster-section">
                <div class="cluster-header">
                    <div class="icon-badge"
                         style="background:linear-gradient(135deg,#4dabf7 0%,#339af0 100%);">&#x1F4C5;</div>
                    <div>
                        <h3 style="margin:0;color:#ffffff !important;">Cluster Holiday Periods</h3>
                        <p style="margin:5px 0 0 0;color:#4dabf7;font-size:0.95rem;">
                            Add multiple leave periods below (each gets a separate approval code)
                        </p>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        total_clusters = len(st.session_state.clusters)
        for i, cluster in enumerate(st.session_state.clusters):
            st.markdown(f"<h4 style='color:#339af0;'>Period {i+1}</h4>", unsafe_allow_html=True)
            c1, c2, c3, c4 = st.columns([2, 2, 1, 1])
            with c1:
                leave_type = st.selectbox(
                    f"Leave Type - Period {i+1}",
                    LEAVE_TYPES,
                    index=LEAVE_TYPES.index(cluster["leave_type"])
                    if cluster["leave_type"] in LEAVE_TYPES else 0,
                    key=f"leave_type_cluster_{i}",
                )
                st.session_state.clusters[i]["leave_type"] = leave_type
            with c2:
                if leave_type == "Half Day":
                    sel = st.date_input(f"Date - Period {i+1}", value=cluster["from_date"],
                                        min_value=datetime.now().date() - timedelta(days=60),
                                        key=f"date_cluster_{i}")
                    st.session_state.clusters[i]["from_date"] = sel
                    st.session_state.clusters[i]["till_date"] = sel
                else:
                    ca, cb = st.columns(2)
                    with ca:
                        fd = st.date_input(f"From - Period {i+1}", value=cluster["from_date"],
                                           min_value=datetime.now().date() - timedelta(days=60),
                                           key=f"from_date_cluster_{i}")
                        st.session_state.clusters[i]["from_date"] = fd
                    with cb:
                        td = st.date_input(f"To - Period {i+1}", value=cluster["till_date"],
                                           min_value=datetime.now().date() - timedelta(days=60),
                                           key=f"till_date_cluster_{i}")
                        st.session_state.clusters[i]["till_date"] = td
            with c3:
                if leave_type != "Select Type":
                    days = calculate_days(st.session_state.clusters[i]["from_date"],
                                         st.session_state.clusters[i]["till_date"], leave_type)
                    d_str = "0.5" if leave_type == "Half Day" else str(days)
                    st.markdown(f"""
                        <div style="background:#e3f2fd;padding:10px;border-radius:8px;text-align:center;">
                            <div style="font-size:0.8rem;color:#1976d2;">Days</div>
                            <div style="font-size:1.2rem;font-weight:bold;color:#0d47a1;">{d_str}</div>
                        </div>""", unsafe_allow_html=True)
            with c4:
                if total_clusters > 1:
                    if st.button("Remove", key=f"remove_cluster_{i}"):
                        st.session_state.clusters.pop(i)
                        st.rerun()

        if st.button("Add Another Period", key="add_cluster"):
            st.session_state.clusters.append({
                "cluster_number": len(st.session_state.clusters) + 1,
                "leave_type": "Select Type",
                "from_date": datetime.now().date(), "till_date": datetime.now().date(),
                "approval_code": "",
            })
            st.rerun()

        total_days = sum(
            (calculate_working_days(c["from_date"], c["till_date"]) if c["leave_type"] == "Full Day"
             else 0.5 if c["leave_type"] == "Half Day" else 0)
            for c in st.session_state.clusters
        )
        st.markdown(f"""
            <div style="background:linear-gradient(135deg,#4dabf7 0%,#339af0 100%);
                        color:white;padding:1rem;border-radius:12px;text-align:center;margin:1rem 0;">
                <div style="font-size:0.9rem;">Total Working Days</div>
                <div style="font-size:2rem;font-weight:bold;">{total_days}</div>
                <div style="font-size:0.8rem;">across {len(st.session_state.clusters)} period(s)</div>
            </div>""", unsafe_allow_html=True)
    else:
        st.markdown("""
            <div style="margin-top:2rem;">
                <div style="display:flex;align-items:center;margin-bottom:1rem;">
                    <div class="icon-badge"
                         style="background:linear-gradient(135deg,#2196f3 0%,#03a9f4 100%);">&#x1F4C5;</div>
                    <div>
                        <h3 style="margin:0;">Leave Details</h3>
                        <p style="margin:5px 0 0 0;color:#718096;font-size:0.95rem;">
                            Enter your leave period details
                        </p>
                    </div>
                </div>
            </div>""", unsafe_allow_html=True)

        c1, c2 = st.columns([1, 1], gap="large")
        with c1:
            leave_type = st.selectbox("Leave Type", LEAVE_TYPES,
                                      index=0, key="leave_type_single")
        with c2:
            if leave_type == "Half Day":
                sel = st.date_input("Date", value=st.session_state.clusters[0]["from_date"],
                                    min_value=datetime.now().date() - timedelta(days=60),
                                    key="date_single")
                from_date = till_date = sel
            else:
                ca, cb = st.columns(2)
                with ca:
                    from_date = st.date_input("Start Date", value=st.session_state.clusters[0]["from_date"],
                                              min_value=datetime.now().date() - timedelta(days=60),
                                              key="from_date_single")
                with cb:
                    till_date = st.date_input("End Date", value=st.session_state.clusters[0]["till_date"],
                                              min_value=datetime.now().date() - timedelta(days=60),
                                              key="till_date_single")

        st.session_state.clusters[0]["leave_type"] = leave_type
        st.session_state.clusters[0]["from_date"]  = from_date
        st.session_state.clusters[0]["till_date"]  = till_date

        if leave_type != "Select Type":
            no_of_days = calculate_days(from_date, till_date, leave_type)
            if leave_type == "Half Day":
                st.markdown("""
                    <div class="metric-card floating-element">
                        <div style="font-size:0.9rem;color:#6b46c1;font-weight:500;">Leave Duration</div>
                        <div style="font-size:2.5rem;font-weight:700;color:#553c9a;margin:10px 0;">0.5</div>
                        <div style="font-size:0.9rem;color:#805ad5;">half day</div>
                    </div>""", unsafe_allow_html=True)
            else:
                st.markdown(f"""
                    <div class="metric-card floating-element">
                        <div style="font-size:0.9rem;color:#6b46c1;font-weight:500;">Leave Duration</div>
                        <div style="font-size:2.5rem;font-weight:700;color:#553c9a;margin:10px 0;">{no_of_days}</div>
                        <div style="font-size:0.9rem;color:#805ad5;">working days</div>
                    </div>""", unsafe_allow_html=True)

    # ── additional details ───────────────────────────────────
    st.markdown("""
        <div style="margin-top:2.5rem;">
            <div style="display:flex;align-items:center;margin-bottom:1rem;">
                <div class="icon-badge"
                     style="background:linear-gradient(135deg,#2196f3 0%,#03a9f4 100%);">&#x1F4DD;</div>
                <div>
                    <h3 style="margin:0;">Additional Details</h3>
                    <p style="margin:5px 0 0 0;color:#718096;font-size:0.95rem;">
                        Provide detailed information about your leave request
                    </p>
                </div>
            </div>
        </div>""", unsafe_allow_html=True)

    purpose = st.text_area(
        "Purpose of Leave", value=st.session_state.form_data_tab1["purpose"],
        placeholder="Please provide a clear and detailed explanation for your leave request...",
        height=120, key="purpose_textarea",
    )

    # ── submit button ────────────────────────────────────────
    _, submit_col, _ = st.columns([1, 2, 1])
    with submit_col:
        disabled = st.session_state.get("submission_in_progress", False)
        if disabled:
            st.info("Processing your submission… Please wait.")
        submit_button = st.button("Submit Leave Request", type="primary",
                                  use_container_width=True, key="submit_leave_request",
                                  disabled=disabled)

        if submit_button and not disabled:
            st.session_state.submission_in_progress = True
            form_check = {"employee_name": employee_name,
                          "employee_code": employee_code, "purpose": purpose}
            is_dup, dup_msg = check_duplicate_submission(form_check)
            if is_dup:
                st.session_state.submission_in_progress = False
                st.markdown(f"""<div class="error-message">
                    <strong>Duplicate Submission Detected</strong><br>{dup_msg}
                </div>""", unsafe_allow_html=True)
            else:
                errors = []
                if not all([employee_name, employee_code, purpose]):
                    errors.append("Please complete all required fields (Name, Employee ID, Purpose)")
                for i, cluster in enumerate(st.session_state.clusters):
                    if cluster["leave_type"] == "Select Type":
                        errors.append(f"Please select leave type for Period {i+1}")
                        break
                    if cluster["leave_type"] == "Full Day" and cluster["from_date"] > cluster["till_date"]:
                        errors.append(f"End date must be on or after start date for Period {i+1}")
                        break
                if errors:
                    st.session_state.submission_in_progress = False
                    html = "<div class='error-message'><strong>Validation Error</strong><br>"
                    for e in errors: html += f"{e}<br>"
                    st.markdown(html + "</div>", unsafe_allow_html=True)
                else:
                    with st.spinner("Submitting your application…"):
                        submission_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        superior_name   = HR_NAME
                        superior_email  = HR_EMAIL
                        sheet = setup_google_sheets()
                        if sheet:
                            try:
                                # Generate unique codes for each period
                                cluster_codes = {}
                                for i in range(len(st.session_state.clusters)):
                                    cluster_codes[i] = generate_approval_password(sheet)
                                    log_debug(f"Code for period {i+1}: {cluster_codes[i]}")

                                # Write each period to sheet
                                # Columns: Submission Date | Employee Code | Employee Name |
                                #          Type of Leave | No of Days | Purpose of Leave |
                                #          From Date | To Date | Superior Name | Superior Email |
                                #          Status | Approval Date | Approval Password |
                                #          Cluster (Yes/No) | Cluster leave Number
                                for i, cluster in enumerate(st.session_state.clusters):
                                    days = calculate_days(cluster["from_date"], cluster["till_date"],
                                                          cluster["leave_type"])
                                    row_data = [
                                        submission_date,
                                        employee_code.strip(),
                                        employee_name.strip(),
                                        cluster["leave_type"].strip(),
                                        str(days) if days is not None else "",
                                        purpose.strip(),
                                        cluster["from_date"].strftime("%Y-%m-%d"),
                                        cluster["till_date"].strftime("%Y-%m-%d"),
                                        superior_name.strip(),
                                        superior_email.strip(),
                                        "Pending",
                                        "",
                                        cluster_codes[i],
                                        "Yes" if is_cluster else "No",
                                        str(i+1) if is_cluster else "",
                                    ]
                                    row_data = [str(x) if x is not None else "" for x in row_data]
                                    if not add_data_to_sheet(sheet, row_data):
                                        raise Exception(f"Failed to write to Google Sheets for period {i+1}")

                                # Send emails
                                email_sent  = False
                                email_error = ""
                                if email_config["configured"]:
                                    try:
                                        clusters_for_email = []
                                        for c in st.session_state.clusters:
                                            cc = c.copy()
                                            cc["employee_code"] = employee_code
                                            cc["purpose"]       = purpose
                                            clusters_for_email.append(cc)
                                        email_sent = send_approval_email(
                                            employee_name, superior_name, superior_email,
                                            clusters_for_email, cluster_codes,
                                        )
                                    except Exception as e:
                                        email_error = str(e)
                                        log_debug(f"Email error: {traceback.format_exc()}")

                                st.session_state.last_submission_hash  = generate_submission_hash(form_check)
                                st.session_state.submission_timestamp  = datetime.now()
                                st.session_state.submission_in_progress = False
                                st.session_state.submission_completed   = True

                                if email_sent:
                                    st.markdown("""
                                        <div class="success-message">
                                            <div style="font-size:3rem;margin-bottom:1rem;">&#x2728;</div>
                                            <div style="font-size:1.5rem;font-weight:600;margin-bottom:10px;">
                                                Application Submitted Successfully!
                                            </div>
                                            <div style="margin-bottom:15px;">
                                                Your leave request has been sent to HR for approval.
                                            </div>
                                        </div>""", unsafe_allow_html=True)
                                    st.balloons()
                                    st.session_state.generated_codes.clear()
                                    st.session_state.reset_form_tab1 = True
                                    time.sleep(2)
                                    st.rerun()
                                else:
                                    st.session_state.cluster_codes   = cluster_codes
                                    st.session_state.show_copy_section = True
                                    st.markdown(f"""
                                        <div class="info-box">
                                            <strong style="color:#ff9800;">&#x1F4E7; Email Notification Issue</strong><br>
                                            Application saved to database successfully!<br>
                                            Email could not be sent automatically.<br>
                                            <small>{email_error}</small>
                                        </div>""", unsafe_allow_html=True)
                                    st.markdown(f"""
                                        <div style="text-align:center;margin:2rem 0;">
                                            <div style="font-size:1.3rem;font-weight:600;color:#673ab7;margin-bottom:1rem;">
                                                Manual Approval Process
                                            </div>
                                            <p style="color:#718096;margin-bottom:1.5rem;">
                                                Please share these approval codes with
                                                <strong>HR (hrvolarfashion@gmail.com)</strong>:
                                            </p>
                                        </div>""", unsafe_allow_html=True)
                                    for i, cluster in enumerate(st.session_state.clusters):
                                        code = cluster_codes[i]
                                        days = calculate_days(cluster["from_date"],
                                                              cluster["till_date"], cluster["leave_type"])
                                        d_str = ("0.5 day" if cluster["leave_type"] == "Half Day"
                                                 else f"{days} days")
                                        st.markdown(f"""
                                            <div style="background:{'#f8f9ff' if i%2==0 else '#f0f2ff'};
                                                        padding:1.5rem;border-radius:12px;margin:1rem 0;
                                                        border-left:4px solid #4dabf7;">
                                                <div style="display:flex;justify-content:space-between;align-items:center;">
                                                    <div>
                                                        <div style="font-size:1.1rem;font-weight:600;color:#339af0;">
                                                            Period {i+1}
                                                        </div>
                                                        <div style="font-size:0.9rem;color:#718096;">
                                                            {cluster["from_date"].strftime("%Y-%m-%d")} to
                                                            {cluster["till_date"].strftime("%Y-%m-%d")} &bull;
                                                            {cluster["leave_type"]} &bull; {d_str}
                                                        </div>
                                                    </div>
                                                    <div style="text-align:center;">
                                                        <div style="font-size:0.9rem;color:#6b46c1;font-weight:500;">
                                                            Approval Code
                                                        </div>
                                                        <div style="font-size:2rem;font-weight:700;color:#553c9a;
                                                                    letter-spacing:4px;font-family:'Courier New',monospace;">
                                                            {code}
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>""", unsafe_allow_html=True)
                                    st.balloons()
                                    st.session_state.generated_codes.clear()
                                    st.session_state.reset_form_tab1 = True
                                    time.sleep(2)
                                    st.rerun()

                            except Exception as e:
                                st.session_state.submission_in_progress = False
                                st.markdown(f"""<div class="error-message">
                                    <strong>Submission Error</strong><br>
                                    Please try again or contact HR.<br>Error: {str(e)}
                                </div>""", unsafe_allow_html=True)
                                log_debug(f"Submission error: {traceback.format_exc()}")
                        else:
                            st.session_state.submission_in_progress = False
                            st.markdown("""<div class="error-message">
                                <strong>&#x1F4CA; Database Connection Error</strong><br>
                                Could not connect to database. Please try again later.
                            </div>""", unsafe_allow_html=True)


# ============================================================
# TAB 2 — APPROVAL PORTAL (HR)
# ============================================================
with tab2:
    st.markdown("""
        <div class="section-header">
            <div class="icon-badge"
                 style="background:linear-gradient(135deg,#2196f3 0%,#03a9f4 100%);">&#x2705;</div>
            <div>
                <h3 style="margin:0;">HR Approval Portal</h3>
                <p style="margin:5px 0 0 0;color:#718096;font-size:0.95rem;">
                    Securely approve or reject leave requests using the approval code
                </p>
            </div>
        </div>""", unsafe_allow_html=True)

    st.markdown("""
        <div style="background:linear-gradient(135deg,#e3f2fd 0%,#bbdefb 100%);
                    padding:1.5rem;border-radius:12px;margin-bottom:2rem;
                    border:1px solid rgba(33,150,243,0.2);">
            <div style="display:flex;align-items:center;">
                <div style="font-size:1.5rem;margin-right:15px;color:#2196f3;">&#x1F512;</div>
                <div>
                    <strong style="color:#0d47a1;">Secure Authentication Required</strong><br>
                    <span style="color:#1565c0;font-size:0.95rem;">
                        Use the unique 5-character approval code sent to you via email.
                    </span>
                </div>
            </div>
        </div>""", unsafe_allow_html=True)

    if st.session_state.reset_form_tab2:
        st.session_state.form_data_tab2        = {"approval_password": "", "action": "Select Decision"}
        st.session_state.reset_form_tab2        = False
        st.session_state.submission_in_progress = False

    approval_code_input = st.text_input(
        "Approval Code",
        value=st.session_state.form_data_tab2["approval_password"],
        type="password",
        placeholder="Enter 5-character code",
        help="Enter the unique code from the approval email",
        key="approval_code_input",
    )

    st.markdown("---")
    action = st.selectbox("Select Action", ["Select Decision", "Approve", "Reject"],
                          index=0, label_visibility="collapsed", key="action_select")

    _, btn_col, _ = st.columns([1, 2, 1])
    with btn_col:
        disabled = st.session_state.get("submission_in_progress", False)
        if disabled:
            st.info("Processing… Please wait.")
        submit_decision = st.button("Submit Decision", type="primary",
                                    use_container_width=True, key="submit_decision_button",
                                    disabled=disabled)

        if submit_decision and not disabled:
            st.session_state.submission_in_progress = True
            if not approval_code_input or action == "Select Decision":
                st.session_state.submission_in_progress = False
                st.markdown("""<div class="error-message">
                    <strong>Missing Information</strong><br>
                    Please enter the approval code and select a decision.
                </div>""", unsafe_allow_html=True)
            elif len(approval_code_input) != 5:
                st.session_state.submission_in_progress = False
                st.markdown("""<div class="error-message">
                    <strong>&#x1F511; Invalid Code Format</strong><br>
                    Please enter the exact 5-character code from the approval email.
                </div>""", unsafe_allow_html=True)
            else:
                with st.spinner("Processing your decision…"):
                    sheet = setup_google_sheets()
                    if sheet:
                        status  = "Approved" if action == "Approve" else "Rejected"
                        success = update_leave_status(sheet, approval_code_input, status)
                        if success:
                            st.session_state.submission_in_progress = False
                            color  = "#155724" if status == "Approved" else "#721c24"
                            bg     = "#d4edda"  if status == "Approved" else "#f8d7da"
                            icon   = "&#x2705;" if status == "Approved" else "&#x274C;"
                            st.markdown(f"""
                                <div style="background:{bg};border-left:4px solid {color};
                                            color:{color};padding:2rem;border-radius:16px;
                                            margin:2rem 0;text-align:center;">
                                    <div style="font-size:3rem;margin-bottom:1rem;">{icon}</div>
                                    <div style="font-size:1.5rem;font-weight:600;margin-bottom:10px;">
                                        Decision Submitted Successfully!
                                    </div>
                                    <div style="margin-bottom:15px;">
                                        The leave request has been <strong>{status.lower()}</strong>.
                                    </div>
                                    <div style="font-size:0.95rem;opacity:0.9;">
                                        Confirmation email sent to HR.
                                    </div>
                                </div>""", unsafe_allow_html=True)
                            st.balloons()
                            st.session_state.reset_form_tab2 = True
                            time.sleep(2)
                            st.rerun()
                        else:
                            st.session_state.submission_in_progress = False
                            st.markdown("""<div class="error-message">
                                <strong>&#x1F510; Authentication Failed</strong><br>
                                Invalid code or code already used.<br>
                                Please check your approval code or contact HR for assistance.
                            </div>""", unsafe_allow_html=True)
                    else:
                        st.session_state.submission_in_progress = False
                        st.markdown("""<div class="error-message">
                            <strong>&#x1F4CA; Database Connection Error</strong><br>
                            Could not connect to the database. Please try again later.
                        </div>""", unsafe_allow_html=True)


# ============================================================
# TAB 3 — OUT OF OFFICE REQUEST (SUBMIT)
# ============================================================
with tab3:
    st.markdown("""
        <div class="section-header">
            <div class="icon-badge"
                 style="background:linear-gradient(135deg,#38d9a9 0%,#20c997 100%);">&#x1F3E2;</div>
            <div>
                <h3 style="margin:0;">Out of Office Request</h3>
                <p style="margin:5px 0 0 0;color:#718096;font-size:0.95rem;">
                    Submit requests for official out-of-office assignments
                </p>
            </div>
        </div>""", unsafe_allow_html=True)

    st.markdown("""
        <div style="background:linear-gradient(135deg,#e3f2fd 0%,#bbdefb 100%);
                    padding:1.5rem;border-radius:12px;margin-bottom:2rem;
                    border:1px solid rgba(33,150,243,0.2);">
            <div style="display:flex;align-items:center;">
                <div style="font-size:1.5rem;margin-right:15px;color:#2196f3;">&#x2139;&#xFE0F;</div>
                <div>
                    <strong style="color:#0d47a1;">How it works</strong><br>
                    <span style="color:#1565c0;font-size:0.95rem;">
                        Your request will be sent to <strong>HR</strong> for review.
                        HR will approve or reject it in the OOO Approval tab,
                        and you will be notified by email.
                    </span>
                </div>
            </div>
        </div>""", unsafe_allow_html=True)

    # ── reset guard (clears the widgets after a successful submission) ──
    if st.session_state.reset_form_tab4:
        st.session_state["wfh_employee_name"]  = ""
        st.session_state["wfh_employee_code"]  = ""
        st.session_state["wfh_employee_email"] = ""
        st.session_state["wfh_request_type"]   = OOO_REQUEST_TYPE
        st.session_state["wfh_start_date"]     = datetime.now().date()
        st.session_state["wfh_end_date"]       = datetime.now().date()
        st.session_state["wfh_reason"]         = ""
        st.session_state.reset_form_tab4            = False
        st.session_state.wfh_submission_in_progress = False

    w1, w2, w3 = st.columns([1, 1, 1], gap="large")
    with w1:
        wfh_employee_name = st.text_input("Employee Name", placeholder="Enter your full name",
                                          key="wfh_employee_name")
    with w2:
        wfh_employee_code = st.text_input("Employee Code", placeholder="e.g., AF-EMP-001",
                                          key="wfh_employee_code")
    with w3:
        wfh_employee_email = st.text_input("Employee Email", placeholder="your.email@company.com",
                                           key="wfh_employee_email")

    st.markdown("---")
    st.markdown("""
        <div style="margin-bottom:1.5rem;">
            <div style="display:flex;align-items:center;margin-bottom:1rem;">
                <div class="icon-badge"
                     style="background:linear-gradient(135deg,#4dabf7 0%,#339af0 100%);">&#x1F4CB;</div>
                <div>
                    <h4 style="margin:0;">Request Type</h4>
                    <p style="margin:5px 0 0 0;color:#718096;font-size:0.9rem;">
                        Type of request you are submitting
                    </p>
                </div>
            </div>
        </div>""", unsafe_allow_html=True)

    wfh_request_type = st.selectbox(
        "Request Type",
        [OOO_REQUEST_TYPE],
        key="wfh_request_type",
    )

    st.markdown("---")
    st.markdown("""
        <div style="margin-bottom:1.5rem;">
            <div style="display:flex;align-items:center;margin-bottom:1rem;">
                <div class="icon-badge"
                     style="background:linear-gradient(135deg,#4caf50 0%,#388e3c 100%);">&#x1F4C5;</div>
                <div>
                    <h4 style="margin:0;">Date Range</h4>
                    <p style="margin:5px 0 0 0;color:#718096;font-size:0.9rem;">
                        Select the start and end dates for your request
                    </p>
                </div>
            </div>
        </div>""", unsafe_allow_html=True)

    d1, d2 = st.columns([1, 1], gap="large")
    with d1:
        wfh_start_date = st.date_input("Start Date",
                                       min_value=datetime.now().date() - timedelta(days=60),
                                       key="wfh_start_date")
    with d2:
        wfh_end_date = st.date_input("End Date",
                                     min_value=datetime.now().date() - timedelta(days=60),
                                     key="wfh_end_date")

    if wfh_start_date and wfh_end_date:
        if wfh_end_date < wfh_start_date:
            st.error("End date cannot be before start date")
        else:
            total_days_wfh = (wfh_end_date - wfh_start_date).days + 1
            st.markdown(f"""
                <div style="background:linear-gradient(135deg,#4dabf7 0%,#339af0 100%);
                            color:white;padding:1rem;border-radius:12px;text-align:center;margin:1rem 0;">
                    <div style="font-size:0.9rem;">Total Duration</div>
                    <div style="font-size:2rem;font-weight:bold;">{total_days_wfh}</div>
                    <div style="font-size:0.8rem;">day(s)</div>
                </div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
        <div style="margin-bottom:1.5rem;">
            <div style="display:flex;align-items:center;margin-bottom:1rem;">
                <div class="icon-badge"
                     style="background:linear-gradient(135deg,#ff9800 0%,#f57c00 100%);">&#x1F4DD;</div>
                <div>
                    <h4 style="margin:0;">Reason for Request</h4>
                    <p style="margin:5px 0 0 0;color:#718096;font-size:0.9rem;">
                        Provide a detailed explanation for your request
                    </p>
                </div>
            </div>
        </div>""", unsafe_allow_html=True)

    wfh_reason = st.text_area(
        "Reason / Purpose",
        placeholder="Please provide a clear and detailed explanation for your request...",
        height=150, key="wfh_reason",
    )

    st.markdown("---")
    _, wfh_submit_col, _ = st.columns([1, 2, 1])
    with wfh_submit_col:
        wfh_submit_disabled = st.session_state.get("wfh_submission_in_progress", False)
        if wfh_submit_disabled:
            st.info("Processing your submission… Please wait.")
        wfh_submit_button = st.button("Submit Request", type="primary",
                                      use_container_width=True, key="submit_wfh_request",
                                      disabled=wfh_submit_disabled)

        if wfh_submit_button and not wfh_submit_disabled:
            st.session_state.wfh_submission_in_progress = True
            wfh_form_data = {
                "employee_name": wfh_employee_name,
                "employee_code": wfh_employee_code,
                "request_type":  wfh_request_type,
                "start_date":    wfh_start_date,
                "end_date":      wfh_end_date,
                "reason":        wfh_reason,
            }
            is_dup, dup_msg = check_duplicate_wfh_submission(wfh_form_data)
            if is_dup:
                st.session_state.wfh_submission_in_progress = False
                st.markdown(f"""<div class="error-message">
                    <strong>Duplicate Submission Detected</strong><br>{dup_msg}
                </div>""", unsafe_allow_html=True)
            else:
                errors = []
                if not all([wfh_employee_name, wfh_employee_code, wfh_reason]):
                    errors.append("Please complete all required fields (Name, Code, Reason)")
                if wfh_employee_email and ("@" not in wfh_employee_email or "." not in wfh_employee_email):
                    errors.append("Please enter a valid employee email address")
                if wfh_end_date < wfh_start_date:
                    errors.append("End date cannot be before start date")

                if errors:
                    st.session_state.wfh_submission_in_progress = False
                    html = "<div class='error-message'><strong>Validation Error</strong><br>"
                    for e in errors: html += f"{e}<br>"
                    st.markdown(html + "</div>", unsafe_allow_html=True)
                else:
                    with st.spinner("Submitting your request…"):
                        wfh_ok, wfh_msg, wfh_email_sent, wfh_code = submit_wfh_request(
                            wfh_employee_name, wfh_employee_code, wfh_employee_email,
                            wfh_request_type, wfh_start_date, wfh_end_date, wfh_reason,
                        )
                    st.session_state.wfh_submission_in_progress = False

                    if wfh_ok:
                        st.session_state.last_wfh_submission_hash = generate_wfh_hash(wfh_form_data)
                        st.session_state.wfh_submission_timestamp = datetime.now()
                        duration_wfh = (wfh_end_date - wfh_start_date).days + 1

                        if wfh_email_sent:
                            st.markdown(f"""
                                <div class="success-message">
                                    <div style="font-size:3rem;margin-bottom:1rem;">&#x2728;</div>
                                    <div style="font-size:1.5rem;font-weight:600;margin-bottom:10px;">
                                        Request Submitted Successfully!
                                    </div>
                                    <div style="margin-bottom:15px;">
                                        Your Out of Office request has been submitted
                                        and HR has been notified.
                                    </div>
                                    <div style="font-size:0.95rem;opacity:0.9;">
                                        Request Type: {wfh_request_type}<br>
                                        Duration: {duration_wfh} day(s)<br>
                                        You will receive an email once a decision is made.
                                    </div>
                                </div>""", unsafe_allow_html=True)
                            st.balloons()
                            st.session_state.reset_form_tab4 = True
                            time.sleep(2)
                            st.rerun()
                        else:
                            # Saved, but the approval email failed -> keep the code on screen for HR.
                            st.session_state.reset_form_tab4 = True
                            st.markdown(f"""
                                <div class="info-box">
                                    <strong style="color:#ff9800;">&#x1F4E7; Email Notification Issue</strong><br>
                                    Your request was saved successfully, but the approval email
                                    could not be sent automatically.<br>
                                    Please inform HR and share this approval code:
                                    <div style="text-align:center;font-size:2rem;font-weight:700;
                                                color:#553c9a;letter-spacing:4px;margin-top:1rem;
                                                font-family:'Courier New',monospace;">{wfh_code}</div>
                                </div>""", unsafe_allow_html=True)
                    else:
                        st.markdown(f"""<div class="error-message">
                            <strong>&#x274C; Submission Error</strong><br>
                            {wfh_msg}<br>
                            Please try again or contact HR for assistance.
                        </div>""", unsafe_allow_html=True)


# ============================================================
# TAB 4 — OOO APPROVAL PORTAL (HR)
# ============================================================
with tab4:
    st.markdown("""
        <div class="section-header">
            <div class="icon-badge"
                 style="background:linear-gradient(135deg,#20c997 0%,#0ca678 100%);">&#x1F4F2;</div>
            <div>
                <h3 style="margin:0;">Out of Office Approval Portal</h3>
                <p style="margin:5px 0 0 0;color:#718096;font-size:0.95rem;">
                    For HR use only — approve or reject Out of Office requests
                </p>
            </div>
        </div>""", unsafe_allow_html=True)

    st.markdown("""
        <div style="background:linear-gradient(135deg,#e0f7f4 0%,#b2dfdb 100%);
                    padding:1.5rem;border-radius:12px;margin-bottom:2rem;
                    border:1px solid rgba(32,201,151,0.3);">
            <div style="display:flex;align-items:center;">
                <div style="font-size:1.5rem;margin-right:15px;color:#0ca678;">&#x1F512;</div>
                <div>
                    <strong style="color:#065f46;">HR Authentication Required</strong><br>
                    <span style="color:#047857;font-size:0.95rem;">
                        Enter the 5-character OOO approval code received by email.
                        This portal is for <strong>HR use only</strong>. The employee is notified
                        automatically once a decision is submitted.
                    </span>
                </div>
            </div>
        </div>""", unsafe_allow_html=True)

    if st.session_state.reset_form_tab5:
        st.session_state["wfh_approval_code_input"] = ""
        st.session_state["wfh_action_select"]       = "Select Decision"
        st.session_state.reset_form_tab5            = False
        st.session_state.wfh_decision_in_progress   = False

    st.markdown("""
        <div style="margin-bottom:1.5rem;">
            <div style="display:flex;align-items:center;margin-bottom:1rem;">
                <div class="icon-badge"
                     style="background:linear-gradient(135deg,#20c997 0%,#0ca678 100%);">&#x1F511;</div>
                <div>
                    <h4 style="margin:0;">Enter OOO Approval Code</h4>
                    <p style="margin:5px 0 0 0;color:#718096;font-size:0.9rem;">
                        The 5-character code was emailed to HR when the employee submitted the request
                    </p>
                </div>
            </div>
        </div>""", unsafe_allow_html=True)

    wfh_code_input = st.text_input(
        "OOO Approval Code",
        type="password",
        placeholder="Enter 5-character OOO approval code",
        help="Enter the unique code from the OOO approval email sent to HR",
        key="wfh_approval_code_input",
    )

    st.markdown("---")
    st.markdown("""
        <div style="margin-bottom:1.5rem;">
            <div style="display:flex;align-items:center;margin-bottom:1rem;">
                <div class="icon-badge"
                     style="background:linear-gradient(135deg,#4caf50 0%,#388e3c 100%);">&#x1F4CB;</div>
                <div>
                    <h4 style="margin:0;">HR Decision</h4>
                    <p style="margin:5px 0 0 0;color:#718096;font-size:0.9rem;">
                        Select your decision for this Out of Office request
                    </p>
                </div>
            </div>
        </div>""", unsafe_allow_html=True)

    wfh_action = st.selectbox("Select Decision", ["Select Decision", "Approve", "Reject"],
                              label_visibility="collapsed", key="wfh_action_select")

    st.markdown("---")
    _, wfh_decision_col, _ = st.columns([1, 2, 1])
    with wfh_decision_col:
        wfh_decision_disabled = st.session_state.get("wfh_decision_in_progress", False)
        if wfh_decision_disabled:
            st.info("Processing your decision… Please wait.")
        wfh_decision_button = st.button("Submit OOO Decision", type="primary",
                                        use_container_width=True, key="submit_wfh_decision_button",
                                        disabled=wfh_decision_disabled)

        if wfh_decision_button and not wfh_decision_disabled:
            st.session_state.wfh_decision_in_progress = True
            wfh_code_clean = (wfh_code_input or "").strip().upper()

            if not wfh_code_clean or wfh_action == "Select Decision":
                st.session_state.wfh_decision_in_progress = False
                st.markdown("""<div class="error-message">
                    <strong>&#x26A0;&#xFE0F; Missing Information</strong><br>
                    Please enter the OOO approval code and select a decision.
                </div>""", unsafe_allow_html=True)
            elif len(wfh_code_clean) != 5:
                st.session_state.wfh_decision_in_progress = False
                st.markdown("""<div class="error-message">
                    <strong>&#x1F511; Invalid Code Format</strong><br>
                    Please enter the exact 5-character OOO approval code from the email.
                </div>""", unsafe_allow_html=True)
            else:
                with st.spinner("Processing your OOO decision…"):
                    wfh_sheet = setup_wfh_sheet()
                    if wfh_sheet:
                        wfh_status  = "Approved" if wfh_action == "Approve" else "Rejected"
                        wfh_success = update_wfh_status(wfh_sheet, wfh_code_clean, wfh_status)
                    else:
                        wfh_status, wfh_success = "", None   # None = could not reach the sheet
                st.session_state.wfh_decision_in_progress = False

                if wfh_success:
                    s_color = "#155724" if wfh_status == "Approved" else "#721c24"
                    s_bg    = "#d4edda"  if wfh_status == "Approved" else "#f8d7da"
                    s_icon  = "&#x2705;" if wfh_status == "Approved" else "&#x274C;"
                    st.markdown(f"""
                        <div style="background:{s_bg};border-left:4px solid {s_color};
                                    color:{s_color};padding:2rem;border-radius:16px;
                                    margin:2rem 0;text-align:center;">
                            <div style="font-size:3rem;margin-bottom:1rem;">{s_icon}</div>
                            <div style="font-size:1.5rem;font-weight:600;margin-bottom:10px;">
                                OOO Decision Submitted Successfully!
                            </div>
                            <div style="margin-bottom:15px;">
                                The Out of Office request has been <strong>{wfh_status.lower()}</strong>.
                            </div>
                            <div style="font-size:0.95rem;opacity:0.9;">
                                &#x2709;&#xFE0F; The employee has been notified by email.<br>
                                A confirmation has been sent to HR.
                            </div>
                        </div>""", unsafe_allow_html=True)
                    st.balloons()
                    st.session_state.reset_form_tab5 = True
                    time.sleep(2)
                    st.rerun()
                elif wfh_success is None:
                    st.markdown("""<div class="error-message">
                        <strong>&#x1F4CA; Database Connection Error</strong><br>
                        Could not connect to the OOO worksheet. Please try again later.
                    </div>""", unsafe_allow_html=True)
                else:
                    st.markdown("""<div class="error-message">
                        <strong>&#x1F510; Authentication Failed</strong><br>
                        Invalid OOO code.<br>
                        Please check the code from the HR email or contact the system administrator.
                    </div>""", unsafe_allow_html=True)


# ============================================================
# FOOTER
# ============================================================
st.markdown("""
    <div class="footer">
        <div style="margin-bottom:1rem;">
            <strong style="color:#673ab7;">ANULACH FASHION PVT LTD</strong><br>
            Human Resources Management System
        </div>
        <div style="font-size:0.9rem;">
            &copy; 2026 ANULACH FASHION. All rights reserved.
        </div>
    </div>
""", unsafe_allow_html=True)
