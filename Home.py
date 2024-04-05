import streamlit as st

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

# take photo or upload image
st.write("Welcome to Ask!")
option = st.radio("Choose an option:", opts := ("Take a picture", "Upload an image"), index=1)
if option == opts[0]:
    image = st.camera_input("Take a picture of the ingredients")
else:
    image = st.file_uploader("Upload an image")

    if image is not None:
        st.image(image, caption="Uploaded Image", use_column_width=True)


