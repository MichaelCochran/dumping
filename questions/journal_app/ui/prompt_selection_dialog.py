from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QListWidget, QListWidgetItem, QPushButton, QCheckBox,
                             QMessageBox)
from PyQt5.QtCore import Qt
from typing import List


class PromptSelectionDialog(QDialog):
    def __init__(self, prompts: List[str], parent=None):
        super().__init__(parent)
        self.prompts = prompts
        self.selected_prompt = None
        self.prompts_to_save = []
        self.setup_ui()
    
    def setup_ui(self):
        self.setWindowTitle("AI Generated Prompts")
        self.setMinimumSize(500, 400)
        
        layout = QVBoxLayout()
        
        title_label = QLabel("Select a prompt to use or save prompts for later:")
        title_label.setWordWrap(True)
        layout.addWidget(title_label)
        
        layout.addSpacing(10)
        
        self.prompt_list = QListWidget()
        
        for prompt in self.prompts:
            item = QListWidgetItem(prompt)
            item.setData(Qt.UserRole, prompt)
            self.prompt_list.addItem(item)
        
        self.prompt_list.itemDoubleClicked.connect(self.use_selected_prompt)
        layout.addWidget(self.prompt_list)
        
        self.save_checkbox = QCheckBox("Add selected prompts to my prompt library")
        self.save_checkbox.setChecked(True)
        layout.addWidget(self.save_checkbox)
        
        layout.addSpacing(10)
        
        button_layout = QHBoxLayout()
        
        use_btn = QPushButton("Use Selected")
        use_btn.clicked.connect(self.use_selected_prompt)
        button_layout.addWidget(use_btn)
        
        save_btn = QPushButton("Save All")
        save_btn.clicked.connect(self.save_all_prompts)
        button_layout.addWidget(save_btn)
        
        button_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def use_selected_prompt(self):
        current_item = self.prompt_list.currentItem()
        
        if not current_item:
            QMessageBox.warning(self, "Error", "Please select a prompt.")
            return
        
        self.selected_prompt = current_item.data(Qt.UserRole)
        
        if self.save_checkbox.isChecked():
            self.prompts_to_save = [self.selected_prompt]
        
        self.accept()
    
    def save_all_prompts(self):
        self.prompts_to_save = self.prompts.copy()
        
        reply = QMessageBox.question(
            self,
            "Save All Prompts",
            f"Save all {len(self.prompts)} prompts to your library?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes
        )
        
        if reply == QMessageBox.Yes:
            self.accept()
    
    def get_selected_prompt(self):
        return self.selected_prompt
    
    def get_prompts_to_save(self):
        return self.prompts_to_save
