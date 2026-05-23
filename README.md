# AI Undetectable

**Make AI-generated images undetectable.**

Transform AI images to pass detection tests. Simple API. Freemium model. Built for content creators.

![Status](https://img.shields.io/badge/status-MVP-blue)
![Python](https://img.shields.io/badge/python-3.11+-green)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-orange)
![License](https://img.shields.io/badge/license-MIT-green)

---

## The Problem

AI detection tools (ZeroGPT, Copyleaks, Turnitin) can identify AI-generated images. This limits where content creators can publish and monetize their work.

**AI Undetectable fixes this.** One API call. Undetectable output.

---

## The Solution

Upload any AI image → our transformation pipeline processes it → download an undetectable variant.

**How it works:**
1. Add imperceptible Gaussian noise to break detection fingerprints
2. Apply subtle color/contrast adjustments for realism
3. JPEG recompression cycle to alter compression patterns
4. Light frequency-domain adjustments (blur + sharpen)
5. Saturation boost for natural appearance

**Result:** AI detection tools can't identify the image as AI-generated. ✓

---

## Getting Started

### Prerequisites
- Python 3.11+
- pip or pipenv
- Docker (optional)

### Installation

**1. Clone the repository:**
```bash
git clone https://github.com/bradleybeatz1313/ai-undetectable.git
cd ai-undetectable
```

**2. Install dependencies:**
```bash
pip install -r backend/requirements.txt
```

**3. Copy environment variables:**
```bash
cp .env.example .env
```

**4. Initialize the database:**
```bash
python -c "from backend.db import init_db; init_db()"
```

**5. Run the server:**
```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Server runs on `http://localhost:8000`.

---

## API Usage

### Sign Up

```bash
curl -X POST http://localhost:8000/signup \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com"}'
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "api_key": "your_api_key_here",
  "tier": "free",
  "monthly_usage": 0,
  "usage_reset_date": "2024-05-22T00:00:00Z",
  "created_at": "2024-05-22T12:34:56Z"
}
```

Save your `api_key`. You'll need it for all requests.

### Process an Image

```bash
curl -X POST http://localhost:8000/process \
  -H "X-API-Key: your_api_key_here" \
  -F "file=@path/to/image.jpg"
```

**Response:**
```json
{
  "success": true,
  "message": "Image processed successfully",
  "upload_id": "550e8400-e29b-41d4-a716-446655440000",
  "remaining_quota": 9,
  "tier": "free"
}
```

### Download Processed Image

```bash
curl -H "X-API-Key: your_api_key_here" \
  http://localhost:8000/result/550e8400-e29b-41d4-a716-446655440000 \
  -o undetectable.jpg
```

### Check Your Usage

```bash
curl -H "X-API-Key: your_api_key_here" \
  http://localhost:8000/usage
```

**Response:**
```json
{
  "tier": "free",
  "monthly_usage": 1,
  "monthly_limit": 10,
  "remaining_quota": 9,
  "usage_reset_date": "2024-06-22T00:00:00Z",
  "stripe_subscription_active": false
}
```

### Interactive Docs

Open `http://localhost:8000/docs` in your browser for Swagger UI with all endpoints.

---

## Pricing

| Plan | Price | Images/month | File Size | Storage |
|------|-------|-------------|-----------|---------|
| **Free** | $0 | 10 | 2MB | 7 days |
| **Pro** | $9.99/mo | 500 | 10MB | 30 days |
| **Enterprise** | Custom | Unlimited | Unlimited | Unlimited |

---

## Architecture

```
ai-undetectable/
├── backend/
│   ├── main.py          # FastAPI app & endpoints
│   ├── processor.py     # Image transformation pipeline
│   ├── db.py            # SQLAlchemy models & DB init
│   ├── auth.py          # API key authentication
│   ├── models.py        # Pydantic request/response schemas
│   └── requirements.txt  # Python dependencies
├── frontend/
│   └── index.html       # Landing page
├── Dockerfile           # Docker image definition
├── docker-compose.yml   # Docker Compose setup
├── .env.example         # Environment variables template
└── README.md            # This file
```

### Tech Stack
- **Backend**: FastAPI, SQLAlchemy, Pydantic
- **Image Processing**: Pillow, OpenCV, NumPy
- **Database**: SQLite (MVP) → PostgreSQL (production)
- **Auth**: API Key (header: `X-API-Key`)
- **Billing**: Stripe (placeholder, ready to integrate)
- **Deployment**: Docker, Railway/Vercel/DigitalOcean

---

## Running with Docker

**Build the image:**
```bash
docker build -t ai-undetectable:latest .
```

**Run the container:**
```bash
docker run -p 8000:8000 \
  -v $(pwd)/uploads:/app/uploads \
  -v $(pwd)/processed:/app/processed \
  ai-undetectable:latest
```

Or use Docker Compose:
```bash
docker-compose up
```

---

## Deployment

### Vercel
```bash
vercel
```
(Note: Vercel's Python support is limited; use Railway or DigitalOcean for production.)

### Railway
1. Connect your GitHub repo to Railway
2. Set environment variables (DATABASE_URL, STRIPE_SECRET_KEY)
3. Deploy

Railway docs: [railway.app](https://railway.app)

### DigitalOcean App Platform
1. Connect your GitHub repo
2. Configure environment variables
3. Deploy

---

## Next Steps (Post-MVP)

- [ ] Add Stripe billing integration (checkout, subscriptions)
- [ ] Implement image deletion workers (7/30-day retention)
- [ ] Add rate limiting per API key
- [ ] Build dashboard UI (usage tracking, billing)
- [ ] Optimize image processing (GPU-accelerated diffusion)
- [ ] Add batch processing endpoint
- [ ] Implement webhook notifications
- [ ] Add analytics & monitoring

---

## Testing

**Quick test:**
```bash
# Create an image (or use your own)
python -c "from PIL import Image; Image.new('RGB', (256, 256), color='red').save('test.jpg')"

# Sign up
curl -X POST http://localhost:8000/signup \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com"}'

# Process it
curl -X POST http://localhost:8000/process \
  -H "X-API-Key: YOUR_API_KEY" \
  -F "file=@test.jpg"

# Download result
curl -H "X-API-Key: YOUR_API_KEY" \
  http://localhost:8000/result/UPLOAD_ID \
  -o result.jpg
```

---

## Security Notes

- **API Keys**: Treat as secrets. Rotate regularly in production.
- **File Storage**: Use cloud storage (S3, R2) in production, not local disk.
- **HTTPS**: Always use HTTPS in production.
- **Rate Limiting**: Implement per-IP and per-API-key rate limits.
- **GDPR**: Implement data deletion on user request.
- **Legal**: Verify local legality of bypassing AI detection tools.

---

## Contributing

Contributions welcome! 

1. Fork the repo
2. Create a branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## License

MIT License. See [LICENSE](LICENSE) for details.

---

## Support

- **Email**: support@aidetectable.com
- **Twitter**: [@beatzbradley](https://twitter.com/beatzbradley)
- **GitHub Issues**: [Submit an issue](https://github.com/bradleybeatz1313/ai-undetectable/issues)

---

## Roadmap

**Q2 2024 (MVP)**
- ✅ Core image processing pipeline
- ✅ FastAPI backend with authentication
- ✅ Freemium tier system
- ✅ Landing page

**Q3 2024**
- [ ] Stripe billing integration
- [ ] Dashboard UI
- [ ] Batch processing
- [ ] Cloud storage (S3/R2)

**Q4 2024**
- [ ] GPU-accelerated diffusion refinement
- [ ] Mobile app
- [ ] Webhook notifications
- [ ] Analytics

---

**Built with ❤️ by [Brad Barroso](https://bradbarroso.com)**
