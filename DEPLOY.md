# Deploying AgentESG to a public demo URL (free)

Backend on Hugging Face Spaces (Docker SDK, always-on, free), frontend on Vercel. Anthropic spend hard-capped four ways. Realistic monthly cost under typical-to-abusive traffic: **$0 hosting + $0–$5 API**.

## 1. Anthropic console (5 min)

1. Sign in at `console.anthropic.com`.
2. **Settings → Workspaces → Create workspace** → name it `agentesg-public-demo`.
3. **Limits → Monthly spend limit** → set to **$5**. This is the only hard, enforced cap; everything else is belt-and-suspenders.
4. **API Keys** → in the new workspace, click **Create Key** → name `hf-space-prod`. Copy it now (you won't see it again). This is the key you'll paste into the HF Space secret.
5. *(Optional)* **Plan & Billing → Notifications** → set an email alert at $2 so you hear about traffic spikes early.

## 2. Hugging Face Space (10 min)

### 2a. Create the Space

1. Sign in at `huggingface.co` and go to `huggingface.co/new-space`.
2. Owner = your account. Name = `agentesg` (your URL will be `huggingface.co/spaces/<you>/agentesg`).
3. **License**: MIT. **Space SDK**: **Docker** → choose **Blank**. **Hardware**: `CPU basic · 2 vCPU · 16 GB` (free).
4. **Visibility**: Public.
5. Click **Create Space**. It will be empty.

### 2b. Set Space secrets

In the new Space, click **Settings → Variables and secrets**. Add:

| Type | Name | Value |
|---|---|---|
| Secret | `ANTHROPIC_API_KEY` | the `hf-space-prod` key from step 1.4 |
| Variable | `DEMO_MODE` | `true` |
| Variable | `ANTHROPIC_MODEL` | `claude-haiku-4-5-20251001` |
| Variable | `CORS_ORIGINS` | leave blank for now — you'll set it after Vercel deploys |

### 2c. Push the code

The Space repo needs the backend code, datasets, and the HF-specific Dockerfile + README at its root. Run from the AgentESG repo root:

```bash
HF_USER="<your-hf-username>"
SPACE_DIR="$(mktemp -d)/agentesg-space"

git clone "https://huggingface.co/spaces/${HF_USER}/agentesg" "$SPACE_DIR"
rsync -a --delete \
  --exclude '.git' \
  --include 'backend/***' \
  --include 'Datasets/***' \
  --include 'deploy/***' \
  --exclude '*' \
  ./ "$SPACE_DIR/"

# Promote the HF-specific Dockerfile + README to the repo root of the Space.
cp deploy/hfspace/Dockerfile "$SPACE_DIR/Dockerfile"
cp deploy/hfspace/README.md  "$SPACE_DIR/README.md"

cd "$SPACE_DIR"
git add -A
git commit -m "Initial deploy"
git push
```

First push triggers the build, which downloads the embedding model and pre-builds the FAISS index — expect ~6–10 min. Watch the build log under **Logs** on the Space page. When it goes green, hit `https://<you>-agentesg.hf.space/api/health` and you should get `{"status":"ok"}`.

## 3. Vercel frontend (5 min)

1. Sign in at `vercel.com` with GitHub.
2. **Add New → Project** → import the AgentESG GitHub repo.
3. **Root Directory**: `frontend`.
4. **Framework Preset**: Vite (auto-detected).
5. **Environment Variables**: add `VITE_API_BASE` with value `https://<you>-agentesg.hf.space/api` (replace `<you>` with your HF username — Vercel strips dots and dashes from `<you>` per HF rules, so check the actual URL on the Space page).
6. Click **Deploy**. ~90 seconds.
7. Note your Vercel URL — something like `agentesg-chethan.vercel.app`.

## 4. Close the loop (CORS)

Back on the HF Space → **Settings → Variables and secrets** → set:

| Variable | Value |
|---|---|
| `CORS_ORIGINS` | `https://agentesg-chethan.vercel.app` (the URL from step 3.7) |

Then **Settings → Restart Space**. After ~30 seconds the new CORS origin takes effect.

## 5. Smoke test

Open your Vercel URL. Click around:

- [ ] `Companies` lists 1000 rows.
- [ ] Open any company → metrics + benchmarks render (no LLM cost).
- [ ] `Rules` tab → evaluate against a company (no LLM cost).
- [ ] `Copilot` → ask "what is ESRS E1?" → should stream a Haiku response (LLM cost = ~$0.0005).
- [ ] Spam the copilot 6 times from the same browser → 6th should return a 429 with the demo-quota message.

If the copilot returns a stub response that says "LLM disabled", your `ANTHROPIC_API_KEY` secret isn't being picked up — recheck the Space's secrets and Restart.

## Layered cost caps (recap)

| Layer | Enforced by | Hard cap |
|---|---|---|
| Workspace monthly spend | Anthropic | $5/mo |
| Default model | env (`ANTHROPIC_MODEL`) | Haiku 4.5 (~15× cheaper than Opus) |
| Per-call output tokens | `AnthropicClient._resolve_max_tokens` | 512 in demo mode |
| Per-IP daily LLM calls | `RateLimitMiddleware` | 5 |
| Global daily LLM calls | `RateLimitMiddleware` | 200 |
| Non-LLM endpoints | n/a | unlimited (zero $) |

Even if the per-IP cap is defeated (e.g., someone rotates IPs), the global cap is hit at 200 calls × 512 tokens × ~$1.50/M-tok output ≈ **$0.15/day** of output, plus inputs ≈ **$0.50/day** total. So even the worst-case full-quota day costs you about fifty cents.

## Rollback

If something breaks in production:

- **Backend**: HF Space → **Settings → Factory rebuild** to repull from main, or push the previous commit to the Space repo.
- **Frontend**: Vercel → **Deployments → ... → Promote to Production** on the previous green deploy.
- **Disable LLM entirely**: HF Space → Settings → delete the `ANTHROPIC_API_KEY` secret → Restart. The app keeps serving with stub responses and zero API cost.

## Local sanity check before deploying

```bash
# From the repo root
docker compose down
DEMO_MODE=true ANTHROPIC_MODEL=claude-haiku-4-5-20251001 docker compose up --build
```

Hit the 6th copilot request locally and confirm you get a 429 before pushing to the Space.
