# QUOT — How to Switch Between AI Providers

## 🎯 5-Step Process to Switch Providers

### Step 1: Update Code Files
Replace your current files with multi-provider versions:
```bash
# Backup originals
mv embeddings.py embeddings_watsonx_only.py
mv qa_bot.py qa_bot_watsonx_only.py

# Use multi-provider versions
cp embeddings_multi.py embeddings.py
cp qa_bot_multi.py qa_bot.py
```

### Step 2: Install Provider Packages
```bash
pip install -r requirements.txt
```

### Step 3: Get API Keys

#### OpenAI
1. Go to https://platform.openai.com/api-keys
2. Click "Create new secret key"
3. Copy key (starts with `sk-`)

#### Anthropic
1. Go to https://console.anthropic.com/settings/keys
2. Click "Create Key"
3. Copy key (starts with `sk-ant-`)

#### Google Gemini
1. Go to https://makersuite.google.com/app/apikey
2. Click "Create API Key"
3. Copy key

#### IBM Watsonx
1. Go to https://cloud.ibm.com/
2. Navigate to Watson Machine Learning
3. Get API key and project ID

### Step 4: Configure .env File

Copy the template:
```bash
cp .env.multi.example .env
```

Edit `.env` with your provider:

**For OpenAI:**
```env
PROVIDER=openai
OPENAI_API_KEY=sk-your_key_here
LLM_MODEL=gpt-3.5-turbo
EMBEDDING_MODEL=text-embedding-3-small
```

**For Anthropic:**
```env
PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-your_key_here
EMBEDDING_PROVIDER=openai          # or: google
OPENAI_API_KEY=sk-your_openai_key  # required when EMBEDDING_PROVIDER=openai
LLM_MODEL=claude-3-5-sonnet-20241022
EMBEDDING_MODEL=text-embedding-3-small
```

**For Google:**
```env
PROVIDER=google
GOOGLE_API_KEY=your_key_here
LLM_MODEL=gemini-1.5-flash
EMBEDDING_MODEL=models/embedding-001
```

**For Watsonx:**
```env
PROVIDER=watsonx
WATSONX_URL=https://us-south.ml.cloud.ibm.com
WATSONX_APIKEY=your_key_here
WATSONX_PROJECT_ID=your_project_id
LLM_MODEL=mistralai/mixtral-8x7b-instruct-v01
EMBEDDING_MODEL=ibm/slate-embedding-125m
```

### Step 5: Re-ingest Documents
**CRITICAL:** You must re-ingest with the new embeddings model:

```bash
# Delete old vector database
rm -rf chroma_db

# Re-ingest with new provider
python ingest.py your_document.pdf
```

## ⚡ Quick Switching Guide

### Scenario: Switch from Watsonx to OpenAI

```bash
# 1. Update .env
PROVIDER=watsonx  →  PROVIDER=openai
WATSONX_APIKEY=... → OPENAI_API_KEY=sk-...

# 2. Update models
LLM_MODEL=mistralai/mixtral-8x7b-instruct-v01 → gpt-3.5-turbo
EMBEDDING_MODEL=ibm/slate-embedding-125m → text-embedding-3-small

# 3. Re-create database (MUST DO!)
rm -rf chroma_db
python ingest.py document.pdf

# 4. Restart app
python app.py  # or python api.py, python discord_bot.py
```

### Scenario: Switch from OpenAI to Anthropic

```bash
# 1. Add Anthropic key to .env
PROVIDER=openai → PROVIDER=anthropic
# Add:  ANTHROPIC_API_KEY=sk-ant-...
# Add:  EMBEDDING_PROVIDER=openai  (Anthropic has no embedding API)
# Keep: OPENAI_API_KEY=...         (still used for embeddings)

# 2. Update LLM model (keep embeddings as OpenAI)
LLM_MODEL=gpt-3.5-turbo → claude-3-5-sonnet-20241022
# Keep: EMBEDDING_MODEL=text-embedding-3-small

# 3. Vector DB already has OpenAI embeddings, no need to re-ingest!
# (Only re-ingest if changing EMBEDDING_MODEL)

# 4. Restart app
python app.py
```

## 📊 Cost Comparison

| Provider | LLM Cost (per 1M tokens) | Embeddings Cost (per 1M tokens) | Speed |
|----------|--------------------------|----------------------------------|-------|
| **OpenAI GPT-3.5** | $0.50 - $1.50 | $0.02 | ⚡⚡⚡ Fast |
| **OpenAI GPT-4** | $10 - $60 | $0.02 | ⚡⚡ Medium |
| **Anthropic Claude Haiku** | $0.25 - $1.25 | N/A (use OpenAI) | ⚡⚡⚡ Fast |
| **Anthropic Claude Sonnet** | $3 - $15 | N/A (use OpenAI) | ⚡⚡ Medium |
| **Google Gemini Flash** | $0.075 - $0.30 | $0.000025 | ⚡⚡⚡ Very Fast |
| **Google Gemini Pro** | $1.25 - $5 | $0.000025 | ⚡⚡ Medium |
| **Watsonx** | Varies by plan | Varies by plan | ⚡⚡ Medium |

## 🎓 Provider-Specific Notes

### OpenAI
- ✅ Easiest to set up
- ✅ Best documented
- ✅ Wide model selection
- ❌ Higher cost than alternatives

### Anthropic (Claude)
- ✅ Excellent at following instructions
- ✅ Long context window (200k tokens)
- ⚠️ No native embeddings (use OpenAI)
- ⚠️ Newer, less community content

### Google Gemini
- ✅ Very cheap ($0.075/1M tokens)
- ✅ Fast (Flash model)
- ✅ Native embeddings
- ⚠️ Sometimes less consistent

### IBM Watsonx
- ✅ Enterprise features
- ✅ Data residency options
- ✅ Open source models available
- ❌ More complex setup
- ❌ Requires IBM Cloud account

## 🚨 Common Mistakes

### ❌ Mistake 1: Forgetting to re-ingest
**Problem:** Using OpenAI embeddings with Watsonx vector DB
**Fix:** Always `rm -rf chroma_db` and re-ingest when changing EMBEDDING_MODEL

### ❌ Mistake 2: Wrong model names
**Problem:** Using `gpt-3.5-turbo` with PROVIDER=watsonx
**Fix:** Check model names for your provider in `multi/.env.example`

### ❌ Mistake 3: Missing embeddings for Anthropic
**Problem:** No embedding API key when using PROVIDER=anthropic
**Fix:** Set EMBEDDING_PROVIDER=openai (or google) and supply the matching API key

### ❌ Mistake 4: Not installing provider packages
**Problem:** ImportError for langchain_openai
**Fix:** `pip install -r requirements.txt`

## ✅ Verification Checklist

Before running, verify:
- [ ] PROVIDER is set correctly in .env
- [ ] API key for chosen provider is in .env
- [ ] LLM_MODEL matches the provider
- [ ] EMBEDDING_MODEL matches the provider
- [ ] If using Anthropic, EMBEDDING_PROVIDER is set (openai or google) with matching API key
- [ ] chroma_db was deleted and re-created with new embeddings
- [ ] All provider packages are installed

## 🔄 Testing Different Providers

Want to compare providers? Keep separate .env files:

```bash
# Create provider-specific configs
cp .env .env.openai
cp .env .env.anthropic
cp .env .env.google

# Edit each with provider-specific settings

# Switch providers
cp .env.openai .env
rm -rf chroma_db
python ingest.py doc.pdf
python app.py

# Compare
cp .env.anthropic .env
rm -rf chroma_db
python ingest.py doc.pdf
python app.py
```

## 💡 Recommendation

**For getting started:** OpenAI (gpt-3.5-turbo)
- Easy setup
- Reliable
- Good docs

**For production:** Compare all based on:
1. Answer quality (test with your docs)
2. Cost (calculate based on your usage)
3. Speed (measure latency)
4. Features (context window, tools, etc.)
