from PIL import Image
import requests
from io import BytesIO
import base64


def img_url(url):
    response = requests.get(url)
    return Image.open(BytesIO(response.content))


def img_to_b64(img, format="PNG"):
    buffered = BytesIO()
    img.save(buffered, format=format)
    return base64.b64encode(buffered.getvalue()).decode('utf-8')
