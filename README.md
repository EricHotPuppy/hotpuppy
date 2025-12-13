# HotPuppy 🐾

An AI-powered puppy image generator that creates a fresh, adorable puppy image every time you visit!

## Features

- 🎨 AI-generated puppy images on every page load
- 🔄 Generate new images without refreshing the page
- 🎲 Random puppy prompts for variety
- 📱 Responsive design that works on all devices
- ⚡ Fast API built with FastAPI
- 🔒 Health check endpoint for AWS App Runner

## Technology Stack

- **Backend**: Python 3 + FastAPI
- **Frontend**: HTML, CSS, JavaScript
- **AI**: OpenAI DALL-E 3 (configurable)
- **Deployment**: AWS App Runner
- **Domain**: hotpuppy.net

## Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. (Optional) Set up AI image generation:
```bash
export OPENAI_API_KEY="your-api-key-here"
```

3. Run the server:
```bash
uvicorn main:app --reload
```

4. Open your browser to `http://localhost:8000`

## Configuration

### AI Image Generation

By default, HotPuppy uses placeholder images. To enable AI generation:

1. **OpenAI DALL-E** (recommended):
   - Get an API key from https://platform.openai.com/
   - Set environment variable: `OPENAI_API_KEY=your-key`
   - The app will automatically use DALL-E 3 for image generation

2. **Alternative AI Services**:
   - Modify `generate_puppy_image()` in `main.py`
   - Options: Stability AI, Midjourney API, Replicate, etc.

## Deployment to AWS App Runner

### Step 1: Create App Runner Service

1. Go to AWS App Runner console
2. Click "Create service"
3. **Source**: Connect to GitHub repository
4. **Repository**: Select your HotPuppy repo
5. **Branch**: main
6. **Build settings**: Use configuration file (`apprunner.yaml`)
7. **Service name**: `hotpuppy-service`
8. Click "Create & deploy"

### Step 2: Configure Environment Variables

1. In App Runner service, go to "Configuration"
2. Add environment variable:
   - Name: `OPENAI_API_KEY`
   - Value: Your OpenAI API key
3. Save and redeploy

### Step 3: Set Up Custom Domain (hotpuppy.net)

1. **In Route53**:
   - Go to your hosted zone for `hotpuppy.net`
   - Note the name servers

2. **In App Runner**:
   - Go to your service → Custom domains
   - Click "Link domain"
   - Enter: `hotpuppy.net` and `www.hotpuppy.net`
   - App Runner will provide validation records

3. **Back in Route53**:
   - Add the validation CNAME records
   - Wait for validation (5-10 minutes)

4. **Add A records** (after validation):
   - Create an ALIAS record for `hotpuppy.net` → App Runner domain
   - Create an ALIAS record for `www.hotpuppy.net` → App Runner domain

### Step 4: Verify

Visit `https://hotpuppy.net` - you should see your site with HTTPS!

## API Endpoints

- `GET /` - Main page (generates new image on each visit)
- `GET /api/new-puppy` - JSON endpoint to fetch a new puppy image
- `GET /health` - Health check endpoint

## Project Structure

```
hotpuppy/
├── main.py                 # FastAPI application
├── templates/
│   └── index.html         # Frontend HTML
├── static/                # Static files (empty for now)
├── requirements.txt       # Python dependencies
├── apprunner.yaml        # AWS App Runner configuration
└── README.md             # This file
```

## Cost Considerations

- **AWS App Runner**: ~$5-10/month for low traffic
- **OpenAI DALL-E 3**: $0.04 per image (standard quality)
- **Route53**: ~$0.50/month for hosted zone

**Tip**: Use placeholder images for development/testing to avoid AI costs!

## License

MIT License - Feel free to use and modify!

## Support

For issues or questions, please open an issue on GitHub.
