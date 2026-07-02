import random
from pathlib import Path
from typing import List, Set


class PromptManager:
    def __init__(self, prompts_file: str):
        self.prompts_file = Path(prompts_file)
        self.prompts: List[str] = []
        self.load_prompts()
    
    def load_prompts(self):
        if self.prompts_file.exists():
            with open(self.prompts_file, 'r', encoding='utf-8') as f:
                self.prompts = [line.strip() for line in f if line.strip()]
        else:
            self.prompts = [
                "What are you grateful for today?",
                "Describe a challenge you faced and how you handled it.",
                "What did you learn about yourself today?"
            ]
            self.save_prompts()
    
    def get_random_prompt(self) -> str:
        if not self.prompts:
            return "What's on your mind today?"
        return random.choice(self.prompts)
    
    def add_prompts(self, new_prompts: List[str]) -> List[str]:
        existing_prompts_normalized = {p.strip().lower() for p in self.prompts}
        added_prompts = []
        
        for prompt in new_prompts:
            prompt = prompt.strip()
            if prompt and prompt.lower() not in existing_prompts_normalized:
                self.prompts.append(prompt)
                existing_prompts_normalized.add(prompt.lower())
                added_prompts.append(prompt)
        
        if added_prompts:
            self.save_prompts()
        
        return added_prompts
    
    def get_all_prompts(self) -> List[str]:
        return self.prompts.copy()
    
    def save_prompts(self):
        self.prompts_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.prompts_file, 'w', encoding='utf-8') as f:
            for prompt in self.prompts:
                f.write(f"{prompt}\n")
    
    def is_unique(self, prompt: str) -> bool:
        prompt_normalized = prompt.strip().lower()
        return prompt_normalized not in {p.strip().lower() for p in self.prompts}
    
    def filter_unique_prompts(self, prompts: List[str]) -> List[str]:
        existing_normalized = {p.strip().lower() for p in self.prompts}
        unique_prompts = []
        
        for prompt in prompts:
            prompt = prompt.strip()
            if prompt and prompt.lower() not in existing_normalized:
                unique_prompts.append(prompt)
                existing_normalized.add(prompt.lower())
        
        return unique_prompts
