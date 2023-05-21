import dbm
import json
import time
from typing import Dict, Optional


class UELocationCache:

    _CACHE_NAME = "UE_Postcodes"
    _CACHE_EXPIRY_SECONDS = 604800  # 7 days

    @classmethod
    def getCacheLocation(cls, postcode: str) -> Optional[Dict]:
        with dbm.open(cls._CACHE_NAME, "c") as db:
            locationData = db.get(postcode)
            if not locationData:
                return None

            locationData = json.loads(locationData)
            createdDate = locationData.pop("create_date")

            if createdDate < time.time() - cls._CACHE_EXPIRY_SECONDS:
                del db[postcode]
                return None

            return locationData

    @classmethod
    def setCacheLocation(cls, postcode: str, location: Dict):
        with dbm.open(cls._CACHE_NAME, "c") as db:
            location["create_date"] = time.time()

            db[postcode] = json.dumps(location)
