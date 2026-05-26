import streamlit as st
import pandas as pd
from datetime import datetime
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

file_path = "data/checkins.csv"

page = st.sidebar.radio(
    "Choose view",
    ["Patient Check-in", "Therapist Dashboard"]
)


def get_ai_reflection(mood, emotions, journal):
    prompt = f"""
You are an AI emotional reflection companion.

You are not a therapist, doctor, or crisis counselor.
Do not diagnose. Do not give medical advice.
Help the user reflect gently.

First classify the user's risk level as one of:
- low: normal stress, sadness, anxiety, overwhelm, loneliness, frustration
- medium: intense distress, hopelessness, feeling trapped, vague safety concerns
- high: self-harm intent, suicide intent, immediate danger, abuse emergency

Then write a response.

Return your answer in this exact format:

Risk level: low/medium/high

Reflection:
[2-3 sentence gentle reflection]

Follow-up questions:
1. [question]
2. [question]

Coping suggestions:
1. [suggestion]
2. [suggestion]

User mood score: {mood}/10
User emotions: {emotions}
User journal entry: {journal}
"""

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )

    return response.output_text


def get_followup_reflection(original_journal, ai_reflection, user_followup):
    prompt = f"""
You are an AI emotional reflection companion.

You are not a therapist, doctor, or crisis counselor.
Do not diagnose. Do not give medical advice.

The user already completed a check-in and received an AI reflection.
Now they are responding to the follow-up question.

Original journal entry:
{original_journal}

Previous AI reflection:
{ai_reflection}

User's follow-up response:
{user_followup}

Write:
1. A deeper reflection, 2-3 sentences.
2. One gentle next question.
3. One small next step.
"""

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )

    return response.output_text


def get_therapist_summary(entries_text):
    prompt = f"""
You are helping create a concise therapist-facing summary.

Do not diagnose.
Do not make clinical claims.
Summarize only what the patient has written and what patterns are visible.

Write:
1. Main emotional themes
2. Repeated stressors or triggers
3. Mood pattern
4. Potential discussion points for the next session
5. Any risk-related notes based only on entries

Patient entries:
{entries_text}
"""

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )

    return response.output_text


st.title("Between Sessions")

if page == "Patient Check-in":
    st.subheader("Agentic AI Mental Wellness Learning Project")

    st.caption(
    "This dashboard is part of a learning project exploring how AI could summarize patient-entered check-ins. "
    "AI summaries are for demonstration only and should not replace clinical judgment."
)

    st.divider()

    st.header("Daily Check-in")

    mood = st.slider(
        "How is your mood today?",
        min_value=1,
        max_value=10,
        value=5
    )

    emotions = st.multiselect(
        "What emotions are present?",
        [
            "Anxious",
            "Sad",
            "Angry",
            "Numb",
            "Overwhelmed",
            "Tired",
            "Lonely",
            "Calm",
            "Hopeful",
            "Happy",
            "Joyful",
            "Grateful",
            "Excited",
            "Proud",
            "Relieved",
            "Content"
        ]
    )

    journal = st.text_area(
        "What is on your mind?",
        height=180
    )

    if st.button("Reflect"):
        if journal.strip() == "":
            st.warning("Please write a few lines before reflecting.")
        else:
            with st.spinner("Reflecting..."):
                ai_reflection = get_ai_reflection(mood, emotions, journal)

            os.makedirs("data", exist_ok=True)

            new_entry = pd.DataFrame([{
                "timestamp": datetime.now().isoformat(),
                "patient_name": "Demo Patient",
                "mood": mood,
                "emotions": ", ".join(emotions) if emotions else "No emotions selected",
                "journal": journal,
                "ai_reflection": ai_reflection
            }])

            if os.path.exists(file_path):
                old_entries = pd.read_csv(file_path)
                all_entries = pd.concat([old_entries, new_entry], ignore_index=True)
            else:
                all_entries = new_entry

            all_entries.to_csv(file_path, index=False)

            st.success("Check-in saved.")

            st.markdown("### Your check-in")
            st.write("**Mood:**", mood)
            st.write("**Emotions:**", ", ".join(emotions) if emotions else "No emotions selected")
            st.write("**Journal:**", journal)

            st.session_state["latest_journal"] = journal
            st.session_state["latest_ai_reflection"] = ai_reflection

            if "Risk level: high" in ai_reflection or "risk level: high" in ai_reflection:
                st.error(
                    "This sounds serious. I’m not equipped to support emergencies. "
                    "If you might hurt yourself or feel unsafe, please contact emergency services now. "
                    "If you are in the U.S. or Canada, call or text 988 for crisis support."
                )
            else:
                st.markdown("### AI Reflection")
                st.write(ai_reflection)

    if "latest_ai_reflection" in st.session_state:
        st.divider()

        st.header("Continue the Reflection")

        followup = st.text_area(
            "Want to respond to one of the follow-up questions?",
            height=120
        )

        if st.button("Continue Reflection"):
            if followup.strip() == "":
                st.warning("Write a response before continuing.")
            else:
                with st.spinner("Thinking..."):
                    deeper_reflection = get_followup_reflection(
                        st.session_state["latest_journal"],
                        st.session_state["latest_ai_reflection"],
                        followup
                    )

                st.markdown("### Deeper Reflection")
                st.write(deeper_reflection)

    st.divider()

    st.header("Mood History")

    if os.path.exists(file_path):
        saved_entries = pd.read_csv(file_path)

        saved_entries["timestamp"] = pd.to_datetime(saved_entries["timestamp"])
        saved_entries = saved_entries.sort_values("timestamp")

        st.line_chart(
            saved_entries,
            x="timestamp",
            y="mood"
        )

        st.header("Past Check-ins")
        st.dataframe(saved_entries)
    else:
        st.info("No check-ins saved yet.")


elif page == "Therapist Dashboard":
    st.subheader("Therapist Dashboard")

    st.caption(
        "This view is designed to help a clinician review patient-entered check-ins. "
        "AI summaries are for review support only and should not replace clinical judgment."
    )

    st.divider()

    if not os.path.exists(file_path):
        st.info("No patient check-ins available yet.")
    else:
        saved_entries = pd.read_csv(file_path)
        saved_entries["timestamp"] = pd.to_datetime(saved_entries["timestamp"])
        saved_entries = saved_entries.sort_values("timestamp")

        st.header("Patients")

        if "patient_name" not in saved_entries.columns:
            saved_entries["patient_name"] = "Demo Patient"

        patient_list = saved_entries["patient_name"].dropna().unique()

        selected_patient = st.selectbox(
            "Select a patient",
            patient_list
        )

        patient_entries = saved_entries[
            saved_entries["patient_name"] == selected_patient
        ]

        st.markdown(f"### Overview for {selected_patient}")

        latest_mood = patient_entries["mood"].iloc[-1]
        average_mood = round(patient_entries["mood"].mean(), 1)
        total_checkins = len(patient_entries)

        col1, col2, col3 = st.columns(3)
        col1.metric("Latest mood", latest_mood)
        col2.metric("Average mood", average_mood)
        col3.metric("Total check-ins", total_checkins)

        st.markdown("### Mood Trend")
        st.line_chart(
            patient_entries,
            x="timestamp",
            y="mood"
        )

        st.markdown("### Recent Check-ins")
        st.dataframe(
            patient_entries[
                ["timestamp", "mood", "emotions", "journal", "ai_reflection"]
            ].tail(5)
        )

        st.markdown("### AI Summary for Therapist")

        if st.button("Generate Therapist Summary"):
            entries_text = patient_entries[
                ["timestamp", "mood", "emotions", "journal", "ai_reflection"]
            ].tail(10).to_string(index=False)

            with st.spinner("Generating summary..."):
                therapist_summary = get_therapist_summary(entries_text)

            st.write(therapist_summary)