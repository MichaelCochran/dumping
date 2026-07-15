import json
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Optional

import feedparser
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWebEngineWidgets import QWebEngineView


STATUSES = ["to do", "in-progress", "blocked", "done"]


@dataclass
class Attachment:
    id: str
    originalName: str
    storedFilename: str
    size: int
    uploadedAt: str


@dataclass
class Task:
    id: str
    title: str
    description: str
    poc: str
    status: str
    attachments: List[Attachment]
    createdAt: str
    updatedAt: str
    dueDate: Optional[str] = None
    completedAt: Optional[str] = None
    archived: bool = False
    archivedAt: Optional[str] = None


@dataclass
class NewsSource:
    id: str
    name: str
    url: str
    type: str  # 'rss' | 'api'


@dataclass
class NewsItem:
    id: str
    title: str
    link: str
    summary: str
    publishedAt: str
    sourceId: str
    sourceName: str
    categories: List[str]


def get_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent


def get_data_paths():
    base_dir = get_base_dir()
    data_dir = base_dir / "data"
    tasks_file = data_dir / "tasks.json"
    attachments_dir = data_dir / "attachments"
    data_dir.mkdir(parents=True, exist_ok=True)
    attachments_dir.mkdir(parents=True, exist_ok=True)
    return data_dir, tasks_file, attachments_dir


NEWS_SOURCES: List[NewsSource] = [
    NewsSource(
        id="the-hacker-news",
        name="The Hacker News",
        url="https://thehackernews.com/feeds/posts/default",
        type="rss",
    ),
    NewsSource(
        id="bleeping-computer",
        name="BleepingComputer",
        url="https://www.bleepingcomputer.com/feed/",
        type="rss",
    ),
    NewsSource(
        id="securityweek",
        name="SecurityWeek",
        url="https://www.securityweek.com/feed",
        type="rss",
    ),
    NewsSource(
        id="cisa-alerts",
        name="CISA Alerts",
        url="https://www.cisa.gov/cybersecurity-advisories/all.xml",
        type="rss",
    ),
    NewsSource(
        id="dod-news",
        name="DoD Cyber News",
        url="https://www.defense.gov/DesktopModules/ArticleCS/RSS.ashx?ContentType=1&Site=945&max=20",
        type="rss",
    ),
]


CATEGORY_RULES = [
    {
        "category": "web-app-hacking",
        "keywords": [
            "xss",
            "sql injection",
            "rce",
            "csrf",
            "deserialization",
            "web application",
            "web app",
        ],
    },
    {
        "category": "new-tools",
        "keywords": [
            "tool",
            "framework",
            "released",
            "introduces",
            "launches",
            "open-source",
            "open source",
        ],
    },
    {
        "category": "gov-defense",
        "keywords": [
            "dod",
            "department of defense",
            "us army",
            "us air force",
            "pentagon",
            "cisa",
            "federal",
            "government",
            "dow",
            "department of war",
        ],
    },
    {
        "category": "vulnerabilities",
        "keywords": [
            "cve-",
            "vulnerability",
            "zero-day",
            "0-day",
            "patch tuesday",
            "security update",
        ],
    },
    {
        "category": "malware-ransomware",
        "keywords": [
            "ransomware",
            "malware",
            "trojan",
            "botnet",
            "phishing",
        ],
    },
]


def categorize_news(title: str, summary: str, source: NewsSource) -> List[str]:
    text = f"{title} {summary}".lower()
    categories: set[str] = set()

    # Special-case certain sources as gov/defense
    if source.id in {"cisa-alerts", "dod-news"}:
        categories.add("gov-defense")

    for rule in CATEGORY_RULES:
        if any(kw in text for kw in rule["keywords"]):
            categories.add(rule["category"])

    if not categories:
        categories.add("general")

    return list(categories)


def fetch_all_news(limit_per_source: int = 25) -> List[NewsItem]:
    items: List[NewsItem] = []

    for source in NEWS_SOURCES:
        if source.type != "rss":
            continue
        try:
            feed = feedparser.parse(source.url)
            for entry in feed.entries[:limit_per_source]:
                title = getattr(entry, "title", "Untitled")
                link = getattr(entry, "link", "")
                summary = getattr(entry, "summary", getattr(entry, "description", ""))
                # published_parsed may be missing
                published = getattr(entry, "published", None) or getattr(entry, "updated", None)
                if published and hasattr(entry, "published_parsed") and entry.published_parsed:
                    dt = datetime(*entry.published_parsed[:6])
                    published_at = dt.isoformat() + "Z"
                else:
                    published_at = datetime.utcnow().isoformat() + "Z"

                categories = categorize_news(title, summary, source)

                item = NewsItem(
                    id=f"{source.id}:{title}:{published_at}",
                    title=title,
                    link=link,
                    summary=summary,
                    publishedAt=published_at,
                    sourceId=source.id,
                    sourceName=source.name,
                    categories=categories,
                )
                items.append(item)
        except Exception:
            continue

    items.sort(key=lambda x: x.publishedAt, reverse=True)
    return items


def load_tasks() -> List[Task]:
    _, tasks_file, _ = get_data_paths()
    if not tasks_file.exists():
        return []
    try:
        raw = tasks_file.read_text(encoding="utf-8")
        if not raw.strip():
            return []
        data = json.loads(raw)
        if not isinstance(data, list):
            return []
        tasks: List[Task] = []
        for item in data:
            attachments = [
                Attachment(
                    id=a.get("id", ""),
                    originalName=a.get("originalName", ""),
                    storedFilename=a.get("storedFilename", ""),
                    size=a.get("size", 0),
                    uploadedAt=a.get("uploadedAt", ""),
                )
                for a in item.get("attachments", [])
            ]
            tasks.append(
                Task(
                    id=item.get("id", ""),
                    title=item.get("title", ""),
                    description=item.get("description", ""),
                    poc=item.get("poc", ""),
                    status=item.get("status", "to do"),
                    attachments=attachments,
                    createdAt=item.get("createdAt", datetime.utcnow().isoformat() + "Z"),
                    updatedAt=item.get("updatedAt", datetime.utcnow().isoformat() + "Z"),
                    dueDate=item.get("dueDate"),
                    completedAt=item.get("completedAt"),
                    archived=item.get("archived", False),
                    archivedAt=item.get("archivedAt"),
                )
            )
        return tasks
    except Exception:
        return []


def save_tasks(tasks: List[Task]) -> None:
    _, tasks_file, _ = get_data_paths()
    try:
        serialisable = []
        for t in tasks:
            serialisable.append(
                {
                    "id": t.id,
                    "title": t.title,
                    "description": t.description,
                    "poc": t.poc,
                    "status": t.status,
                    "attachments": [
                        {
                            "id": a.id,
                            "originalName": a.originalName,
                            "storedFilename": a.storedFilename,
                            "size": a.size,
                            "uploadedAt": a.uploadedAt,
                        }
                        for a in t.attachments
                    ],
                    "createdAt": t.createdAt,
                    "updatedAt": t.updatedAt,
                    "dueDate": t.dueDate,
                    "completedAt": t.completedAt,
                    "archived": t.archived,
                    "archivedAt": t.archivedAt,
                }
            )
        tasks_file.write_text(json.dumps(serialisable, indent=2), encoding="utf-8")
    except Exception:
        pass


class TaskCard(QtWidgets.QFrame):
    def __init__(
        self,
        task: Task,
        on_status_change,
        on_view,
        on_edit,
        on_archive,
        on_delete,
        on_manage_attachments,
        on_selection_changed=None,
        parent=None,
    ):
        super().__init__(parent)
        self.task = task
        self.on_status_change = on_status_change
        self.on_view = on_view
        self.on_edit = on_edit
        self.on_archive = on_archive
        self.on_delete = on_delete
        self.on_manage_attachments = on_manage_attachments
        self.on_selection_changed = on_selection_changed

        self.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)

        title_row = QtWidgets.QHBoxLayout()
        
        self.select_checkbox = QtWidgets.QCheckBox()
        self.select_checkbox.stateChanged.connect(self.on_checkbox_changed)
        title_row.addWidget(self.select_checkbox)
        
        title_label = QtWidgets.QLabel(task.title or "(no title)")
        title_font = title_label.font()
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setWordWrap(True)
        title_row.addWidget(title_label, stretch=1)
        
        layout.addLayout(title_row)

        if task.poc:
            poc_label = QtWidgets.QLabel(f"POC: {task.poc}")
            layout.addWidget(poc_label)

        # Attachments summary (only if there are any)
        att_count = len(task.attachments)
        if att_count:
            attachments_row = QtWidgets.QHBoxLayout()
            attachments_row.addWidget(QtWidgets.QLabel(f"Attachments: {att_count}"))
            attachments_row.addStretch(1)
            layout.addLayout(attachments_row)

        # Status + actions row
        btn_row = QtWidgets.QHBoxLayout()

        # Status dropdown (Move...)
        status_menu = QtWidgets.QMenu(self)
        for st in STATUSES:
            if st == task.status:
                continue
            action = status_menu.addAction(st.replace("-", " ").title())
            action.triggered.connect(lambda _, s=st: self.change_status(s))

        status_btn = QtWidgets.QToolButton()
        status_btn.setText("Move...")
        status_btn.setPopupMode(QtWidgets.QToolButton.ToolButtonPopupMode.InstantPopup)
        status_btn.setMenu(status_menu)
        status_btn.setToolButtonStyle(QtCore.Qt.ToolButtonStyle.ToolButtonTextOnly)
        status_btn.setFixedWidth(90)
        btn_row.addWidget(status_btn)

        # Actions dropdown (View/Edit/Attach/Archive/Delete)
        actions_menu = QtWidgets.QMenu(self)
        view_action = actions_menu.addAction("View")
        view_action.triggered.connect(self.view_task)
        edit_action = actions_menu.addAction("Edit")
        edit_action.triggered.connect(self.edit_task)
        attach_action = actions_menu.addAction("Attach")
        attach_action.triggered.connect(self.manage_attachments)
        archive_action = actions_menu.addAction("Archive")
        archive_action.triggered.connect(self.archive_task)
        delete_action = actions_menu.addAction("Delete")
        delete_action.triggered.connect(self.delete_task)

        actions_btn = QtWidgets.QToolButton()
        actions_btn.setText("Actions")
        actions_btn.setPopupMode(QtWidgets.QToolButton.ToolButtonPopupMode.InstantPopup)
        actions_btn.setMenu(actions_menu)
        actions_btn.setToolButtonStyle(QtCore.Qt.ToolButtonStyle.ToolButtonTextOnly)
        actions_btn.setFixedWidth(90)
        btn_row.addWidget(actions_btn)

        # push buttons to the left, keep spacing flexible
        btn_row.addStretch(1)

        layout.addLayout(btn_row)

    def change_status(self, new_status: str):
        if callable(self.on_status_change):
            self.on_status_change(self.task, new_status)

    def view_task(self):
        if callable(self.on_view):
            self.on_view(self.task)

    def edit_task(self):
        if callable(self.on_edit):
            self.on_edit(self.task)

    def delete_task(self):
        if callable(self.on_delete):
            self.on_delete(self.task)

    def archive_task(self):
        if callable(self.on_archive):
            self.on_archive(self.task)

    def manage_attachments(self):
        if callable(self.on_manage_attachments):
            self.on_manage_attachments(self.task)
    
    def on_checkbox_changed(self, state):
        if callable(self.on_selection_changed):
            self.on_selection_changed(self.task, state == QtCore.Qt.CheckState.Checked.value)
    
    def set_selected(self, selected: bool):
        self.select_checkbox.setChecked(selected)
    
    def is_selected(self) -> bool:
        return self.select_checkbox.isChecked()


class EditTaskDialog(QtWidgets.QDialog):
    def __init__(self, task: Task, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Task")
        self.task = task

        layout = QtWidgets.QFormLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)

        self.title_edit = QtWidgets.QLineEdit(task.title)
        self.poc_edit = QtWidgets.QLineEdit(task.poc)
        self.desc_edit = QtWidgets.QPlainTextEdit(task.description)

        self.status_combo = QtWidgets.QComboBox()
        for st in STATUSES:
            self.status_combo.addItem(st.replace("-", " ").title(), st)
        idx = STATUSES.index(task.status) if task.status in STATUSES else 0
        self.status_combo.setCurrentIndex(idx)

        # Due date editor
        self.due_date_edit = QtWidgets.QDateEdit()
        self.due_date_edit.setCalendarPopup(True)
        self.due_date_edit.setDisplayFormat("yyyy-MM-dd")
        if task.dueDate:
            try:
                y, m, d = map(int, task.dueDate.split("-"))
                self.due_date_edit.setDate(QtCore.QDate(y, m, d))
            except Exception:
                self.due_date_edit.setDate(QtCore.QDate.currentDate())
        else:
            self.due_date_edit.setDate(QtCore.QDate.currentDate())

        layout.addRow("Title:", self.title_edit)
        layout.addRow("POC:", self.poc_edit)
        layout.addRow("Description:", self.desc_edit)
        layout.addRow("Status:", self.status_combo)
        layout.addRow("Due Date:", self.due_date_edit)

        btn_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.StandardButton.Ok
            | QtWidgets.QDialogButtonBox.StandardButton.Cancel
        )
        btn_box.accepted.connect(self.accept)
        btn_box.rejected.connect(self.reject)
        layout.addRow(btn_box)

    def apply_changes(self):
        self.task.title = self.title_edit.text().strip()
        self.task.poc = self.poc_edit.text().strip()
        self.task.description = self.desc_edit.toPlainText().strip()
        if self.due_date_edit.date().isValid():
            self.task.dueDate = self.due_date_edit.date().toString("yyyy-MM-dd")
        else:
            self.task.dueDate = None
        new_status = self.status_combo.currentData()
        return new_status


class ViewTaskDialog(QtWidgets.QDialog):
    def __init__(self, task: Task, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Task Details")

        layout = QtWidgets.QFormLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)

        def fmt(text: str) -> str:
            return text or "(none)"

        def fmt_dt(value: Optional[str]) -> str:
            if not value:
                return "(none)"
            try:
                dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
                return dt.strftime("%y-%m-%d %H:%M")
            except Exception:
                return value

        layout.addRow("Title:", QtWidgets.QLabel(fmt(task.title)))
        layout.addRow("POC:", QtWidgets.QLabel(fmt(task.poc)))
        layout.addRow("Status:", QtWidgets.QLabel(task.status.replace("-", " ").title()))

        desc = QtWidgets.QPlainTextEdit(task.description or "")
        desc.setReadOnly(True)
        desc.setFixedHeight(120)
        layout.addRow("Description:", desc)

        layout.addRow("Created At:", QtWidgets.QLabel(fmt_dt(task.createdAt)))
        layout.addRow("Updated At:", QtWidgets.QLabel(fmt_dt(task.updatedAt)))
        layout.addRow("Due Date:", QtWidgets.QLabel(fmt(task.dueDate or "")))
        layout.addRow("Completed At:", QtWidgets.QLabel(fmt_dt(task.completedAt or "")))
        layout.addRow("Archived:", QtWidgets.QLabel("Yes" if task.archived else "No"))
        layout.addRow("Archived At:", QtWidgets.QLabel(fmt_dt(task.archivedAt or "")))

        layout.addRow("Attachments:", QtWidgets.QLabel(str(len(task.attachments))))

        btn_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.StandardButton.Close)
        btn_box.rejected.connect(self.reject)
        btn_box.accepted.connect(self.accept)
        layout.addRow(btn_box)


class BoardTab(QtWidgets.QWidget):
    def __init__(self, tasks: List[Task], on_tasks_changed, parent=None):
        super().__init__(parent)
        self.tasks = tasks
        self.on_tasks_changed = on_tasks_changed
        self.selected_tasks = set()
        self.task_cards = {}

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(8)

        # Quick add area
        form_layout = QtWidgets.QVBoxLayout()

        top_row = QtWidgets.QHBoxLayout()
        self.title_edit = QtWidgets.QLineEdit()
        self.poc_edit = QtWidgets.QLineEdit()

        top_row.addWidget(QtWidgets.QLabel("Title:"))
        top_row.addWidget(self.title_edit)
        top_row.addWidget(QtWidgets.QLabel("POC:"))
        top_row.addWidget(self.poc_edit)

        form_layout.addLayout(top_row)

        bottom_row = QtWidgets.QHBoxLayout()
        self.desc_edit = QtWidgets.QPlainTextEdit()
        self.desc_edit.setPlaceholderText("Description")
        self.desc_edit.setFixedHeight(60)
        bottom_row.addWidget(self.desc_edit, stretch=1)

        # Due date with calendar popup + text entry
        self.due_date_edit = QtWidgets.QDateEdit()
        self.due_date_edit.setCalendarPopup(True)
        self.due_date_edit.setDisplayFormat("yyyy-MM-dd")
        self.due_date_edit.setDate(QtCore.QDate.currentDate())
        self.due_date_edit.setMinimumWidth(110)
        bottom_row.addWidget(self.due_date_edit)

        add_button = QtWidgets.QPushButton("Add Task")
        add_button.clicked.connect(self.add_task)
        bottom_row.addWidget(add_button)

        form_layout.addLayout(bottom_row)

        main_layout.addLayout(form_layout)
        
        batch_actions_row = QtWidgets.QHBoxLayout()
        
        select_all_btn = QtWidgets.QPushButton("Select All")
        select_all_btn.clicked.connect(self.select_all_tasks)
        batch_actions_row.addWidget(select_all_btn)
        
        deselect_all_btn = QtWidgets.QPushButton("Deselect All")
        deselect_all_btn.clicked.connect(self.deselect_all_tasks)
        batch_actions_row.addWidget(deselect_all_btn)
        
        self.selected_count_label = QtWidgets.QLabel("Selected: 0")
        batch_actions_row.addWidget(self.selected_count_label)
        
        batch_actions_row.addStretch(1)
        
        delete_selected_btn = QtWidgets.QPushButton("Delete Selected")
        delete_selected_btn.clicked.connect(self.delete_selected_tasks)
        batch_actions_row.addWidget(delete_selected_btn)
        
        move_selected_btn = QtWidgets.QToolButton()
        move_selected_btn.setText("Move Selected")
        move_selected_menu = QtWidgets.QMenu(self)
        for st in STATUSES:
            action = move_selected_menu.addAction(st.replace("-", " ").title())
            action.triggered.connect(lambda _, s=st: self.move_selected_tasks(s))
        move_selected_btn.setMenu(move_selected_menu)
        move_selected_btn.setPopupMode(QtWidgets.QToolButton.ToolButtonPopupMode.InstantPopup)
        batch_actions_row.addWidget(move_selected_btn)
        
        main_layout.addLayout(batch_actions_row)

        # Columns area
        columns_layout = QtWidgets.QHBoxLayout()
        self.column_widgets = {}

        for status in STATUSES:
            col_widget = QtWidgets.QWidget()
            col_layout = QtWidgets.QVBoxLayout(col_widget)
            col_layout.setContentsMargins(4, 4, 4, 4)
            col_layout.setSpacing(4)

            header_label = QtWidgets.QLabel(status.replace("-", " ").title())
            header_font = header_label.font()
            header_font.setBold(True)
            header_label.setFont(header_font)
            col_layout.addWidget(header_label)

            scroll_area = QtWidgets.QScrollArea()
            scroll_area.setWidgetResizable(True)
            inner = QtWidgets.QWidget()
            inner_layout = QtWidgets.QVBoxLayout(inner)
            inner_layout.setContentsMargins(0, 0, 0, 0)
            inner_layout.setSpacing(4)
            scroll_area.setWidget(inner)

            col_layout.addWidget(scroll_area)

            columns_layout.addWidget(col_widget)
            self.column_widgets[status] = inner

        main_layout.addLayout(columns_layout)

        self.refresh()

    def refresh(self):
        # Clear columns (remove widgets and stretches)
        self.task_cards.clear()
        for inner in self.column_widgets.values():
            layout = inner.layout()
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()

        # Add cards in current task order
        for task in self.tasks:
            if task.archived:
                continue
            inner = self.column_widgets.get(task.status)
            if inner is None:
                continue
            card = TaskCard(
                task,
                self.change_status,
                self.view_task,
                self.edit_task,
                self.archive_task,
                self.delete_task,
                self.manage_attachments,
                self.on_task_selection_changed,
            )
            self.task_cards[task.id] = card
            inner.layout().addWidget(card)

        # One stretch at the bottom so cards stay packed at top
        for inner in self.column_widgets.values():
            inner.layout().addStretch(1)
        
        self.update_selected_count()

    def add_task(self):
        title = self.title_edit.text().strip()
        if not title:
            return
        poc = self.poc_edit.text().strip()
        description = self.desc_edit.toPlainText().strip()
        due_date_str = None
        if self.due_date_edit.date().isValid():
            due_date_str = self.due_date_edit.date().toString("yyyy-MM-dd")
        now = datetime.utcnow().isoformat() + "Z"
        new_task = Task(
            id=f"pyqt-{int(datetime.utcnow().timestamp() * 1000)}",
            title=title,
            description=description,
            poc=poc,
            status="to do",
            attachments=[],
            createdAt=now,
            updatedAt=now,
            dueDate=due_date_str,
            completedAt=None,
            archived=False,
            archivedAt=None,
        )
        # Insert at the front so new tasks appear at the top of the column
        self.tasks.insert(0, new_task)
        save_tasks(self.tasks)
        self.title_edit.clear()
        self.poc_edit.clear()
        self.desc_edit.clear()
        self.due_date_edit.setDate(QtCore.QDate.currentDate())
        self.refresh()
        if callable(self.on_tasks_changed):
            self.on_tasks_changed()

    def change_status(self, task: Task, new_status: str):
        if task.status == new_status:
            return
        now = datetime.utcnow().isoformat() + "Z"
        old_status = task.status
        task.status = new_status
        if old_status != "done" and new_status == "done":
            task.completedAt = now
        elif old_status == "done" and new_status != "done":
            task.completedAt = None
        task.updatedAt = now
        save_tasks(self.tasks)
        self.refresh()
        if callable(self.on_tasks_changed):
            self.on_tasks_changed()

    def edit_task(self, task: Task):
        dialog = EditTaskDialog(task, self)
        if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            old_status = task.status
            new_status = dialog.apply_changes()
            now = datetime.utcnow().isoformat() + "Z"
            # Update status and completedAt consistent with backend rules
            if new_status not in STATUSES:
                new_status = old_status
            task.status = new_status
            if old_status != "done" and new_status == "done":
                task.completedAt = now
            elif old_status == "done" and new_status != "done":
                task.completedAt = None
            task.updatedAt = now
            save_tasks(self.tasks)
            self.refresh()
            if callable(self.on_tasks_changed):
                self.on_tasks_changed()

    def archive_task(self, task: Task):
        if task.archived:
            return
        now = datetime.utcnow().isoformat() + "Z"
        task.archived = True
        task.archivedAt = now
        task.updatedAt = now
        save_tasks(self.tasks)
        self.refresh()
        if callable(self.on_tasks_changed):
            self.on_tasks_changed()

    def view_task(self, task: Task):
        dialog = ViewTaskDialog(task, self)
        dialog.exec()

    def delete_task(self, task: Task):
        reply = QtWidgets.QMessageBox.question(
            self,
            "Delete Task",
            f"Are you sure you want to delete this task?\n\n{task.title}",
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No,
        )
        if reply != QtWidgets.QMessageBox.StandardButton.Yes:
            return

        # Remove from list (and optionally could delete attachment files here)
        self.tasks = [t for t in self.tasks if t.id != task.id]
        save_tasks(self.tasks)
        self.refresh()
        if callable(self.on_tasks_changed):
            self.on_tasks_changed()

    def manage_attachments(self, task: Task):
        dialog = AttachmentsDialog(task, self)
        if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            # Attachments may have changed
            save_tasks(self.tasks)
            self.refresh()
            if callable(self.on_tasks_changed):
                self.on_tasks_changed()
    
    def on_task_selection_changed(self, task: Task, selected: bool):
        if selected:
            self.selected_tasks.add(task.id)
        else:
            self.selected_tasks.discard(task.id)
        self.update_selected_count()
    
    def update_selected_count(self):
        count = len(self.selected_tasks)
        self.selected_count_label.setText(f"Selected: {count}")
    
    def select_all_tasks(self):
        for task in self.tasks:
            if not task.archived:
                self.selected_tasks.add(task.id)
                card = self.task_cards.get(task.id)
                if card:
                    card.set_selected(True)
        self.update_selected_count()
    
    def deselect_all_tasks(self):
        self.selected_tasks.clear()
        for card in self.task_cards.values():
            card.set_selected(False)
        self.update_selected_count()
    
    def delete_selected_tasks(self):
        if not self.selected_tasks:
            QtWidgets.QMessageBox.information(
                self,
                "No Selection",
                "Please select at least one task to delete."
            )
            return
        
        count = len(self.selected_tasks)
        reply = QtWidgets.QMessageBox.question(
            self,
            "Delete Selected Tasks",
            f"Are you sure you want to delete {count} selected task(s)?",
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No,
        )
        if reply != QtWidgets.QMessageBox.StandardButton.Yes:
            return
        
        self.tasks = [t for t in self.tasks if t.id not in self.selected_tasks]
        self.selected_tasks.clear()
        save_tasks(self.tasks)
        self.refresh()
        if callable(self.on_tasks_changed):
            self.on_tasks_changed()
    
    def move_selected_tasks(self, new_status: str):
        if not self.selected_tasks:
            QtWidgets.QMessageBox.information(
                self,
                "No Selection",
                "Please select at least one task to move."
            )
            return
        
        now = datetime.utcnow().isoformat() + "Z"
        for task in self.tasks:
            if task.id in self.selected_tasks:
                old_status = task.status
                task.status = new_status
                if old_status != "done" and new_status == "done":
                    task.completedAt = now
                elif old_status == "done" and new_status != "done":
                    task.completedAt = None
                task.updatedAt = now
        
        self.selected_tasks.clear()
        save_tasks(self.tasks)
        self.refresh()
        if callable(self.on_tasks_changed):
            self.on_tasks_changed()


class AttachmentsDialog(QtWidgets.QDialog):
    def __init__(self, task: Task, parent=None):
        super().__init__(parent)
        self.task = task
        self.setWindowTitle("Attachments")

        self.data_dir, self.tasks_file, self.attachments_dir = get_data_paths()

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(6)

        self.list_widget = QtWidgets.QListWidget()
        layout.addWidget(self.list_widget)

        btn_row = QtWidgets.QHBoxLayout()
        add_btn = QtWidgets.QPushButton("Add")
        open_btn = QtWidgets.QPushButton("Open")
        delete_btn = QtWidgets.QPushButton("Delete")
        close_btn = QtWidgets.QPushButton("Close")
        btn_row.addWidget(add_btn)
        btn_row.addWidget(open_btn)
        btn_row.addWidget(delete_btn)
        btn_row.addStretch(1)
        btn_row.addWidget(close_btn)
        layout.addLayout(btn_row)

        add_btn.clicked.connect(self.add_attachment)
        open_btn.clicked.connect(self.open_selected)
        delete_btn.clicked.connect(self.delete_selected)
        close_btn.clicked.connect(self.accept)

        self.refresh_list()

    def refresh_list(self):
        self.list_widget.clear()
        for att in self.task.attachments:
            name = att.originalName or att.storedFilename
            size_kb = att.size / 1024 if att.size else 0
            item = QtWidgets.QListWidgetItem(f"{name} ({size_kb:.1f} KB)")
            item.setData(QtCore.Qt.ItemDataRole.UserRole, att)
            self.list_widget.addItem(item)

    def add_attachment(self):
        from PyQt6.QtWidgets import QFileDialog

        file_path, _ = QFileDialog.getOpenFileName(self, "Select attachment")
        if not file_path:
            return

        try:
            src = Path(file_path)
            stored_filename = f"{int(datetime.utcnow().timestamp() * 1000)}_{src.name}"
            dest = self.attachments_dir / stored_filename
            shutil.copy2(src, dest)

            att = Attachment(
                id=f"att-{int(datetime.utcnow().timestamp() * 1000)}",
                originalName=src.name,
                storedFilename=stored_filename,
                size=dest.stat().st_size,
                uploadedAt=datetime.utcnow().isoformat() + "Z",
            )
            self.task.attachments.append(att)
            self.refresh_list()
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Error", f"Failed to add attachment:\n{e}")

    def _current_attachment(self) -> Optional[Attachment]:
        item = self.list_widget.currentItem()
        if not item:
            return None
        return item.data(QtCore.Qt.ItemDataRole.UserRole)

    def open_selected(self):
        att = self._current_attachment()
        if not att:
            return
        path = self.attachments_dir / att.storedFilename
        if not path.exists():
            QtWidgets.QMessageBox.warning(self, "Missing file", f"File not found:\n{path}")
            return
        try:
            os.startfile(str(path))
        except AttributeError:
            try:
                if sys.platform == "darwin":
                    subprocess.run(["open", str(path)], check=False)
                else:
                    subprocess.run(["xdg-open", str(path)], check=False)
            except Exception as e:
                QtWidgets.QMessageBox.warning(self, "Error", f"Could not open file:\n{e}")

    def delete_selected(self):
        att = self._current_attachment()
        if not att:
            return
        reply = QtWidgets.QMessageBox.question(
            self,
            "Delete Attachment",
            f"Delete attachment '{att.originalName}'?",
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No,
        )
        if reply != QtWidgets.QMessageBox.StandardButton.Yes:
            return

        path = self.attachments_dir / att.storedFilename
        if path.exists():
            try:
                path.unlink()
            except Exception:
                pass

        self.task.attachments = [a for a in self.task.attachments if a.id != att.id]
        self.refresh_list()


class MetricsTab(QtWidgets.QWidget):
    def __init__(self, tasks: List[Task], parent=None):
        super().__init__(parent)
        self.tasks = tasks

        layout = QtWidgets.QFormLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)

        self.active_label = QtWidgets.QLabel("-")
        self.archived_label = QtWidgets.QLabel("-")
        self.completed7_label = QtWidgets.QLabel("-")
        self.completed30_label = QtWidgets.QLabel("-")
        self.avg_cycle_label = QtWidgets.QLabel("-")

        layout.addRow("Active tasks:", self.active_label)
        layout.addRow("Archived tasks:", self.archived_label)
        layout.addRow("Completed last 7 days:", self.completed7_label)
        layout.addRow("Completed last 30 days:", self.completed30_label)
        layout.addRow("Average cycle time (days):", self.avg_cycle_label)

        self.refresh()

    def refresh(self):
        now = datetime.utcnow()
        sec_in_day = 24 * 60 * 60
        active = 0
        archived = 0
        c7 = 0
        c30 = 0
        cycles = []

        for t in self.tasks:
            if t.archived:
                archived += 1
            else:
                active += 1

            if t.completedAt:
                try:
                    completed_dt = datetime.fromisoformat(t.completedAt.replace("Z", "+00:00"))
                except Exception:
                    continue
                days_ago = (now - completed_dt.replace(tzinfo=None)).total_seconds() / sec_in_day
                if days_ago <= 7:
                    c7 += 1
                if days_ago <= 30:
                    c30 += 1

                if t.createdAt:
                    try:
                        created_dt = datetime.fromisoformat(t.createdAt.replace("Z", "+00:00"))
                        cycle = (
                            completed_dt.replace(tzinfo=None) - created_dt.replace(tzinfo=None)
                        ).total_seconds() / sec_in_day
                        if cycle >= 0:
                            cycles.append(cycle)
                    except Exception:
                        pass

        avg_cycle = sum(cycles) / len(cycles) if cycles else 0.0

        self.active_label.setText(str(active))
        self.archived_label.setText(str(archived))
        self.completed7_label.setText(str(c7))
        self.completed30_label.setText(str(c30))
        self.avg_cycle_label.setText(f"{avg_cycle:.1f}")


class WebViewDialog(QtWidgets.QDialog):
    def __init__(self, url: str, title: str = "Article Viewer", parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(1000, 700)
        
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        toolbar = QtWidgets.QHBoxLayout()
        toolbar.setContentsMargins(8, 8, 8, 8)
        
        self.back_btn = QtWidgets.QPushButton("←")
        self.back_btn.setFixedWidth(40)
        self.back_btn.clicked.connect(self.go_back)
        toolbar.addWidget(self.back_btn)
        
        self.forward_btn = QtWidgets.QPushButton("→")
        self.forward_btn.setFixedWidth(40)
        self.forward_btn.clicked.connect(self.go_forward)
        toolbar.addWidget(self.forward_btn)
        
        self.refresh_btn = QtWidgets.QPushButton("⟳")
        self.refresh_btn.setFixedWidth(40)
        self.refresh_btn.clicked.connect(self.reload_page)
        toolbar.addWidget(self.refresh_btn)
        
        self.url_label = QtWidgets.QLabel(url)
        self.url_label.setStyleSheet("padding: 4px; background: #1a1a1a; border-radius: 3px;")
        toolbar.addWidget(self.url_label, stretch=1)
        
        self.open_external_btn = QtWidgets.QPushButton("Open in Browser")
        self.open_external_btn.clicked.connect(lambda: self.open_external(url))
        toolbar.addWidget(self.open_external_btn)
        
        close_btn = QtWidgets.QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        toolbar.addWidget(close_btn)
        
        layout.addLayout(toolbar)
        
        self.web_view = QWebEngineView()
        self.web_view.setUrl(QtCore.QUrl(url))
        self.web_view.urlChanged.connect(self.update_url_label)
        layout.addWidget(self.web_view)
        
        self.update_navigation_buttons()
    
    def go_back(self):
        if self.web_view.history().canGoBack():
            self.web_view.back()
        self.update_navigation_buttons()
    
    def go_forward(self):
        if self.web_view.history().canGoForward():
            self.web_view.forward()
        self.update_navigation_buttons()
    
    def reload_page(self):
        self.web_view.reload()
    
    def update_url_label(self, url):
        self.url_label.setText(url.toString())
        self.update_navigation_buttons()
    
    def update_navigation_buttons(self):
        self.back_btn.setEnabled(self.web_view.history().canGoBack())
        self.forward_btn.setEnabled(self.web_view.history().canGoForward())
    
    def open_external(self, url):
        import webbrowser
        webbrowser.open(url)


class NewsCard(QtWidgets.QFrame):
    def __init__(self, news_item: NewsItem, parent=None):
        super().__init__(parent)
        self.news_item = news_item
        
        self.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(6)
        
        header_row = QtWidgets.QHBoxLayout()
        
        try:
            dt = datetime.fromisoformat(news_item.publishedAt.replace("Z", "+00:00"))
            date_str = dt.strftime("%m-%d")
        except Exception:
            date_str = "N/A"
        
        date_label = QtWidgets.QLabel(date_str)
        date_font = date_label.font()
        date_font.setBold(True)
        date_label.setFont(date_font)
        header_row.addWidget(date_label)
        
        header_row.addStretch(1)
        
        source_label = QtWidgets.QLabel(news_item.sourceName)
        source_label.setStyleSheet("color: #888;")
        header_row.addWidget(source_label)
        
        layout.addLayout(header_row)
        
        title_label = QtWidgets.QLabel(news_item.title)
        title_font = title_label.font()
        title_font.setBold(True)
        title_font.setPointSize(title_font.pointSize() + 1)
        title_label.setFont(title_font)
        title_label.setWordWrap(True)
        layout.addWidget(title_label)
        
        if news_item.summary:
            summary_text = news_item.summary[:200] + "..." if len(news_item.summary) > 200 else news_item.summary
            summary_label = QtWidgets.QLabel(summary_text)
            summary_label.setWordWrap(True)
            summary_label.setStyleSheet("color: #aaa;")
            layout.addWidget(summary_label)
        
        if news_item.categories:
            cats_str = ", ".join([c.replace("-", " ").title() for c in news_item.categories])
            cats_label = QtWidgets.QLabel(cats_str)
            cats_label.setStyleSheet("color: #0078d7; font-size: 10pt;")
            layout.addWidget(cats_label)
        
        self.setMinimumHeight(120)
        self.setMaximumHeight(200)
    
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            dialog = WebViewDialog(self.news_item.link, self.news_item.title, self.parent())
            dialog.exec()
        super().mousePressEvent(event)


class NewsTab(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.all_items: List[NewsItem] = []

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        controls = QtWidgets.QHBoxLayout()

        self.source_combo = QtWidgets.QComboBox()
        self.source_combo.addItem("All sources", "")
        for src in NEWS_SOURCES:
            self.source_combo.addItem(src.name, src.id)
        controls.addWidget(QtWidgets.QLabel("Source:"))
        controls.addWidget(self.source_combo)

        self.category_combo = QtWidgets.QComboBox()
        self.category_combo.addItem("All categories", "")
        for cat in [
            "web-app-hacking",
            "new-tools",
            "gov-defense",
            "vulnerabilities",
            "malware-ransomware",
            "general",
        ]:
            self.category_combo.addItem(cat.replace("-", " ").title(), cat)
        controls.addWidget(QtWidgets.QLabel("Category:"))
        controls.addWidget(self.category_combo)

        self.search_edit = QtWidgets.QLineEdit()
        self.search_edit.setPlaceholderText("Search title or summary")
        controls.addWidget(self.search_edit, stretch=1)

        self.refresh_button = QtWidgets.QPushButton("Refresh")
        controls.addWidget(self.refresh_button)

        layout.addLayout(controls)

        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.cards_container = QtWidgets.QWidget()
        self.cards_layout = QtWidgets.QGridLayout(self.cards_container)
        self.cards_layout.setContentsMargins(0, 0, 0, 0)
        self.cards_layout.setSpacing(8)
        
        scroll_area.setWidget(self.cards_container)
        layout.addWidget(scroll_area)

        self.refresh_button.clicked.connect(self.refresh_news)
        self.source_combo.currentIndexChanged.connect(self.apply_filters)
        self.category_combo.currentIndexChanged.connect(self.apply_filters)
        self.search_edit.textChanged.connect(self.apply_filters)

        self.refresh_news()

    def refresh_news(self):
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.CursorShape.WaitCursor)
        try:
            self.all_items = fetch_all_news(limit_per_source=25)
        finally:
            QtWidgets.QApplication.restoreOverrideCursor()
        self.apply_filters()

    def apply_filters(self):
        source_id = self.source_combo.currentData()
        category_id = self.category_combo.currentData()
        query = self.search_edit.text().strip().lower()

        filtered: List[NewsItem] = []
        for item in self.all_items:
            if source_id and item.sourceId != source_id:
                continue
            if category_id and category_id not in item.categories:
                continue
            if query:
                text = f"{item.title} {item.summary}".lower()
                if query not in text:
                    continue
            filtered.append(item)

        while self.cards_layout.count():
            item = self.cards_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        for idx, news_item in enumerate(filtered):
            card = NewsCard(news_item)
            row = idx // 2
            col = idx % 2
            self.cards_layout.addWidget(card, row, col)
        
        self.cards_layout.setRowStretch(len(filtered) // 2 + 1, 1)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cyber Dashboard (PyQt)")
        self.resize(1200, 700)

        self.tasks: List[Task] = load_tasks()

        central = QtWidgets.QWidget()
        self.setCentralWidget(central)

        layout = QtWidgets.QVBoxLayout(central)

        title_label = QtWidgets.QLabel("Cyber Dashboard")
        font = title_label.font()
        font.setPointSize(font.pointSize() + 2)
        font.setBold(True)
        title_label.setFont(font)
        layout.addWidget(title_label)

        self.tabs = QtWidgets.QTabWidget()
        layout.addWidget(self.tabs)

        self.board_tab = BoardTab(self.tasks, on_tasks_changed=self.on_tasks_changed)
        self.metrics_tab = MetricsTab(self.tasks)
        self.news_tab = NewsTab()

        self.tabs.addTab(self.board_tab, "Board")
        self.tabs.addTab(self.metrics_tab, "Metrics")
        self.tabs.addTab(self.news_tab, "News")

    def on_tasks_changed(self):
        self.metrics_tab.refresh()


def apply_dark_palette(app: QtWidgets.QApplication):
    app.setStyle("Fusion")
    palette = QtGui.QPalette()

    palette.setColor(QtGui.QPalette.ColorRole.Window, QtGui.QColor(30, 30, 30))
    palette.setColor(QtGui.QPalette.ColorRole.WindowText, QtCore.Qt.GlobalColor.white)
    palette.setColor(QtGui.QPalette.ColorRole.Base, QtGui.QColor(25, 25, 25))
    palette.setColor(QtGui.QPalette.ColorRole.AlternateBase, QtGui.QColor(45, 45, 45))
    palette.setColor(QtGui.QPalette.ColorRole.ToolTipBase, QtCore.Qt.GlobalColor.white)
    palette.setColor(QtGui.QPalette.ColorRole.ToolTipText, QtCore.Qt.GlobalColor.white)
    palette.setColor(QtGui.QPalette.ColorRole.Text, QtCore.Qt.GlobalColor.white)
    palette.setColor(QtGui.QPalette.ColorRole.Button, QtGui.QColor(45, 45, 45))
    palette.setColor(QtGui.QPalette.ColorRole.ButtonText, QtCore.Qt.GlobalColor.white)
    palette.setColor(QtGui.QPalette.ColorRole.BrightText, QtCore.Qt.GlobalColor.red)
    palette.setColor(QtGui.QPalette.ColorRole.Highlight, QtGui.QColor(0, 120, 215))
    palette.setColor(QtGui.QPalette.ColorRole.HighlightedText, QtCore.Qt.GlobalColor.white)

    app.setPalette(palette)


def main():
    app = QtWidgets.QApplication(sys.argv)
    apply_dark_palette(app)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
