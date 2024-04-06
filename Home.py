import os
import time

import streamlit as st
import dotenv
from PIL import Image

from api.ocr import ocr
from main import OpenAIChatAgentExt, DBApiExt

dotenv.load_dotenv()
# if "agent" not in st.session_state:
st.session_state.agent = OpenAIChatAgentExt(os.environ, OpenAIChatAgentExt.ANYSCALE_MODELS[0])
if "db_api" not in st.session_state:
    st.session_state.db_api = DBApiExt(os.environ)
if "chat_id" not in st.session_state: st.session_state.chat_id = None
if "title" not in st.session_state: st.session_state.title = "Title"
if "exclude" not in st.session_state: st.session_state.exclude = []
agent = st.session_state.agent


def reset_session():
    st.session_state.clear()
    st.session_state.db_api = DBApiExt(os.environ)


def load_chat(chat):
    st.session_state.agent.message_history = chat.get("message_history")
    st.session_state.title = chat.get("title")
    st.session_state.chat_id = chat.id


def delete_chat(chat):
    if chat.id == st.session_state.chat_id: reset_session()
    chat.reference.delete()


def message_stream(text: str):
    for ch in text:
        yield ch
        time.sleep(0.01)


st.set_page_config(page_title="Helt Pro", page_icon="💪🏽")
st.set_option("client.showSidebarNavigation", False)

st.markdown(
    """
    <style>
        #MainMenu{
            visibility: hidden;
        }
    </style>
    """, unsafe_allow_html=True
)

st.title("Health Guard")
st.subheader("LLM-powered Health Assistant")
st.caption("Powered by LLaMA2 and Mistral")

st.write("Welcome to Ask!")
raw_ocr = None
option = st.radio("Choose an option:", opts := ("Take a picture", "Upload an image", "Manual Entry"), index=1)
if option == opts[0]:
    image = st.camera_input("Take a picture of the ingredients")
elif option == opts[1]:
    image = st.file_uploader("Upload an image")
    if image is not None: st.image(image, caption="Uploaded Image", use_column_width=True)
else:
    image = None
    raw_ocr = st.text_area("Enter the ingredients here", height=200)

if image:
    image = Image.open(image)
    raw_ocr = ocr(image)

if raw_ocr:
    with agent:
        st.success(raw_ocr)
        pro_ocr = agent.process_raw_ocr(raw_ocr)
        with st.expander("Ingredients"):
            st.subheader(pro_ocr.product_name)
            for ingredient in pro_ocr.ingredients: st.warning(ingredient)
