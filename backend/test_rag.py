# backend/test_rag.py
from app.core.config import settings  # loads .env, sets OPENAI_API_KEY
from app.agent.rag import retrieve

import os
#let's load open ai api key from env variable
os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY


from app.agent.rag import retrieve

print(retrieve("how do I open the bronze door"))
print("---")
print(retrieve("what is the iron key"))
print("---")
print(retrieve("final truth puzzle vault"))