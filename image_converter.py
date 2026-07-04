import os
from PIL import Image

def process_and_convert_icon(input_path: str, output_path: str, fmt: str, size: tuple = None) -> bool:
    """Preserves image transparency and handles cross-format conversion layers (ICO, PNG, WEBP, JPEG)."""
    try:
        with Image.open(input_path) as img:
            # Preserve alpha channels transparency context rules mapping layout
            if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
                if fmt.upper() in ('JPEG', 'JPG'):
                    # Flatten transparency matrix layers onto a clean solid white backdrop
                    canvas = Image.new('RGB', img.size, (255, 255, 255))
                    canvas.paste(img, mask=img.split()[3])
                    img = canvas
                else:
                    img = img.convert('RGBA')
            else:
                if fmt.upper() not in ('JPEG', 'JPG'):
                    img = img.convert('RGBA')
                else:
                    img = img.convert('RGB')
                    
            if size:
                img = img.resize(size, Image.Resampling.LANCZOS)
                
            save_fmt = 'JPEG' if fmt.upper() == 'JPG' else fmt.upper()
            img.save(output_path, format=save_fmt, quality=100)
            return True
    except Exception:
        return False

