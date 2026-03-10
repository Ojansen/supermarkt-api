import json
import os
import re
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date
from io import BytesIO
from os.path import abspath, dirname, join

import requests
from mistralai import Mistral, DocumentURLChunk
from mistralai.extra import response_format_from_pydantic_model
from PIL import Image
from pydantic import BaseModel
from tqdm import tqdm


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


# --- Store configuration: slug -> (wk_id, display_name) ---

STORES = {
    "ah":       (17, "Albert Heijn"),
    "jumbo":    (40, "Jumbo"),
    "plus":     (20, "Plus"),
    "kruidvat": (8,  "Kruidvat"),
    "lidl":     (26, "Lidl"),
    "aldi":     (21, "Aldi"),
}

OUTPUT_DIR = join(dirname(abspath(__file__)), "public", "v1")


# --- voordeelmuis.nl scraping ---

VOORDEELMUIS_URL = (
    "https://www.voordeelmuis.nl/cgi-bin/my2.cgi"
    "?action=loadJSON&cleanQuery=AwW{wk_id}&lwb=0&upb=500&tb=ab"
)

DUTCH_MONTHS = {
    "jan": 1, "feb": 2, "mrt": 3, "apr": 4, "mei": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "okt": 10, "nov": 11, "dec": 12,
}


def parse_period(period_str: str) -> tuple[date, date] | None:
    """Parse '16-22 feb' or '28 jan - 3 feb' into (date_from, date_to)."""
    period_str = period_str.replace("\xa0", " ").replace("&nbsp;", " ")
    period_str = period_str.strip().lower()

    # Pattern: "28 jan - 3 feb" (cross-month)
    m = re.match(
        r"(\d{1,2})\s+(\w+)\s*-\s*(\d{1,2})\s+(\w+)", period_str
    )
    if m:
        day_from, mon_from, day_to, mon_to = m.groups()
        month_from = DUTCH_MONTHS.get(mon_from)
        month_to = DUTCH_MONTHS.get(mon_to)
        if month_from and month_to:
            year = date.today().year
            return (
                date(year, month_from, int(day_from)),
                date(year, month_to, int(day_to)),
            )

    # Pattern: "16-22 feb" (same month)
    m = re.match(r"(\d{1,2})-(\d{1,2})\s+(\w+)", period_str)
    if m:
        day_from, day_to, mon = m.groups()
        month = DUTCH_MONTHS.get(mon)
        if month:
            year = date.today().year
            return (
                date(year, month, int(day_from)),
                date(year, month, int(day_to)),
            )

    return None


def fetch_voordeelmuis(wk_id: int) -> list[dict]:
    url = VOORDEELMUIS_URL.format(wk_id=wk_id)
    resp = requests.get(url)
    resp.raise_for_status()
    all_entries = resp.json().get("data", [])
    today = date.today()
    active = []
    for entry in all_entries:
        period = entry.get("period", "")
        parsed = parse_period(period)
        if parsed and parsed[0] <= today <= parsed[1] and is_food_entry(entry):
            active.append(entry)
    return active


FOOD_KEYWORDS = {
    # beverages
    "koffie", "koffiebonen", "koffiecups", "koffiepads", "oploskoffie",
    "thee", "bier", "wijn", "frisdrank", "limonade", "siroop", "sap",
    "water", "melk", "chocolademelk", "energiedrank", "cider", "smoothie",
    # dairy
    "kaas", "yoghurt", "boter", "room", "kwark", "vla", "dessert",
    "roomkaas", "cottage", "mozzarella", "brie", "camembert", "cheddar",
    "gouda", "edam", "stilton",
    # meat & fish
    "vlees", "vis", "kip", "varken", "rundvlees", "gehakt", "worst",
    "ham", "spek", "zalm", "haring", "garnalen", "tonijn", "kabeljauw",
    "kipfilet", "tartaar", "rookworst", "salami",
    # produce
    "groenten", "fruit", "appel", "appels", "peer", "tomaat", "tomaten",
    "komkommer", "paprika", "ui", "aardappel", "banaan", "sinaasappel",
    "citroen", "aardbei", "druif", "mandarijn", "mandarijnen", "knoflook",
    "sla", "spinazie", "broccoli", "wortel", "champignon", "champignons",
    "shi-takes", "kastanjechampignons", "courgette", "aubergine", "asperge",
    "prei", "bloemkool", "spruitjes", "biet", "witlof", "peren",
    # pantry
    "pasta", "rijst", "brood", "meel", "suiker", "zout", "saus", "soep",
    "olie", "azijn", "mayonaise", "ketchup", "mosterd", "jam", "honing",
    "pindakaas", "appelstroop", "chips", "koekjes", "crackers", "popcorn",
    "noten", "pinda", "walnoot", "amandel", "cashew",
    # sweets & snacks
    "chocolade", "snoep", "drop", "lollipop", "bonbon", "praline",
    "stroopwafel", "speculaas", "pepernoot", "marshmallow",
    # frozen & ready
    "diepvries", "pizza", "maaltijd", "lasagne", "patat", "frites",
    "ijs", "sorbet",
    # bakery
    "croissant", "cake", "taart", "muffin", "bagel", "wrap", "pita",
    "beschuit", "ontbijtkoek", "poffertjes",
    # eggs & breakfast
    "eieren", "scharreleieren", "havermout", "granola", "muesli",
    "cornflakes", "ontbijt",
    # condiments & ingredients
    "kruiden", "peper", "oregano", "basilicum", "peterselie", "dille",
    "gember", "kurkuma", "kaneel", "vanille", "cacao",
    # food indicators
    "bio", "organic", "koeling", "nutri", "recept", "vegetarisch",
    "vegan", "glutenvrij", "lactosevrij", "limonadesiroop",
    "doritos", "lays", "pringles", "hero", "teisseire",
}


def is_food_entry(entry: dict) -> bool:
    kw_set = {k.lower() for k in entry.get("kw", [])}
    return bool(kw_set & FOOD_KEYWORDS)


def get_image_urls(deal_entries: list[dict]) -> list[str]:
    urls = []
    for entry in deal_entries:
        entry_id = entry["id"]
        folder = entry_id // 1000
        urls.append(
            f"https://www.voordeelmuis.nl/img/jpg240/{folder}/{entry_id}.jpg"
        )
    return urls


# --- PDF building ---


def build_pdf_from_images(image_urls: list[str]) -> bytes:
    images = []
    for url in tqdm(image_urls, desc="Downloading images", unit="img"):
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



def run_pipeline(store_name: str, config: tuple):
    wk_id, display_name = config

    print(f"[{store_name}] Fetching deals from voordeelmuis.nl (wk_id={wk_id})")
    deal_entries = fetch_voordeelmuis(wk_id)
    print(f"[{store_name}] Found {len(deal_entries)} deal entries")

    periods = [e.get("period", "") for e in deal_entries if e.get("period")]
    most_common_period = Counter(periods).most_common(1)[0][0] if periods else ""
    parsed = parse_period(most_common_period)
    van = parsed[0].isoformat() if parsed else ""
    tot = parsed[1].isoformat() if parsed else ""

    output_path = join(OUTPUT_DIR, f"{store_name}.json")
    if os.path.exists(output_path):
        with open(output_path) as f:
            existing = json.load(f)
        if existing.get("van") == van and existing.get("tot") == tot:
            print(f"[{store_name}] Cache hit (period {van}–{tot}), skipping OCR")
            return

    image_urls = get_image_urls(deal_entries)
    print(f"[{store_name}] Building PDF from {len(image_urls)} images...")
    pdf_bytes = build_pdf_from_images(image_urls)

    print(f"[{store_name}] Running OCR...")
    deals = ocr_to_deals(pdf_bytes, store_name)

    week = date.today().isocalendar().week

    output = {
        "winkel": store_name,
        "winkel_naam": display_name,
        "week": week,
        "van": van,
        "tot": tot,
        "producten": [p.model_dump() for p in deals.producten],
    }
    with open(output_path, "w") as f:
        json.dump(output, f, ensure_ascii=False)

    print(f"[{store_name}] Wrote {len(deals.producten)} products to {output_path}")


def run_all():
    with ThreadPoolExecutor() as executor:
        futures = {
            executor.submit(run_pipeline, store_name, config): store_name
            for store_name, config in STORES.items()
        }
        for future in as_completed(futures):
            store_name = futures[future]
            try:
                future.result()
            except Exception as e:
                print(f"[{store_name}] Error: {e}")
