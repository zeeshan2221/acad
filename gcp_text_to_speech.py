import openai
from env import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY

def synthesize_text_with_audio_profile(text, output, effects_profile_id='medium-bluetooth-speaker-class-device', language_code="en-US"):
    """Synthesizes speech from the input string of text."""

    response = openai.Completion.create(
        engine="davinci",
        prompt=f"Please synthesize speech for the following text: \"{text}\"",
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.7,
    )

    # The response's audio_content is binary.
    with open(output, "wb") as out:
        out.write(response.choices[0].audio_content)
        print('Audio content written to file "%s"' % output)
