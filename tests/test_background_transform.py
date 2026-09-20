import io

from PIL import Image

from poster import render_background


def source():
    image = Image.new('RGB', (100, 100), 'red')
    image.paste('blue', (50, 0, 100, 100))
    buffer = io.BytesIO()
    image.save(buffer, 'PNG')
    return buffer


def test_background_pan_and_default_reset():
    image = source()
    default = render_background(image, size=(100, 100))
    moved = render_background(image, {'x': 25}, size=(100, 100))
    assert default.getpixel((60, 50)) == (0, 0, 255, 255)
    assert moved.getpixel((60, 50)) == (255, 0, 0, 255)
    assert moved.getpixel((0, 50)) == (255, 255, 255, 255)
    assert render_background(image, size=(100, 100)).tobytes() == default.tobytes()


def test_background_scales_about_center_without_changing_export_size():
    small = render_background(source(), {'scale': .5}, size=(100, 100))
    assert small.size == (100, 100)
    assert small.getpixel((10, 50)) == (255, 255, 255, 255)
    assert small.getpixel((30, 50)) == (255, 0, 0, 255)
    assert small.getpixel((60, 50)) == (0, 0, 255, 255)
