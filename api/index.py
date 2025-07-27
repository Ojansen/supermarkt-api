import json
import re
from enum import Enum
from typing import Any

import requests
from flask import Flask, render_template
from requests import Response

app = Flask(__name__)


class SupermarketNames(Enum):
    ah = "ah"
    jumbo = "jumbo"
    plus = "plus"
    kruidvat = "kruidvat"


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


def pipeline(base: str, week: str):
    url = base + week

    print(f"\nProcessing: {url}")
    resp = requests.get(url)
    if resp.status_code != 200:
        print(f"Failed to fetch page: {url}")

    data = fetch_publitas_data(resp)
    images = extract_images(data)
    return [base + image for image in images]


@app.route("/api/cron", methods=["GET"])
def cron():
    pass


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


# @app.route("/v1/<name>", methods=["GET"])
# def index(name: str):
#     match name:
#         # case SupermarketNames.ah.name:
#         #     # ("https://folder.ah.nl", "/bonus-week-31-2025/page/1")
#         #     base = "https://folder.ah.nl"
#         #     week = "/bonus-week-31-2025/page/1"
#         #     return pipeline(base, week)
#         case SupermarketNames.jumbo.name:
#             base = "https://view.publitas.com"
#             week = "/jumbo-supermarkten/jumbo-actiefolder-jmta-30/page/1"
#             return pipeline(base, week)
#         case SupermarketNames.plus.name:
#             base = "https://view.publitas.com"
#             week = "/plus-preview-nl/plus-week-31-2025-v1/page/1"
#             return pipeline(base, week)
#         case SupermarketNames.kruidvat.name:
#             base = "https://folder.kruidvat.nl"
#             week = "/kruidvat-folder-week-30-21-juli-2025-t-m-3-augustus-2025/page/1"
#             return pipeline(base, week)
#         case _:
#             return [f"That is not a valid supermarket name"]
#
#     return None
