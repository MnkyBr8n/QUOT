# Provider Comparison - Technical Details

## 📋 Quick Reference Card

| Feature | Watsonx | OpenAI | Anthropic | Google |
|---------|---------|--------|-----------|--------|
| **Setup Difficulty** | 🔴 Hard | 🟢 Easy | 🟡 Medium | 🟢 Easy |
| **Python Package** | `ibm-watsonx-ai` | `langchain-openai` | `langchain-anthropic` | `langchain-google-genai` |
| **Auth Method** | URL + API Key + Project ID | API Key only | API Key only | API Key only |
| **Native Embeddings** | ✅ Yes | ✅ Yes | ❌ No (use OpenAI) | ✅ Yes |
| **Best LLM Model** | Mixtral 8x7B | GPT-4 | Claude 3.5 Sonnet | Gemini 1.5 Pro |
| **Cheapest LLM** | Varies | GPT-3.5 Turbo | Claude Haiku | Gemini Flash |
| **Max Context** | Varies (32k typical) | 128k | 200k | 2M tokens! |
| **Rate Limits** | Based on plan | Tier-based | Tier-based | Generous |
| **Best For** | Enterprise | General use | Complex tasks | Cost-sensitive |

## 🔧 Code Changes Required

### Embeddings Module

#### Before (Watsonx only):
```python
from langchain_community.embeddings import WatsonxEmbeddings

WatsonxEmbeddings(
    model_id="ibm/slate-embedding-125m",
    url=url,
    apikey=apikey,
    project_id=project_id
)
```

#### After (Multi-provider):
```python
provider = os.getenv("PROVIDER")

if provider == "watsonx":
    from langchain_community.embeddings import WatsonxEmbeddings
    return WatsonxEmbeddings(url=..., apikey=..., project_id=...)

elif provider == "openai":
    from langchain_openai import OpenAIEmbeddings
    return OpenAIEmbeddings(api_key=...)

elif provider == "google":
    from langchain_google_genai import GoogleGenerativeAIEmbeddings
    return GoogleGenerativeAIEmbeddings(google_api_key=...)
```

### QA Bot Module

#### Before (Watsonx only):
```python
from langchain_community.llms import WatsonxLLM

WatsonxLLM(
    model_id="mistralai/mixtral-8x7b-instruct-v01",
    url=url,
    apikey=apikey,
    project_id=project_id,
    params={"temperature": 0, "max_new_tokens": 512}
)
```

#### After (Multi-provider with XML-structured prompts)

```python
from langchain_core.prompts import PromptTemplate

_DOCUMENT_PROMPT = PromptTemplate(
    input_variables=["page_content"],
    template="<document>\n{page_content}\n</document>",
)
_QA_PROMPT = PromptTemplate(
    input_variables=["context", "question"],
    template=(
        "Answer the question using only the context below.\n"
        "If the answer is not in the context, say you don't know.\n\n"
        "<context>\n{context}\n</context>\n\n"
        "Question: {question}\n\nAnswer:"
    ),
)

qa = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=retriever,
    return_source_documents=True,
    chain_type_kwargs={
        "prompt": _QA_PROMPT,
        "document_prompt": _DOCUMENT_PROMPT,
        "document_variable_name": "context",
    },
)
```

## 📦 Package Requirements by Provider

### Watsonx Only:
```
langchain>=0.1.0
langchain-community>=0.0.10
ibm-watsonx-ai>=0.2.0
```

### OpenAI Only:
```
langchain>=0.1.0
langchain-openai>=0.0.5
openai>=1.3.0
```

### Anthropic Only (+ OpenAI for embeddings):
```
langchain>=0.1.0
langchain-anthropic>=0.1.0
anthropic>=0.8.0
langchain-openai>=0.0.5  # For embeddings
openai>=1.3.0            # For embeddings
```

### Google Only:
```
langchain>=0.1.0
langchain-google-genai>=0.0.5
google-generativeai>=0.3.0
```

### All Providers:
```
# Use multi/requirements.txt - includes all of the above
```

## 🔑 Environment Variables by Provider

### Watsonx:
```env
PROVIDER=watsonx
WATSONX_URL=https://us-south.ml.cloud.ibm.com
WATSONX_APIKEY=your_key
WATSONX_PROJECT_ID=your_project_id
LLM_MODEL=mistralai/mixtral-8x7b-instruct-v01
EMBEDDING_MODEL=ibm/slate-embedding-125m
```

### OpenAI:
```env
PROVIDER=openai
OPENAI_API_KEY=sk-...
LLM_MODEL=gpt-3.5-turbo
EMBEDDING_MODEL=text-embedding-3-small
```

### Anthropic:
```env
PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-...
EMBEDDING_PROVIDER=openai   # or: google (Anthropic has no embedding API)
OPENAI_API_KEY=sk-...       # required when EMBEDDING_PROVIDER=openai
LLM_MODEL=claude-3-5-sonnet-20241022
EMBEDDING_MODEL=text-embedding-3-small
```

### Google:
```env
PROVIDER=google
GOOGLE_API_KEY=your_key
LLM_MODEL=gemini-1.5-flash
EMBEDDING_MODEL=models/embedding-001
```

## ⚙️ Parameter Name Differences

| Feature | Watsonx | OpenAI | Anthropic | Google |
|---------|---------|--------|-----------|--------|
| **Temperature** | `temperature` | `temperature` | `temperature` | `temperature` |
| **Max Tokens** | `max_new_tokens` | `max_tokens` | `max_tokens` | `max_output_tokens` |
| **API Key Param** | `apikey` | `api_key` | `api_key` | `google_api_key` |
| **Model Param** | `model_id` | `model` | `model` | `model` |
| **Top P** | `top_p` | `top_p` | `top_p` | `top_p` |
| **Top K** | `top_k` | N/A | `top_k` | `top_k` |

## 🎯 Model Selection Guide

### For Accuracy (Quality over Speed):
1. **OpenAI GPT-4** - Best general purpose
2. **Anthropic Claude 3.5 Sonnet** - Best for complex reasoning
3. **Google Gemini Pro** - Good balance
4. **Watsonx Mixtral** - Good for specialized domains

### For Speed (Latency):
1. **Google Gemini Flash** - Fastest
2. **OpenAI GPT-3.5 Turbo** - Very fast
3. **Anthropic Claude Haiku** - Fast
4. **Watsonx Mixtral** - Medium

### For Cost (Cheapest):
1. **Google Gemini Flash** - $0.075/1M tokens
2. **Anthropic Claude Haiku** - $0.25/1M tokens
3. **OpenAI GPT-3.5** - $0.50/1M tokens
4. **Watsonx** - Varies by plan

### For Long Documents (Context Window):
1. **Google Gemini** - 2M tokens
2. **Anthropic Claude** - 200k tokens
3. **OpenAI GPT-4** - 128k tokens
4. **Watsonx** - Varies (32k typical)

## 🔄 Migration Checklist

When switching from Watsonx to another provider:

### Step 1: Code Changes
- [ ] Replace `embeddings.py` with `embeddings_multi.py`
- [ ] Replace `qa_bot.py` with `qa_bot_multi.py`

### Step 2: Dependencies
- [ ] Install new provider packages
- [ ] Verify imports work

### Step 3: Configuration
- [ ] Update PROVIDER in .env
- [ ] Add new provider API key
- [ ] Update LLM_MODEL name
- [ ] Update EMBEDDING_MODEL name

### Step 4: Data Migration
- [ ] Delete old chroma_db folder
- [ ] Re-run ingest.py with new provider
- [ ] Verify vector DB created

### Step 5: Testing
- [ ] Test with sample questions
- [ ] Verify answer quality
- [ ] Check response time
- [ ] Monitor costs

## 💰 Cost Calculator

### Assumptions for 1000 Questions/Day:

**OpenAI (GPT-3.5):**
- Questions: 1000/day × 100 tokens = 100k tokens/day
- Answers: 1000/day × 200 tokens = 200k tokens/day
- Cost: ~$0.30/day = $9/month

**Anthropic (Claude Haiku):**
- Same usage pattern
- Cost: ~$0.15/day = $4.50/month

**Google (Gemini Flash):**
- Same usage pattern
- Cost: ~$0.023/day = $0.70/month

**Note:** Add embedding costs and retrieval overhead.

## 🎓 Learning Resources

### OpenAI
- Docs: https://platform.openai.com/docs
- Cookbook: https://cookbook.openai.com/

### Anthropic
- Docs: https://docs.anthropic.com/
- Prompt Library: https://docs.anthropic.com/claude/page/prompts

### Google
- Docs: https://ai.google.dev/docs
- Quickstart: https://ai.google.dev/tutorials/python_quickstart

### Watsonx
- Docs: https://www.ibm.com/docs/en/watsonx-as-a-service
- Getting Started: https://www.ibm.com/cloud/watson-machine-learning
