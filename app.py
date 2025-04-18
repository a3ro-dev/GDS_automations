import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os
import re
import json
import base64
import hmac
import hashlib
from backend.backend import generate_personalized_message, get_base_template # Import get_base_template here
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Page Configuration ---
st.set_page_config(
    page_title="GDS-Lucknow MUN 2025",
    page_icon="🗿", # Changed icon
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- Custom CSS --- (Centralized and Improved)
st.markdown("""
<style>
    /* General Styles */
    body {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji";
    }
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        padding-left: 2rem;
        padding-right: 2rem;
    }
    h1, h2, h3 {
        color: #1E3A8A; /* Dark Blue */
        font-weight: 600;
    }
    h1 {
        border-bottom: 2px solid #DBEAFE; /* Light Blue */
        padding-bottom: 0.5rem;
        margin-bottom: 1.5rem;
    }
    h3 {
        margin-top: 1.5rem;
        margin-bottom: 0.75rem;
    }

    /* Buttons */
    .stButton > button {
        background-color: #2563EB; /* Medium Blue */
        color: white;
        border-radius: 8px;
        border: none;
        padding: 0.6rem 1.2rem;
        font-weight: 500;
        transition: background-color 0.2s ease;
        width: auto; /* Default width */
        min-width: 120px;
    }
    .stButton > button:hover {
        background-color: #1D4ED8; /* Darker Blue */
    }
    .stButton > button:active {
        background-color: #1E40AF; /* Even Darker Blue */
    }
    /* Specific Button Styling (e.g., full width if needed) */
    .stButton.full-width > button {
        width: 100%;
    }
    /* Back Button Style */
    .stButton.back-button > button {
        background-color: #F3F4F6; /* Light Gray */
        color: #374151; /* Dark Gray Text */
        font-weight: 500;
    }
    .stButton.back-button > button:hover {
        background-color: #E5E7EB; /* Medium Gray */
    }

    /* Forms & Inputs */
    .stTextInput input, .stTextArea textarea, .stSelectbox select, .stDateInput input {
        border-radius: 8px;
        border: 1px solid #D1D5DB; /* Gray border */
        padding: 0.5rem 0.75rem;
    }
    .stTextInput input:focus, .stTextArea textarea:focus, .stSelectbox select:focus, .stDateInput input:focus {
        border-color: #2563EB; /* Blue border on focus */
        box-shadow: 0 0 0 2px #BFDBFE; /* Blue glow */
    }
    .stForm {
        border: 1px solid #E5E7EB; /* Light Gray border */
        border-radius: 8px;
        padding: 1.5rem;
        background-color: #FFFFFF;
        margin-bottom: 1.5rem;
    }
    .stForm label {
        font-weight: 500;
        color: #374151; /* Dark Gray */
    }

    /* Highlight Box */
    .highlight {
        padding: 1.5rem;
        border-radius: 8px;
        background-color: #EFF6FF; /* Very Light Blue */
        border-left: 5px solid #3B82F6; /* Medium Blue */
        margin-bottom: 1.5rem;
        color: #1E3A8A; /* Dark Blue Text */
    }
    .highlight h3 {
        margin-top: 0;
        color: #1E40AF; /* Slightly darker blue for heading */
    }
    .highlight p {
        margin-bottom: 0.5rem;
    }
    .highlight small {
        color: #6B7280; /* Gray text */
        font-size: 0.9em;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
        border-bottom: 2px solid #E5E7EB;
    }
    .stTabs [data-baseweb="tab"] {
        height: 48px;
        white-space: pre-wrap;
        background-color: transparent;
        border-radius: 4px 4px 0 0;
        padding: 0.75rem 1rem;
        color: #4B5563; /* Gray */
    }
    .stTabs [aria-selected="true"] {
        background-color: transparent;
        font-weight: 600;
        color: #1D4ED8; /* Darker Blue */
        border-bottom: 3px solid #1D4ED8;
    }

    /* Text Area & Preview Box */
    .styled-text-box {
        padding: 1.5rem;
        border: 1px solid #D1D5DB; /* Gray border */
        border-radius: 8px;
        background-color: #F9FAFB; /* Very Light Gray */
        margin-bottom: 1.5rem;
        font-family: monospace;
        white-space: pre-wrap; /* Preserve line breaks */
        line-height: 1.6;
        color: #1F2937; /* Dark Gray Text */
    }

    /* Expander */
    .stExpander {
        border: 1px solid #E5E7EB;
        border-radius: 8px;
        overflow: hidden; /* Ensures border radius applies correctly */
    }
    .stExpander header {
        background-color: #F9FAFB;
        padding: 0.75rem 1rem;
        border-bottom: 1px solid #E5E7EB;
    }
    .stExpander header:hover {
        background-color: #F3F4F6;
    }

    /* Mobile Responsiveness */
    @media screen and (max-width: 768px) {
        .main .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }
        .stButton > button {
            width: 100%; /* Full width buttons on mobile */
        }
        .stForm {
            padding: 1rem;
        }
        /* Stack columns on mobile */
        div[data-testid="column"] {
            width: 100% !important;
            margin-bottom: 1rem;
        }
        div[data-testid="column"]:last-child {
            margin-bottom: 0;
        }
    }
</style>
""", unsafe_allow_html=True)

# --- Constants & Session State Initialization ---
CREDENTIALS = {
    os.getenv("USER_NAME", "delegateAffairsManager"): os.getenv("USER_PASSWORD", "GDSFTW")
}
CSV_PATH = "delegates.csv"
DEFAULT_COLUMNS = ["Name", "Contact Info", "Response Status", "Follow-up Date"]
STATUS_OPTIONS = ["Interested", "No Response", "Registered", "Rejected"]
SECRET_KEY = os.getenv("SECRET_KEY", "GDS-LUCKNOW-MUN-2025-SECRET-KEY")
COOKIE_NAME = "gds_auth"

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'current_page' not in st.session_state:
    st.session_state.current_page = "home"
if 'username' not in st.session_state:
    st.session_state.username = None

# --- Helper Functions (Authentication, CSV, Filtering, etc.) ---
def ensure_csv_exists():
    if not os.path.exists(CSV_PATH):
        df = pd.DataFrame(columns=DEFAULT_COLUMNS)
        df.to_csv(CSV_PATH, index=False)
        return df
    try:
        df = pd.read_csv(CSV_PATH)
        # Convert 'Follow-up Date' strings to datetime for data_editor compatibility
        if 'Follow-up Date' in df.columns:
            df['Follow-up Date'] = pd.to_datetime(
                df['Follow-up Date'],
                format='%d %B %Y',
                errors='coerce'
            )
        return df
    except pd.errors.EmptyDataError:
        # If CSV exists but is empty, return an empty DataFrame with correct columns
        return pd.DataFrame(columns=DEFAULT_COLUMNS)
    except Exception as e:
        st.error(f"Error reading CSV: {e}")
        return pd.DataFrame(columns=DEFAULT_COLUMNS)

def save_to_csv(df):
    try:
        df.to_csv(CSV_PATH, index=False)
    except Exception as e:
        st.error(f"Error saving CSV: {e}")

def authenticate(username, password):
    return username in CREDENTIALS and CREDENTIALS[username] == password

def create_auth_token(username):
    payload = {
        "username": username,
        "exp": (datetime.now() + timedelta(days=30)).timestamp()
    }
    payload_str = json.dumps(payload)
    encoded_payload = base64.b64encode(payload_str.encode()).decode()
    signature = hmac.new(SECRET_KEY.encode(), encoded_payload.encode(), hashlib.sha256).hexdigest()
    return f"{encoded_payload}.{signature}"

def validate_auth_token(token):
    try:
        encoded_payload, signature = token.split(".", 1)
        expected_signature = hmac.new(SECRET_KEY.encode(), encoded_payload.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(signature, expected_signature):
            return None
        payload_str = base64.b64decode(encoded_payload).decode()
        payload = json.loads(payload_str)
        if datetime.fromtimestamp(payload["exp"]) < datetime.now():
            return None
        return payload["username"]
    except Exception as e:
        print(f"Error validating token: {e}")
        return None

def check_saved_credentials():
    query_params = st.query_params.to_dict() # Get a mutable dictionary
    if COOKIE_NAME in query_params:
        token = query_params[COOKIE_NAME][0] # Access first element if it's a list
        username = validate_auth_token(token)
        if username:
            st.session_state.authenticated = True
            st.session_state.username = username
            return True
    return False

def save_credentials(username):
    token = create_auth_token(username)
    st.query_params[COOKIE_NAME] = token

def clear_saved_credentials():
    if COOKIE_NAME in st.query_params:
        del st.query_params[COOKIE_NAME]
    st.session_state.username = None

def filter_dataframe(df, query):
    if query:
        query_lower = query.lower()
        # Ensure all columns are string type for filtering
        df_str = df.astype(str)
        mask = df_str.apply(lambda row: any(query_lower in val.lower() for val in row), axis=1)
        return df[mask]
    return df

def navigate_to(page):
    st.session_state.current_page = page
    st.rerun()

# --- Page Rendering Functions ---

def show_login_page():
    st.title("GDS-Lucknow MUN 2025")
    st.subheader("Delegate Affairs System")

    if check_saved_credentials():
        st.rerun()

    with st.form("login_form"):
        st.markdown("### Login")
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        remember_me = st.checkbox("Remember me", value=True, help="Stay logged in on this device", key="login_remember")
        submit_button = st.form_submit_button("Login")

        if submit_button:
            if authenticate(username, password):
                st.session_state.authenticated = True
                st.session_state.username = username
                if remember_me:
                    save_credentials(username)
                else:
                    # Clear any potentially existing cookie if not remembering
                    clear_saved_credentials()
                st.success("Login successful! Redirecting...")
                st.rerun()
            else:
                st.error("Invalid username or password")

def show_home_page():
    st.title("GDS-Lucknow MUN 2025 - Delegate Affairs System")

    if st.session_state.username:
        st.markdown(f"#### Welcome, {st.session_state.username}!")

    st.markdown("--- ") # Divider

    col1, col2 = st.columns(2)

    with col1:
        with st.container(border=True):
            st.subheader("📧 Cold Email Generator")
            st.write("Generate personalized outreach messages for potential delegates.")
            if st.button("Go to Email Generator", key="goto_email"):
                navigate_to("email_generator")

    with col2:
        with st.container(border=True):
            st.subheader("👥 Delegate Management")
            st.write("Manage delegate contacts, responses, and follow-ups.")
            if st.button("Go to Delegate Management", key="goto_delegates"):
                navigate_to("delegate_management")

    # Logout button at the bottom
    st.markdown("--- ")
    if st.button("Logout", key="logout_home", type="secondary"):
        clear_saved_credentials()
        st.session_state.authenticated = False
        st.session_state.username = None # Explicitly clear username
        st.rerun()

def show_email_generator():
    st.title("Cold Email Generator")

    # Back button
    if st.button("← Back to Home", key="back_from_email", type="secondary"):
        navigate_to("home")

    st.markdown("""
    <div class="highlight">
        <h3>Delegate Outreach Email Generator</h3>
        <p>Generate personalized invitation messages for the Global Diplomatic Summit-Lucknow MUN 2025.</p>
        <p><small>Use the basic template for quick outreach or generate a personalized message with specific delegate details.</small></p>
    </div>
    """, unsafe_allow_html=True)

    tabs = st.tabs(["📋 Basic Template", "✨ Personalized Message"])

    # --- Basic Template Tab ---
    with tabs[0]:
        st.markdown("### Basic Template Message")
        st.write("Use this pre-written message as a starting point:")

        base_template = get_base_template()

        # Display the template in a styled box
        st.markdown(f'<div class="styled-text-box">{base_template}</div>', unsafe_allow_html=True)

        st.markdown("### Customize & Copy")
        edited_template = st.text_area(
            "Edit the template if needed:",
            value=base_template,
            height=250, # Increased height
            key="template_edit_area"
        )

        # Use Streamlit button for copy action (more reliable)
        if st.button("Copy Template to Clipboard", key="copy_template_button", use_container_width=True):
            st.toast("Template copied!", icon="📋")
            # Use streamlit-js-eval or clipboard library if direct JS injection is problematic
            # For simplicity, we'll just show a toast here.
            # You might need to install pyperclip: pip install pyperclip
            try:
                import pyperclip
                pyperclip.copy(edited_template)
            except ImportError:
                st.warning("Could not copy automatically. Please copy manually from the text area.")
            except Exception as e:
                 st.warning(f"Could not copy automatically ({e}). Please copy manually.")

    # --- Personalized Message Tab ---
    with tabs[1]:
        st.markdown("### Generate Personalized Message")
        st.write("Enter delegate details to create a unique invitation:")

        with st.form("email_form"):
            delegate_name = st.text_input("Delegate Name *", placeholder="Enter delegate's full name", key="delegate_name_input")

            st.markdown("**Basic Details (Optional)**")
            col1, col2 = st.columns(2)
            with col1:
                committee_preference = st.selectbox(
                    "Committee Preference",
                    ["", "UNSC", "UNHRC", "ECOSOC", "DISEC", "WHO", "ICJ", "Crisis Committee"],
                    key="committee_pref"
                )
                position = st.selectbox(
                    "Position",
                    ["", "Delegate", "Head Delegate", "Faculty Advisor", "Observer"],
                    key="position_select"
                )
            with col2:
                institution = st.text_input("Institution/University", placeholder="e.g., Harvard University", key="institution_input")
                experience_level = st.selectbox(
                    "Experience Level",
                    ["", "First-time", "Beginner", "Intermediate", "Advanced", "Professional"],
                    key="experience_select"
                )

            with st.expander("Additional Customization Options"):
                event_highlight = st.text_area(
                    "Event Highlight",
                    placeholder="Mention specific conference highlights or special events (max 200 chars)",
                    max_chars=200,
                    key="event_highlight_input"
                )
                special_invite = st.text_input(
                    "Special Invitation Note",
                    placeholder="e.g., Based on your exceptional performance at XYZ conference...",
                    key="special_invite_input"
                )
                deadline_info = st.date_input(
                    "Registration Deadline",
                    value=None,
                    key="deadline_input"
                )
                tone_choice = st.select_slider(
                    "Message Tone",
                    options=["Formal", "Semi-formal", "Conversational"],
                    value="Semi-formal",
                    key="tone_slider"
                )

            submit_email = st.form_submit_button("Generate Personalized Email", use_container_width=True)

        if submit_email:
            if not delegate_name:
                st.warning("Please enter a Delegate Name to generate an email.")
            else:
                details = {"name": delegate_name}
                # Add optional fields only if they have a value
                if committee_preference: details["committee"] = committee_preference
                if position: details["position"] = position
                if institution: details["institution"] = institution
                if experience_level: details["experience_level"] = experience_level
                if event_highlight: details["event_highlight"] = event_highlight
                if special_invite: details["special_invite"] = special_invite
                if deadline_info: details["deadline"] = deadline_info.strftime("%B %d, %Y")
                details["tone"] = tone_choice

                with st.spinner("✨ Generating personalized email..."):
                    try:
                        personalized_message = generate_personalized_message(details)
                        if personalized_message:
                            st.success("Email generated successfully!")
                            st.session_state.generated_message = personalized_message # Store for editing/copying
                            st.session_state.current_delegate_name = delegate_name # Store name for adding to list
                        else:
                            st.error("Failed to generate email. Check backend logs or API keys.")
                    except Exception as e:
                        st.error(f"An error occurred: {str(e)}")

        # Display generated message outside the form if it exists in session state
        if 'generated_message' in st.session_state and st.session_state.generated_message:
            st.markdown("--- ")
            st.markdown("### Generated Email Preview")
            st.markdown(f'<div class="styled-text-box">{st.session_state.generated_message}</div>', unsafe_allow_html=True)

            st.markdown("### Edit & Actions")
            edited_message = st.text_area(
                "Edit the message if needed:",
                value=st.session_state.generated_message,
                height=250,
                key="generated_edit_area"
            )

            col1, col2 = st.columns(2)
            with col1:
                if st.button("Copy Generated Message", key="copy_generated_button", use_container_width=True):
                    st.toast("Generated message copied!", icon="✨")
                    try:
                        import pyperclip
                        pyperclip.copy(edited_message)
                        st.session_state.generated_message = edited_message # Update session state if edited before copy
                    except ImportError:
                        st.warning("Could not copy automatically. Please copy manually.")
                    except Exception as e:
                        st.warning(f"Could not copy automatically ({e}). Please copy manually.")

            with col2:
                if st.button("Add to Delegate List", key="add_delegate_button", help="Add this delegate to your tracking list", use_container_width=True):
                    if 'current_delegate_name' in st.session_state and st.session_state.current_delegate_name:
                        df = ensure_csv_exists()
                        # Check if delegate already exists
                        if st.session_state.current_delegate_name in df['Name'].values:
                            st.warning(f"Delegate '{st.session_state.current_delegate_name}' already exists in the list.")
                        else:
                            follow_up = (datetime.now() + timedelta(days=3)).strftime("%d %B %Y")
                            new_row = pd.DataFrame({
                                "Name": [st.session_state.current_delegate_name],
                                "Contact Info": ["Add contact info"], # Default placeholder
                                "Response Status": ["No Response"],
                                "Follow-up Date": [follow_up]
                            })
                            df = pd.concat([df, new_row], ignore_index=True)
                            save_to_csv(df)
                            st.success(f"✅ Delegate '{st.session_state.current_delegate_name}' added to tracking list!")
                            # Optionally clear generated message after adding
                            # del st.session_state.generated_message
                            # del st.session_state.current_delegate_name
                            # st.rerun()
                    else:
                        st.error("Delegate name not found to add to the list.")

            # Tips Expander
            with st.expander("💡 Tips for Effective Delegate Outreach"):
                st.markdown("""
                - **Personalize:** Add specific details about why they'd be a good fit.
                - **Follow up:** If no response, follow up gently after 3-4 days.
                - **Be Concise:** Keep your message brief and to the point.
                - **Highlight Benefits:** Focus on what they'll gain from participating.
                - **Clear Call to Action:** Make it obvious what you want them to do next (e.g., register, visit website).
                """)

def show_delegate_management():
    st.title("Delegate Management")

    if st.button("← Back to Home", key="back_from_delegates", type="secondary"):
        navigate_to("home")

    df = ensure_csv_exists()

    # --- Add New Delegate Form ---
    with st.expander("➕ Add New Delegate"):
        with st.form("add_delegate_form"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Name *", key="add_name")
                contact_info = st.text_input("Contact Info (Email/Phone)", key="add_contact")
            with col2:
                response_status = st.selectbox("Response Status", STATUS_OPTIONS, key="add_status")
                follow_up_date = st.date_input("Follow-up Date", value=datetime.now().date() + timedelta(days=3), key="add_date")

            submit_delegate = st.form_submit_button("Add Delegate", use_container_width=True)

            if submit_delegate:
                if not name:
                    st.warning("Delegate Name is required.")
                elif name in df['Name'].values:
                     st.warning(f"Delegate '{name}' already exists.")
                else:
                    formatted_date = follow_up_date.strftime("%d %B %Y")
                    new_row = pd.DataFrame({
                        "Name": [name],
                        "Contact Info": [contact_info],
                        "Response Status": [response_status],
                        "Follow-up Date": [formatted_date]
                    })
                    df = pd.concat([df, new_row], ignore_index=True)
                    save_to_csv(df)
                    st.success(f"Added delegate: {name}")
                    st.rerun() # Rerun to update the list below

    st.markdown("--- ")
    st.subheader("Current Delegates")

    # --- Search & Filter ---
    search_query = st.text_input("Search Delegates", placeholder="Search by name, contact, status...", key="search_delegates")
    filtered_df = filter_dataframe(df, search_query)

    st.write(f"Showing {len(filtered_df)} of {len(df)} delegates.")

    # --- Display Delegates --- (Using st.data_editor for inline editing)
    if not filtered_df.empty:
        # Configure columns for data_editor
        column_config = {
            "Name": st.column_config.TextColumn("Name", required=True),
            "Contact Info": st.column_config.TextColumn("Contact Info"),
            "Response Status": st.column_config.SelectboxColumn(
                "Response Status",
                options=STATUS_OPTIONS,
                required=True,
            ),
            "Follow-up Date": st.column_config.DateColumn(
                "Follow-up Date",
                format="DD MMMM YYYY", # Format for display and input
                required=True,
            ),
        }

        # Use st.data_editor for a table-like editing experience
        edited_df = st.data_editor(
            filtered_df,
            column_config=column_config,
            num_rows="dynamic", # Allow adding/deleting rows
            key="delegate_editor",
            use_container_width=True,
            hide_index=True, # Don't show pandas index
        )

        # --- Save Changes from Data Editor ---
        # Detect changes by comparing edited_df with the original filtered_df
        # This comparison needs care, especially with data types (like dates)
        # A simple approach: if the data editor is used, assume changes might have happened
        # and update the main dataframe (df)

        # Create a button to explicitly save changes made in the editor
        if st.button("Save Changes to Delegate List", key="save_editor_changes", type="primary"):
            try:
                # Update the original DataFrame (df) based on changes in edited_df
                # This requires matching rows, e.g., by Name if it's unique, or by index
                # For simplicity, let's update based on the index from filtered_df
                # Convert Follow-up Date back to string format for saving
                edited_df_copy = edited_df.copy()
                if 'Follow-up Date' in edited_df_copy.columns:
                     # Ensure the column exists and handle potential NaT values before formatting
                    edited_df_copy['Follow-up Date'] = pd.to_datetime(edited_df_copy['Follow-up Date']).dt.strftime('%d %B %Y').fillna('')

                # Update existing rows in the main df
                df.update(edited_df_copy)

                # Handle added rows (rows in edited_df not in filtered_df's original index)
                new_rows = edited_df_copy[~edited_df_copy.index.isin(filtered_df.index)]
                if not new_rows.empty:
                    df = pd.concat([df, new_rows]).reset_index(drop=True)

                # Handle deleted rows (rows in filtered_df not in edited_df's index)
                deleted_indices = filtered_df.index.difference(edited_df.index)
                if not deleted_indices.empty:
                    df = df.drop(index=deleted_indices).reset_index(drop=True)

                save_to_csv(df)
                st.success("Delegate list updated successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"Error saving changes: {e}")

    else:
        st.info("No delegates found matching your search criteria, or the list is empty.")

    # --- Export Functionality ---
    st.markdown("--- ")
    if not df.empty:
        csv_data = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Export Delegates as CSV",
            data=csv_data,
            file_name="delegates_export.csv",
            mime="text/csv",
            key="export_csv",
            use_container_width=True
        )

# --- Main App Logic ---
def main():
    Path("backend").mkdir(exist_ok=True)

    if not st.session_state.authenticated:
        # Try to authenticate using saved credentials before showing login
        if not check_saved_credentials():
            show_login_page()
        else:
            # If check_saved_credentials was successful, it sets authenticated state
            # We need to rerun to reflect the logged-in state
            st.rerun()
    else:
        # User is authenticated, show the requested page
        page = st.session_state.current_page
        if page == "home":
            show_home_page()
        elif page == "email_generator":
            show_email_generator()
        elif page == "delegate_management":
            show_delegate_management()
        else:
            # Default to home page if current_page is invalid
            show_home_page()

if __name__ == "__main__":
    main()