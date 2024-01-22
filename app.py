import streamlit as st
from st_audiorec import st_audiorec
from clarifai.base import Audio, Image, Text
from clarifai.image_processor import AsyncVideoProcessor
import asyncio
from clarifai.transcription import ClarifaiTranscription
from clarifai.workflows import ClarifaiMultimodalToSpeechWF

st.session_state.clicked = False
st.session_state.audio_input = b''
st.session_state.audio_output = None
st.session_state.picture = b''
st.title("Ilens")
message = st.empty()
transcriber = ClarifaiTranscription()
llm_wf = ClarifaiMultimodalToSpeechWF()
image_processor = AsyncVideoProcessor()
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

async def handle_submit(audio, clip):
    print("handling submit")
    async def get_image():
        best_frame = await image_processor.process_video(clip)
        image_bytes = await asyncio.to_thread(
            image_processor.convert_result_image_to_bytes, best_frame
        )
        return image_bytes
    async def get_transcript():
        transcript = (
            await asyncio.to_thread(
                transcriber.run,
                {
                    "audio": Audio(base64=audio),
                },
            )
        )[0]["text"]
        return transcript
    image_bytes, transcript = await asyncio.gather(get_image(), get_transcript())
    if not transcript:
        message.error("No transcript found")
    if len(transcript) > 500:
        message.error("Transcript too long")
    elif len(transcript) < 10:
        message.error("Transcript too short")
    audio_stream = (
        await asyncio.to_thread(
            llm_wf.run,
            {
                "text": Text(raw=transcript),
                "image": Image(base64=image_bytes),
            },
        )
    )[0]["audio"]
    st.session_state.audio_output = audio_stream.getvalue()
    message.success("Done")
    st.audio(st.session_state.audio_output, format="audio/wav")  # Display the audio

st.header("Result")
if st.session_state.audio_output:
    st.audio(st.session_state.audio_output, format="audio/wav")
if st.session_state.picture:
    st.image(st.session_state.picture)

if st.button("Submit", type='primary', key="submit", use_container_width=True):
    if st.session_state.audio_input and st.session_state.picture:
        asyncio.run(handle_submit(st.session_state.audio_input, st.session_state.picture))
    else:
        st.error("You have to take a picture of your surroundings and ask your question. \
            That's how this works.")