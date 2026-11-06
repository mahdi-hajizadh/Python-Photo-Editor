
# photo_app.py
# Run with: streamlit run photo_app.py

import numpy as np
import streamlit as st
from PIL import Image, ImageOps
from sklearn.datasets import load_sample_image

st.title("My Photo Editor")

# 1. Open a photo
uploaded = st.file_uploader(
    "Choose a photo",
    type=["jpg", "jpeg", "png"]
)

if uploaded is None:
    photo = load_sample_image("china.jpg")
else:
    picture = ImageOps.exif_transpose(Image.open(uploaded))
    picture.thumbnail((700, 700))
    photo = np.array(picture.convert("RGB"))

photo = photo.astype(float)

# 2. Controls
amount = st.slider(
    "Brightness",
    min_value=-100,
    max_value=100,
    value=0
)

make_gray = st.checkbox("Black and white")
make_negative = st.checkbox("Negative")
keep = st.checkbox("Keep only one colour")

# 3. Adjust brightness
result = np.clip(photo + amount, 0, 255)

# 4. Keep one colour
if keep:
    colours = ["red", "green", "blue"]
    choice = st.selectbox("Which colour stays?", colours)

    channel = colours.index(choice)

    limit = st.slider(
        "How strong must the colour be?",
        min_value=0,
        max_value=100,
        value=25
    )

    # Convert the image to grayscale
    gray = result.mean(axis=2)

    # Find pixels where the selected colour stands out
    mask = result[:, :, channel] - gray > limit

    # Make a three-channel grayscale image
    gray3 = np.stack([gray, gray, gray], axis=2)

    # Restore the original colours at selected pixels
    pop = gray3.copy()
    pop[mask] = result[mask]

    result = pop

    # Calculate the percentage of pixels kept in colour
    percentage = mask.mean() * 100

    st.write(
        f"{percentage:.1f}% of the photo remains in colour."
    )

# 5. Black and white
if make_gray:
    result = result.mean(axis=2)
    result = np.stack([result, result, result], axis=2)

# 6. Negative
if make_negative:
    result = 255 - result

# 7. Show before and after
st.image(
    [photo.astype("uint8"), np.clip(result, 0, 255).astype("uint8")],
    caption=["Before", "After"],
    width=330
)
