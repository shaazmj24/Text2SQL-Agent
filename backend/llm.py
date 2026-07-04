from dotenv import load_dotenv
import os 
from google import genai 
import time

load_dotenv()   
api_k = os.getenv("gemini_api_key") 

if not api_k:  
    raise ValueError("Api key not found")
client = genai.Client(api_key=api_k) 

def ask_gemini(prompt: str) -> dict: 
    for _ in range(3):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            return response.text

        except Exception as e:
            print("Retrying...")
            time.sleep(4)

    raise Exception("Gemini unavailable")


