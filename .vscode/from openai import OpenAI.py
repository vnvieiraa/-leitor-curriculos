from openai import OpenAI

client = OpenAI()

response = client.responses.create(model="gpt-5-astra", input="Write a short bedtime story about a unicorn.")

print(response.output_text)