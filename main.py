import json
import os
import re
from typing import Any

import requests
from flask.cli import load_dotenv
from openai import OpenAI
from pydantic import BaseModel
from requests import Response

PUBLITAS_URLS = [
    "https://view.publitas.com/jumbo-supermarkten/jumbo-actiefolder-jmta-30/page/1",
    "https://folder.ah.nl/bonus-week-31-2025/page/1",
]


class FolderItem(BaseModel):
    title: str
    description: str
    items: list[str]
    offer: str
    price_before: float
    price_after: float


PUBLITAS_DICT = [
    (
        "https://view.publitas.com",
        "/jumbo-supermarkten/jumbo-actiefolder-jmta-30/page/1",
    ),
    ("https://folder.ah.nl", "/bonus-week-31-2025/page/1"),
    (
        "https://folder.kruidvat.nl",
        "/kruidvat-folder-week-30-21-juli-2025-t-m-3-augustus-2025/page/1",
    ),
    ("https://view.publitas.com", "/plus-preview-nl/plus-week-31-2025-v1/page/1"),
]


def extract_images(data: Any) -> list[str]:
    images = []
    for spread in data.get("spreads", []):
        for page in spread.get("pages", []):
            img_url = page["images"]["at600"]
            if img_url:
                images.append(img_url)
    return images


def fetch_publitas_data(resp: Response):
    match = re.search(r"var\s+data\s+=\s+({.*?});", resp.text, re.DOTALL)
    if not match:
        raise ValueError(f"No data JSON found in page: {resp.url}")

    return json.loads(match.group(1))


def main():
    for base, week in PUBLITAS_DICT:
        url = base + week

        print(f"\nProcessing: {url}")
        resp = requests.get(url)
        if resp.status_code != 200:
            print(f"Failed to fetch page: {url}")
            continue

        data = fetch_publitas_data(resp)
        images = extract_images(data)

        print([base + image for image in images])

    # client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    #
    # response = client.responses.parse(
    #     model="gpt-4.1-mini",
    #     input=[
    #         {
    #             "role": "user",
    #             "content": [
    #                 {"type": "input_text", "text": "what's in this image?"},
    #                 {
    #                     "type": "input_image",
    #                     "image_url": images[0],
    #                 },
    #             ],
    #         }
    #     ],
    #     text_format=FolderItem,
    # )
    #
    # print(response.output_parsed)


if __name__ == "__main__":
    load_dotenv()
    main()
