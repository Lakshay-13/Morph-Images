import streamlit as st
import cv2
import imageio
import numpy as np
from PIL import Image
from io import BytesIO
import base64
import time
import os

def load_image(uploaded_file):
    return np.array(Image.open(uploaded_file))

def morph_images(img1, img2, num_steps):
    morphed_images = []

    for step in range(num_steps):
        t = step / (num_steps - 1)
        morphed_img = cv2.addWeighted(img1, 1 - t, img2, t, 0)
        morphed_images.append(morphed_img)

    return morphed_images

def add_border(img, border_size, border_color):
    return cv2.copyMakeBorder(img, border_size, border_size, border_size, border_size, cv2.BORDER_CONSTANT, value=border_color)

def create_gif(images, output_filename, duration, border_size=0, border_color=(0, 0, 0)):
    if border_size > 0:
        images = [add_border(img, border_size, border_color) for img in images]
    imageio.mimsave(output_filename, images, format='GIF', duration=duration)

def get_image_download_link(img, file_name="morphed_graph.gif", text="Save Image"):
    buffered = BytesIO()
    img.save(buffered, format="GIF")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    href = f'<a href="data:image/gif;base64,{img_str}" download="{file_name}" style="text-decoration:none;color:white;">{text}</a>'
    return href

def get_gif_download_link(output_filename, file_name="morphed_graph.gif", text="Save Image"):
    with open(output_filename, "rb") as f:
        img_bytes = f.read()
    img_str = base64.b64encode(img_bytes).decode()
    href = f'<a href="data:image/gif;base64,{img_str}" download="{file_name}" style="text-decoration:none;color:white;">{text}</a>'
    return href

st.title("Graph Morphing")

uploaded_files = st.file_uploader("Upload the graph images (2 or more)", type=["png", "jpg", "jpeg"], accept_multiple_files=True)

if len(uploaded_files) >= 2:
    num_steps = st.slider("Number of steps", 2, 100, 10)
    duration = st.slider("Duration between frames (s)", 0.05, 0.5, 0.2)
    gif_time = num_steps * duration

    col1, col2 = st.columns([2, 5])
    with col1:
        border_enabled = st.checkbox("Enable border")
    with col2:
        st.write(f"Total GIF time: {gif_time:.2f} seconds")

    if border_enabled:
        border_color = st.color_picker("Border color", value="#000000")
        border_color = tuple(int(border_color.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))
        border_size = st.slider("Border size", 0, 50, 10)
    else:
        border_size = 0

    if st.button("Morph and create GIF"):
        img1 = load_image(uploaded_files[0])
        for uploaded_file in uploaded_files[1:]:
            img2 = load_image(uploaded_file)
            morphed_images = morph_images(img1, img2, num_steps)
            create_gif(morphed_images, "morphed_graph.gif", duration, border_size, border_color if border_enabled else None)
            st.image("morphed_graph.gif")
            img1 = img2

        output_filename = "morphed_graph.gif"
        
        file_name = st.text_input("Enter file name:", "morphed_graph.gif")
        st.markdown(get_gif_download_link(output_filename, file_name=file_name), unsafe_allow_html=True)
        time.sleep(10)
        os.remove(output_filename)


else:
    st.warning("Please upload at least 2 graph images.")
  
