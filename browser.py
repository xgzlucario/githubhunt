import asyncio
import os
import time

from PIL import Image
from pydoll.browser import Chrome
from pydoll.browser.options import ChromiumOptions


class Browser:
    def __init__(self, binary_path: str):
        options = ChromiumOptions()
        options.add_argument("--headless=new")
        options.add_argument("--disable-notifications")
        options.add_argument("--window-size=1000,1000")
        if binary_path:
            options.binary_location = binary_path
            
        self.browser = Chrome(options=options)

    async def __aenter__(self):
        await self.browser.start()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.browser.stop()

    async def take_screenshot(
        self, url: str, path: str = "images/readme.png", quality: int = 90
    ) -> list[Image.Image]:
        tab = await self.browser.new_tab()

        try:
            await tab.go_to(url)

            # 等待页面加载完成
            await tab._wait_page_load()

            os.makedirs(os.path.dirname(path), exist_ok=True)
            await tab.take_screenshot(path=path, quality=quality, beyond_viewport=True)

        finally:
            await tab.close()

        # 切分成多张最大高度为 2000px 的图片
        each_height = 2000

        image = Image.open(path)
        width, height = image.size
        images = []
        for i in range(0, height, each_height):
            crop_image = image.crop((0, i, width, min(i + each_height, height)))
            images.append(crop_image)

        return images


async def main():
    async with Browser() as browser:
        url = "https://github.com/xgzlucario/githubhunt/blob/master/README.md"

        for i in range(3):
            start_time = time.time()
            images = await browser.take_screenshot(url=url, path="images/readme.png")
            end_time = time.time()
            print(f"Time taken: {end_time - start_time} seconds")

            for i, image in enumerate(images):
                image.save(f"images/readme_{i}.png")

            print(f"Saved {len(images)} images")


if __name__ == "__main__":
    asyncio.run(main())
