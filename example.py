import os
from openai import OpenAI

if not os.path.exists(".env"):
    raise FileNotFoundError(".env file not found")

with open(".env", "r") as f:
    for line in f:
        key, value = line.strip().split("=")
        os.environ[key] = value

client = OpenAI(
  api_key=os.getenv("OPENAI_API_KEY")
)

completion = client.chat.completions.create(
  model="gpt-4o-mini",
  store=True,
  messages=[
    {"role": "user", "content": "write a haiku about ai"}
  ]
)

print(completion.choices[0].message)
