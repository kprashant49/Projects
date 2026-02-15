from openai import OpenAI

client = OpenAI(api_key="")

response = client.responses.create(
    model="gpt-4.1",
    tools=[{"type": "web_search"}],
    input="Latest RBI repo rate in India"
)

print(response.output_text)
