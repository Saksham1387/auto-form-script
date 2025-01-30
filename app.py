from langchain_openai import ChatOpenAI
from browser_use import Agent
import asyncio
from dotenv import load_dotenv
load_dotenv()

async def main():
    agent = Agent(
        task="Fill this google form https://docs.google.com/forms/d/e/1FAIpQLSc8QrSmlnAQslljTFKNIC0LwWQAhUcP7BhlyB_i2GIrPDInnA/viewform  with random options 10 times",
        llm=ChatOpenAI(model="gpt-4o"),
    )
    result = await agent.run()
    print(result)

asyncio.run(main())