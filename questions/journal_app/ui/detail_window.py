from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QTextEdit, QPushButton, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal
from datetime import datetime


class DetailWindow(QDialog):
    entry_updated = pyqtSignal(int)
    entry_deleted = pyqtSignal(int)
    
    def __init__(self, entry: dict, db_manager, parent=None):
        super().__init__(parent)
        self.entry = entry
        self.db_manager = db_manager
        self.is_editing = False
        self.setup_ui()
    
    def setup_ui(self):
        self.setWindowTitle("Entry Details")
        self.setMinimumSize(500, 400)
        
        layout = QVBoxLayout()
        
        date_str = self.entry['date'].strftime("%B %d, %Y, %I:%M %p")
        date_label = QLabel(f"Date: {date_str}")
        date_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(date_label)
        
        prompt_label = QLabel(f"Prompt: {self.entry['prompt']}")
        prompt_label.setWordWrap(True)
        prompt_label.setStyleSheet("font-style: italic; margin-bottom: 10px;")
        layout.addWidget(prompt_label)
        
        self.content_edit = QTextEdit()
        self.content_edit.setPlainText(self.entry['content'])
        self.content_edit.setReadOnly(True)
        layout.addWidget(self.content_edit)
        
        button_layout = QHBoxLayout()
        
        self.edit_btn = QPushButton("Edit")
        self.edit_btn.clicked.connect(self.toggle_edit_mode)
        button_layout.addWidget(self.edit_btn)
        
        self.delete_btn = QPushButton("Delete")
        self.delete_btn.clicked.connect(self.delete_entry)
        button_layout.addWidget(self.delete_btn)
        
        button_layout.addStretch()
        
        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self.save_entry)
        self.save_btn.setVisible(False)
        button_layout.addWidget(self.save_btn)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def toggle_edit_mode(self):
        self.is_editing = not self.is_editing
        self.content_edit.setReadOnly(not self.is_editing)
        self.edit_btn.setText("Cancel" if self.is_editing else "Edit")
        self.save_btn.setVisible(self.is_editing)
        
        if not self.is_editing:
            self.content_edit.setPlainText(self.entry['content'])
    
    def save_entry(self):
        new_content = self.content_edit.toPlainText()
        
        if not new_content.strip():
            QMessageBox.warning(self, "Error", "Entry content cannot be empty.")
            return
        
        success = self.db_manager.update_entry(self.entry['id'], new_content)
        
        if success:
            self.entry['content'] = new_content
            QMessageBox.information(self, "Success", "Entry updated successfully.")
            self.toggle_edit_mode()
            self.entry_updated.emit(self.entry['id'])
        else:
            QMessageBox.warning(self, "Error", "Failed to update entry.")
    
    def delete_entry(self):
        reply = QMessageBox.question(
            self, 
            "Confirm Delete",
            "Are you sure you want to delete this entry? This cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            success = self.db_manager.delete_entry(self.entry['id'])
            
            if success:
                QMessageBox.information(self, "Success", "Entry deleted successfully.")
                self.entry_deleted.emit(self.entry['id'])
                self.close()
            else:
                QMessageBox.warning(self, "Error", "Failed to delete entry.")
