# Questions 15, 16, 17, 18, 25, 26, 29, 30 and 60
import asyncio
import json
import logging
import re

from groq import Groq
from django.conf import settings

logger = logging.getLogger(__name__)

class ContentGenerationError(Exception):
    pass

def build_prompt(topic_title):
    # Questions 16, 17, 25, 26 and 29
    return f"""
You are an educational content generator.

Create complete study material for this topic:
{topic_title}

Return ONLY valid JSON without markdown fences.

Use exactly this structure:
{{
  "notes": "Detailed notes as readable paragraphs.",
  "keyPoints": [
    "Point 1",
    "Point 2",
    "Point 3",
    "Point 4",
    "Point 5"
  ],
  "summary": "Short topic summary.",
  "quiz": {{
    "title": "Quiz title",
    "description": "Quiz description",

    "questions": [
      {{
        "questionText": "Question text",
        "options": [
          {{
            "text": "Option A",
            "isCorrect": false
          }},
          {{
            "text": "Option B",
            "isCorrect": true
          }},
          {{
            "text": "Option C",
            "isCorrect": false
          }},
          {{
            "text": "Option D",
            "isCorrect": false
          }}
        ]
      }}
    ]
  }}
}}

Create five questions.
Each question must have exactly four options.
Exactly one option must be correct.
""".strip()

def _post_to_groq(topic_title):

    if not settings.GROQ_API_KEY:
        raise ContentGenerationError(
            "GROQ_API_KEY is missing in the .env file."
        )

    client = Groq(
        api_key=settings.GROQ_API_KEY
    )

    try:

        response = client.chat.completions.create(

            model=settings.GROQ_MODEL,

            messages=[
                {
                    "role": "user",
                    "content": build_prompt(topic_title),
                }
            ],

            temperature=0.4,

            max_tokens=4096,
        )

        generated_text = (
            response.choices[0]
            .message.content
        )

    except Exception as exc:

        logger.exception("Groq request failed.")

        raise ContentGenerationError(
            f"Groq API Error : {exc}"
        )

    return parse_generated_json(
        generated_text
    )

async def generate_course_material(topic_title):

    return await asyncio.to_thread(

        _post_to_groq,

        topic_title,
    )

def parse_generated_json(generated_text):
    # Question 18
    cleaned_text = generated_text.strip()

    cleaned_text = re.sub(
        r"^```(?:json)?\s*",
        "",
        cleaned_text,
        flags=re.IGNORECASE,
    )

    cleaned_text = re.sub(
        r"\s*```$",
        "",
        cleaned_text,
    )

    try:
        data = json.loads(cleaned_text)
    except json.JSONDecodeError as exc:
        raise ContentGenerationError(
            "AI response was not valid JSON."
        ) from exc

    required_keys = {
        "notes",
        "keyPoints",
        "summary",
        "quiz",
    }

    missing = required_keys.difference(
        data.keys()
    )

    if missing:
        raise ContentGenerationError(
            "AI response is incomplete. Missing: "
            + ", ".join(sorted(missing))
        )

    return data
