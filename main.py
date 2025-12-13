import os
import base64
import logging
import traceback
from datetime import datetime
from typing import Optional
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
import httpx

from database import init_db, add_image, get_latest_image, get_all_images, get_image_count

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Debug mode from environment
DEBUG_MODE = os.getenv("DEBUG", "false").lower() == "true"
if DEBUG_MODE:
    logger.setLevel(logging.DEBUG)
    logger.info("🐛 Debug mode enabled")

app = FastAPI(title="HotPuppy - Evolving AI Art")

# Add session middleware for tracking first-time users
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SESSION_SECRET", "hotpuppy-secret-key-change-in-production"))

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    try:
        logger.info("🚀 Starting HotPuppy application...")
        init_db()
        logger.info("✅ Database initialized")

        # Create seed image if database is empty
        count = get_image_count()
        logger.info(f"📊 Current image count: {count}")

        if count == 0:
            logger.info("🌱 No seed image found, creating one...")
            await create_seed_image()
        else:
            logger.info(f"✅ Seed image exists, ready to serve")

    except Exception as e:
        logger.error(f"❌ Startup error: {e}")
        logger.error(traceback.format_exc())
        raise


async def create_seed_image():
    """Create the initial 'hotpuppy' seed image"""
    seed_prompt = "a hot puppy - a stylish, cool, fashionable puppy wearing sunglasses, vibrant and eye-catching, digital art"

    openai_api_key = os.getenv("OPENAI_API_KEY")

    if openai_api_key:
        logger.info("🎨 Attempting to generate seed image with DALL-E...")
        try:
            async with httpx.AsyncClient() as client:
                logger.debug(f"📤 Sending request to OpenAI API")
                response = await client.post(
                    "https://api.openai.com/v1/images/generations",
                    headers={
                        "Authorization": f"Bearer {openai_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "dall-e-3",
                        "prompt": seed_prompt,
                        "n": 1,
                        "size": "1024x1024",
                        "quality": "standard"
                    },
                    timeout=60.0
                )

                logger.debug(f"📥 Response status: {response.status_code}")

                if response.status_code == 200:
                    data = response.json()
                    image_url = data["data"][0]["url"]
                    add_image(image_url, seed_prompt, user_input=None, is_seed=True)
                    logger.info(f"✅ Seed image created successfully via DALL-E")
                    return
                else:
                    error_data = response.text
                    logger.error(f"❌ OpenAI API error {response.status_code}: {error_data}")

        except httpx.TimeoutException as e:
            logger.error(f"⏱️ Timeout error generating seed image: {e}")
        except httpx.RequestError as e:
            logger.error(f"🌐 Network error generating seed image: {e}")
        except Exception as e:
            logger.error(f"❌ Unexpected error generating seed image: {e}")
            logger.error(traceback.format_exc())
    else:
        logger.warning("⚠️ OPENAI_API_KEY not configured")

    # Fallback placeholder
    placeholder_url = "https://placedog.net/1024/1024?id=1"
    add_image(placeholder_url, seed_prompt, user_input=None, is_seed=True)
    logger.info(f"⚠️ Using placeholder for seed image")


async def evolve_image(current_image_url: str, current_prompt: str, user_input: str):
    """
    Evolve the image based on current image (70%) + user input (30%)

    Since DALL-E 3 doesn't support img2img directly, we'll use a clever prompt
    that describes the current image and incorporates the new input.

    For true img2img with weight control, consider:
    - Stability AI (init_image + strength parameter)
    - Replicate (various models with img2img)
    """

    logger.info(f"🔄 Evolving image with user input: '{user_input}'")

    # Create evolved prompt: describe current + add new input
    evolved_prompt = f"Building upon this concept: {current_prompt}. Now evolving with this addition: {user_input}. Maintain 70% of the original style and subject, while incorporating 30% of the new idea. Keep the same artistic style and overall composition."

    logger.debug(f"📝 Evolved prompt: {evolved_prompt}")

    openai_api_key = os.getenv("OPENAI_API_KEY")

    if openai_api_key:
        logger.info("🎨 Generating evolved image with DALL-E...")
        try:
            async with httpx.AsyncClient() as client:
                logger.debug(f"📤 Sending evolution request to OpenAI API")
                response = await client.post(
                    "https://api.openai.com/v1/images/generations",
                    headers={
                        "Authorization": f"Bearer {openai_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "dall-e-3",
                        "prompt": evolved_prompt,
                        "n": 1,
                        "size": "1024x1024",
                        "quality": "standard"
                    },
                    timeout=60.0
                )

                logger.debug(f"📥 Evolution response status: {response.status_code}")

                if response.status_code == 200:
                    data = response.json()
                    logger.info("✅ Image evolved successfully via DALL-E")
                    return {
                        "image_url": data["data"][0]["url"],
                        "prompt": evolved_prompt,
                        "success": True
                    }
                else:
                    error_data = response.text
                    logger.error(f"❌ OpenAI API error {response.status_code}: {error_data}")
                    return {
                        "success": False,
                        "error": f"OpenAI API error {response.status_code}: {error_data[:200]}"
                    }

        except httpx.TimeoutException as e:
            logger.error(f"⏱️ Timeout error evolving image: {e}")
            return {"success": False, "error": "Request timed out (60s). Please try again."}
        except httpx.RequestError as e:
            logger.error(f"🌐 Network error evolving image: {e}")
            return {"success": False, "error": f"Network error: {str(e)}"}
        except Exception as e:
            logger.error(f"❌ Unexpected error evolving image: {e}")
            logger.error(traceback.format_exc())
            return {"success": False, "error": f"Unexpected error: {str(e)}"}
    else:
        logger.warning("⚠️ OPENAI_API_KEY not configured, using placeholder")

    # Fallback: slight variation in placeholder
    image_count = get_image_count()
    placeholder_url = f"https://placedog.net/1024/1024?id={image_count + 1}"
    logger.info(f"⚠️ Using placeholder image for evolution")
    return {
        "image_url": placeholder_url,
        "prompt": evolved_prompt,
        "success": True,
        "fallback": True
    }


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Main page - shows current image with evolution input"""
    try:
        logger.debug("📄 Serving home page")
        # Get current image
        current_image = get_latest_image()

        if current_image:
            logger.debug(f"🖼️ Current image ID: {current_image.get('id')}")
        else:
            logger.warning("⚠️ No current image found")

        # Mark this session as having visited
        request.session["visited"] = True

        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "current_image": current_image,
                "total_images": get_image_count()
            }
        )
    except Exception as e:
        logger.error(f"❌ Error serving home page: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error loading home page: {str(e)}")


@app.post("/evolve")
async def evolve(request: Request, user_input: str = Form(...)):
    """Evolve the current image based on user input"""
    try:
        logger.info(f"🔄 Evolution request received: '{user_input}'")

        # Validate input
        if not user_input or not user_input.strip():
            logger.warning("⚠️ Empty user input")
            return JSONResponse(
                {"success": False, "error": "User input cannot be empty"},
                status_code=400
            )

        # Get current image
        current = get_latest_image()
        if not current:
            logger.error("❌ No current image found for evolution")
            return JSONResponse(
                {"success": False, "error": "No seed image found. Please wait for initialization."},
                status_code=400
            )

        logger.debug(f"📍 Evolving from image ID: {current.get('id')}")

        # Generate evolved image
        result = await evolve_image(
            current["image_url"],
            current["prompt"],
            user_input.strip()
        )

        if result.get("success"):
            # Save to database
            try:
                image_id = add_image(
                    result["image_url"],
                    result["prompt"],
                    user_input=user_input.strip(),
                    is_seed=False
                )
                logger.info(f"✅ Evolution saved with ID: {image_id}")

                return JSONResponse({
                    "success": True,
                    "image_id": image_id,
                    "image_url": result["image_url"],
                    "user_input": user_input.strip(),
                    "fallback": result.get("fallback", False)
                })
            except Exception as db_error:
                logger.error(f"❌ Database error saving evolution: {db_error}")
                logger.error(traceback.format_exc())
                return JSONResponse({
                    "success": False,
                    "error": f"Database error: {str(db_error)}"
                }, status_code=500)
        else:
            error_msg = result.get("error", "Unknown error")
            logger.error(f"❌ Evolution failed: {error_msg}")
            return JSONResponse({
                "success": False,
                "error": error_msg
            }, status_code=500)

    except Exception as e:
        logger.error(f"❌ Unexpected error in /evolve endpoint: {e}")
        logger.error(traceback.format_exc())
        return JSONResponse({
            "success": False,
            "error": f"Server error: {str(e)}"
        }, status_code=500)


@app.get("/archive", response_class=HTMLResponse)
async def archive(request: Request):
    """Archive page showing evolution history"""
    try:
        logger.debug("📚 Serving archive page")
        images = get_all_images()
        logger.debug(f"📊 Retrieved {len(images)} images for archive")

        return templates.TemplateResponse(
            "archive.html",
            {
                "request": request,
                "images": images,
                "total_images": len(images)
            }
        )
    except Exception as e:
        logger.error(f"❌ Error serving archive page: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error loading archive: {str(e)}")


@app.get("/api/current")
async def get_current():
    """API endpoint to get current image"""
    try:
        logger.debug("🔍 API request for current image")
        current = get_latest_image()
        if current:
            logger.debug(f"✅ Returned current image ID: {current.get('id')}")
            return current
        else:
            logger.warning("⚠️ No current image found")
            return {"error": "No images found"}
    except Exception as e:
        logger.error(f"❌ Error in /api/current: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/archive")
async def get_archive():
    """API endpoint to get all images"""
    try:
        logger.debug("🔍 API request for archive")
        images = get_all_images()
        logger.debug(f"✅ Returned {len(images)} images")
        return {"images": images, "total": len(images)}
    except Exception as e:
        logger.error(f"❌ Error in /api/archive: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    """Health check endpoint for AWS App Runner"""
    try:
        count = get_image_count()
        logger.debug(f"💚 Health check - {count} evolutions")
        return {
            "status": "healthy",
            "service": "hotpuppy",
            "total_evolutions": count,
            "debug_mode": DEBUG_MODE
        }
    except Exception as e:
        logger.error(f"❌ Health check failed: {e}")
        return {
            "status": "unhealthy",
            "service": "hotpuppy",
            "error": str(e)
        }
