import json
import os

import openai
from pydantic import BaseModel

script_dir = os.path.dirname(__file__)


def prompt_template(input_text: str, **_):
    return f"""
    the user has provided the following information:
    ---
    {input_text}
    ---
    give conclusion or ask for more information
    """


def summary_template(input_text: str, old_summary: str, agent_text: str, **_):
    if not old_summary:
        return f"""
        summarizing the user grievance:
        ---
        {input_text}
        """
    return f"""
    the below is the old summary:
    ---
    {old_summary}
    ---
    Update the summary with new information:
    ---
    {input_text}
    """


def end_template(input_text: str, **_):
    return f"""
    End of the conversation. The user has requested to end the conversation.
    ---
    {input_text}
    """


class OpenAIChatAgent:
    ANYSCALE_API_KEY: str
    OPENAI_API_KEY: str
    OPENAI_URI: str = "https://api.openai.com/v1"
    ANYSCALE_URI: str = "https://api.endpoints.anyscale.com/v1"
    ANYSCALE_MODELS = [
        "mistralai/Mistral-7B-Instruct-v0.1",
        "mistralai/Mixtral-8x7B-Instruct-v0.1",
        "HuggingFaceH4/zephyr-7b-beta",
        "meta-llama/Llama-2-7b-chat-hf",
        "meta-llama/Llama-2-13b-chat-hf",
        "meta-llama/Llama-2-70b-chat-hf",
        "Meta-Llama/Llama-Guard-7b",
        "codellama/CodeLlama-34b-Instruct-hf",
        "mlabonne/NeuralHermes-2.5-Mistral-7B",
        "google/gemma-7b-it",
    ]
    OPENAI_MODELS = [
        "gpt-3.5-turbo",
    ]

    def __init__(self, secrets, model: str):
        with open(os.path.join(script_dir, "llm_settings.json")) as f: self.settings = json.load(f)
        self.ANYSCALE_API_KEY = secrets["ANYSCALE_API_KEY"]
        self.OPENAI_API_KEY = secrets["OPENAI_API_KEY"]
        self.message_history = [
            {
                "role": "system",
                "content": self.settings["prompts"]["system"]
            },
            {
                "role": "assistant",
                "content": self.settings["prompts"]["greeting"]
            },
        ]
        self.model = model

    def __enter__(self):
        self.client = openai.OpenAI(
            base_url=self.ANYSCALE_URI if self.model in self.ANYSCALE_MODELS else self.OPENAI_URI,
            api_key=self.ANYSCALE_API_KEY if self.model in self.ANYSCALE_MODELS else self.OPENAI_API_KEY,
        )
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client.close()
        self.client = None

    def update_message_history(self, content, role):
        self.message_history.append({
            'role': role,
            'content': content
        })

    def chat(self, input_text: str, ingredients: list[str], preferences: list[str], **kwargs) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                self.message_history[0],
                {"role": "user", "content": f"I have a product with the following ingredients: {', '.join(ingredients)} "
                                            f"and my preferences are: {', '.join(preferences)}"},
                *self.message_history[1:],
                {"role": "user", "content": prompt_template(input_text, **kwargs)}
            ],
            temperature=self.settings["temperature"],
        )
        assistant_response = response.choices[0].message.content
        self.update_message_history(input_text, 'user')
        self.update_message_history(assistant_response, 'assistant')
        return assistant_response

    def end_chat(self, input_text: str, **kwargs) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": self.settings["prompts"]["end"]
                },
                {
                    "role": "user",
                    "content": end_template(input_text, **kwargs)
                }
            ],
            temperature=self.settings["temperature"],
        )
        assistant_response = response.choices[0].message.content
        self.update_message_history(input_text, 'user')
        self.update_message_history(assistant_response, 'assistant')
        return assistant_response

    class Summary(BaseModel):
        summary: str
        title: str

    def get_summary(self, text: str, old_summary: str, **kwargs) -> "Summary":
        chat_completion = self.client.chat.completions.create(
            model="mistralai/Mistral-7B-Instruct-v0.1",
            response_format={  # noqa
                "type": "json_object",
                "schema": self.Summary.model_json_schema()
            },
            messages=[
                {"role": "system", "content": self.settings["prompts"]["system"]},
                {"role": "user", "content": summary_template(old_summary, text, "", **kwargs)},
            ],
            temperature=0.6,
            max_tokens=256,
            seed=1234,
        )
        json_msg = chat_completion.choices[0].message.content
        try:
            return self.Summary.parse_obj(eval(json_msg))
        except SyntaxError:
            return self.Summary(summary="error", title="Error")
