from groq import Groq
from dotenv import load_dotenv
load_dotenv(override=True)
groq = Groq()
model = "openai/gpt-oss-120b"

response = groq.chat.completions.create(
    model=model,
    messages=[
        {"role": "user", "content": "Hello, how are you?"}
    ]
)

print(response.choices[0].message.content)