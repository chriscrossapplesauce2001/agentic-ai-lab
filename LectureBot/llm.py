"""One small client for every lab: chat, raw completion and embeddings.

Both model servers speak the OpenAI API, so the same code reaches either:

    academic   GWDG Academic Cloud (Chat AI), large models, needs your API key
               from the Onboarding notebook (saved in ~/.academic_cloud_key)
    spark      Ollama on the lab server, small models, no key

The labs use the Academic Cloud. There is no automatic fallback: without a
saved key, every call stops with a message pointing to the Onboarding. To use
the lab server instead, switch explicitly: set LLM_BACKEND=spark before importing.

Responses are the plain OpenAI JSON, so what you learn here works with any
OpenAI-compatible provider:

    response = chat([{"role": "user", "content": "Hi"}])
    response["choices"][0]["message"]["content"]   # the reply
    response["usage"]["prompt_tokens"]             # tokens the model read
"""

import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path

KEY_FILE = Path.home() / ".academic_cloud_key"

BACKENDS = {
    "academic": {
        "base_url": "https://chat-ai.academiccloud.de/v1",
        "chat_model": "qwen3-30b-a3b-instruct-2507",
        "embed_model": "qwen3-embedding-4b",
    },
    "spark": {
        "base_url": "http://localhost:11434/v1",
        "chat_model": "qwen2.5:7b",
        "embed_model": "qwen3-embedding:0.6b",
    },
}

# Context window per model, in tokens (from the providers' model docs).
CONTEXT_LENGTH = {
    "qwen3-30b-a3b-instruct-2507": 262_144,
    "openai-gpt-oss-120b": 131_072,
    "qwen3.8-27b": 262_144,
    "meta-llama-3.1-8b-instruct": 131_072,
    "qwen2.5:7b": 32_768,
}

BACKEND = os.environ.get("LLM_BACKEND", "academic")
BASE_URL = BACKENDS[BACKEND]["base_url"]
CHAT_MODEL = BACKENDS[BACKEND]["chat_model"]
EMBED_MODEL = BACKENDS[BACKEND]["embed_model"]


def _post(path, body, retries=3):
    headers = {"Content-Type": "application/json"}
    if BACKEND == "academic":
        if not KEY_FILE.exists():
            raise RuntimeError(NO_KEY)
        headers["Authorization"] = f"Bearer {KEY_FILE.read_text().strip()}"
    request = urllib.request.Request(BASE_URL + path, data=json.dumps(body).encode(), headers=headers)
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(request, timeout=300) as response:
                return json.load(response)
        except urllib.error.HTTPError as error:
            # 429 = rate limit (requests per minute): wait, then try again.
            if error.code == 429 and attempt < retries:
                wait = int(error.headers.get("Retry-After") or 20)
                print(f"(rate limit reached, waiting {wait} s)")
                time.sleep(wait)
                continue
            detail = error.read().decode(errors="replace")[:300]
            raise RuntimeError(f"{BACKEND} answered HTTP {error.code}: {detail}") from None


def chat(messages, model=None, **options):
    """Send a conversation, get the model's reply as OpenAI JSON.

    options are passed through, e.g. temperature=0, max_tokens=200, tools=[...].
    """
    return _post("/chat/completions", {"model": model or CHAT_MODEL, "messages": messages, **options})


def complete(prompt, model=None, **options):
    """Continue plain text: no chat template, the model reads exactly `prompt`."""
    if BACKEND == "spark":
        # Ollama's /v1/completions wraps the prompt in the chat template anyway;
        # only its native endpoint has a raw mode. Reshaped into OpenAI JSON.
        if "max_tokens" in options:
            options["num_predict"] = options.pop("max_tokens")
        request = urllib.request.Request(
            BASE_URL.removesuffix("/v1") + "/api/generate",
            data=json.dumps({"model": model or CHAT_MODEL, "prompt": prompt, "raw": True,
                             "stream": False, "options": options}).encode())
        with urllib.request.urlopen(request, timeout=300) as response:
            r = json.load(response)
        return {"choices": [{"text": r["response"], "finish_reason": r.get("done_reason")}],
                "usage": {"prompt_tokens": r["prompt_eval_count"], "completion_tokens": r["eval_count"]}}
    return _post("/completions", {"model": model or CHAT_MODEL, "prompt": prompt, **options})


def embed(texts, model=None):
    """Turn each text into a vector (a list of numbers)."""
    response = _post("/embeddings", {"model": model or EMBED_MODEL, "input": texts})
    return [item["embedding"] for item in response["data"]]


def context_length(model=None):
    """The model's context window in tokens, or None if unknown."""
    return CONTEXT_LENGTH.get(model or CHAT_MODEL)


NO_KEY = ("No Academic Cloud API key saved. Run the Onboarding notebook "
          "(Onboarding/onboarding.ipynb), Steps 1 to 3, then restart this notebook.")

print(f"llm: using {BACKEND} ({BASE_URL}), chat model {CHAT_MODEL}")
if BACKEND == "academic" and not KEY_FILE.exists():
    print(f"llm: WARNING: {NO_KEY}")
