from __future__ import annotations
from dataclasses import dataclass
import os
import requests
import re

from loguru import logger


def extract_unit_info(title: str, description: str = "") -> UnitInfo:
    """Extract unit information from Amazon product title and description."""
    text = f"{title} {description}".lower()

    # Initialize unit info
    unit_type = ""
    unit_size = ""
    package_count = 0
    selling_unit = ""

    # Extract package count - look for "pack of X", "count of X", "(X)" patterns
    count_patterns = [
        r"pack of (\d+)",
        r"count of (\d+)",
        r"\((\d+)\s*pack\)",
        r"\((\d+)\s*count\)",
        r"\(pack of (\d+)\)",
        r"(\d+)\s*pack",
        r"(\d+)-pack",
        r"(\d+)\s*count",
    ]

    for pattern in count_patterns:
        match = re.search(pattern, text)
        if match:
            package_count = int(match.group(1))
            break

    # Extract unit size - look for weight/volume measurements
    size_patterns = [
        (r"(\d+\.?\d*)\s*(fl oz|fluid ounce|fluid ounces)", "fl oz"),
        (r"(\d+\.?\d*)\s*(oz|ounce|ounces)", "oz"),
        (r"(\d+\.?\d*)\s*(lb|lbs|pound|pounds)", "lb"),
        (r"(\d+\.?\d*)\s*(g|gram|grams)", "g"),
        (r"(\d+\.?\d*)\s*(kg|kilogram|kilograms)", "kg"),
        (r"(\d+\.?\d*)\s*(ml|milliliter|milliliters)", "ml"),
        (r"(\d+\.?\d*)\s*(l|liter|liters)", "l"),
    ]

    for pattern, normalized_unit in size_patterns:
        match = re.search(pattern, text)
        if match:
            unit_size = f"{match.group(1)}{normalized_unit}"
            break

    # Extract unit type - look for container types (order matters - more specific first)
    type_patterns = [
        "pack",
        "packs",
        "bag",
        "bags",
        "box",
        "boxes",
        "bottle",
        "bottles",
        "can",
        "cans",
        "jar",
        "jars",
        "piece",
        "pieces",
        "bar",
        "bars",
        "tube",
        "tubes",
    ]

    # Extract unit type with proper priority handling
    for unit in type_patterns:
        if unit in text:
            unit_type = unit.rstrip("s")  # Remove plural 's'
            break

    # Override with 'pack' only in specific contexts where no other container is the primary item
    if "pack of" in text and not any(
        f"{container}s" in text or f"{container}," in text
        for container in ["can", "bottle", "jar", "bag", "box"]
    ):
        unit_type = "pack"

    # Determine selling unit based on extracted info
    if package_count > 1 and unit_size and unit_type:
        selling_unit = f"individual {unit_size} {unit_type}"
    elif unit_size and unit_type:
        selling_unit = f"one {unit_size} {unit_type}"
    elif unit_type:
        selling_unit = f"one {unit_type}"
    elif package_count > 1:
        selling_unit = "individual piece"
    else:
        selling_unit = "individual item"

    return UnitInfo(
        unit_type=unit_type,
        unit_size=unit_size,
        package_count=package_count,
        selling_unit=selling_unit,
    )


@dataclass(frozen=True, kw_only=True)
class UnitInfo:
    """Extracted unit information from product title/description."""

    unit_type: str = ""  # bag, box, piece, bottle, etc.
    unit_size: str = ""  # 2.17oz, 5lb, individual, etc.
    package_count: int = 0  # number of units in package
    selling_unit: str = ""  # what customer receives


@dataclass(frozen=True, kw_only=True)
class Item:
    id: str
    name: str
    description: str
    price_usd: float
    url: str
    rating: float
    unit_info: UnitInfo

    @staticmethod
    def from_canopy(item: dict) -> Item:
        title = item["title"]
        description = item["optimizedDescription"]
        unit_info = extract_unit_info(title, description)

        return Item(
            id=item["asin"],
            name=title,
            description=description,
            price_usd=item["price"]["value"],
            url=item["url"],
            rating=item["rating"],
            unit_info=unit_info,
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "price_usd": self.price_usd,
            "url": self.url,
            "rating": self.rating,
            "unit_type": self.unit_info.unit_type,
            "unit_size": self.unit_info.unit_size,
            "package_count": self.unit_info.package_count,
            "selling_unit": self.unit_info.selling_unit,
        }


def search_product(keywords: str, limit: int) -> list[Item]:
    # Define the URL of the GraphQL endpoint
    url = "https://graphql.canopyapi.co/"

    # Define the GraphQL query
    query = """
    query amazonProduct($searchTerm: String!, $limit: BigInt!) {
        amazonProductSearchResults(input: {searchTerm: $searchTerm}) {
            productResults(input: {limit: $limit}) {
                results {
                    asin
                    price {
                        value
                        currency
                    }
                    rating
                    title
                    url
                    optimizedDescription
                }
            }
        }
    }
    """

    headers = {
        "Content-Type": "application/json",
        "API-KEY": os.getenv("CANOPY_API_KEY"),
    }

    variables = {
        "searchTerm": keywords,
        "limit": limit,
    }

    # Define the request payload
    payload = {"query": query, "variables": variables}
    logger.debug(f"Payload: {payload}")

    # Send the POST request to the GraphQL endpoint
    response = requests.post(url, json=payload, headers=headers)

    if response.status_code != 200:
        logger.error(
            f"Query failed to run with a {response.status_code} status code."
        )
        logger.error(f"Response: {response.text}")

    data = response.json()
    logger.debug(f"Response data: {data}")

    items = [
        Item.from_canopy(item)
        for item in data["data"]["amazonProductSearchResults"][
            "productResults"
        ]["results"]
    ]

    return items
