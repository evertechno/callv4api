import streamlit as st
import requests
import json
from datetime import datetime
import pandas as pd

# Page configuration
st.set_page_config(
    page_title="MSP API Manager",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: #2c3e50;
        margin-top: 2rem;
        margin-bottom: 1rem;
        border-bottom: 2px solid #1f77b4;
        padding-bottom: 0.5rem;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
    }
    .error-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
    }
    .info-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        color: #0c5460;
    }
    </style>
""", unsafe_allow_html=True)

# API Configuration
BASE_URL = "https://vwhxcuylitpawxjplfnq.supabase.co/functions/v1/msp-gateway"

class MSPAPIClient:
    """Client for MSP API operations"""
    
    def __init__(self, api_key):
        self.api_key = api_key
        self.headers = {
            "Content-Type": "application/json",
            "x-msp-api-key": api_key
        }
    
    def get_enboxes(self):
        """Fetch all Enboxes"""
        try:
            response = requests.get(
                f"{BASE_URL}/enboxes",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json(), None
        except requests.exceptions.RequestException as e:
            return None, str(e)
    
    def create_enbox(self, email, password, display_name, create_via="direct"):
        """Create a new Enbox"""
        try:
            payload = {
                "email": email,
                "password": password,
                "display_name": display_name,
                "create_via": create_via
            }
            response = requests.post(
                f"{BASE_URL}/enboxes",
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            return response.json(), None
        except requests.exceptions.RequestException as e:
            return None, str(e)
    
    def get_enbox(self, enbox_id):
        """Get specific Enbox details"""
        try:
            response = requests.get(
                f"{BASE_URL}/enboxes/{enbox_id}",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json(), None
        except requests.exceptions.RequestException as e:
            return None, str(e)
    
    def update_enbox(self, enbox_id, update_data):
        """Update an Enbox"""
        try:
            response = requests.put(
                f"{BASE_URL}/enboxes/{enbox_id}",
                headers=self.headers,
                json=update_data
            )
            response.raise_for_status()
            return response.json(), None
        except requests.exceptions.RequestException as e:
            return None, str(e)
    
    def delete_enbox(self, enbox_id):
        """Delete an Enbox"""
        try:
            response = requests.delete(
                f"{BASE_URL}/enboxes/{enbox_id}",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json(), None
        except requests.exceptions.RequestException as e:
            return None, str(e)

def init_session_state():
    """Initialize session state variables"""
    if 'api_key' not in st.session_state:
        st.session_state.api_key = None
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'enboxes_data' not in st.session_state:
        st.session_state.enboxes_data = None

def authenticate():
    """Handle API key authentication"""
    st.markdown('<div class="main-header">🔐 MSP API Manager</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="info-box">Enter your MSP API key to manage customer Enboxes</div>', unsafe_allow_html=True)
    
    # Try to get API key from secrets first
    api_key_from_secrets = None
    try:
        api_key_from_secrets = st.secrets.get("msp_api_key")
    except:
        pass
    
    if api_key_from_secrets:
        st.info("API key loaded from secrets")
        api_key = api_key_from_secrets
        if st.button("Use API Key from Secrets", type="primary"):
            st.session_state.api_key = api_key
            st.session_state.authenticated = True
            st.rerun()
    
    st.markdown("---")
    st.subheader("Or enter API key manually:")
    
    api_key_input = st.text_input(
        "MSP API Key",
        type="password",
        placeholder="msp_your_key_here",
        help="Enter your MSP API key. It should start with 'msp_'"
    )
    
    if st.button("Connect", type="primary"):
        if api_key_input and api_key_input.startswith("msp_"):
            # Test the API key
            client = MSPAPIClient(api_key_input)
            data, error = client.get_enboxes()
            
            if error:
                st.markdown(f'<div class="error-box">❌ Authentication failed: {error}</div>', unsafe_allow_html=True)
            else:
                st.session_state.api_key = api_key_input
                st.session_state.authenticated = True
                st.success("✅ Successfully authenticated!")
                st.rerun()
        else:
            st.markdown('<div class="error-box">❌ Please enter a valid API key (must start with "msp_")</div>', unsafe_allow_html=True)

def display_enboxes_list(client):
    """Display list of all Enboxes"""
    st.markdown('<div class="section-header">📦 Enboxes</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    
    with col2:
        if st.button("🔄 Refresh", use_container_width=True):
            st.session_state.enboxes_data = None
    
    # Fetch enboxes
    if st.session_state.enboxes_data is None:
        with st.spinner("Loading Enboxes..."):
            data, error = client.get_enboxes()
            
            if error:
                st.markdown(f'<div class="error-box">❌ Error loading Enboxes: {error}</div>', unsafe_allow_html=True)
                return
            
            st.session_state.enboxes_data = data
    
    data = st.session_state.enboxes_data
    
    if not data or len(data) == 0:
        st.info("No Enboxes found. Create your first one below!")
        return
    
    # Display count
    st.metric("Total Enboxes", len(data))
    
    # Convert to DataFrame for better display
    df_data = []
    for enbox in data:
        df_data.append({
            "ID": enbox.get("id", "N/A"),
            "Email": enbox.get("email", "N/A"),
            "Display Name": enbox.get("display_name", "N/A"),
            "Created Via": enbox.get("create_via", "N/A"),
            "Created At": enbox.get("created_at", "N/A")
        })
    
    df = pd.DataFrame(df_data)
    
    # Search functionality
    search_term = st.text_input("🔍 Search Enboxes", placeholder="Search by email, name, or ID...")
    
    if search_term:
        mask = df.astype(str).apply(lambda x: x.str.contains(search_term, case=False, na=False)).any(axis=1)
        df = df[mask]
    
    # Display table
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )
    
    # Detailed view
    with st.expander("📋 View Detailed JSON"):
        selected_id = st.selectbox(
            "Select Enbox to view details",
            options=[enbox.get("id") for enbox in data],
            format_func=lambda x: f"{x} - {next((e.get('email') for e in data if e.get('id') == x), 'N/A')}"
        )
        
        if selected_id:
            selected_enbox = next((e for e in data if e.get("id") == selected_id), None)
            if selected_enbox:
                st.json(selected_enbox)

def create_enbox_form(client):
    """Form to create a new Enbox"""
    st.markdown('<div class="section-header">➕ Create New Enbox</div>', unsafe_allow_html=True)
    
    with st.form("create_enbox_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            email = st.text_input(
                "Email *",
                placeholder="customer@example.com",
                help="Customer's email address"
            )
            display_name = st.text_input(
                "Display Name *",
                placeholder="Customer Name",
                help="Customer's display name"
            )
        
        with col2:
            password = st.text_input(
                "Password *",
                type="password",
                placeholder="Secure password",
                help="Secure password for the Enbox"
            )
            create_via = st.selectbox(
                "Create Via",
                options=["direct", "api", "portal"],
                help="Method of creation"
            )
        
        submitted = st.form_submit_button("Create Enbox", type="primary", use_container_width=True)
        
        if submitted:
            if not email or not password or not display_name:
                st.markdown('<div class="error-box">❌ Please fill in all required fields</div>', unsafe_allow_html=True)
            elif "@" not in email:
                st.markdown('<div class="error-box">❌ Please enter a valid email address</div>', unsafe_allow_html=True)
            else:
                with st.spinner("Creating Enbox..."):
                    result, error = client.create_enbox(email, password, display_name, create_via)
                    
                    if error:
                        st.markdown(f'<div class="error-box">❌ Error creating Enbox: {error}</div>', unsafe_allow_html=True)
                    else:
                        st.markdown('<div class="success-box">✅ Enbox created successfully!</div>', unsafe_allow_html=True)
                        st.json(result)
                        st.session_state.enboxes_data = None  # Clear cache to refresh list
                        st.balloons()

def manage_enbox(client):
    """Manage individual Enbox"""
    st.markdown('<div class="section-header">⚙️ Manage Enbox</div>', unsafe_allow_html=True)
    
    # Get list of enboxes for selection
    data, error = client.get_enboxes()
    
    if error or not data:
        st.warning("No Enboxes available to manage. Create one first!")
        return
    
    selected_id = st.selectbox(
        "Select Enbox to manage",
        options=[enbox.get("id") for enbox in data],
        format_func=lambda x: f"{next((e.get('email') for e in data if e.get('id') == x), 'N/A')} ({x})"
    )
    
    if not selected_id:
        return
    
    tab1, tab2, tab3 = st.tabs(["📄 View Details", "✏️ Update", "🗑️ Delete"])
    
    with tab1:
        if st.button("Fetch Details", type="primary"):
            with st.spinner("Loading details..."):
                result, error = client.get_enbox(selected_id)
                
                if error:
                    st.markdown(f'<div class="error-box">❌ Error: {error}</div>', unsafe_allow_html=True)
                else:
                    st.json(result)
    
    with tab2:
        st.info("Update Enbox information")
        
        with st.form("update_enbox_form"):
            new_display_name = st.text_input("New Display Name", placeholder="Leave empty to keep current")
            new_email = st.text_input("New Email", placeholder="Leave empty to keep current")
            
            update_submitted = st.form_submit_button("Update Enbox", type="primary")
            
            if update_submitted:
                update_data = {}
                if new_display_name:
                    update_data["display_name"] = new_display_name
                if new_email:
                    update_data["email"] = new_email
                
                if update_data:
                    with st.spinner("Updating..."):
                        result, error = client.update_enbox(selected_id, update_data)
                        
                        if error:
                            st.markdown(f'<div class="error-box">❌ Error: {error}</div>', unsafe_allow_html=True)
                        else:
                            st.markdown('<div class="success-box">✅ Enbox updated successfully!</div>', unsafe_allow_html=True)
                            st.json(result)
                            st.session_state.enboxes_data = None
                else:
                    st.warning("Please provide at least one field to update")
    
    with tab3:
        st.warning("⚠️ This action cannot be undone!")
        
        confirm = st.checkbox("I confirm I want to delete this Enbox")
        
        if st.button("Delete Enbox", type="primary", disabled=not confirm):
            with st.spinner("Deleting..."):
                result, error = client.delete_enbox(selected_id)
                
                if error:
                    st.markdown(f'<div class="error-box">❌ Error: {error}</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="success-box">✅ Enbox deleted successfully!</div>', unsafe_allow_html=True)
                    st.session_state.enboxes_data = None
                    st.rerun()

def main():
    """Main application"""
    init_session_state()
    
    # Authentication check
    if not st.session_state.authenticated:
        authenticate()
        return
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 🔑 API Connection")
        st.success("✅ Connected")
        
        if st.button("🔓 Disconnect", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.api_key = None
            st.session_state.enboxes_data = None
            st.rerun()
        
        st.markdown("---")
        st.markdown("### 📚 Navigation")
        page = st.radio(
            "Select Page",
            ["Dashboard", "Create Enbox", "Manage Enbox"],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        st.markdown("### ℹ️ About")
        st.caption("MSP API Manager v1.0")
        st.caption("Manage customer Enboxes programmatically")
    
    # Initialize API client
    client = MSPAPIClient(st.session_state.api_key)
    
    # Main content
    st.markdown('<div class="main-header">📦 MSP API Manager</div>', unsafe_allow_html=True)
    
    if page == "Dashboard":
        display_enboxes_list(client)
    elif page == "Create Enbox":
        create_enbox_form(client)
    elif page == "Manage Enbox":
        manage_enbox(client)

if __name__ == "__main__":
    main()
