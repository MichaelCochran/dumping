import win32com.client
import pythoncom
import time
import json
import os
from datetime import datetime
from typing import List, Dict, Optional
import argparse
import sys

# Configure UTF-8 encoding for Windows console
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        # Python < 3.7
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

class EmailTaskGenerator:
    # Default configuration - single source of truth
    DEFAULT_CONFIG = {
        "check_interval_seconds": 300,
        "monitor_folders": ["Inbox"],
        "tasks_output_file": "generated_tasks.json",
        "use_ai": False,
        "ai_api_key": "",
        "ai_model": "gpt-4",
        "max_emails_per_run": 10,
        "processed_emails_file": "processed_emails.json"
    }
    
    def __init__(self, config_path: str = "config.json"):
        self.config_path = config_path
        self.config = self.load_config(config_path)
        self.outlook = None
        self.namespace = None
        self.tasks_file = self.config.get("tasks_output_file", "generated_tasks.json")
        self.processed_emails = self.load_processed_emails()
        
    def load_config(self, config_path: str) -> dict:
        """Load config from file, create with defaults if it doesn't exist."""
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # Create config file with defaults
            print(f"Config file not found. Creating {config_path} with default settings...")
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(self.DEFAULT_CONFIG, f, indent=2)
            return self.DEFAULT_CONFIG.copy()
    
    def load_processed_emails(self) -> set:
        processed_file = self.config.get("processed_emails_file", "processed_emails.json")
        if os.path.exists(processed_file):
            with open(processed_file, 'r') as f:
                return set(json.load(f))
        return set()
    
    def save_processed_emails(self):
        processed_file = self.config.get("processed_emails_file", "processed_emails.json")
        with open(processed_file, 'w') as f:
            json.dump(list(self.processed_emails), f, indent=2)
    
    def connect_outlook(self):
        try:
            pythoncom.CoInitialize()
            self.outlook = win32com.client.Dispatch("Outlook.Application")
            self.namespace = self.outlook.GetNamespace("MAPI")
            print("✓ Connected to Outlook")
            return True
        except Exception as e:
            print(f"✗ Failed to connect to Outlook: {e}")
            print("Make sure Outlook is installed and running.")
            return False
    
    def get_folder(self, folder_name: str):
        try:
            return self.namespace.GetDefaultFolder(6).Folders(folder_name)
        except:
            try:
                return self.namespace.GetDefaultFolder(6)
            except Exception as e:
                print(f"✗ Could not access folder '{folder_name}': {e}")
                return None
    
    def extract_email_data(self, email) -> Dict:
        try:
            return {
                "subject": email.Subject,
                "sender": email.SenderName,
                "sender_email": email.SenderEmailAddress,
                "body": email.Body,
                "received_time": str(email.ReceivedTime),
                "importance": email.Importance,
                "has_attachments": email.Attachments.Count > 0,
                "attachment_count": email.Attachments.Count,
                "entry_id": email.EntryID
            }
        except Exception as e:
            print(f"✗ Error extracting email data: {e}")
            return None
    
    def generate_task_with_ai(self, email_data: Dict) -> Dict:
        if not self.config.get("use_ai") or not self.config.get("ai_api_key"):
            return self.generate_task_template(email_data)
        
        try:
            import openai
            openai.api_key = self.config["ai_api_key"]
            
            prompt = f"""Analyze this email and generate a concise task description with priority level.

Email Subject: {email_data['subject']}
From: {email_data['sender']} ({email_data['sender_email']})
Received: {email_data['received_time']}
Body Preview: {email_data['body'][:500]}...

Generate a JSON response with:
- task_title: Short, actionable task title
- task_description: Brief description of what needs to be done
- priority: high/medium/low
- estimated_time: Estimated time to complete (e.g., "30 min", "2 hours")
- category: Type of task (e.g., "Response Required", "Review", "Action Item", "FYI")
"""
            
            response = openai.ChatCompletion.create(
                model=self.config.get("ai_model", "gpt-4"),
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            
            ai_response = json.loads(response.choices[0].message.content)
            return {
                **ai_response,
                "email_subject": email_data['subject'],
                "email_sender": email_data['sender'],
                "email_received": email_data['received_time'],
                "generated_at": datetime.now().isoformat(),
                "method": "ai"
            }
        except Exception as e:
            print(f"⚠ AI generation failed, using template: {e}")
            return self.generate_task_template(email_data)
    
    def generate_task_template(self, email_data: Dict) -> Dict:
        priority = "high" if email_data.get("importance", 1) == 2 else "medium"
        
        category = "FYI"
        subject_lower = email_data['subject'].lower()
        if any(word in subject_lower for word in ["urgent", "asap", "deadline", "important"]):
            priority = "high"
            category = "Action Item"
        elif any(word in subject_lower for word in ["review", "feedback", "check"]):
            category = "Review"
        elif any(word in subject_lower for word in ["?", "question", "request"]):
            category = "Response Required"
        
        return {
            "task_title": email_data['subject'][:60],
            "task_description": f"{category}: Email from {email_data['sender']}",
            "priority": priority,
            "estimated_time": "15 min",
            "category": category,
            "email_subject": email_data['subject'],
            "email_sender": email_data['sender'],
            "email_received": email_data['received_time'],
            "generated_at": datetime.now().isoformat(),
            "method": "template"
        }
    
    def save_task(self, task: Dict):
        tasks = []
        if os.path.exists(self.tasks_file):
            with open(self.tasks_file, 'r') as f:
                tasks = json.load(f)
        
        tasks.append(task)
        
        with open(self.tasks_file, 'w') as f:
            json.dump(tasks, f, indent=2)
        
        print(f"✓ Task saved: {task['task_title']}")
    
    def process_email(self, email):
        email_data = self.extract_email_data(email)
        if not email_data:
            return None
        
        entry_id = email_data['entry_id']
        if entry_id in self.processed_emails:
            return None
        
        print(f"\n📧 Processing: {email_data['subject'][:60]}")
        print(f"   From: {email_data['sender']}")
        
        task = self.generate_task_with_ai(email_data)
        self.save_task(task)
        
        self.processed_emails.add(entry_id)
        self.save_processed_emails()
        
        return task
    
    def process_recent_emails(self, folder_name: str = "Inbox", limit: int = None):
        folder = self.get_folder(folder_name)
        if not folder:
            return []
        
        messages = folder.Items
        messages.Sort("[ReceivedTime]", True)
        
        limit = limit or self.config.get("max_emails_per_run", 10)
        processed_tasks = []
        count = 0
        
        print(f"\n🔍 Scanning {folder_name} for recent emails...")
        
        for message in messages:
            if count >= limit:
                break
            
            try:
                if hasattr(message, 'Subject'):
                    task = self.process_email(message)
                    if task:
                        processed_tasks.append(task)
                        count += 1
            except Exception as e:
                print(f"⚠ Error processing email: {e}")
                continue
        
        print(f"\n✓ Processed {len(processed_tasks)} emails")
        return processed_tasks
    
    def monitor_mode(self):
        print("\n🔄 Starting email monitor mode...")
        print("Press Ctrl+C to stop\n")
        
        try:
            while True:
                for folder_name in self.config.get("monitor_folders", ["Inbox"]):
                    self.process_recent_emails(folder_name, limit=5)
                
                interval = self.config.get("check_interval_seconds", 60)
                print(f"\n💤 Waiting {interval} seconds before next check...")
                time.sleep(interval)
        
        except KeyboardInterrupt:
            print("\n\n✓ Monitor stopped")
    
    def list_tasks(self):
        if not os.path.exists(self.tasks_file):
            print("No tasks generated yet.")
            return
        
        with open(self.tasks_file, 'r') as f:
            tasks = json.load(f)
        
        if not tasks:
            print("No tasks found.")
            return
        
        print(f"\n📋 Generated Tasks ({len(tasks)} total)\n")
        print("=" * 80)
        
        for i, task in enumerate(tasks, 1):
            priority_icon = "🔴" if task['priority'] == 'high' else "🟡" if task['priority'] == 'medium' else "🟢"
            print(f"\n{i}. {priority_icon} [{task['priority'].upper()}] {task['task_title']}")
            print(f"   Category: {task['category']}")
            print(f"   Est. Time: {task['estimated_time']}")
            print(f"   Email: {task['email_subject'][:60]}")
            print(f"   From: {task['email_sender']}")
            print(f"   Generated: {task['generated_at']}")
        
        print("\n" + "=" * 80)

def main():
    parser = argparse.ArgumentParser(description="Outlook Email Task Generator")
    parser.add_argument(
        "mode",
        choices=["monitor", "process", "list", "board"],
        help="Mode: 'monitor' for real-time, 'process' for on-demand, 'list' to view tasks, 'board' to launch Kanban board"
    )
    parser.add_argument(
        "--folder",
        default="Inbox",
        help="Outlook folder to process (default: Inbox)"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Maximum number of emails to process (default: 10)"
    )
    parser.add_argument(
        "--config",
        default="config.json",
        help="Path to config file (default: config.json)"
    )
    
    args = parser.parse_args()
    
    if args.mode == "board":
        import subprocess
        import sys
        subprocess.run([sys.executable, "kanban_board.py"])
        return
    
    generator = EmailTaskGenerator(args.config)
    
    if not generator.connect_outlook():
        return
    
    if args.mode == "monitor":
        generator.monitor_mode()
    elif args.mode == "process":
        generator.process_recent_emails(args.folder, args.limit)
    elif args.mode == "list":
        generator.list_tasks()

if __name__ == "__main__":
    main()
