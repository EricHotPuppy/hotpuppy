# HotPuppy 🐾

An evolving, collaborative AI art experience where each visitor contributes to the transformation of a single, continuously morphing image.

## Concept

HotPuppy starts with one AI-generated "HOT" puppy seed image - a cool, stylish pup with attitude! Each visitor can add their own creative twist, evolving the image based on:
- **50% of the current image** - Maintains core character
- **50% of the visitor's input** - Dramatic, visible transformations

Watch the image evolve from a hot puppy into something completely unexpected through collective creativity!

## Features

- 🎨 **AI-Powered Evolution** - DALL-E 3 integration for image generation
- 🔄 **Continuous Morphing** - Each contribution builds on the last
- 📚 **Complete Archive** - Carousel view of the entire evolution history
- 💾 **SQLite Database** - Persistent storage of all evolutions
- 🎯 **Simple Interface** - Just type and evolve
- 🐛 **Debug Mode** - Comprehensive logging for easy troubleshooting
- ⚡ **Health Monitoring** - Built-in health checks for AWS App Runner

## How It Works

1. **First Visit** → See the current evolved image
2. **Add Your Twist** → Enter text in the input box (e.g., "add a sunset" or "make it cyberpunk")
3. **Evolution Happens** → AI generates a new image combining current (70%) + your input (30%)
4. **View History** → Click "Archive" to see all evolutions in a beautiful carousel

## Technology Stack

- **Backend**: Python 3 + FastAPI
- **Frontend**: HTML, CSS, JavaScript (vanilla)
- **Database**: SQLite3
- **AI**: OpenAI DALL-E 3
- **Deployment**: AWS App Runner
- **Domain**: hotpuppy.net

## Local Development

### Prerequisites

- Python 3.8+
- OpenAI API key (optional for development)

### Setup

1. **Navigate to project**:
```bash
cd /home/user/hotpuppy
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **(Optional) Configure OpenAI API key**:
```bash
export OPENAI_API_KEY="sk-your-key-here"
export SESSION_SECRET="your-random-secret"
export DEBUG="true"  # Enable debug logging
```

4. **Run the server**:
```bash
uvicorn main:app --reload
```

5. **Open browser**:
```
http://localhost:8000
```

### Without OpenAI API Key

The app works without an API key using placeholder puppy images. Perfect for development and testing!

## Project Structure

```
hotpuppy/
├── main.py                # FastAPI app with evolution logic
├── database.py            # SQLite database operations
├── templates/
│   ├── index.html        # Main evolution page
│   └── archive.html      # Archive carousel
├── static/               # Static files (empty for now)
├── requirements.txt      # Python dependencies
├── apprunner.yaml       # AWS App Runner config
├── DEPLOYMENT.md        # Detailed deployment guide
├── README.md            # This file
└── .gitignore          # Git ignore rules
```

## Deployment to AWS App Runner

See [DEPLOYMENT.md](DEPLOYMENT.md) for complete step-by-step instructions including:
- Creating the App Runner service
- Configuring environment variables
- Setting up custom domain (hotpuppy.net)
- DNS configuration with Route53

### Quick Deploy Steps

1. **Push to GitHub**
2. **Create App Runner service** pointing to your repo
3. **Set environment variables**:
   - `OPENAI_API_KEY` - Your OpenAI key
   - `SESSION_SECRET` - Random secret for sessions
   - `DEBUG` - Set to "true" for detailed logs
4. **Configure domain** via Route53
5. **Done!** Visit hotpuppy.net

## API Endpoints

- `GET /` - Main evolution page
- `POST /evolve` - Evolve the image (form: `user_input`)
- `GET /archive` - Archive carousel page
- `GET /api/current` - JSON: Current image data
- `GET /api/archive` - JSON: All images
- `GET /health` - Health check (includes evolution count)

## Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `OPENAI_API_KEY` | OpenAI API key for DALL-E 3 | None | No* |
| `SESSION_SECRET` | Secret for session cookies | Auto-generated | No** |
| `DEBUG` | Enable debug logging | `false` | No |

\* Without API key, uses placeholder images
\** Should be set in production for security

### Debug Mode

Enable detailed logging:
```bash
export DEBUG="true"
uvicorn main:app --reload
```

Features:
- 🔍 Request/response logging
- 📊 Database operation tracking
- 🎨 AI generation details
- ❌ Full error tracebacks

## Database Schema

```sql
CREATE TABLE images (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    image_url TEXT NOT NULL,
    prompt TEXT NOT NULL,
    user_input TEXT,
    is_seed BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

## Evolution Algorithm

The evolution prompt combines current and new concepts:

```python
evolved_prompt = f"""
Building upon this concept: {current_prompt}.
Now evolving with this addition: {user_input}.
Maintain 70% of the original style and subject,
while incorporating 30% of the new idea.
Keep the same artistic style and overall composition.
"""
```

**Note**: DALL-E 3 doesn't support true img2img with weight control. For better results, consider:
- Stability AI (Stable Diffusion with `init_image` + `strength`)
- Replicate API (various img2img models)

The implementation in `main.py` includes placeholders for alternative backends.

## Cost Considerations

### Development (Placeholder Images)
- **Free** - No API costs

### Production (with DALL-E)
- **AWS App Runner**: ~$5-10/month (1 vCPU, 2GB RAM, low traffic)
- **Route53**: ~$0.50/month (hosted zone)
- **DALL-E 3**: $0.04 per image generation
- **Example**: 100 evolutions/month = $4 + $5-10 + $0.50 ≈ **$10-15/month**

### Cost Optimization
- Use `quality: "standard"` instead of `"hd"` ($0.08)
- Consider rate limiting to prevent abuse
- Cache API responses if needed

## Archive Carousel Features

- ⬅️ ➡️ **Arrow Navigation** - Click or keyboard
- 📅 **Timestamps** - See when each evolution happened
- 💬 **User Inputs** - View what text created each evolution
- 🌱 **Seed Badge** - Identifies the original image
- 📱 **Responsive** - Works on all devices

## Error Handling

Comprehensive error handling with:
- Input validation
- API timeout handling (60s)
- Network error recovery
- Database error logging
- User-friendly error messages
- Full traceback logging (debug mode)

## Security

- Session middleware for user tracking
- Input sanitization
- SQL injection protection (parameterized queries)
- Environment variable secrets
- HTTPS enforced by App Runner
- Rate limiting recommended for production

## Future Enhancements

Possible improvements:
- [ ] User authentication
- [ ] Voting system for evolutions
- [ ] Branch evolutions (multiple paths)
- [ ] Image download feature
- [ ] Social sharing
- [ ] Better img2img with Stable Diffusion
- [ ] Custom model fine-tuning
- [ ] Animation of evolution sequence

## Troubleshooting

### "No seed image found"
- Wait 30-60s for seed generation
- Check logs for OpenAI API errors
- Verify `OPENAI_API_KEY` if set

### Images not generating
- Check `DEBUG=true` logs
- Verify OpenAI API key validity
- Check OpenAI account credits
- Review error messages in logs

### Archive page empty
- Database not initialized
- Check file permissions for `hotpuppy.db`
- Review startup logs

### Database errors
- Ensure write permissions in app directory
- Check disk space
- Review database.py error logs

## Development Tips

1. **Start without API key** - Use placeholders first
2. **Enable debug mode** - `DEBUG=true` shows everything
3. **Check health endpoint** - `/health` shows system status
4. **Use API endpoints** - Test with `/api/current` and `/api/archive`
5. **Monitor logs** - Watch for 🎨 and ❌ emojis in output

## Contributing

Ideas for contributions:
- Alternative AI backends (Stable Diffusion, Midjourney)
- Better evolution algorithms
- UI/UX improvements
- Mobile app
- Additional archive views

## License

MIT License - Feel free to use and modify!

## Support

- **Issues**: Open an issue on GitHub
- **Logs**: Check with `DEBUG=true`
- **Health**: Visit `/health` endpoint

---

**Made with ❤️ and AI** - Watch creativity evolve, one input at a time.
