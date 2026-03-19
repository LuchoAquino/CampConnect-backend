import uuid
import urllib.parse
import urllib.request
import json
from app.db.client import supabase
from app.config import settings

def generate_and_upload_poster(title: str, category: str, date_str: str, location: str, description: str = "") -> str | None:
    # 1. Reliable Fallback (Randomized Stock Image)
    seed_val = uuid.uuid4().int % 10000
    fallback_url = f"https://loremflickr.com/800/600/{category},group,activity?lock={seed_val}"
    
    # 2. Check if Cloudflare credentials exist
    if not settings.CLOUDFLARE_ACCOUNT_ID or not settings.CLOUDFLARE_API_TOKEN:
        print("Cloudflare credentials missing, using fallback.")
        return fallback_url

    try:
        # 3. Preparation for Cloudflare Workers AI
        cf_url = f"https://api.cloudflare.com/client/v4/accounts/{settings.CLOUDFLARE_ACCOUNT_ID}/ai/run/@cf/stabilityai/stable-diffusion-xl-base-1.0"
        
        date_formatted = date_str[:16].replace('T', ' ')
        
        # RESTORING USER'S DETAILED PROMPT
        prompt = f"""A professional, modern event poster with a clean layout and vibrant design.
The poster is composed of two main sections separated by a dynamic diagonal line.

Top Section: Contains a high-resolution, wide-angle photograph of {category} related activity. The lighting in the photo should be dramatic and engaging.

Bottom Section (Solid Dark Background):
- An elegant, neon blue title "{title.upper()}" in a large, modern sans-serif font.
- Above the title, a small, subtle text box with "{category.upper()}" in all caps.
- Below the title, a descriptive text block: "{description[:100]}..."
- Further down, a stacked row of key event details with clear, stylized icons:
  - Calendar Icon: "{date_formatted}"
  - Map Pin Icon: "{location.upper()}"

- Additional graphics:
  - On the left side, slightly overlapping the photo and text section, a modern dynamic illustration of a person related to {category}.
  - A subtle logo placeholder is in the lower center, and possibly other small supporting graphics.
The overall design is sophisticated, with clear visual hierarchy and a strong contrast between the dark background and bright text/graphics."""

        headers = {
            "Authorization": f"Bearer {settings.CLOUDFLARE_API_TOKEN}",
            "Content-Type": "application/json"
        }
        
        body = json.dumps({"prompt": prompt})
        
        # 4. Request image generation via POST (No character limit issues here)
        req = urllib.request.Request(cf_url, data=body.encode('utf-8'), headers=headers, method="POST")
        
        with urllib.request.urlopen(req, timeout=20) as response:
            image_data = response.read()

        # 5. Upload to Supabase Storage
        filename = f"cf_ai_{uuid.uuid4().hex}.png"
        supabase.storage.from_("event-posters").upload(
            filename,
            image_data,
            {"content-type": "image/png"}
        )
        
        # 6. Retrieve Public URL
        url_res = supabase.storage.from_("event-posters").get_public_url(filename)
        return url_res
        
    except Exception as e:
        print(f"Cloudflare AI Generation failed: {e}")
        return fallback_url
