from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QTextEdit, QPushButton, QMessageBox, QInputDialog,
                             QLineEdit, QDialog)
from PyQt5.QtCore import Qt
from .search_window import SearchWindow
from .prompt_selection_dialog import PromptSelectionDialog


class MainWindow(QMainWindow):
    def __init__(self, db_manager, prompt_manager, claude_api_manager, settings, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.prompt_manager = prompt_manager
        self.claude_api = claude_api_manager
        self.settings = settings
        self.current_prompt = ""
        self.setup_ui()
        self.load_random_prompt()
    
    def setup_ui(self):
        self.setWindowTitle("Journal Entry")
        self.setMinimumSize(600, 500)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        
        prompt_layout = QHBoxLayout()
        prompt_title = QLabel("Today's Prompt:")
        prompt_title.setStyleSheet("font-weight: bold; font-size: 12pt;")
        prompt_layout.addWidget(prompt_title)
        
        prompt_layout.addStretch()
        
        new_prompt_btn = QPushButton("New Prompt")
        new_prompt_btn.clicked.connect(self.load_random_prompt)
        new_prompt_btn.setToolTip("Get a different random prompt from your library")
        prompt_layout.addWidget(new_prompt_btn)
        
        ai_prompt_btn = QPushButton("Get AI Prompt")
        ai_prompt_btn.clicked.connect(self.get_ai_prompts)
        ai_prompt_btn.setToolTip("Generate new prompts using Claude AI")
        prompt_layout.addWidget(ai_prompt_btn)
        
        layout.addLayout(prompt_layout)
        
        self.prompt_label = QLabel()
        self.prompt_label.setWordWrap(True)
        self.prompt_label.setStyleSheet(
            "font-size: 11pt; font-style: italic; padding: 10px; "
            "background-color: #f0f0f0; border-radius: 5px; margin: 10px 0;"
        )
        layout.addWidget(self.prompt_label)
        
        layout.addSpacing(10)
        
        entry_label = QLabel("Your Entry:")
        entry_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(entry_label)
        
        self.entry_text = QTextEdit()
        self.entry_text.setPlaceholderText("Write your thoughts here...")
        layout.addWidget(self.entry_text)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        submit_btn = QPushButton("Submit")
        submit_btn.setStyleSheet("padding: 8px 20px; font-weight: bold;")
        submit_btn.clicked.connect(self.submit_entry)
        button_layout.addWidget(submit_btn)
        
        open_btn = QPushButton("Open")
        open_btn.setStyleSheet("padding: 8px 20px;")
        open_btn.clicked.connect(self.open_search)
        button_layout.addWidget(open_btn)
        
        layout.addLayout(button_layout)
        
        central_widget.setLayout(layout)
    
    def load_random_prompt(self):
        self.current_prompt = self.prompt_manager.get_random_prompt()
        self.prompt_label.setText(self.current_prompt)
    
    def submit_entry(self):
        content = self.entry_text.toPlainText().strip()
        
        if not content:
            QMessageBox.warning(self, "Error", "Please write something before submitting.")
            return
        
        try:
            self.db_manager.save_entry(self.current_prompt, content)
            QMessageBox.information(self, "Success", "Entry saved successfully!")
            
            self.entry_text.clear()
            self.load_random_prompt()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save entry: {str(e)}")
    
    def open_search(self):
        search_window = SearchWindow(self.db_manager, self)
        search_window.exec_()
    
    def get_ai_prompts(self):
        if not self.claude_api.is_configured():
            api_key, ok = QInputDialog.getText(
                self,
                "API Key Required",
                "Enter your Claude API key:",
                QLineEdit.Password
            )
            
            if ok and api_key:
                self.claude_api.set_api_key(api_key)
                self.settings.save_claude_api_key(api_key)
            else:
                return
        
        try:
            reply = QMessageBox.question(
                self,
                "Generate Prompts",
                "This will use your Claude API to generate new prompts. Continue?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            
            if reply != QMessageBox.Yes:
                return
            
            self.statusBar().showMessage("Generating prompts...", 3000)
            
            generated_prompts = self.claude_api.generate_prompts(count=5)
            
            unique_prompts = self.prompt_manager.filter_unique_prompts(generated_prompts)
            
            if not unique_prompts:
                QMessageBox.information(
                    self,
                    "No New Prompts",
                    "All generated prompts already exist in your library. Try again for different prompts."
                )
                return
            
            dialog = PromptSelectionDialog(unique_prompts, self)
            
            if dialog.exec_() == QDialog.Accepted:
                selected = dialog.get_selected_prompt()
                to_save = dialog.get_prompts_to_save()
                
                if to_save:
                    added = self.prompt_manager.add_prompts(to_save)
                    if added:
                        QMessageBox.information(
                            self,
                            "Success",
                            f"Added {len(added)} new prompt(s) to your library."
                        )
                
                if selected:
                    self.current_prompt = selected
                    self.prompt_label.setText(self.current_prompt)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate prompts: {str(e)}")
