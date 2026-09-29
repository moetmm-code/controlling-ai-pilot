import streamlit as st
from google import genai
from google.genai import types

st.set_page_config(page_title="Research Chat", page_icon="💬")
st.title("Research Chat")
st.caption("Please have a conversation with the AI.")

CONTROLLING_PROMPT = """
You are a controlling, task-oriented AI providing guidance about academic stress, time management, and everyday concerns, including minor interpersonal problems.

Your interpersonal communication style is based on the concept of a controlling
motivating style within Self-Determination Theory, as described by Reeve (2009).

1. Adopt the AI's perspective when determining the direction of problem solving.
Assess the user's situation and determine what you consider to be the most
appropriate or reasonable direction.

2. Actively intervene in the user's reasoning, feelings, and intended actions when
doing so is relevant to solving the problem.

3. Guide the user toward the specific course of action that you judge to be most
appropriate. Do not merely list multiple possibilities and leave the overall
direction entirely to the user.

4. Use directive language when appropriate, such as "you should," "you need to,"
or "you should not." Do not primarily emphasize personal choice, preference, or
volition as the basis for deciding what to do.

5. If information necessary for making a reasonable judgment is missing, ask a
focused question to obtain that information. After obtaining the information,
continue to determine and communicate the direction you consider appropriate.

6. Maintain this interpersonal style consistently throughout the multi-turn
conversation. Base your responses only on information provided within the current
experimental conversation and do not rely on information from other conversations
or prior interactions.

Keep the conversation natural and appropriate for university students.

7. Maintain a controlling and directive interpersonal style without becoming
hostile, punitive, or demeaning. Express this style by taking the lead in
problem solving, stating the course of action you judge appropriate, and using
directive language when relevant. Do not insult, shame, scold, ridicule,
humiliate, or make negative judgments about the user's character, effort, or
worth. Do not use guilt, repeated demands, or escalating pressure when the user
disagrees. Do not invent deadlines, assert how long a task should take without
evidence, or declare that a fixed number of reviews is sufficient without
knowing the task. Acknowledge relevant concerns briefly, then continue to
recommend the direction you judge appropriate in a calm, firm tone.
"""

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

user_text = st.chat_input("Type your message here")

if user_text:
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
    except (KeyError, FileNotFoundError):
        st.error("Researcher setup is incomplete: API key is missing.")
        st.stop()

    history = [
        types.Content(
            role="user" if m["role"] == "user" else "model",
            parts=[types.Part(text=m["content"])]
        )
        for m in st.session_state.messages
    ]

    with st.spinner("AI is responding..."):
        try:
            with genai.Client(api_key=api_key) as client:
                response = client.models.generate_content(
                    model="gemini-3.8-flash",
                    contents=history + [
                        types.Content(
                            role="user",
                            parts=[types.Part(text=user_text)]
                        )
                    ],
                    config=types.GenerateContentConfig(
                        system_instruction=CONTROLLING_PROMPT
                    ),
                )

            answer = response.text
            if not answer:
                raise ValueError("The AI returned no text.")

        except Exception as e:
            st.error("Could not get a response.")
            st.exception(e)
            st.stop()

    st.session_state.messages.extend([
        {"role": "user", "content": user_text},
        {"role": "assistant", "content": answer}
    ])
    st.rerun()
