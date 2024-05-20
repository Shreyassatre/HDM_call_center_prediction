import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# Function to calculate contactability for a given day
def calculate_contactability(batch_size, attempts):
    contact_rate = 0
    remaining = batch_size
    total_attempts = 0
    contacts_made = 0
    
    # Attempting to contact leads
    for answered_pct, interested_pct, not_interested_pct in attempts:
        answered = int(remaining * answered_pct)
        contacts_made += answered
        contact_rate += answered
        remaining -= answered
        total_attempts += batch_size

    return contact_rate, contacts_made, total_attempts

# Function to generate the call center prediction
@st.cache_data
def generate_prediction(total_leads, num_days, num_callers, avg_calls_per_day, attempts):
    leads_per_day = total_leads // num_days
    total_calls_per_day = num_callers * avg_calls_per_day
    
    results = []
    total_contacted = 0
    total_attempts_made = 0
    
    for day in range(1, num_days + 1):
        # Calculate the current day's batch
        current_batch_size = leads_per_day
        
        # Calculate the contactability for the current day
        contact_rate, contacts_made, attempts_made = calculate_contactability(current_batch_size, attempts[:3])
        
        # Adjust for carryover from previous days
        carryover_contacts = 0
        carryover_attempts = 0
        for i in range(1, min(day, 5)):
            previous_batch_size = leads_per_day
            previous_day_attempts = attempts[3 + i - 1:3 + i + 1] if i < 4 else [attempts[7], attempts[8]]
            additional_contacts, _, additional_attempts = calculate_contactability(previous_batch_size * (1 - 0.5 ** i), previous_day_attempts)
            carryover_contacts += additional_contacts
            carryover_attempts += additional_attempts
        
        total_contact_rate = contact_rate + carryover_contacts
        total_contacted += total_contact_rate
        total_attempts_made += attempts_made + carryover_attempts
        
        results.append({
            "Day": day,
            "Batch Size": current_batch_size,
            "Carryover Contacts": carryover_contacts,
            "Total Contacts": contacts_made + carryover_contacts,
            "Total Contact Rate": total_contact_rate,
            "Total Attempts": attempts_made + carryover_attempts,
            "Cumulative Contacted": total_contacted,
            "Cumulative Attempts": total_attempts_made
        })
    
    return results

# Set up the input fields
st.title("Call Center Contact Prediction")

total_leads = st.number_input("Total Leads", min_value=1, step=1)
num_days = st.number_input("Number of Days", min_value=4, step=1)
num_callers = st.number_input("Number of Callers", min_value=1, step=1)
avg_calls_per_day = st.number_input("Average Calls per Caller per Day", min_value=1, step=1)

# Set up the contactability fields in a table
st.write("Contactability Attempts:")
attempt_data = {
    "Attempt": [f"Attempt {i}" for i in range(1, 10)],
    "Answered %": [25, 15, 10, 12, 10, 10, 8, 6, 5],
    "Interested %": [0.0] * 9,
    "Not Interested %": [0.0] * 9,
}
attempt_df = pd.DataFrame(attempt_data)
edited_df = st.data_editor(attempt_df)

attempts = [
    (edited_df.iloc[i, 1] / 100, edited_df.iloc[i, 2] / 100, edited_df.iloc[i, 3] / 100)
    for i in range(9)
]

# Generate prediction when all inputs are provided
if total_leads and num_days and num_callers and avg_calls_per_day:
    results = generate_prediction(total_leads, num_days, num_callers, avg_calls_per_day, attempts)
    result_df = pd.DataFrame(results)
    
    st.write("Prediction Results:")
    st.write(result_df)
    
    # Plotting results
    fig2 = px.line(result_df, x="Day", y="Carryover Contacts", title="Carryover Contacts per Day")
    fig3 = px.line(result_df, x="Day", y="Total Contacts", title="Total Contacts per Day")
    fig4 = px.line(result_df, x="Day", y="Cumulative Contacted", title="Cumulative Contacts Made")
    fig5 = px.line(result_df, x="Day", y="Total Attempts", title="Total Attempts Made per Day")
    fig6 = px.line(result_df, x="Day", y="Cumulative Attempts", title="Cumulative Attempts Made")
    
    st.plotly_chart(fig2)
    st.plotly_chart(fig3)
    st.plotly_chart(fig4)
    st.plotly_chart(fig5)
    st.plotly_chart(fig6)
else:
    st.write("Please fill in all input fields to generate the prediction.")
