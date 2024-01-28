import datetime
from datetime import datetime
import pandas as pd
import streamlit as st

from donation_system import ShelterDonationSystem

def donation_system():
    if "shelter_donation_system" not in st.session_state:
        st.session_state["shelter_donation_system"] = ShelterDonationSystem()
    return st.session_state["shelter_donation_system"]


if __name__ == "__main__":
    # Streamlit App Layout
    st.title("Donation Management System")
    col1, col2 = st.columns(2)

    # Donation Registration in the first column
    with col1:
        st.header("Register Donation")
        
        with st.form("Donation Form", ):
            donor_name = st.text_input("Donor's Name")

            # Show perishable checkbox and expiration date input only for 'Food'
            placeholder_donation_type = st.empty()
            placeholder_perishable = st.empty()
            placeholder_expiration_date = st.empty()
            placeholder_amount = st.empty()

            date = st.date_input("Date of Donation", datetime.now())
            submit_donation = st.form_submit_button("Register Donation")

    is_perishable = False
    amount = 0
    with placeholder_donation_type:
        donation_type = st.selectbox("Type of Donation", ['Money', 'Food'])
    with placeholder_perishable:
        if donation_type == 'Food':
            is_perishable = st.checkbox("Is this a perishable item?")
    with placeholder_expiration_date:
        if is_perishable:
            expiration_date = st.date_input("Expiration Date", datetime.now())
    with placeholder_amount:
        if donation_type == 'Money':
            amount = st.number_input("Amount (Dollars)", step=1.0)
        else:
            amount = st.number_input("Quantity (lbs)", step=1.0)

    if submit_donation:
        donor_name = donor_name.strip()
        donor_name = donor_name if donor_name else "Anonymous"
        if amount <= 0:
            st.error("Please enter a positive donation amount.")
        else:
            donation_system().register_donation(donor_name, donation_type, amount, date, expiration_date if is_perishable else datetime.max.date())
            st.success("Donation registered successfully.")

    # Donation Distribution in the second column
    with col2:
        st.header("Record a Distribution")
        
        with st.form("Distribution Form"):
            placeholder_donation_type = st.empty()
            placeholder_dist_amount = st.empty()
            dist_date = st.date_input("Date of Distribution", datetime.now(), key='dist_date')
            submit_distribution = st.form_submit_button("Record Distribution")
            
    with placeholder_donation_type:
        dist_type = st.selectbox("Type of Distribution", ['Money', 'Food'],)

    with placeholder_dist_amount:
        if dist_type == 'Money':
            dist_amount = st.number_input("Amount Distributed (Dollars)", step=1.0)
        else:
            dist_amount = st.number_input("Quantity Distributed (lbs)", step=1.0)

    if submit_distribution:
        if dist_amount <= 0:
            st.error("Please enter a positive distribution amount.")
        else:
            error = donation_system().distribute_donation(dist_type, dist_amount, dist_date)
            if error: 
                st.error(error)
            else:
                st.success("Distribution recorded successfully.")

    st.header("Generate Reports")
    if st.button("Generate Inventory Report"):
        inventory_report, chart_data = donation_system().generate_inventory_report()
        _ = [st.write(f"{key}: {value}") for key, value in inventory_report.items()]
        
        if chart_data:
            dates = list(chart_data.keys())
            amounts = list(chart_data.values())
            data = pd.DataFrame({'Date': dates, 'Amount(lbs)': amounts})
            data['Date'] = pd.to_datetime(data['Date'])
            st.line_chart(data.set_index('Date'))

    if st.button("Generate Donator Report"):
        donator_report = donation_system().generate_donator_report()
        st.table(donator_report)