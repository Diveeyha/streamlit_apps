import streamlit as st
import random
from birds.database import load_csv, get_birds_by_family
from birds.audio import find_bird_urls


def initialize_session_state():
    if 'question_number' not in st.session_state:
        st.session_state.question_number = 0
    if 'player_score' not in st.session_state:
        st.session_state.player_score = 0


def update_score(player_choice, correct_answer):
    if player_choice == correct_answer:
        st.session_state.player_score += 1


@st.cache_data
def bird_data(bird_filter):
    birds = bird_filter.sample(frac=1)
    # st.data_editor(birds)
    return birds


def get_audio(question_number, birds, answer):
    audio_file = find_bird_urls(birds['name'])
    url = random.choice(audio_file[answer])
    return url


def reset():
    st.session_state.my_selectbox = birds['name'].sort_values(ignore_index=True)[0]


def filter():
    if st.session_state.txt_filter == "All":
        bird_filter = load_csv()
        return bird_filter
    elif st.session_state.txt_filter == "Waterfowl":
        bird_filter = get_birds_by_family('anatidae')
        return bird_filter


st.title("North American Bird Quiz")
initialize_session_state()

tab1, tab2 = st.tabs(["Bird List", "Audio"])
with tab1:
    st.radio("Filter by", ["All", "Waterfowl"], horizontal=True, key="txt_filter")
    st.dataframe(filter(), hide_index=True)

with tab2:
    with st.form("Audio Quiz"):
        birds = bird_data(filter())
        ind = st.session_state.question_number
        answer = birds.iloc[ind, 0]
        # st.write(birds.iloc[ind, 0])
        st.audio(get_audio(ind, birds, answer))

        guess = st.selectbox("Select:", birds['name'].sort_values(), label_visibility="collapsed", key="my_selectbox")

        if st.form_submit_button("Submit", on_click=reset):
            update_score(guess, answer)
            st.session_state.question_number += 1

col1, col2, col3 = st.columns([1, 1, 1], gap="small")
with col1:
    st.empty()
with col2:
    if st.button("Finished", key="finished", type="primary"):
        st.success("Quiz Finished!")
        st.write(f"Your Score: {st.session_state.player_score} correct out of {st.session_state.question_number}.")

with col3:
    if st.button("Reset", key="reset", on_click=reset, type="primary"):
        st.session_state.question_number = 0
        st.session_state.player_score = 0
        bird_data.clear()
        st.experimental_rerun()

# st.session_state
