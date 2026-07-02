from anthropic import Anthropic
from typing import List, Optional


class ClaudeAPIManager:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.client = None
        if api_key:
            self.client = Anthropic(api_key=api_key)
    
    def set_api_key(self, api_key: str):
        self.api_key = api_key
        self.client = Anthropic(api_key=api_key)
    
    def is_configured(self) -> bool:
        return self.api_key is not None and self.client is not None
    
    def generate_prompts(self, count: int = 5) -> List[str]:
        if not self.is_configured():
            raise ValueError("API key not configured")
        
        try:
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1024,
                messages=[
                    {
                        "role": "user",
                        "content": f"Generate {count} thoughtful journaling prompts for personal reflection and deep introspection. Each prompt should encourage self-discovery, emotional awareness, or meaningful contemplation. Return only the prompts, one per line, without numbering or additional commentary."
                    }
                ]
            )
            
            prompts_text = message.content[0].text
            prompts = [line.strip() for line in prompts_text.strip().split('\n') if line.strip()]
            
            cleaned_prompts = []
            for prompt in prompts:
                prompt = prompt.lstrip('0123456789.-) ')
                if prompt:
                    cleaned_prompts.append(prompt)
            
            return cleaned_prompts
        
        except Exception as e:
            raise Exception(f"Failed to generate prompts: {str(e)}")
