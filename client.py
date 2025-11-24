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
            "weather":{ 
                "transport": "streamable_http",
                "url": "http://127.0.0.1:8000/mcp"
            }
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
        # Prefer the agent's async entrypoint if available so tools are
        # invoked using the async code paths (avoids StructuredTool sync errors).
        payload = {"messages":[{"role":"user","content": "what is the current weather in New York City?"}]}
        if hasattr(agent, "ainvoke"):
            weather_call = agent.ainvoke(payload)
        else:
            weather_call = agent.invoke(payload)

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
# math full response: {'messages': [HumanMessage(content='what is (3/5) x 12?', additional_kwargs={}, response_metadata={}, id='d11f8e26-e6be-4ba5-b80b-abc77ffc0925'), AIMessage(content='\\((3/5)\\times 12 = \\frac{3\\times12}{5}= \\frac{36}{5}=7.2\\).', additional_kwargs={'reasoning_content': 'The user asks: "what is (3/5) x 12?" They want the multiplication result. So compute (3/5)*12 = 3*12/5 = 36/5 = 7.2. So answer: 7.2.'}, response_metadata={'token_usage': {'completion_tokens': 98, 'prompt_tokens': 238, 'total_tokens': 336, 'completion_time': 0.103437148, 'completion_tokens_details': {'reasoning_tokens': 57}, 'prompt_time': 0.016631044, 'prompt_tokens_details': None, 'queue_time': 0.102630386, 'total_time': 0.120068192}, 'model_name': 'openai/gpt-oss-20b', 'system_fingerprint': 'fp_e99e93f2ac', 'service_tier': 'on_demand', 'finish_reason': 'stop', 'logprobs': None, 'model_provider': 'groq'}, id='lc_run--9f6d06ca-e741-4090-8846-c97091942c8e-0', usage_metadata={'input_tokens': 238, 'output_tokens': 98, 'total_tokens': 336, 'output_token_details': {'reasoning': 57}})]}
# Math Response: \((3/5)\times 12 = \frac{3\times12}{5}= \frac{36}{5}=7.2\).
# Invoking weather tool...
# weather_response: {'messages': [HumanMessage(content='what is the current weather in New York City?', additional_kwargs={}, response_metadata={}, id='fec14670-4b2f-40a2-8bce-4cfa4be3d4c6'), AIMessage(content='', additional_kwargs={'reasoning_content': 'We need to use the get_current_weather function.', 'tool_calls': [{'id': 'fc_29bfb9ee-3163-41ee-a031-a630c8b338a0', 'function': {'arguments': '{"location":"New York City"}', 'name': 'get_current_weather'}, 'type': 'function'}]}, response_metadata={'token_usage': {'completion_tokens': 37, 'prompt_tokens': 237, 'total_tokens': 274, 'completion_time': 0.036958229, 'completion_tokens_details': {'reasoning_tokens': 11}, 'prompt_time': 0.011620975, 'prompt_tokens_details': None, 'queue_time': 0.200442454, 'total_time': 0.048579204}, 'model_name': 'openai/gpt-oss-20b', 'system_fingerprint': 'fp_a8c584dda7', 'service_tier': 'on_demand', 'finish_reason': 'tool_calls', 'logprobs': None, 'model_provider': 'groq'}, id='lc_run--67244a61-0340-4ff9-afde-3acea554bb48-0', tool_calls=[{'name': 'get_current_weather', 'args': {'location': 'New York City'}, 'id': 'fc_29bfb9ee-3163-41ee-a031-a630c8b338a0', 'type': 'tool_call'}], usage_metadata={'input_tokens': 237, 'output_tokens': 37, 'total_tokens': 274, 'output_token_details': {'reasoning': 11}}), ToolMessage(content='The current weather in New York City is sunny with a temperature of 35°C.', name='get_current_weather', id='0b18e01e-6037-4f0d-927a-05c6701452a1', tool_call_id='fc_29bfb9ee-3163-41ee-a031-a630c8b338a0'), AIMessage(content='The current weather in New\u202fYork\u202fCity is sunny with a temperature of **35\u202f°C**.', additional_kwargs={'reasoning_content': 'The user asked: "what is the current weather in New York City?" We already responded with the tool. The assistant responded with "The current weather in New York City is sunny with a temperature of 35°C." That is fine. But maybe we should confirm. The user may want more details. But we have answered. Probably fine.'}, response_metadata={'token_usage': {'completion_tokens': 100, 'prompt_tokens': 283, 'total_tokens': 383, 'completion_time': 0.100971419, 'completion_tokens_details': {'reasoning_tokens': 70}, 'prompt_time': 0.016001434, 'prompt_tokens_details': None, 'queue_time': 0.061774276, 'total_time': 0.116972853}, 'model_name': 'openai/gpt-oss-20b', 'system_fingerprint': 'fp_e99e93f2ac', 'service_tier': 'on_demand', 'finish_reason': 'stop', 'logprobs': None, 'model_provider': 'groq'}, id='lc_run--5345a6b9-0964-4af9-8a0f-be2c76364c89-0', usage_metadata={'input_tokens': 283, 'output_tokens': 100, 'total_tokens': 383, 'output_token_details': {'reasoning': 70}})]}
# Weather Response: The current weather in New York City is sunny with a temperature of **35 °C**.