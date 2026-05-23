import { Router, type IRouter } from "express";
import multer from "multer";
import sharp from "sharp";
import { v4 as uuidv4 } from "uuid";
import { logger } from "../lib/logger";

const router: IRouter = Router();

const upload = multer({
  storage: multer.memoryStorage(),
  limits: { fileSize: 10 * 1024 * 1024 },
});

const DEMO_API_KEY = process.env["DEMO_API_KEY"] ?? "demo-key-free-tier";

function validateApiKey(apiKey: string | undefined): boolean {
  if (!apiKey) return false;
  return apiKey.length > 0;
}

async function processImage(inputBuffer: Buffer): Promise<Buffer> {
  const image = sharp(inputBuffer);
  const metadata = await image.metadata();

  const width = metadata.width ?? 256;
  const height = metadata.height ?? 256;
  const channels = (metadata.channels ?? 3) as 1 | 2 | 3 | 4;

  const rawBuffer = await image.raw().toBuffer();

  const noiseBuffer = Buffer.alloc(rawBuffer.length);
  for (let i = 0; i < rawBuffer.length; i++) {
    const noise = (Math.random() - 0.5) * 6;
    noiseBuffer[i] = Math.round(noise);
  }

  const noisyBuffer = Buffer.alloc(rawBuffer.length);
  for (let i = 0; i < rawBuffer.length; i++) {
    noisyBuffer[i] = Math.max(0, Math.min(255, rawBuffer[i] + noiseBuffer[i]));
  }

  const processed = await sharp(noisyBuffer, {
    raw: { width, height, channels },
  })
    .modulate({
      brightness: 1.02,
      saturation: 1.08,
    })
    .sharpen({ sigma: 0.8 })
    .jpeg({ quality: 94 })
    .toBuffer();

  return processed;
}

router.post("/process", upload.single("file"), async (req, res) => {
  const apiKey = req.headers["x-api-key"] as string | undefined;

  if (!validateApiKey(apiKey)) {
    res.status(401).json({ error: "Missing or invalid X-API-Key header" });
    return;
  }

  if (!req.file) {
    res.status(400).json({ error: "No file uploaded" });
    return;
  }

  const validExts = [".jpg", ".jpeg", ".png", ".gif", ".webp"];
  const filename = req.file.originalname ?? "image.jpg";
  const ext = filename.slice(filename.lastIndexOf(".")).toLowerCase();

  if (!validExts.includes(ext)) {
    res.status(400).json({
      error: `Invalid format. Supported: ${validExts.join(", ")}`,
    });
    return;
  }

  const fileSizeMb = req.file.size / (1024 * 1024);
  const maxSizeMb = 10;

  if (fileSizeMb > maxSizeMb) {
    res.status(413).json({
      error: `File too large. Max size: ${maxSizeMb}MB`,
    });
    return;
  }

  try {
    const uploadId = uuidv4();
    const processed = await processImage(req.file.buffer);

    res.json({
      success: true,
      message: "Image processed successfully",
      upload_id: uploadId,
      remaining_quota: 9,
      tier: "free",
    });

    req.log.info({ uploadId, fileSizeMb: fileSizeMb.toFixed(2) }, "Image processed");
  } catch (err) {
    req.log.error({ err }, "Image processing failed");
    res.status(500).json({ error: "Failed to process image" });
  }
});

router.get("/result/:uploadId", async (req, res) => {
  const apiKey = req.headers["x-api-key"] as string | undefined;

  if (!validateApiKey(apiKey)) {
    res.status(401).json({ error: "Missing or invalid X-API-Key header" });
    return;
  }

  res.status(404).json({
    error: "Upload not found. Note: processed images are not stored in this demo.",
  });
});

router.get("/usage", (req, res) => {
  const apiKey = req.headers["x-api-key"] as string | undefined;

  if (!validateApiKey(apiKey)) {
    res.status(401).json({ error: "Missing or invalid X-API-Key header" });
    return;
  }

  res.json({
    tier: "free",
    monthly_usage: 0,
    monthly_limit: 10,
    remaining_quota: 10,
    usage_reset_date: new Date().toISOString(),
    stripe_subscription_active: false,
  });
});

router.post("/signup", (req, res) => {
  const { email } = req.body as { email?: string };

  if (!email) {
    res.status(400).json({ error: "Email is required" });
    return;
  }

  const userId = uuidv4();
  const apiKey = `sk_free_${uuidv4().replace(/-/g, "").slice(0, 32)}`;

  res.json({
    id: userId,
    api_key: apiKey,
    tier: "free",
    monthly_usage: 0,
    usage_reset_date: new Date().toISOString(),
    created_at: new Date().toISOString(),
  });
});

export default router;
