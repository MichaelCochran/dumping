from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QMessageBox)
from PyQt5.QtCore import Qt


class AuthDialog(QDialog):
    def __init__(self, is_first_time: bool = False, parent=None):
        super().__init__(parent)
        self.is_first_time = is_first_time
        self.password = None
        self.setup_ui()
    
    def setup_ui(self):
        self.setWindowTitle("Authentication" if not self.is_first_time else "Setup")
        self.setModal(True)
        self.setMinimumWidth(350)
        
        layout = QVBoxLayout()
        
        if self.is_first_time:
            title_label = QLabel("Welcome! Create a password to secure your journal.")
            title_label.setWordWrap(True)
        else:
            title_label = QLabel("Enter your password to access your journal.")
            title_label.setWordWrap(True)
        
        layout.addWidget(title_label)
        layout.addSpacing(20)
        
        password_label = QLabel("Password:")
        layout.addWidget(password_label)
        
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.returnPressed.connect(self.handle_submit)
        layout.addWidget(self.password_input)
        
        if self.is_first_time:
            confirm_label = QLabel("Confirm Password:")
            layout.addWidget(confirm_label)
            
            self.confirm_input = QLineEdit()
            self.confirm_input.setEchoMode(QLineEdit.Password)
            self.confirm_input.returnPressed.connect(self.handle_submit)
            layout.addWidget(self.confirm_input)
        
        layout.addSpacing(20)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        if not self.is_first_time:
            cancel_btn = QPushButton("Cancel")
            cancel_btn.clicked.connect(self.reject)
            button_layout.addWidget(cancel_btn)
        
        submit_btn = QPushButton("Create" if self.is_first_time else "Login")
        submit_btn.setDefault(True)
        submit_btn.clicked.connect(self.handle_submit)
        button_layout.addWidget(submit_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        self.password_input.setFocus()
    
    def handle_submit(self):
        password = self.password_input.text()
        
        if not password:
            QMessageBox.warning(self, "Error", "Password cannot be empty.")
            return
        
        if self.is_first_time:
            confirm = self.confirm_input.text()
            if password != confirm:
                QMessageBox.warning(self, "Error", "Passwords do not match.")
                return
            
            if len(password) < 4:
                QMessageBox.warning(self, "Error", "Password must be at least 4 characters.")
                return
        
        self.password = password
        self.accept()
    
    def get_password(self) -> str:
        return self.password
