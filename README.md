# Agentic AI Lab

Module infAgAI. Over four exercises you build an AI agent from scratch: first a
plain model call, then a reasoning loop you write yourself, then the same thing
with a framework.

## The exercises

Work through them in order. Each one builds on the last.

| | | |
|---|---|---|
| **exercise0** | LLM basics | What a token is, what `temperature` does, what a chat call looks like |
| **exercise1** | Talking to the model | Calling the model directly, no framework in the way |
| **exercise2** | Building an agent | The ReAct loop and tool use, written by hand |
| **exercise3** | Doing it with a framework | The same agent, built with LangChain |

## How to work

1. Open an exercise from the start page and run the cells from top to bottom.
2. Fill in every cell marked as a task. Cells you are not meant to change are
   locked.
3. Your work saves by itself. Sign in again later and it is still there.

## What runs where

The language model runs on the lab server, not on your laptop. There is nothing
to install and no API key to enter. Everything happens in your browser.

Because everyone shares the same server, a cell can take a few seconds longer
when the lab is busy. That is normal.

## If something goes wrong

| Problem | What to do |
|---|---|
| A cell hangs or the output looks stuck | Kernel menu, then "Restart Kernel", then run the cells again from the top |
| An error mentions a name that is not defined | You have most likely left a task cell unfilled further up |
| A notebook will not open at all | Ask the lab instructor |
| You forgot your password | Ask the lab instructor, it can be reset |

## Working on your own machine

Not required, and not supported during the lab. If you want to run the exercises
locally anyway, you need Ollama with the `qwen3.5:4b` model and the Python
packages `ollama`, `langchain` and `langgraph`.
