# ~ lib.py

import json
import multiprocessing
import os
import time

import openai
import redis
import rq

from image_search_api import get_images
from worker import conn

r = redis.Redis(host='localhost', port=6379, db=0)
q = rq.Queue(connection=conn)
openai.api_key = os.environ.get("OPENAI_API_KEY")

def qid2qck(qid): return f"prompt-{qid}"

def lang_id2natural_lang_lang(lid):
  return {
    "en": "English",
    "nl": "Dutch",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "it": "Italian",
    "pt": "Portuguese",
    "ru": "Russian",
    "ja": "Japanese",
    "ko": "Korean",
    "zh": "Chinese",
    "ar": "Arabic",
    "hi": "Hindi",
    "bn": "Bengali",
    "pa": "Punjabi",
    "te": "Telugu",
    "tr": "Turkish",
    "id": "Indonesian",
    "vi": "Vietnamese",
    "th": "Thai",
    "ms": "Malay",
    "ur": "Urdu",
    "fa": "Persian",
    "mr": "Marathi",
    "da": "Danish",
  }.get(lid, "English")

def get_retry():
  return rq.Retry(max=10, interval=[1] * 7 + [3, 5, 10])


def generate_clip(text, ip, i, qid, language_id) -> dict: # instance path, index in slides, audio id, query id
  fn = get_audio_clip_path(ip, qid, i)
  response = openai.Completion.create(
      engine="text-davinci-002",
      prompt=f"Please create an audio clip for the following text: {text}",
      max_tokens=1024,
      n=1,
      stop=None,
      temperature=0.7,
  )
  audio_text = response.choices[0].text
  synthesize_text_with_audio_profile(audio_text, output=fn)
  return dict()

def generate_image(query) -> dict:
  image_url = get_images(query)[0]
  return dict(url=image_url)


MAX_TRIES = 5
def execute(task):
  print("executing task", task)
  try_i = 0
  while try_i < MAX_TRIES:
    try:
      func = task.get("func")
      ret = func(**task.get("kwargs"))
      return dict(**ret, status="ready")
    except Exception as e:
      print("Encountered exception", task, e)
    try_i += 1
    time.sleep(1.5 ** try_i) # exponential delay
  return dict(status="failed")


def generate_presentation(qid, query_text, user_prof, instance_path, language_id):
  language_name = lang_id2natural_lang_lang(language_id)  
  query = f'Write content for a slide deck about {query_text} for a listener who is a {user_prof}. Write the result in {language_name}. Return a JSON list with data about each slide. The list consists of ' \
              f'objects with a "text" key containing a paragraph ' \
              'that is spoken by the presenter, a "title" key to name the slide with low verbose, a "key_points" key which
