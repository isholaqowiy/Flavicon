import os
import aiohttp
from config import TEMP_DIR

def ensure_temp_directory():
    if not os.path.exists(TEMP_DIR):
        os.makedirs(TEMP_DIR)

def clean_user_files(user_id: int):
    if not os.path.exists(TEMP_DIR):
        return
    for filename in os.listdir(TEMP_DIR):
        if filename.startswith(f"fav_{user_id}_"):
            try:
                os.remove(os.path.join(TEMP_DIR, filename))
            except Exception:
                pass

async def download_file(url: str, dest_path: str) -> bool:
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(url, timeout=10) as response:
                if response.status == 200:
                    with open(dest_path, 'wb') as f:
                        f.write(await response.read())
                    return True
    except Exception:
        pass
    return False

