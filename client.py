from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent

from langchain_groq import ChatGroq

from dotenv import load_dotenv
load_dotenv()   

import asyncio
import inspect


async def main():
    client = MultiServerMCPClient(
        {
            "math":{
                "command": "python",
                "args": ["mathserver.py"],
                "transport": "stdio"
            },
            # Weather tool removed for now to simplify debugging (start with math only)
            # "weather":{ 
            #     "transport": "streamable_http",
            #     "url": "http://localhost:8000/mcp"
            # }
        }
    )

    import os
    os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")
    tools = await client.get_tools()
    # print loaded tools defensively in case tool objects differ
    try:
        tool_names = [getattr(tool, "name", repr(tool)) for tool in tools]
    except Exception:
        tool_names = [repr(tool) for tool in tools]
    
    model=ChatGroq(model="openai/gpt-oss-20b") #qwen-qwq-32b
    agent=create_agent(model, tools)   

    print("Invoking math tool...")
    try:
        math_call = agent.invoke({"messages":[{"role":"user","content": "what is (3/5) x 12?"}]})
        if inspect.isawaitable(math_call):
            math_response = await asyncio.wait_for(math_call, timeout=60)
        else:
            math_response = math_call
    except asyncio.TimeoutError:
        print("Math invoke timed out after 60s")
        return
    except Exception as e:
        print("Math invoke failed:", repr(e))
        return

    # Debug: print full response object to inspect structure
    print("math full response:", repr(math_response))
    # Try to read common fields safely
    if isinstance(math_response, dict):
        if "message" in math_response:
            print("Math Response:", math_response["message"][-1]["content"])
        elif "messages" in math_response:
            # messages may be objects (e.g., HumanMessage/AIMessage), so access .content if present
            last = math_response["messages"][-1]
            content = getattr(last, "content", None)
            print("Math Response:", content)
        else:
            print("Math response has no 'message' or 'messages' key; inspect above output")

    print("Invoking weather tool...")
    try:
        weather_call = agent.invoke({"messages":[{"role":"user","content": "what is the current weather in New York City?"}]})
        if inspect.isawaitable(weather_call):
            weather_response = await asyncio.wait_for(weather_call, timeout=60)
        else:
            weather_response = weather_call
    except asyncio.TimeoutError:
        print("Weather invoke timed out after 60s")
        return
    except Exception as e:
        print("Weather invoke failed:", repr(e))
        return

    print("weather_response:", repr(weather_response))
    # Support both 'message' and 'messages' shapes
    if isinstance(weather_response, dict):
        if "message" in weather_response:
            last = weather_response["message"][-1]
            print("Weather Response:", getattr(last, "content", None))
        elif "messages" in weather_response:
            last = weather_response["messages"][-1]
            print("Weather Response:", getattr(last, "content", None))
        else:
            print("Weather response has no 'message' or 'messages' key; inspect above output")


if __name__ == "__main__":
    asyncio.run(main())



# Invoking math tool...
# math full response: {'messages': [HumanMessage(content='what is (3+5) x 12?', additional_kwargs={}, response_metadata={}, id='f9c09601-71df-4e72-ba40-8ae7fb3c0f62'), 
# AIMessage(content='\\( (3+5) \\times 12 = 8 \\times 12 = 96 \\).', additional_kwargs={'reasoning_content': "User asks for (3+5) x 12. That's 8 * 12 = 96. They likely want the result. No function needed."}, response_metadata={'token_usage': {'completion_tokens': 64, 'prompt_tokens': 160, 'total_tokens': 224, 'completion_time': 0.064544282, 'completion_tokens_details': {'reasoning_tokens': 33}, 'prompt_time': 0.01070067, 'prompt_tokens_details': None, 'queue_time': 0.05088959, 'total_time': 0.075244952}, 'model_name': 'openai/gpt-oss-20b', 'system_fingerprint': 'fp_e99e93f2ac', 'service_tier': 'on_demand', 'finish_reason': 'stop', 'logprobs': None, 'model_provider': 'groq'}, id='lc_run--0c744c96-2822-4999-8d5e-6f240ffa6965-0', usage_metadata={'input_tokens': 160, 'output_tokens': 64, 'total_tokens': 224, 'output_token_details': {'reasoning': 33}})]}

# Math Response: \( (3+5) \times 12 = 8 \times 12 = 96 \).

# Invoking weather tool...
# weather_response: {'messages': [HumanMessage(content='what is the current weather in New York City?', additional_kwargs={}, response_metadata={}, id='f188a66a-5f3a-41d5-b58e-5a7cd27f00e9'), AIMessage(content='I’m sorry, but I don’t have access to real‑time data, so I can’t tell you the current weather in New\u202fYork City. You might want to check a weather website or app for the latest information.', additional_kwargs={'reasoning_content': "User asks current weather. We can't browse. Must refuse or say unknown. We can say we can't fetch real-time data."}, response_metadata={'token_usage': {'completion_tokens': 81, 'prompt_tokens': 159, 'total_tokens': 240, 'completion_time': 0.083439614, 'completion_tokens_details': {'reasoning_tokens': 26}, 'prompt_time': 0.010555792, 'prompt_tokens_details': None, 'queue_time': 0.050633888, 'total_time': 0.093995406}, 'model_name': 'openai/gpt-oss-20b', 'system_fingerprint': 'fp_e99e93f2ac', 'service_tier': 'on_demand', 'finish_reason': 'stop', 'logprobs': None, 'model_provider': 'groq'}, id='lc_run--69e5b6fb-6d24-4fb8-ab3f-9352210b76f5-0', usage_metadata={'input_tokens': 159, 'output_tokens': 81, 'total_tokens': 240, 'output_token_details': {'reasoning': 26}})]}
# Weather Response: I’m sorry, but I don’t have  access to real‑time data, so I can’t tell you the current weather in New York City. You might want to check a weather website or app for the latest information.