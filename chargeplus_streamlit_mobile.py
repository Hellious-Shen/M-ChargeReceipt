# Regenerate the mobile-friendly Streamlit app file after kernel reset

mobile_friendly_app = """
import streamlit as st
import fitz  # PyMuPDF
import pandas as pd
import re
from datetime import datetime
from io import BytesIO

# 🔐 Login using st.secrets
def login():
    st.title("🔒 Charge+ Receipt App Login")

    if "login_attempted" not in st.session_state:
        st.session_state["login_attempted"] = False

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username in st.secrets["users"] and st.secrets["users"][username] == password:
            st.session_state["authenticated"] = True
        else:
            st.session_state["login_attempted"] = True

    if st.session_state["login_attempted"] and not st.session_state.get("authenticated", False):
        st.error("❌ Invalid username or password")


# 🚪 Session check
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    login()
    st.stop()


# -------------------------------
# Mobile-Optimized App UI
# -------------------------------

st.title("📱 Charge+ Receipt Extractor")
st.markdown("Upload your Charge+ PDF receipts below. The app works great on both desktop and mobile.")

with st.container():
    uploaded_files = st.file_uploader("📤 Upload Charge+ PDF receipts", type=["pdf"], accept_multiple_files=True)

if uploaded_files:
    records = []

    with st.spinner("🔍 Processing receipts..."):
        for file in uploaded_files:
            doc = fitz.open(stream=file.read(), filetype="pdf")
            text = "".join([page.get_text() for page in doc])

            data = {}
            try:
                date_match = re.search(r"Date:\\s*(\\d{1,2} \\w+ \\d{4})", text)
                data['Date'] = date_match.group(1)
                data['Parsed Date'] = datetime.strptime(data['Date'], "%d %b %Y")
            except:
                data['Date'] = "N/A"
                data['Parsed Date'] = None

            try:
                location_match = re.search(r"Charging Station\\s*(.+)", text)
                data['Location'] = location_match.group(1).strip()
            except:
                data['Location'] = "N/A"

            try:
                kwh_match = re.search(r"Energy Consumption\\s*([\\d.]+)\\s*kWh", text)
                data['Energy (kWh)'] = float(kwh_match.group(1))
            except:
                data['Energy (kWh)'] = None

            try:
                cost_match = re.search(r"Charge\\+ Credit used.*?S\\$ ([\\d.]+)", text, re.DOTALL)
                data['Cost (SGD)'] = float(cost_match.group(1))
            except:
                data['Cost (SGD)'] = None

            data['Filename'] = file.name
            records.append(data)

    df = pd.DataFrame(records)

    if 'Parsed Date' in df.columns:
        df['Month'] = df['Parsed Date'].dt.to_period('M')
        summary = df.groupby('Month')[['Energy (kWh)', 'Cost (SGD)']].sum().reset_index()
    else:
        summary = pd.DataFrame()

    st.subheader("📋 Extracted Charging Log")
    st.dataframe(df, use_container_width=True, height=300)

    st.subheader("📊 Monthly Summary")
    st.dataframe(summary, use_container_width=True, height=200)

    def to_excel_bytes(df):
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
        output.seek(0)
        return output

    st.download_button("⬇️ Download Full Log (Excel)", data=to_excel_bytes(df),
                       file_name="ChargePlus_Charging_Log.xlsx", use_container_width=True)

    st.download_button("⬇️ Download Monthly Summary (Excel)", data=to_excel_bytes(summary),
                       file_name="ChargePlus_Monthly_Summary.xlsx", use_container_width=True)
"""

# Save to file
mobile_friendly_app_path = "/mnt/data/chargeplus_streamlit_mobile.py"
with open(mobile_friendly_app_path, "w") as f:
    f.write(mobile_friendly_app)

mobile_friendly_app_path
