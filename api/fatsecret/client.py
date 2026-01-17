from typing import Optional
        
import aiohttp
from datetime import datetime, timezone, timedelta

from .models import TokenData, FoodSearchResponse, Food
from .constants import FATSECRET_TOKEN_URL, FATSECRET_API_URL
from .save_system import SaveSystem


class FatSecretClient:
    
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        save_path: Optional[str] = None
    ) -> None:
        self.save_id = f"{self.__class__.__name__}"
        self.save_system = SaveSystem(save_path) if save_path else None
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
        self._load_token_data()

    async def get_food_data(
        self,
        food_name: str,
        max_results: int = 1
    ) -> list[Food]:
        if not self._validate_token():
            success = await self._update_access_token()
            if not success:
                return []
        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {self.access_token.access_token}"
            }
            params = {
                "search_expression": food_name,
                "max_results": max_results,
                "format": "json"
            }
            try:
                async with session.get(
                    FATSECRET_API_URL + "/foods/search/v1",
                    headers=headers,
                    params=params
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        food_response = FoodSearchResponse.model_validate(result)
                        if isinstance(food_response.foods.food, list):
                            return food_response.foods.food
                        else:
                            return [food_response.foods.food]
                    else:
                        print(f"Failed to get food data: {response.status}")
                        return []
            except Exception as e:
                print(f"Error requesting food data: {str(e)}")
                return []

    async def _update_access_token(self) -> bool:
        token_data = await self._request_access_token()
        if token_data:
            self.access_token = token_data
            self._save_token_data()
            return True
        return False
    
    def _validate_token(self) -> bool:
        if not self.access_token:
            return False
        expiration_time = self.access_token.created_at + timedelta(seconds=self.access_token.expires_in)
        return datetime.now(timezone.utc) < expiration_time

    async def _request_access_token(self) -> Optional[TokenData]:
        async with aiohttp.ClientSession() as session:
            data = {
                "grant_type": "client_credentials",
                "scope": "basic"
            }
            try:
                async with session.post(
                    FATSECRET_TOKEN_URL,
                    data=data,
                    auth=aiohttp.BasicAuth(self.client_id, self.client_secret)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return TokenData.model_validate(result)
                    else:
                        print(f"Failed to get access token: {response.status}")
                        return None
            except Exception as e:
                print(f"Error requesting access token: {str(e)}")
                return None
            
    def _load_token_data(self) -> None:
        if not self.save_system:
            return
        data = self.save_system.load(self.save_id)
        if data:
            try:
                self.access_token = TokenData.model_validate(data)
            except Exception as e:
                print(f"Error loading token data: {str(e)}")

    def _save_token_data(self) -> None:
        if not self.save_system or not self.access_token:
            return
        self.save_system.save(self.save_id, self.access_token.model_dump(mode='json'))
        