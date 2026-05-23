# AI Undetectable — Quick Start Guide

Get up and running in 5 minutes.

## Option 1: Local Python

**1. Install dependencies:**
```bash
pip install -r backend/requirements.txt
```

**2. Start the server:**
```bash
cd backend
uvicorn main:app --reload --port 8000
```

Server: `http://localhost:8000`
Docs: `http://localhost:8000/docs`

**3. Test it:**
```bash
# Sign up
curl -X POST http://localhost:8000/signup \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com"}'

# Copy the api_key from the response above, then:
curl -X POST http://localhost:8000/process \
  -H "X-API-Key: YOUR_API_KEY" \
  -F "file=@test_image.jpg"
```

---

## Option 2: Docker

**1. Build:**
```bash
docker build -t ai-undetectable:latest .
```

**2. Run:**
```bash
docker run -p 8000:8000 \
  -v $(pwd)/uploads:/app/uploads \
  -v $(pwd)/processed:/app/processed \
  ai-undetectable:latest
```

**3. Access:** `http://localhost:8000/docs`

---

## Option 3: Docker Compose (Recommended)

```bash
docker-compose up
```

Then test at `http://localhost:8000`.

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/signup` | Create a new user account |
| GET | `/user` | Get current user info |
| GET | `/usage` | Get usage stats |
| POST | `/process` | Upload & process image |
| GET | `/result/{upload_id}` | Download processed image |
| GET | `/status/{upload_id}` | Check processing status |
| GET | `/health` | Health check |
| GET | `/docs` | Swagger UI documentation |

---

## Next Steps

1. **Test the API**: Visit `http://localhost:8000/docs` and try endpoints
2. **Customize**: Edit `processor.py` to adjust image transformation
3. **Database**: Switch from SQLite to PostgreSQL for production
4. **Billing**: Integrate Stripe (placeholder code already in `main.py`)
5. **Deploy**: Push to GitHub, connect to Railway/DigitalOcean/Vercel

---

## File Structure

```
ai-undetectable/
├── backend/
│   ├── main.py              ← FastAPI app (all endpoints)
│   ├── processor.py         ← Image transformation logic
│   ├── db.py                ← Database models & setup
│   ├── auth.py              ← API key authentication
│   ├── models.py            ← Pydantic schemas
│   └── requirements.txt      ← Python dependencies
├── frontend/
│   └── index.html           ← Landing page
├── Dockerfile               ← Docker image config
├── docker-compose.yml       ← Docker Compose setup
├── README.md                ← Full documentation
├── QUICKSTART.md            ← This file
└── .env.example             ← Environment variables template
```

---

## Troubleshooting

**Port 8000 already in use?**
```bash
uvicorn main:app --port 8001
```

**Import errors?**
```bash
pip install -r backend/requirements.txt --force-reinstall
```

**Database corrupted?**
```bash
rm backend/ai_undetectable.db
# Restart the server to reinitialize
```

---

## Questions?

- Check `README.md` for full documentation
- Visit `http://localhost:8000/docs` for interactive API docs
- Email: support@aidetectable.com

---

**Ready? Let's go:** `docker-compose up` 🚀
