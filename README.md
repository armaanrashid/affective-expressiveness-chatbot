# Affective Expressiveness Chatbot

This project implements a simple web‑based chatbot that can adopt one of
seven affective expressiveness conditions (Neutral, Polite, Supportive,
Warm, Very Warm, Over‑Expressive and Uncanny).  It is designed to
replicate the conditions used in the *When AI Feels Too Much*
experiment, allowing you to run interactive studies where participants
chat with a large language model instead of reading static vignettes.

The chatbot is built using [Flask](https://flask.palletsprojects.com) for
the server and the [OpenAI API](https://platform.openai.com/docs/api-reference/chat) to
generate responses.  A lightweight HTML/JS front‑end runs entirely in
the browser and communicates with the Flask back‑end via a JSON API.

## Features

* **Seven affective conditions** – Each conversation starts with a
  system prompt that instructs the model to adopt a different tone,
  ranging from detached and factual (Neutral) to boundary‑crossing
  intimacy (Uncanny).  These prompts are inspired by the vignettes
  used in the original experiment and are defined in `app.py`.

* **Client‑side conversation history** – The server does not store
  chat sessions.  The browser maintains the history and sends it
  along with each new user message.  This makes it easy to embed
  the chatbot into other pages (e.g. Qualtrics) without server‑side
  session state.

* **Environment‑configured API key** – The OpenAI API key is read from
  the `OPENAI_API_KEY` environment variable.  You can supply your own
  key without modifying the code.

* **Adjustable condition via URL** – The front‑end reads a `condition`
  query parameter (e.g. `?condition=Warm`) and preselects that
  condition in the drop‑down.  This enables Qualtrics to pass the
  assigned condition when redirecting participants.

## Prerequisites

* Python 3.9 or higher
* An OpenAI API key (you can obtain one from the
  [OpenAI dashboard](https://platform.openai.com/account/api-keys))

## Installation

Clone or download this repository, then install the dependencies:

```bash
python -m venv venv
source venv/bin/activate  # on Windows use venv\Scripts\activate
pip install -r requirements.txt
```

## Running the server locally

Export your OpenAI API key and start the Flask development server:

```bash
export OPENAI_API_KEY="sk-..."
python app.py
```

By default the app listens on port 5000.  Visit `http://localhost:5000`
in your browser to load the chat interface.  You can change the port
by setting the `PORT` environment variable.

## Testing different conditions

You can choose the condition from the drop‑down at the top of the chat
page.  Alternatively, pass it as a query parameter in the URL:

```
http://localhost:5000/?condition=Warm
```

This will preselect “Warm” in the drop‑down.  If no parameter is
provided the default condition is “Neutral”.

## Deploying on GitHub / third‑party platforms

This repository is self‑contained and can be hosted using any provider
that supports Python/Flask (e.g. Heroku, Render, Railway, Fly.io) or
container‑based deployment.  To deploy on a service, you will
typically create a `Procfile` or Dockerfile.  Below is a simple
example `Procfile` for a Heroku‑style deployment:

```
web: gunicorn app:app --bind 0.0.0.0:$PORT
```

You will also need to set the `OPENAI_API_KEY` environment variable in
the provider’s configuration and possibly create a `requirements.txt`
file (already provided in this repo).

## Embedding into Qualtrics

To integrate this chatbot into Qualtrics after randomizing participants
into conditions, redirect them to your hosted chat page with the
`condition` and `pid` query parameters:

```
https://your-hosted-chatbot.com/?condition=${e://Field/condition}&pid=${e://Field/PROLIFIC_PID}
```

On the Qualtrics side, set up a **Randomizer** element in the Survey
Flow that assigns one of the seven conditions and stores it as
Embedded Data named `condition`.  After the chat, you can redirect
participants back to Qualtrics for the post‑chat survey.

## Notes on safety

The system prompts include explicit instructions not to provide
therapy, medical advice, diagnosis, or crisis counselling and to keep
replies concise.  However, you should monitor the chatbot’s
responses during pilot testing to ensure that the model adheres to
these instructions under your specific usage conditions.  Adjust the
prompts as needed to maintain participant safety.

## Customization

Feel free to modify the tone descriptions in `app.py` to better match
your research needs.  You can also adjust `temperature`,
`max_tokens`, or use a different model when calling
`openai.ChatCompletion.create`.  If you wish to include exemplar
dialogue from the vignettes for each condition, you can prepend
additional example messages to the `messages` list before calling
OpenAI.

## License

This project is provided for academic research purposes.  You may
modify and extend it as needed for your own experiments.