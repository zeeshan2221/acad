import openai
from env import OPENAI_API_KEY

# Set up the OpenAI API client
openai.api_key = OPENAI_API_KEY

def get_images(query):
    # Use the OpenAI API to generate a list of image URLs
    response = openai.Image.create(
        prompt=f"Search for images of {query}",
        n=1,
        size="1024x1024"
    )

    # Extract the URLs from the response and return them as a list
    image_links = [image.url for image in response.data]
    return image_links
