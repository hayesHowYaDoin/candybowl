from __future__ import annotations
from dataclasses import dataclass
import os
import requests

from loguru import logger


@dataclass(frozen=True, kw_only=True)
class Item:
    id: str
    name: str
    description: str
    price_usd: float
    url: str
    rating: float

    @staticmethod
    def from_canopy(item: dict) -> Item:
        return Item(
            id=item["asin"],
            name=item["title"],
            description=item["optimizedDescription"],
            price_usd=item["price"]["value"],
            url=item["url"],
            rating=item["rating"],
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "price_usd": self.price_usd,
            "url": self.url,
            "rating": self.rating,
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
