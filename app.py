
# 1. IMPORTS (NO Streamlit usage here)
import random
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
import streamlit as st

# ===== 2. PAGE CONFIG (FIRST Streamlit command) =====
st.set_page_config(
    page_title="SAI FITNESS - Member Management",
    layout="wide",
    initial_sidebar_state="auto",
    menu_items={
        'Report a bug': None,
        'Get help': None,
        'About': None
    }
)

# ===== 3. SECURITY MEASURES =====
hide_github_icon = """
<style>
#MainMenu {visibility: hidden;}
header {visibility: hidden;}
footer {visibility: hidden;}
.stDeployButton {display:none;}
.css-1rs6os.edgvbvh3 {display:none;}
.css-1lsmgbg.egzxvld0 {display:none;}
</style>
"""
st.markdown(hide_github_icon, unsafe_allow_html=True)

# Updated background CSS for the app
page_bg_style = """
<style>
/* Background with your original image */
.stApp {
    background: 
        linear-gradient(rgba(0, 0, 0, 0.6), 
        url("https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fwallpaperaccess.com%2Ffull%2F1439676.jpg&f=1&nofb=1&ipt=a38fd89a1c75846a83039cf38969594b8670aa7f4861e506d59fbecb326892a0&ipo=images");
    background-size: cover;
    background-repeat: no-repeat;
    background-attachment: fixed;
    background-position: center;
}

/* Gold Text EVERYWHERE */
h1, h2, h3, h4, h5, h6, p, div, label, 
.stTextInput>div>div>input, .stRadio>div,
.stButton>button, .stAlert {
    color: #FFD700 !important;  /* Pure gold */
    font-family: 'Arial', sans-serif !important;
    font-weight: 600 !important;
    text-shadow: 1px 1px 3px #000000;
}

/* Main Header */
h1 {
    font-size: 2.5rem !important;
    font-weight: 800 !important;
    text-align: center;
    text-shadow: 2px 2px 5px #000000;
}

/* View All Members Table */
.gold-table {
    width: 98% !important;
    margin: 0 auto !important;
    background-color: rgba(0,0,0,0.7) !important;
    backdrop-filter: blur(3px);
    border-radius: 8px;
    overflow: auto;
}

.gold-table table {
    width: 100% !important;
}

.gold-table th {
    background-color: rgba(40,40,40,0.9) !important;
    color: #FFD700 !important;
    font-size: 15px !important;
    padding: 10px 8px !important;
    position: sticky;
    top: 0;
}

.gold-table td {
    color: #FFD700 !important;
    font-size: 14px !important;
    padding: 8px 6px !important;
    border-bottom: 1px solid rgba(255,215,0,0.2) !important;
}

/* Mobile Responsiveness */
@media screen and (max-width: 768px) {
    .gold-table {
        width: 100% !important;
        font-size: 90% !important;
    }
    .gold-table th {
        font-size: 14px !important;
        padding: 8px 5px !important;
    }
    .gold-table td {
        font-size: 13px !important;
        padding: 6px 4px !important;
    }
}
</style>
"""



# Inject the CSS into the app
st.markdown(page_bg_style, unsafe_allow_html=True)

class GymModel:
    def __init__(self):
        self.sheet = self.google_sheet()

    def code_and_date(self):
        # Generate a unique code
        unique_code = random.randint(1000, 9999)
        # Get the current date
        current_date = datetime.now().strftime("%Y-%m-%d")
        return unique_code, current_date

    def google_sheet(self):
        try:
            scopes = ["https://www.googleapis.com/auth/spreadsheets"]
            creds = Credentials.from_service_account_info(st.secrets["gcp_creds"], scopes=scopes)
            client = gspread.authorize(creds)
            sheet_id = "1dJ9Cqlqr8SiR4fovXpWtYh7tWPA8-gsx648Yr-uhb1c"
            return client.open_by_key(sheet_id).worksheet("Sheet1")
        except Exception as e:
            st.error(f"🔴 Error accessing Google Sheets: {str(e)}")
            st.stop()  # Prevent the app from continuing with errors

    def update_google_sheet(self, member_name, join_date, phone_no, code):
        # Append new data as a row in the sheet
        new_row = [member_name, join_date, phone_no, code]
        self.sheet.append_row(new_row)

    def view_member_details(self, search_value):
        # Get all rows from the sheet
        rows = self.sheet.get_all_values()

        # Search for a member by phone number or unique code
        for row in rows[1:]:  # Skip the header row
            if row[2] == search_value:  # Check phone number
                return {"Member Name": row[0], "Join Date": row[1], "Phone Number": row[2], "Code": row[3]}
            elif row[3] == search_value:  # Check unique code
                return {"Member Name": row[0], "Join Date": row[1], "Phone Number": row[2], "Code": row[3]}

        # If not found
        return None

    def get_all_members(self):
        # Get all rows and return the data excluding the header
        rows = self.sheet.get_all_values()
        return rows[1:]  # Exclude the header row

    def get_total_member_count(self):
        # Get total number of members (excluding header row)
        rows = self.sheet.get_all_values()
        return len(rows) - 1  # Subtract 1 for the header row

    def web_interface(self):
        st.markdown("<h1 style='text-align: center;'>SAI FITNESS</h1>", unsafe_allow_html=True)

        # Display total member count at the top
        total_members = self.get_total_member_count()
        st.markdown(f"##### Total Members: {total_members}")

                # Initialize session state for member_name and phone_no if they are not already set
        # Streamlit form for adding new members
        # Streamlit form for adding new members
        # Streamlit form for adding new members
        with st.form("data_entry_form", clear_on_submit=True):
            st.subheader("Add New Member")
            member_name = st.text_input("**Member Name**")
            phone_no = st.text_input("**Phone Number**")
            
            submitted = st.form_submit_button("**Submit**")
            
            if submitted:
                if member_name and phone_no:
                    # Get existing data with error handling
                    try:
                        existing_data = self.sheet.get_all_values()
                        existing_phones = [row[2] for row in existing_data[1:]] if len(existing_data) > 1 else []
                        
                        if not phone_no.isdigit() or len(phone_no) != 10:
                            st.error("📵 Phone number must be 10 digits!")
                        elif phone_no in existing_phones:
                            st.error("⛔ This number is already registered!")
                        else:
                            code, join_date = self.code_and_date()
                            self.update_google_sheet(member_name, join_date, phone_no, code)
                            st.success("✅ Member added successfully!")
                    except Exception as e:
                        st.error(f"⚠️ System error: {str(e)}")
                else:
                    st.warning("🔸 Please fill all fields!")





        # Options for viewing or searching members
        st.subheader("Dashboard")
        view_option = st.radio(
            "**Choose an option**",
            ("None", "View All Members", "Search Member Details")
        )

        # Option: View All Members
        if view_option == "View All Members":
            st.subheader("**All Members List**")
            rows = self.get_all_members()
            if rows:
                # Convert rows to HTML with custom styling
                table_html = f"""
                <div class="mobile-table">
                <table>
                    <thead>
                        <tr>
                            {"".join(f"<th>{header}</th>" for header in ["Name", "Join Date", "Phone", "Code"])}
                        </tr>
                    </thead>
                    <tbody>
                        {"".join(f"<tr>{''.join(f'<td>{cell}</td>' for cell in row)}</tr>" for row in rows)}
                    </tbody>
                </table>
                </div>
                """

                st.markdown(table_html, unsafe_allow_html=True)
            else:
                st.info("No members found.")
                    
        # Option: Search Member Details
        elif view_option == "Search Member Details":
            st.subheader("Search Member Details")
            search_value = st.text_input("Enter Phone Number or Unique Code")
            search_button = st.button("Search")

            if search_button:
                result = self.view_member_details(search_value)
                if result:
                    st.write("### Member Details:")
                    for key, value in result.items():
                        st.write(f"**{key}**: {value}")
                else:
                    st.error("**No member found with the given details.**")

# Main entry point
if __name__ == "__main__":
    gym_model = GymModel()
    gym_model.web_interface()
