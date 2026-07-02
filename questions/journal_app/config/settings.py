from pathlib import Path
import os
from dotenv import load_dotenv


class Settings:
    def __init__(self, app_dir: Path = None):
        if app_dir is None:
            app_dir = Path(__file__).parent.parent
        
        self.app_dir = app_dir
        self.db_path = app_dir / "journal.db"
        self.prompts_path = app_dir.parent / "prompts.txt"
        self.env_path = app_dir / ".env"
        self.salt_path = app_dir / ".salt"
        
        load_dotenv(self.env_path)
        
        self.claude_api_key = os.getenv("CLAUDE_API_KEY")
    
    def save_claude_api_key(self, api_key: str):
        self.claude_api_key = api_key
        
        lines = []
        if self.env_path.exists():
            with open(self.env_path, 'r') as f:
                lines = f.readlines()
        
        found = False
        for i, line in enumerate(lines):
            if line.startswith('CLAUDE_API_KEY='):
                lines[i] = f'CLAUDE_API_KEY={api_key}\n'
                found = True
                break
        
        if not found:
            lines.append(f'CLAUDE_API_KEY={api_key}\n')
        
        with open(self.env_path, 'w') as f:
            f.writelines(lines)
    
    def get_salt(self) -> bytes:
        if self.salt_path.exists():
            with open(self.salt_path, 'rb') as f:
                return f.read()
        return None
    
    def save_salt(self, salt: bytes):
        with open(self.salt_path, 'wb') as f:
            f.write(salt)
