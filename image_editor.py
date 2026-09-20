import base64
import io
from pathlib import Path

import streamlit.components.v1 as components


_editor = components.declare_component('poster_image_editor_v5', path=str(Path(__file__).parent / 'image_editor'))


def image_url(image):
    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    return 'data:image/png;base64,' + base64.b64encode(buffer.getvalue()).decode('ascii')


def poster_editor(background, overlay, transform, editing, revision, key):
    return _editor(background=image_url(background), overlay=image_url(overlay),
                   image_width=background.width, image_height=background.height,
                   transform=transform, editing=editing, revision=revision,
                   key=key, default=None)
