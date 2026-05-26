# Between Sessions

Between Sessions is a learning project exploring agentic AI patterns in a mental wellness context. It is not therapy, diagnosis, medical advice, or crisis support.

## Project Overview

This project is a Streamlit-based AI application that allows a user to complete emotional check-ins, receive AI-generated reflections, continue a follow-up reflection, and view mood history over time.

It also includes a therapist-facing dashboard that summarizes patient-entered check-ins for demonstration purposes.

## Why I Built This

I built this project to learn the basics of agentic AI through a practical, product-oriented use case.

The goal was to understand how AI applications can go beyond a simple chatbot by adding:

- user input
- memory
- risk-aware routing
- follow-up context
- dashboarding
- summarization workflows

## Features

### Patient Check-in

- Mood score input
- Emotion selection
- Journal entry
- AI-generated emotional reflection
- Risk classification: low, medium, or high
- High-risk safety routing
- Follow-up reflection flow
- Mood history chart
- Past check-ins table

### Therapist Dashboard

- Patient selection
- Latest mood
- Average mood
- Total check-ins
- Mood trend chart
- Recent check-ins table
- AI-generated therapist-facing summary

## Why This Is Agentic AI

This project uses several agentic AI patterns:

1. **Input interpretation**  
   The AI reads a user’s emotional check-in and interprets the context.

2. **Risk-aware routing**  
   The app changes behavior depending on the risk level returned by the AI.

3. **Memory**  
   The app stores past check-ins and uses them for mood history and therapist summaries.

4. **Follow-up context**  
   The app lets the user continue the reflection using previous journal context and the AI’s earlier response.

5. **Tool-like actions**  
   The app saves entries, reads stored history, creates charts, and generates summaries based on selected patient data.

## Tech Stack

- Python
- Streamlit
- OpenAI API
- Pandas
- python-dotenv
- CSV storage

## Safety and Scope

This project is for learning and demonstration only.

It does not provide:

- therapy
- diagnosis
- medical advice
- medication advice
- crisis support
- emergency services

## How to Run Locally

1. Clone the repo.

2. Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create a `.env` file:

```bash
OPENAI_API_KEY=your_api_key_here
```

5. Run the app:

```bash
streamlit run app.py
```

## Project Structure

```text
between-sessions-ai/
  app.py
  README.md
  requirements.txt
  .gitignore
  data/
    checkins.csv
```

Note: `.env`, `.venv/`, and `data/checkins.csv` should not be uploaded to GitHub.

## Future Improvements

- Structured JSON output from AI responses
- Better patient management
- Multiple demo patients
- Stronger safety guardrails
- More robust crisis handling
- Authentication
- Database instead of CSV storage
- Streamlit deployment
- Evaluation test cases for low, medium, and high-risk inputs