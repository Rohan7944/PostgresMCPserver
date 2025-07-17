from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_groq import ChatGroq

from dotenv import load_dotenv
load_dotenv()

import asyncio

async def main():
    client = MultiServerMCPClient(
        {
            "MathServer": {
                "command": "python",
                "args": ["mathserver.py"],
                "transport": "stdio",
            },
            "WeatherServer": {
                "url": "http://localhost:8000/mcp/",
                "transport": "streamable_http",
                }
            }
    )
    # import os ## uncomment this
    # os.environ["GROQ_API_KEY"] = "" ## your key
    groq = ChatGroq(model="llama-3.3-70b-versatile")
    tools = await client.get_tools()
    agent = create_react_agent(groq, tools)
    
    math_result = await agent.ainvoke(
        {"messages":[{"role": "user", "content": "What is 3 + 5 * 12?"}]}
    )
    print("Math result:", math_result['messages'][-1].content)

    weather_result = await agent.ainvoke(
        {"messages":[{"role": "user", "content": "What is the weather in Tokyo?"}]}
    )
    print("Weather result:", weather_result['messages'][-1].content)

asyncio.run(main())