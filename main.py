import os
import random
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import httpx

app = FastAPI(title="HotPuppy - AI Puppy Image Generator")

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Puppy-related prompts for variety
PUPPY_PROMPTS = [
    "a cute golden retriever puppy playing in a sunny garden",
    "an adorable husky puppy with blue eyes in the snow",
    "a playful corgi puppy running on the beach",
    "a tiny chihuahua puppy wearing a sweater",
    "a fluffy samoyed puppy smiling at the camera",
    "a beagle puppy with big brown eyes",
    "a dalmatian puppy with spots playing with a ball",
    "a german shepherd puppy looking curious",
    "a pug puppy with a wrinkly face",
    "a border collie puppy herding sheep",
]


async def generate_puppy_image():
    """
    Generate a puppy image using AI.
    This uses placeholder images for now - configure with your preferred AI service.
    Options: OpenAI DALL-E, Stability AI, or other image generation APIs.
    """

    # Get API key from environment (if configured)
    openai_api_key = os.getenv("OPENAI_API_KEY")

    if openai_api_key:
        # Use OpenAI DALL-E API
        try:
            async with httpx.AsyncClient() as client:
                prompt = random.choice(PUPPY_PROMPTS)
                response = await client.post(
                    "https://api.openai.com/v1/images/generations",
                    headers={
                        "Authorization": f"Bearer {openai_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "dall-e-3",
                        "prompt": prompt,
                        "n": 1,
                        "size": "1024x1024"
                    },
                    timeout=30.0
                )

                if response.status_code == 200:
                    data = response.json()
                    return {
                        "image_url": data["data"][0]["url"],
                        "prompt": prompt,
                        "source": "DALL-E 3"
                    }
        except Exception as e:
            print(f"Error generating image with DALL-E: {e}")

    # Fallback to placeholder puppy images
    puppy_id = random.randint(1, 100)
    return {
        "image_url": f"https://placedog.net/800/600?id={puppy_id}",
        "prompt": "Random adorable puppy",
        "source": "Placeholder Service (Configure OPENAI_API_KEY for AI generation)"
    }


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Main page - generates a new puppy image on each visit"""
    image_data = await generate_puppy_image()

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "image_url": image_data["image_url"],
            "prompt": image_data["prompt"],
            "source": image_data["source"]
        }
    )


@app.get("/health")
async def health():
    """Health check endpoint for AWS App Runner"""
    return {"status": "healthy", "service": "hotpuppy"}


@app.get("/api/new-puppy")
async def new_puppy():
    """API endpoint to get a new puppy image"""
    image_data = await generate_puppy_image()
    return image_data
