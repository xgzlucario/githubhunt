import asyncio
import os

from PIL import Image
from pydoll.browser import Chrome
from pydoll.browser.options import ChromiumOptions


async def take_screenshot(url: str, path: str = 'images/readme.png', quality: int = 90) -> list[Image.Image]:
    options = ChromiumOptions()
    options.add_argument('--headless=new')
    options.add_argument('--disable-notifications')
    options.add_argument('--window-size=1000,1000')

    async with Chrome(options=options) as browser:
        tab = await browser.start()
        await tab.go_to(url)

        # 等待页面加载完成
        await asyncio.sleep(3)

        os.makedirs(os.path.dirname(path), exist_ok=True)
        await tab.take_screenshot(path=path, quality=quality, beyond_viewport=True)

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
    url = 'https://github.com/xgzlucario/githubhunt/blob/master/README.md'

    for i in range(10):
        images = await take_screenshot(url=url, path='images/readme.png')
        for i, image in enumerate(images):
            image.save(f'images/readme_{i}.png')

        print(f'Saved {len(images)} images')


if __name__ == '__main__':
    asyncio.run(main())