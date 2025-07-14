from loguru import logger

from candybowl import amazon


def search_product(name: str) -> str:
    """Searches the marketplace for a product by name and returns a JSON string of the results.

    Args:
        name: The name of the product to search for.

    Returns:
        A JSON string representation of the search results. The fields for each item are as follows:
            - id: Unique identifier for the item in the marketplace.
            - name: The name of the item.
            - description: A description of the item.
            - price_usd: The price of the item in USD.
            - url: A link to the item in the marketplace.
            - rating: The average rating of the item based on user reviews.
        In the event of an error, returns an error message.
    """
    logger.info(f"Searching for product: {name}")

    try:
        items = amazon.search_product(name, limit=5)
        results_json = {"results": [item.to_dict() for item in items]}

        logger.info(f"Search results: {results_json}")
        return str(results_json)

    except Exception as ex:
        logger.error(f"Error searching for product: {ex}")
        return f"Error: {ex}"
