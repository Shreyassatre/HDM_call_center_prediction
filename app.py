import streamlit as st
import pandas as pd

# Set up the input fields
total_leads = st.number_input("Total Leads", min_value=1, step=1)
num_days = st.number_input("Number of Days", min_value=4, step=1)
num_callers = st.number_input("Number of Callers", min_value=1, step=1)
avg_calls_per_day = st.number_input("Average Calls per Caller per Day", min_value=1, step=1)

# Set up the contactability fields in a table
attempts = []
st.write("Contactability Attempts:")
attempt_data = {
    "Attempt": [f"Attempt {i}" for i in range(1, 10)],
    "Answered %": [0.0] * 9,
    "Interested %": [0.0] * 9,
    "Not Interested %": [0.0] * 9,
}
attempt_df = pd.DataFrame(attempt_data)
edited_df = st.data_editor(attempt_df)

for i in range(9):
    attempts.append(
        (
            edited_df.iloc[i, 1] / 100,
            edited_df.iloc[i, 2] / 100,
            edited_df.iloc[i, 3] / 100,
        )
    )

answered_leads =0
lead_batch_size = total_leads // (num_days - 3)
remaining_leads = lead_batch_size-answered_leads
# Calculate the cohort report


for day in range(num_days):
    daily_calls = num_callers * avg_calls_per_day
    if day <= 1:
        attempt_range = 3
    elif day <= 3:
        attempt_range = 2
    else:
        attempt_range = 1

    
    interested_leads = int(answered_leads * sum(attempt[1] for attempt in attempts[:attempt_range]))
    not_interested_leads = answered_leads - interested_leads
    remaining_leads -= answered_leads

    remaining_leads += lead_batch_size

    cohort_report.iloc[day, 0] = remaining_leads
    for i in range(day, num_days):
        cohort_report.iloc[i, day] = answered_leads

# Display the cohort report
st.write("Cohort Report:")
st.dataframe(cohort_report)