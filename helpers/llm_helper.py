from ollama import Client

from config import Config

system_prompt = Config.SYSTEM_PROMPT


def chat(user_prompt, model):
    client = Client(
        host='http://localhost:11434',
    )
    stream = client.chat(
        model=model,
        messages=[{'role': 'assistant', 'content': system_prompt},
                  {'role': 'user', 'content': f"Model being used is {model}.{user_prompt}"}],
        stream=True,
    )

    return stream


# handles stream response back from LLM
def stream_parser(stream):
    for chunk in stream:
        yield chunk['message']['content']
