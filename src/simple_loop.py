from openai import OpenAI
import os

# Set your API key
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def gpt_request(prompt):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=15000
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"An error occurred: {str(e)}"

print("Welcome! Ask your questions to gpt-4o-mini. Type 'exit' to end the program.")

while True:
    user_input = input("\nYour question: ")
    
    if user_input.lower() == "exit":
        print("Goodbye!")
        break
    
    answer = gpt_request(user_input)
    print("\nAnswer:", answer)
