import random
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
import streamlit as st

# ===== 2. PAGE CONFIG =====
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

# Updated background and text styling
# Updated background CSS for the app
# Updated background CSS for the app
page_bg_style = """
<style>
/* Background Image */
.stApp {
    background-image: url("https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fwallpaperaccess.com%2Ffull%2F1439676.jpg&f=1&nofb=1&ipt=a38fd89a1c75846a83039cf38969594b8670aa7f4861e506d59fbecb326892a0&ipo=images");
    background-size: cover;
    background-repeat: no-repeat;
    background-attachment: fixed;
    background-position: center;
}

/* Text Color and Font */
h1, h2, h3, h4, h5, h6, p, div, label {
    color: #FF4500; /* Deep Bright Orange */
    font-family: 'Arial', sans-serif;
}

/* Make "Member Name" & "Phone Number" labels bigger */
label {
    font-size: 24px !important; /* Increased size */
    font-weight: bold;
}

/* Increase font size for radio button labels */
div[data-baseweb="radio"] {
    font-size: 22px !important;
    font-weight: bold;
}

/* Increase font size for radio button options (None, View All Members, etc.) */
.stRadio label {
    font-size: 20px !important;
    font-weight: bold;
}

/* Table Styling */
table {
    width: 100%;
    border-collapse: collapse;
    background: rgba(0, 0, 0, 0.7); /* Black Transparent Background */
    color: #FF4500; /* Deep Bright Orange Font */
    border-radius: 10px;
}

th, td {
    border: 1px solid #FF4500;
    padding: 10px;
    text-align: center;
}

th {
    background-color: black;
    font-weight: bold;
    color: #FF4500; /* Deep Bright Orange Headers */
    font-size: 18px;
}

td {
    font-size: 16px;
}
</style>
"""

# Inject the CSS into the app
st.markdown(page_bg_style, unsafe_allow_html=True)



class GymModel:
    def __init__(self):
        self.sheet = self.google_sheet()

    def code_and_date(self):
        unique_code = random.randint(1000, 9999)
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
            st.stop()

    def update_google_sheet(self, member_name, join_date, phone_no, code):
        new_row = [member_name, join_date, phone_no, code]
        self.sheet.append_row(new_row)

    def view_member_details(self, search_value):
        rows = self.sheet.get_all_values()
        for row in rows[1:]:
            if row[2] == search_value or row[3] == search_value:
                return {"Member Name": row[0], "Join Date": row[1], "Phone Number": row[2], "Code": row[3]}
        return None

    def get_all_members(self):
        rows = self.sheet.get_all_values()
        return rows[1:]

    def get_total_member_count(self):
        rows = self.sheet.get_all_values()
        return len(rows) - 1

    def web_interface(self):
        st.header('SAI FITNESS')

        total_members = self.get_total_member_count()
        st.markdown(f"##### Total Members: {total_members}")

        with st.form("data_entry_form", clear_on_submit=True):
            st.subheader("Add New Member")
            member_name = st.text_input("**Member Name**")
            phone_no = st.text_input("**Phone Number**")
            
            submitted = st.form_submit_button("**Submit**")
            
            if submitted:
                if member_name and phone_no:
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

        st.subheader("Dashboard")
        view_option = st.radio(
            "**Choose an option**",
            ("None", "View All Members", "Search Member Details")
        )

        if view_option == "View All Members":
            st.subheader("**All Members List**")
            rows = self.get_all_members()
            if rows:
                table_html = f"""
                <style>
                table {{
                    width: 100%;
                    border-collapse: collapse;
                }}
                th, td {{
                    border: 1px solid #FF4500;
                    padding: 8px;
                    text-align: left;
                    color: #FF4500;
                }}
                th {{
                    background-color: #333333;
                    color: white;
                    font-weight: bold;
                }}
                td {{
                    font-weight: normal;
                }}
                </style>
                <table>
                    <thead>
                        <tr>
                            {"".join(f"<th>{header}</th>" for header in ["Member Name", "Join Date", "Phone Number", "Code"])}
                        </tr>
                    </thead>
                    <tbody>
                        {"".join(f"<tr>{''.join(f'<td>{cell}</td>' for cell in row)}</tr>" for row in rows)}
                    </tbody>
                </table>
                """
                st.markdown(table_html, unsafe_allow_html=True)
            else:
                st.info("No members found.")

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

if __name__ == "__main__":
    gym_model = GymModel()
    gym_model.web_interface()
