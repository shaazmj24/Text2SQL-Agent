from dotenv import load_dotenv
import os 
from google import genai 
import time

load_dotenv()  
#print(os.getenv("gemini_api_key"))     , how is this allowed 
client = genai.Client(api_key=os.getenv("gemini_api_key")) 

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
            time.sleep(5)

    raise Exception("Gemini unavailable")





