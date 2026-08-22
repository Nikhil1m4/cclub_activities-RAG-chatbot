import os, requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.environ.get('GROQ_API_KEY')
res = requests.get('https://api.groq.com/openai/v1/models', headers={'Authorization': f'Bearer {api_key}'})
print([m['id'] for m in res.json().get('data', [])])
