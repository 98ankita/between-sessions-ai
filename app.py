import streamlit as st
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI
import os

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Session-only storage.
# Each browser session gets its own check-ins.
# Friends using the deployed app will not see each other's entries.
if "checkins" not in st.session_state:
    st.session_state["checkins"] = []

if "followup_counter" not in st.session_state:
    st.session_state["followup_counter"] = 0

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
Now they are responding to one of the follow-up questions.

Original journal entry:
{original_journal}

Previous AI reflection:
{ai_reflection}

User's follow-up response:
{user_followup}

Write a closing follow-up response.

Return:
1. A deeper reflection, 2-3 sentences.
2. One small grounding or coping step the user can try today.
3. One thing the user could consider discussing with their therapist or a trusted support person.

Important:
- Do not ask another follow-up question.
- Do not continue the conversation indefinitely.
- Keep the tone warm, grounded, and practical.
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
        "This is a learning project exploring agentic AI patterns in a mental wellness context. "
        "It is not therapy, diagnosis, medical advice, or crisis support. "
        "Entries are stored only for your current browser session."
    )

    st.divider()

    st.header("Daily Check-in")

    patient_name = st.text_input(
        "Patient name",
        value="Demo Patient",
        help="For this learning project, names are used as demo identifiers. A real product would use unique patient IDs."
    )

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
            clean_patient_name = patient_name.strip() if patient_name.strip() else "Demo Patient"

            with st.spinner("Reflecting..."):
                ai_reflection = get_ai_reflection(mood, emotions, journal)

            new_entry = {
                "timestamp": datetime.now().isoformat(),
                "patient_name": clean_patient_name,
                "mood": mood,
                "emotions": ", ".join(emotions) if emotions else "No emotions selected",
                "journal": journal,
                "ai_reflection": ai_reflection
            }

            st.session_state["checkins"].append(new_entry)

            st.session_state["latest_journal"] = journal
            st.session_state["latest_ai_reflection"] = ai_reflection

            if "latest_deeper_reflection" in st.session_state:
                del st.session_state["latest_deeper_reflection"]

            st.session_state["followup_counter"] += 1

            st.success("Check-in saved for this session.")

            st.markdown("### Your check-in")
            st.write("**Patient name:**", clean_patient_name)
            st.write("**Mood:**", mood)
            st.write("**Emotions:**", ", ".join(emotions) if emotions else "No emotions selected")
            st.write("**Journal:**", journal)

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

        st.caption(
            "You can respond once to the reflection above. The app will give a closing reflection, "
            "a small next step, and something you may want to bring into a future therapy or support conversation."
        )

        followup_key = f"followup_text_{st.session_state['followup_counter']}"

        followup = st.text_area(
            "Want to respond to one of the follow-up questions?",
            height=120,
            key=followup_key
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

                st.session_state["latest_deeper_reflection"] = deeper_reflection
                st.session_state["followup_counter"] += 1
                st.rerun()

        if "latest_deeper_reflection" in st.session_state:
            st.markdown("### Closing Reflection")
            st.write(st.session_state["latest_deeper_reflection"])

    st.divider()

    st.header("Mood History")

    if len(st.session_state["checkins"]) > 0:
        saved_entries = pd.DataFrame(st.session_state["checkins"])
        saved_entries["timestamp"] = pd.to_datetime(saved_entries["timestamp"])
        saved_entries = saved_entries.sort_values("timestamp")

        patient_options = saved_entries["patient_name"].dropna().unique()

        selected_history_patient = st.selectbox(
            "View mood history for",
            patient_options
        )

        history_entries = saved_entries[
            saved_entries["patient_name"] == selected_history_patient
        ]

        st.line_chart(
            history_entries,
            x="timestamp",
            y="mood"
        )

        st.header("Past Check-ins for Selected Patient")
        st.dataframe(history_entries)
    else:
        st.info("No check-ins saved in this session yet.")

    if len(st.session_state["checkins"]) > 0:
        if st.button("Clear my session data"):
            st.session_state["checkins"] = []

            for key in [
                "latest_journal",
                "latest_ai_reflection",
                "latest_deeper_reflection"
            ]:
                if key in st.session_state:
                    del st.session_state[key]

            st.session_state["followup_counter"] += 1
            st.rerun()


elif page == "Therapist Dashboard":
    st.subheader("Therapist Dashboard")

    st.caption(
        "This dashboard is part of a learning project exploring how AI could summarize patient-entered check-ins. "
        "AI summaries are for demonstration only and should not replace clinical judgment. "
        "This dashboard only shows entries from the current browser session."
    )

    st.divider()

    if len(st.session_state["checkins"]) == 0:
        st.info("No patient check-ins available in this session yet.")
    else:
        saved_entries = pd.DataFrame(st.session_state["checkins"])
        saved_entries["timestamp"] = pd.to_datetime(saved_entries["timestamp"])
        saved_entries = saved_entries.sort_values("timestamp")

        st.header("Patients")

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