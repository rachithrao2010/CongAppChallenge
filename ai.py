import json
import os

import httpx
from google import genai
from google.genai import errors, types


class AIError(Exception):
    pass


FALLBACK_MODEL = 'gemini-flash-lite-latest'


def complete(system, prompt):
    client = genai.Client(
        api_key=os.environ['GEMINI_API_KEY'],
        http_options=types.HttpOptions(timeout=60000, retry_options=types.HttpRetryOptions(attempts=1)),
    )
    models = dict.fromkeys([os.environ.get('GEMINI_MODEL', FALLBACK_MODEL), FALLBACK_MODEL])
    for model in models:
        try:
            response = client.models.generate_content(
                model=model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system,
                    response_mime_type='application/json',
                ),
            )
            return response.text or ''
        except httpx.TimeoutException:
            raise AIError('The AI took too long to answer. Try again.')
        except errors.APIError as e:
            # overloaded, so try the next model
            if e.code in (503, 504) and model != FALLBACK_MODEL:
                continue
            if e.code in (429, 503, 504):
                raise AIError('The AI is busy right now. Give it a minute and try again.')
            if 'API_KEY' in str(e):
                raise AIError('Gemini rejected the API key. Check GEMINI_API_KEY in your .env file.')
            raise AIError('The AI had trouble with that one. Try again.')


def ask(system, prompt):
    if not os.environ.get('GEMINI_API_KEY'):
        raise AIError("The resume translator isn't set up yet. GEMINI_API_KEY is missing.")

    text = complete(system, prompt).strip()
    if text.startswith('```'):
        text = text.split('\n', 1)[1].rsplit('```', 1)[0]
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        raise AIError("The AI sent back something we couldn't read. Try again.")
