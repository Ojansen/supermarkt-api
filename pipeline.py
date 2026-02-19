import json
import os
from datetime import date
from io import BytesIO
from os.path import abspath, dirname, join

import requests
from mistralai import Mistral, DocumentURLChunk
from mistralai.extra import response_format_from_pydantic_model
from PIL import Image
from pydantic import BaseModel


# --- Pydantic models for structured OCR extraction ---


class Product(BaseModel):
    naam: str  # product name
    omschrijving: str  # description of the offer
    items: list[str]  # specific product variants
    aanbieding: str  # offer type (e.g. "1+1", "2e halve prijs")
    prijs_eerst: float  # price before
    prijs_nu: float  # price after


class WeeklyDeals(BaseModel):
    producten: list[Product]


# --- Store configuration ---

STORES = {
    "ah": ("publitas", "https://folder.ah.nl", "/bonus-week-8-2026"),
    "jumbo": (
        "pdf",
        "https://view.publitas.com/171/2841137/pdfs/"
        "d1b35057-1b3d-48b3-b997-0c55f6261768.pdf",
    ),
    "plus": (
        "publitas",
        "https://view.publitas.com",
        "/plus-preview-nl/plus-week-8-2026",
    ),
    "kruidvat": (
        "publitas",
        "https://folder.kruidvat.nl",
        "/kruidvat-folder-8-16-februari-2026-t-m-22-februari-2026",
    ),
}

OUTPUT_DIR = join(dirname(abspath(__file__)), "public", "v1")


# --- Scraping ---


def fetch_image_urls(base: str, path: str) -> list[str]:
    url = base + path + "/spreads.json"
    resp = requests.get(url)
    resp.raise_for_status()
    spreads = resp.json()

    images = []
    for spread in spreads:
        for page in spread.get("pages", []):
            img_url = page["images"]["at600"]
            if img_url:
                images.append(base + img_url)
    return images


# --- PDF building ---


def build_pdf_from_images(image_urls: list[str]) -> bytes:
    images = []
    for url in image_urls:
        resp = requests.get(url)
        resp.raise_for_status()
        img = Image.open(BytesIO(resp.content))
        if img.mode != "RGB":
            img = img.convert("RGB")
        images.append(img)

    pdf_buffer = BytesIO()
    images[0].save(
        pdf_buffer, format="PDF", save_all=True, append_images=images[1:]
    )
    pdf_buffer.seek(0)
    return pdf_buffer.read()


# --- Mistral OCR ---


def ocr_to_deals(pdf_bytes: bytes, store_name: str) -> WeeklyDeals:
    client = Mistral(api_key=os.environ["MISTRAL_API_KEY"])

    uploaded_file = client.files.upload(
        file={"file_name": f"{store_name}.pdf", "content": pdf_bytes},
        purpose="ocr",
    )

    signed_url = client.files.get_signed_url(
        file_id=uploaded_file.id, expiry=1
    )

    response = client.ocr.process(
        model="mistral-ocr-latest",
        document=DocumentURLChunk(document_url=signed_url.url),
        document_annotation_format=response_format_from_pydantic_model(
            WeeklyDeals
        ),
    )

    client.files.delete(file_id=uploaded_file.id)

    return WeeklyDeals.model_validate_json(response.document_annotation)


# --- Pipeline ---


def get_pdf_bytes(store_name: str, config: tuple) -> bytes:
    store_type = config[0]

    if store_type == "pdf":
        pdf_url = config[1]
        print(f"[{store_name}] Downloading PDF from {pdf_url}")
        resp = requests.get(pdf_url)
        resp.raise_for_status()
        return resp.content

    # publitas: scrape images and build PDF
    base, path = config[1], config[2]
    print(f"[{store_name}] Fetching {base}{path}/spreads.json")
    image_urls = fetch_image_urls(base, path)
    print(f"[{store_name}] Found {len(image_urls)} page images")
    print(f"[{store_name}] Building PDF from images...")
    return build_pdf_from_images(image_urls)


def run_pipeline(store_name: str, config: tuple):
    pdf_bytes = get_pdf_bytes(store_name, config)

    print(f"[{store_name}] Running OCR...")
    deals = ocr_to_deals(pdf_bytes, store_name)

    week = date.today().isocalendar().week
    output = {"week": week, "producten": [p.model_dump() for p in deals.producten]}

    output_path = join(OUTPUT_DIR, f"{store_name}.json")
    with open(output_path, "w") as f:
        json.dump(output, f, ensure_ascii=False)

    print(f"[{store_name}] Wrote {len(deals.producten)} products to {output_path}")


def run_all():
    for store_name, config in STORES.items():
        try:
            run_pipeline(store_name, config)
        except Exception as e:
            print(f"[{store_name}] Error: {e}")
