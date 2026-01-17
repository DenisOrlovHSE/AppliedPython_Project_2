import aiohttp

from .constants import OFF_API_URL


class OFFClient:

    def __init__(self) -> None:
        self.base_url = OFF_API_URL
        self.base_header = {
            "User-Agent": "MyApp/1.0 (daorlov@edu.hse.ru)"
        }

    async def get_calories_per_100g(
        self,
        product_name: str
    ) -> float | None:
        try:
            endpoint = f"{self.base_url}/cgi/search.pl"
            params = {
                "search_terms": product_name,
                "search_simple": 1,
                "json": 1,
                "fields": "product_name,nutriments"
            }
            async with aiohttp.ClientSession() as session:
                async with session.get(endpoint, params=params, headers=self.base_header) as response:
                    response.raise_for_status()
                    data = await response.json()
                    products = data.get("products", [])
                    if products:
                        first_product = products[0]
                        nutriments = first_product.get("nutriments", {})
                        return nutriments.get("energy-kcal_100g")
            return None
        except Exception as e:
            print(f"Error fetching product data: {e}")
            return None