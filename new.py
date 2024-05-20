import streamlit as st
import pandas as pd

# Set up the input fields
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
edited_df = st.experimental_data_editor(attempt_df)

attempts = [(edited_df.iloc[i, 1] / 100, edited_df.iloc[i, 2] / 100, edited_df.iloc[i, 3] / 100) for i in range(9)]

# Calculate leads per day
leads_per_day = total_leads // num_days

# Initialize data structures to hold the results
daily_stats = []
remaining_leads = [leads_per_day] * num_days

# Initialize cumulative totals
total_contacted = 0
total_attempts_made = 0

# Calculate contactability for each day
for day in range(num_days):
    current_batch_size = remaining_leads[day]
    contacts_made = 0
    attempts_made = 0
    
    # Process new batch of leads
    for i in range(3):
        contacts_made += current_batch_size * attempts[i][0]
        attempts_made += current_batch_size
        current_batch_size -= current_batch_size * attempts[i][0]
    
    carryover_contacts = 0
    carryover_attempts = 0
    
    # Process remaining leads from previous days
    if day > 0:
        for prev_day in range(day):
            if prev_day + 4 < day:
                continue
            attempt_index = 3 + (day - prev_day - 1)
            remaining_day_leads = remaining_leads[prev_day]
            carryover_contacts += remaining_day_leads * attempts[attempt_index][0]
            carryover_attempts += remaining_day_leads
            remaining_leads[prev_day] -= remaining_day_leads * attempts[attempt_index][0]
    
    # Calculate totals
    total_contacts = contacts_made + carryover_contacts
    total_contact_rate = (total_contacts / leads_per_day) * 100
    total_attempts = attempts_made + carryover_attempts
    total_contacted += total_contacts
    total_attempts_made += total_attempts
    
    # Store the day's statistics
    daily_stats.append({
        "Day": day + 1,
        "Batch Size": int(leads_per_day),
        "Contacts Made": int(contacts_made),
        "Carryover Contacts": int(carryover_contacts),
        "Total Contacts": int(total_contacts),
        "Total Contact Rate (%)": round(total_contact_rate, 2),
        "Total Attempts": int(total_attempts),
        "Cumulative Contacted": int(total_contacted),
        "Cumulative Attempts": int(total_attempts_made)
    })
    
    # Update remaining leads for the current day
    remaining_leads[day] -= contacts_made

# Convert daily statistics to a DataFrame for display
daily_stats_df = pd.DataFrame(daily_stats)

# Display results
st.write("Daily Contactability Rates:")
st.write(daily_stats_df)

# Calculate and display total contactability
total_contactability = sum([day["Total Contacts"] for day in daily_stats])
st.write(f"Total Contactability over {num_days} days: {int(total_contactability)}")
