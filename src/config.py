import os
from dotenv import load_dotenv

load_dotenv()

TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
SETLISTFM_API_KEY = os.getenv("SETLISTFM_API_KEY") # Rate limit max. 2.0/second and max. 1440/DAY. (can request upgrade)

# Langfuse
LANGFUSE_PUBLIC_KEY = os.getenv("LANGFUSE_PUBLIC_KEY")
LANGFUSE_SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY")
