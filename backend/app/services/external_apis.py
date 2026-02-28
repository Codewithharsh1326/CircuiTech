import httpx
from app.core.config import settings

# ---------------------------------------------------------------------------
# DigiKey API Integration
# ---------------------------------------------------------------------------
_digikey_token: str | None = None

async def _get_digikey_token() -> str:
    global _digikey_token
    if _digikey_token:
        # In a production app, you'd check token expiry here. 
        # For this prototype, we'll cache it for the life of the server or refetch on 401.
        return _digikey_token

    url = "https://api.digikey.com/v1/oauth2/token"
    payload = {
        "client_id": settings.digikey_client_id,
        "client_secret": settings.digikey_client_secret,
        "grant_type": "client_credentials"
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, data=payload)
        response.raise_for_status()
        data = response.json()
        _digikey_token = data.get("access_token")
        return _digikey_token

async def search_digikey(keywords: str) -> list[dict]:
    """Search DigiKey for components and return a simplified part list."""
    token = await _get_digikey_token()
    
    url = "https://api.digikey.com/Search/v3/Products/Keyword"
    headers = {
        "Authorization": f"Bearer {token}",
        "X-DIGIKEY-Client-Id": settings.digikey_client_id,
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    
    payload = {
        "Keywords": keywords,
        "RecordCount": 3,
        "RecordStartPosition": 0,
        "Sort": {
            "SortOption": "SortByPrice",
            "Direction": "Ascending"
        },
        "FilterOptionsRequest": {
            "SearchOptions": ["InStock"]
        }
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=payload)
        
        # Simple token refresh logic if it expired
        if response.status_code == 401:
            global _digikey_token
            _digikey_token = None
            token = await _get_digikey_token()
            headers["Authorization"] = f"Bearer {token}"
            response = await client.post(url, headers=headers, json=payload)

        response.raise_for_status()
        data = response.json()

        results = []
        for product in data.get("Products", []):
            cost = 0.0
            pricing = product.get("StandardPricing", [])
            if pricing:
                cost = pricing[0].get("UnitPrice", 0.0)

            results.append({
                "partNumber": product.get("ManufacturerPartNumber", ""),
                "manufacturer": product.get("Manufacturer", {}).get("Value", ""),
                "description": product.get("ProductDescription", ""),
                "unitPrice": cost
            })
            
        return results

# ---------------------------------------------------------------------------
# Octopart (Nexar) API Integration
# ---------------------------------------------------------------------------
async def search_octopart(mpn: str) -> dict | None:
    """Fetch real-time stock and pricing for an MPN using Nexar GraphQL."""
    url = "https://api.nexar.com/graphql"
    headers = {
        "Authorization": f"Bearer {settings.octopart_api_key}",
        "Content-Type": "application/json"
    }
    
    query = """
    query Search($mpn: String!) {
      supSearch(q: $mpn, limit: 1) {
        results {
          part {
            mpn
            manufacturer {
              name
            }
            shortDescription
            sellers {
              company {
                name
              }
              offers {
                prices {
                  price
                  currency
                }
                inventoryLevel
              }
            }
          }
        }
      }
    }
    """
    
    payload = {
        "query": query,
        "variables": {"mpn": mpn}
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=payload)
        
        if response.status_code != 200:
            return None
            
        data = response.json()
        
        try:
            part = data["data"]["supSearch"]["results"][0]["part"]
            
            # Find the best price (first available USD price in stock)
            best_price = 0.0
            for seller in part.get("sellers", []):
                for offer in seller.get("offers", []):
                    if offer.get("inventoryLevel", 0) > 0:
                        prices = offer.get("prices", [])
                        if prices and prices[0].get("currency") == "USD":
                            best_price = prices[0].get("price", 0.0)
                            break
                if best_price > 0:
                    break

            return {
                "partNumber": part.get("mpn", ""),
                "manufacturer": part.get("manufacturer", {}).get("name", ""),
                "description": part.get("shortDescription", ""),
                "unitPrice": best_price
            }
        except (KeyError, IndexError):
            return None
