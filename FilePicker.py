from textual.screen import Screen
from textual.widgets import ListView, ListItem, Label
from textual.containers import Vertical
from platformdirs import user_downloads_dir
from pathlib import Path


class FilePickerScreen(Screen):
    BINDINGS = [("q", "app.pop_screen()", "Cancel")]

    def __init__(self, start_path: Path = None):
        super().__init__()
        self.current_dir = start_path or Path(user_downloads_dir())

    def compose(self):
        yield Vertical(
            Label(f"📁 {self.current_dir}", id="dir_label"),
            ListView(*self.get_dir_items(), id="file_list"),
        )

    def get_dir_items(self):
        items = []

        # Add special entries for up and cancel
        items.append(ListItem(Label("[⬆️  ..]", id="up", markup=False)))
        items.append(ListItem(Label("[❌ Cancel]", id="cancel", markup=False)))

        # List directories and PDF files, sorted by date
        for entry in sorted(
            self.current_dir.iterdir(),
            key=lambda e: (not e.is_dir(), -e.stat().st_mtime)
        ):
            if entry.is_dir() or entry.suffix.lower() == ".pdf":
                prefix = "[DIR] " if entry.is_dir() else ""
                items.append(ListItem(Label(f"{prefix}{entry.name}", markup=False)))
        return items

    def refresh_list(self):
        file_list = self.query_one(ListView)
        file_list.clear()
        for item in self.get_dir_items():
            file_list.append(item)
        self.query_one("#dir_label", Label).update(f"📁 {self.current_dir}")

    def on_list_view_selected(self, event: ListView.Selected):
        label: Label = event.item.query_one(Label)
        text = str(label.renderable)

        # Handle "up" (parent directory)
        if text == "[⬆️  ..]":
            if self.current_dir.parent != self.current_dir:
                self.current_dir = self.current_dir.parent
                self.refresh_list()
            return

        # Handle "cancel" (exit picker)
        if text == "[❌ Cancel]":
            self.app.pop_screen()
            return

        # Handle file selection (normal file or directory)
        is_dir = text.startswith("[DIR] ")
        name = text[6:] if is_dir else text
        path = self.current_dir / name

        if is_dir:
            self.current_dir = path
            self.refresh_list()
        else:
            self.dismiss(path.resolve())
