from PIL import Image, ExifTags
from typing import Dict, Any

def extract_exif(image: Image.Image) -> Dict[str, Any]:
    exif_data = {}
    try:
        raw = image.getexif()
        if not raw:
            return {"present": False, "fields": {}, "note": "No EXIF metadata found."}

        for tag_id, value in raw.items():
            tag = ExifTags.TAGS.get(tag_id, str(tag_id))
            # keep only a few safe fields (avoid dumping everything)
            if tag in ["Make", "Model", "Software", "DateTimeOriginal", "DateTime", "Artist"]:
                exif_data[tag] = str(value)

        present = True
        note = "EXIF present." if exif_data else "EXIF present but no common camera fields."
        return {"present": present, "fields": exif_data, "note": note}

    except Exception as e:
        return {"present": False, "fields": {}, "note": f"EXIF read error: {e}"}
