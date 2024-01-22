from time import sleep
import streamlit as st
from random import choice
from clarifai.base import Image, Text
from clarifai.image_processing import ClarifaiImageDetection
from clarifai.text_to_speech import ClarifaiTextToSpeech

flag = False
detector = ClarifaiImageDetection()
tts = ClarifaiTextToSpeech()
st.session_state.transcription=b''
st.session_state.text  = ''
st.session_state.old_picture = b''
st.write("This page demonstrates monitoring where you take a picture and the AI classfies it\
 and tells you how near or far they are. It will be read our to our user with the browser talk back feature but\
 since we don't have access to that, we would be using our text to speech model to do the honors")
message = st.empty()  
cols = st.columns([1, 4, 1])
# with st.container() as image_container:
picture = cols[1].camera_input(label="Take an image of your surroundings")
if picture and st.session_state.old_picture != picture:
    message.info('Analyzing image')
    st.session_state.old_picture = picture
    result = detector.run({"image": Image(base64=picture.read())})
    transcription = detector.construct_warning(result[0])
    message.info('Generating audio')
    audio_warning = tts.run({"text": Text(raw=transcription)})[0]['audio']
    st.session_state.transcription = audio_warning
    message.success('Audio generated')
    sleep(0.5)
    message.empty()

st.header("Result")
st.audio(st.session_state.transcription)
