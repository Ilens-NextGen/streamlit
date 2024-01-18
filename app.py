import streamlit as st
from st_audiorec import st_audiorec
from PIL import Image

st.session_state.clicked=False
# st.session_state.audio_input = None
st.session_state.audio_output = None
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
    if not 'audio_input' in st.session_state and not 'picture' in st.session_state:
        st.error("You have to take a picture of your surroundings and ask your question.\
            That 's how this works.")
        return
    st.session_state.clicked = True
    st.session_state.audio_output=st.session_state.audio_input
    st.write("Result")
    st.audio(st.session_state.audio_output)
    print("Done")

st.button("Submit", type='primary', on_click=handle_submit, key="submit", use_container_width=True)

if st.session_state.clicked:
    print("yes")
    print(st.session_state.audio_output)
