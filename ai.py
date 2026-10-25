import json
import os

from google import genai
from google.genai import errors, types


class AIError(Exception):
    pass


def complete(system, prompt):
    client = genai.Client(api_key=os.environ['GEMINI_API_KEY'])
    try:
        response = client.models.generate_content(
            model=os.environ.get('GEMINI_MODEL', 'gemini-flash-latest'),
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system,
                response_mime_type='application/json',
            ),
        )
    except errors.APIError as e:
        if e.code == 429:
            raise AIError('The AI is busy right now. Give it a minute and try again.')
        if 'API_KEY' in str(e):
            raise AIError('Gemini rejected the API key. Check GEMINI_API_KEY in your .env file.')
        raise AIError('The AI had trouble with that one. Try again.')
    return response.text or ''


def ask(system, prompt, sample):
    if not os.environ.get('GEMINI_API_KEY'):
        return sample

    text = complete(system, prompt).strip()
    if text.startswith('```'):
        text = text.split('\n', 1)[1].rsplit('```', 1)[0]
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        raise AIError("The AI sent back something we couldn't read. Try again.")
