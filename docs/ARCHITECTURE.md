# Architecture and quality notes

## Source audit

The supplied source was a single `app_photo1.py` Streamlit script. It imported NumPy, Pillow, Streamlit, and scikit-learn solely for a default sample image. Its controls were brightness, black-and-white, negative, and selective red/green/blue color; the output was a side-by-side preview. It lacked export, input validation, automated tests, and separation of GUI and processing logic. It reduced uploaded images to 700 × 700 pixels.

## Design

- `app.py` owns Streamlit widgets, upload handling, feedback, previews, and downloads.
- `src/photo_editor/processing.py` owns validated settings, image decoding, deterministic pixel processing, and export encoding.
- `apply_edits` does not mutate its input and uses the source's original transformation order.
- Upload bytes are decoded anew on Streamlit reruns, preventing cumulative edits.
- scikit-learn was removed: the sample image was not part of the core editing functionality and added a large runtime dependency.

## Security and compatibility

No credentials or personal data were found in the supplied script. Uploaded images are processed in memory and not written to disk by the application. JPEG/PNG signatures are verified by Pillow; malformed files are rejected. Input pixel count is limited to 40 megapixels. For production hosting, also configure reverse-proxy upload size limits and memory quotas.

Runtime dependency ranges are deliberately bounded, but no lockfile is provided. For reproducible deployments, resolve and lock dependencies in the deployment environment.

## License verification

The included MIT text is a proposed license for this package. The source file did not contain a license notice, and GitHub repository licensing/contributor permissions were not independently established. Confirm ownership and authorization before publishing under MIT.

## Validation scope

Pytest covers file decoding, bad inputs, EXIF orientation, all original effects, composition order, non-mutation, export, and edge cases. A live Streamlit browser session requires a runtime with Streamlit installed and should be checked before production deployment.
