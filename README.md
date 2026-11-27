# Python Photo Editor

A lightweight, browser-based photo editor built with **Streamlit**, **Pillow**, and **NumPy**. Edits are calculated from the original uploaded image and can be downloaded at full resolution.

## Features

- Upload JPEG and PNG photographs with EXIF orientation correction.
- Brightness adjustment (-100 to +100), with channel clipping.
- Black-and-white conversion using the original arithmetic-mean method.
- Negative (color inversion) effect.
- Selective color: retain prominent red, green, or blue pixels, with adjustable threshold and percentage feedback.
- Side-by-side before/after preview.
- Download full-resolution PNG or JPEG (configurable JPEG quality).
- Input validation and clear error messages.

The original application's processing order is preserved: **brightness → selective color → grayscale → negative**. When grayscale is enabled, selective-color pixels are also converted to grayscale.

## Requirements

Python 3.10 or newer is recommended. A current Python 3.11 or 3.12 installation is a practical choice.

## Install and run

```powershell
git clone https://github.com/mahdi-hajizadh/Python-Photo-Editor.git
cd Python-Photo-Editor
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

On macOS/Linux, use `python3 -m venv .venv` and `source .venv/bin/activate` instead of the Windows commands. Open the local URL printed by Streamlit.

## Usage

1. Upload a JPEG or PNG using the sidebar.
2. Change brightness or toggle black-and-white, negative, or selective color.
3. Compare the original and edited previews.
4. Choose PNG or JPEG and download the edited image.

Uploaded originals are not overwritten. Preview images are resized by the browser interface, not by the processing pipeline.

## Testing

```powershell
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

## Project structure

```text
app.py                     Streamlit user interface
src/photo_editor/          Pure image operations and image I/O
tests/                     Pytest regression tests
docs/                      Architecture and operational notes
requirements.txt           Runtime dependencies
requirements-dev.txt       Test dependencies
```

## Known limitations

- Input is limited to JPEG and PNG; alpha channels are flattened to RGB.
- Images over 40 million pixels are rejected to limit resource use.
- The Streamlit UI is designed for interactive browser use, not batch editing.
- Grayscale and selective color intentionally retain the original project's arithmetic-mean algorithm rather than a perceptual-luminance algorithm.
- Processing uses memory proportional to image size; large photos may be slow.

## Future improvements

- Optional luminance-based grayscale mode.
- A verified visual-regression test suite for the Streamlit interface.
- Optional drag-to-compare preview if justified by user needs.

## License

MIT — see [LICENSE](LICENSE). **Before publishing, confirm that the repository owner and any other contributors have authorized MIT licensing of all included code.** No third-party sample image is bundled.
