import os

from smolagents.models.openai import OpenAIChatModel

model = OpenAIChatModel(
    model_name="deepseek-ai/DeepSeek-R1",
    api_key=os.getenv("TOGETHER_API_KEY"),
)