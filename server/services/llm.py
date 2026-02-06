import requests
import json

class LLMService:
    def __init__(self, model="qwen2.5:7b", host="http://localhost:11434"):
        self.model = model
        self.host = host
        self.api_url = f"{host}/api/generate"

    def generate(self, prompt, system_prompt="You are Este, a helpful kiosk assistant for USTP."):
        """
        Generates text from Ollama.
        """
        full_prompt = f"{system_prompt}\n\nUser: {prompt}\nAssistant:"
        
        payload = {
            "model": self.model,
            "prompt": full_prompt,
            "stream": False,
            "keep_alive": -1
        }

        try:
            response = requests.post(self.api_url, json=payload)
            response.raise_for_status()
            data = response.json()
            return data.get("response", "")
        except Exception as e:
            print(f"LLM Error: {e}")
            return "I apologize, but I am having trouble thinking right now."

    def stream_generate(self, prompt, system_prompt="You are Este, a helpful kiosk assistant for USTP."):
        """
        Yields tokens for streaming response.
        """
        full_prompt = f"{system_prompt}\n\nUser: {prompt}\nAssistant:"
        
        payload = {
            "model": self.model,
            "prompt": full_prompt,
            "stream": True,
            "keep_alive": -1
        }

        try:
            with requests.post(self.api_url, json=payload, stream=True) as response:
                response.raise_for_status()
                for line in response.iter_lines():
                    if line:
                        body = json.loads(line)
                        if "response" in body:
                            yield body["response"]
        except Exception as e:
            print(f"LLM Stream Error: {e}")
            yield "Error."
