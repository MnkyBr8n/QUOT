"""
Chainlit front-end for the RAG QA system.

Run from a provider directory so qa_bot is on the path, e.g.:
    cd openai && chainlit run ../chainlit.py

Or set QUOT_DIR to point at the provider folder:
    QUOT_DIR=anthropic chainlit run chainlit.py
"""
import logging
import os
import sys

import chainlit as cl

# Allow callers to set which provider directory contains qa_bot.py.
# Default: openai (safe starting point).
_provider = os.getenv("QUOT_DIR", "openai")
_provider_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), _provider)
if _provider_path not in sys.path:
    sys.path.insert(0, _provider_path)

try:
    from qa_bot import build_qa_chain  # noqa: E402
except ImportError as exc:
    raise ImportError(
        f"Could not import qa_bot from '{_provider_path}'. "
        "Set QUOT_DIR to the provider folder (e.g. QUOT_DIR=anthropic)."
    ) from exc

logger = logging.getLogger(__name__)


@cl.on_chat_start
async def start():
    try:
        qa = build_qa_chain()
        cl.user_session.set("qa", qa)
        await cl.Message("Ready! Ask me anything.").send()
    except Exception as e:
        logger.error(f"Failed to initialize QA chain: {e}")
        await cl.Message(
            "Failed to initialize the QA system. Check your .env configuration."
        ).send()


@cl.on_message
async def main(message: cl.Message):
    qa = cl.user_session.get("qa")
    if qa is None:
        await cl.Message("QA system not initialized. Please restart the session.").send()
        return
    try:
        result = qa({"query": message.content})
        await cl.Message(result["result"]).send()
    except Exception as e:
        logger.error(f"Query failed: {e}")
        await cl.Message("Failed to process your question. Please try again.").send()
