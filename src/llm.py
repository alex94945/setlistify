import os
from smolagents import OpenAIServerModel        # ← correct import for Together

model = OpenAIServerModel(
    model_id="deepseek-ai/DeepSeek-R1",         # any Together-hosted slug
    api_base="https://api.together.xyz/v1",     # Together’s OpenAI-compatible URL
    api_key=os.getenv("TOGETHER_API_KEY"),
    timeout=60,                                 # optional
)
