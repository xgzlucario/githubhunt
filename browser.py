import requests
from PIL import Image
import io
import os

BROWSER_API_URL = "http://localhost:3000"


def take_screenshot(url: str) -> list[Image.Image]:
    response = requests.post(
        f"{BROWSER_API_URL}/v1/screenshot",
        json={
            "url": url,
            "delay": 1,
            "fullPage": True,
        },
    )

    if response.status_code != 200:
        raise Exception(
            f"Failed to take screenshot: {response.status_code} {response.text}"
        )

    image = Image.open(io.BytesIO(response.content))

    # 切分成多张最大高度为 2000px 的图片
    each_height = 2000

    width, height = image.size
    images = []
    for i in range(0, height, each_height):
        crop_image = image.crop((0, i, width, min(i + each_height, height)))
        images.append(crop_image)

    return images


if __name__ == "__main__":
    os.makedirs("images", exist_ok=True)

    images = take_screenshot("https://github.com/xgzlucario/githubhunt")
    for i, image in enumerate(images):
        image.save(f"images/crop_image_{i}.png")
