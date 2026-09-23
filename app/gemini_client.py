import time

from google import genai
from google.genai import errors

from app.config import GEMINI_API_KEY


client = genai.Client(
    api_key=GEMINI_API_KEY
)


MODELS = [
    "gemini-3.5-flash-lite",
    "gemini-3.6-flash",
]


def generate_with_fallback(
    prompt,
    config=None,
    max_retries=2
):

    errors_seen = []

    for model in MODELS:

        for attempt in range(max_retries):

            try:

                print(
                    f"\nTrying Gemini model: {model}"
                    f" | Attempt: {attempt + 1}"
                )

                response = client.models.generate_content(
                    model=model,
                    contents=prompt,
                    config=config
                )

                if response.text:

                    print(
                        f"SUCCESS: {model}"
                    )

                    return response

                raise RuntimeError(
                    f"{model} returned an empty response."
                )

            except errors.ServerError as e:

                error_message = (
                    f"{model} -> ServerError: {e}"
                )

                print(error_message)

                errors_seen.append(
                    error_message
                )

                if attempt < max_retries - 1:

                    wait_time = 2 ** attempt

                    print(
                        f"Waiting {wait_time} seconds..."
                    )

                    time.sleep(wait_time)

            except errors.APIError as e:

                error_message = (
                    f"{model} -> APIError: {e}"
                )

                print(error_message)

                errors_seen.append(
                    error_message
                )

                # 429 means quota/rate limit.
                # Trying the same model again is pointless.
                break

            except Exception as e:

                error_message = (
                    f"{model} -> {type(e).__name__}: {e}"
                )

                print(error_message)

                errors_seen.append(
                    error_message
                )

                break

    error_details = "\n".join(errors_seen)

    raise RuntimeError(
        "All Gemini models failed.\n\n"
        f"Details:\n{error_details}"
    )