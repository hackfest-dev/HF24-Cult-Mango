import os

import dotenv

dotenv.load_dotenv()

from api.llm import OpenAIChatAgent

if __name__ == '__main__':
    with OpenAIChatAgent(os.environ, OpenAIChatAgent.ANYSCALE_MODELS[0]) as agent:
        print("Agent:", agent.message_history[-1]["content"])
        while True:
            print("Agent:", agent.chat(input_text=input("User: ")))
