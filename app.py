"""Streamlit entry point: run with `streamlit run app.py`."""

import streamlit as st
from PIL import Image

from src.photo_editor import EditSettings, apply_edits, encode_image, load_image

st.set_page_config(page_title="Python Photo Editor", page_icon="🖼️", layout="wide")
st.markdown("""<style>
.block-container {max-width: 1250px; padding-top: 2rem;}
[data-testid="stSidebar"] {border-right: 1px solid rgba(128,128,128,.2);}
</style>""", unsafe_allow_html=True)
st.title("Photo Editor")
st.caption("Non-destructive color adjustments · Full-resolution export · JPEG and PNG")

with st.sidebar:
    st.header("Photo")
    upload = st.file_uploader("Choose a JPEG or PNG", type=["jpg", "jpeg", "png"])
    st.header("Adjustments")
    brightness = st.slider("Brightness", -100, 100, 0)
    grayscale = st.checkbox("Black and white")
    negative = st.checkbox("Negative")
    selective = st.checkbox("Keep only one colour")
    color = st.selectbox("Colour to keep", ["red", "green", "blue"], disabled=not selective)
    threshold = st.slider("Colour strength threshold", 0, 100, 25, disabled=not selective)
    st.header("Export")
    export_format = st.selectbox("File format", ["PNG", "JPEG"])
    quality = st.slider("JPEG quality", 1, 100, 95, disabled=export_format != "JPEG")

if upload is None:
    st.info("Upload a JPEG or PNG image to start editing. Your original file stays unchanged.")
    st.stop()

try:
    # Upload bytes are the source of truth; processing never overwrites them.
    original = load_image(upload.getvalue())
    settings = EditSettings(
        brightness=brightness,
        grayscale=grayscale,
        negative=negative,
        selective_color=selective,
        color=color,
        threshold=threshold,
    )
    edited, percentage = apply_edits(original, settings)
except (ValueError, OSError, MemoryError, Image.DecompressionBombError) as exc:
    st.error(f"Unable to process this image: {exc}")
    st.stop()

st.caption(f"Original resolution: {original.width:,} × {original.height:,} pixels")
if percentage is not None:
    st.info(f"{percentage:.1f}% of the photo remains in colour.")

before, after = st.columns(2, gap="large")
with before:
    st.subheader("Before")
    st.image(original, use_container_width=True)
with after:
    st.subheader("After")
    st.image(edited, use_container_width=True)

try:
    data = encode_image(edited, export_format, quality)
except (ValueError, OSError, MemoryError) as exc:
    st.error(f"Could not prepare the download: {exc}")
else:
    suffix = "png" if export_format == "PNG" else "jpg"
    mime = "image/png" if export_format == "PNG" else "image/jpeg"
    stem = upload.name.rsplit(".", 1)[0]
    st.download_button(
        "Download edited image", data=data, file_name=f"{stem}_edited.{suffix}",
        mime=mime, type="primary", use_container_width=True,
    )
