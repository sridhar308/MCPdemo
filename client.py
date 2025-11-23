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
        math_call = agent.invoke({"messages":[{"role":"user","content": "what is (3+5) x 12?"}]})
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
    print("math_response:", repr(math_response))
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



#     Invoking math tool...
# math_response: {'messages': [HumanMessage(content='what is (3+5) x 12?', additional_kwargs={}, response_metadata={}, id='0da6fa3b-8ec7-4047-a003-d2d709fb32e0'), AIMessage(content='(3\u202f+\u202f5)\u202f×\u202f12\u202f=\u202f8\u202f×\u202f12\u202f=\u202f**96**', additional_kwargs={'reasoning_content': 'We need to compute (3+5) x 12. That\'s 8 * 12 = 96. We might want to use the multiply function? But we can just compute. The user asked "what is (3+5) x 12?" It\'s a simple arithmetic question. Provide answer.'}, response_metadata={'token_usage': {'completion_tokens': 97, 'prompt_tokens': 160, 'total_tokens': 257, 'completion_time': 0.099669963, 'completion_tokens_details': {'reasoning_tokens': 63}, 'prompt_time': 0.008964367, 'prompt_tokens_details': None, 'queue_time': 0.051338562, 'total_time': 0.10863433}, 'model_name': 'openai/gpt-oss-20b', 'system_fingerprint': 'fp_e99e93f2ac', 'service_tier': 'on_demand', 'finish_reason': 'stop', 'logprobs': None, 'model_provider': 'groq'}, id='lc_run--1fbfa320-db4f-49e3-98ba-7688fce66929-0', usage_metadata={'input_tokens': 160, 'output_tokens': 97, 'total_tokens': 257, 'output_token_details': {'reasoning': 63}})]}
# Math Response: (3 + 5) × 12 = 8 × 12 = **96**
# Invoking weather tool...
# weather_response: {'messages': [HumanMessage(content='what is the current weather in New York City?', additional_kwargs={}, response_metadata={}, id='fefff63f-a7ec-4d16-95b6-880cdb85e970'), AIMessage(content='I’m sorry, but I can’t provide that.', additional_kwargs={'reasoning_content': 'User asks for current weather in NYC. I must refuse because it requires real-time data. I must give a refusal.'}, response_metadata={'token_usage': {'completion_tokens': 45, 'prompt_tokens': 159, 'total_tokens': 204, 'completion_time': 0.045295394, 'completion_tokens_details': {'reasoning_tokens': 25}, 'prompt_time': 0.015915906, 'prompt_tokens_details': None, 'queue_time': 0.142369293, 'total_time': 0.0612113}, 'model_name': 'openai/gpt-oss-20b', 'system_fingerprint': 'fp_e99e93f2ac', 'service_tier': 'on_demand', 'finish_reason': 'stop', 'logprobs': None, 'model_provider': 'groq'}, id='lc_run--a01a7430-8a0c-4527-b02e-1cf8063eb914-0', usage_metadata={'input_tokens': 159, 'output_tokens': 45, 'total_tokens': 204, 'output_token_details': {'reasoning': 25}})]}
# Weather Response: I’m sorry, but I can’t provide that.