import openai
import os

# Set OpenAI API key
openai.api_key = "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"

def synthesize_text_with_audio_profile(text, output, effects_profile_id='medium-bluetooth-speaker-class-device', language_code="en-US"):
    """Synthesizes speech from the input string of text."""
    
    # Set OpenAI API parameters
    model_engine = "text-davinci-002"
    prompt = f"Say '{text}' in {language_code} with {effects_profile_id} effects."
    max_tokens = 60
    
    # Call OpenAI API to generate speech
    response = openai.Completion.create(
        engine=model_engine,
        prompt=prompt,
        max_tokens=max_tokens,
        n=1,
        stop=None,
        temperature=0.8,
    )

    # The response's audio_content is binary.
    with open(output, "wb") as out:
        out.write(response.choices[0].audio_content)
        print('Audio content written to file "%s"' % output)
