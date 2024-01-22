import streamlit as st
from st_audiorec import st_audiorec
from PIL import Image

st.session_state.clicked = False
st.session_state.audio_input = None
st.session_state.audio_output = None
st.session_state.picture = None
st.title("Ilens")
body = st.columns(2)
m_m, m_m_results = body

with m_m.container() as audio_container:
    wav_audio_data = st_audiorec()
    if wav_audio_data:
        st.session_state.audio_input = wav_audio_data

with m_m_results.container() as image_container:
    picture = st.camera_input(label="Take an image of your surroundings")
    if picture:
        st.session_state.picture = picture

def handle_submit():
    print("handling submit")
    if not ('audio_input' in st.session_state and 'picture' in st.session_state):
        st.error("You have to take a picture of your surroundings and ask your question. \
            That's how this works.")
        return
    st.session_state.audio_output = st.session_state.audio_input
    st.audio(st.session_state.audio_output, format="audio/wav")  # Display the audio
    st.image(st.session_state.picture)  # Display the image
    print("Done")

st.header("Result")
if st.session_state.audio_output:
    st.audio(st.session_state.audio_output, format="audio/wav")
if st.session_state.picture:
    st.image(st.session_state.picture)

if st.button("Submit", type='primary', key="submit", use_container_width=True):
    handle_submit()