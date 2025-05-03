from textual.app import App, ComposeResult
from textual.containers import Vertical, Horizontal
from textual.widgets import (
    Button,
    Label,
    Input,
    Static,
    Select,
)
from textual.screen import ModalScreen
from textual.reactive import reactive
from textual import on

import fitz  # PyMuPDF
import os
from platformdirs import user_downloads_dir
from pathlib import Path

from datetime import datetime

from FilePicker import FilePickerScreen

FILE_DIR = Path(user_downloads_dir())

class PDFMarkerApp(App):
    CSS = """
    Screen {
        align: center middle;
        padding: 2;
    }
    #form {
        width: 70%;
        border: round $accent;
        padding: 2;
    }
    Input, Select {
        width: 100%;
    }
    """

    pdf_path = reactive("")
    show_extra_input = reactive(False)

    def compose(self) -> ComposeResult:
        yield Static("PDF Annotation Tool", id="title", classes="bold")

        with Vertical(id="form"):
            yield Button("Select PDF File", id="select_file")
            yield Label("No file selected", id="file_label")

            yield Label("État:")
            yield Select(options=[
                ("Payé", "Payé"),
                ("Remboursé", "Remboursé"),
                ("Annulé", "Annulé"),
            ], id="etat")

            yield Label("à:", id="text_label")
            yield Input(placeholder="à", id="text_input")

            yield Label("Date du payement:")
            yield Input(value=datetime.now().strftime("%d-%m-%y"), id="date_input")

            yield Label("via:")
            yield Select(options=[
                ("virement", "virement"),
                ("domiciliation", "domiciliation"),
                ("VISA", "VISA"),
                ("PayPal", "PayPal"),
                ("Liquide", "Liquide"),
            ], id="method")

            yield Label("Autre Note:")
            yield Input(placeholder="Note libre", id="note_input")

            with Horizontal():
                yield Button("Submit", id="submit", variant="success")
                yield Button("Cancel", id="cancel", variant="error")

    def on_mount(self):
        self.query_one("#text_input", Input).display = False
        self.query_one("#text_label", Label).display = False
    
    def set_pdf_path(self, path):
        self.pdf_path = str(path)  # Get the file path when popped
        if path:
            self.query_one("#file_label", Label).update(self.pdf_path)
        else:
            # Handle cancellation or no file selected
            self.query_one("#file_label", Label).update("No file selected")


    @on(Button.Pressed, "#select_file")
    async def open_file_picker(self):
        await self.push_screen(FilePickerScreen(FILE_DIR), callback=self.set_pdf_path)  # Push FilePickerScreen


    @on(Select.Changed, "#etat")
    def toggle_extra_input(self, event: Select.Changed):
        self.show_extra_input = event.value == "Remboursé"
        self.query_one("#text_input", Input).visible = self.show_extra_input

    @on(Button.Pressed, "#submit")
    def handle_submit(self):
        if not self.pdf_path:
            self.query_one("#file_label", Label).update("❌ No file selected")
            return

        file_name = os.path.basename(self.pdf_path).split(".")[0]
        file_dir = os.path.dirname(self.pdf_path)

        etat = self.query_one("#etat", Select).value
        date = self.query_one("#date_input", Input).value
        via = self.query_one("#method", Select).value
        note = self.query_one("#note_input", Input).value
        custom_text = self.query_one("#text_input", Input).value if self.show_extra_input else ""

        if etat == "Remboursé":
            text = f"{file_name} \n{etat} le {date} \nà {custom_text} \npar RIFT \nvia {via}"
        elif etat == "Annulé":
            text = f"{file_name} \n{etat} le {date} \npar NdC:"
        else:
            text = f"{file_name} \n{etat} le {date} \npar RIFT \nvia {via}"

        if note:
            text += f"\n{note}"

        rect = fitz.Rect(100, 100, 300, 150)
        self.annotate_pdf(file_dir, file_name, text, rect)

        self.query_one("#file_label", Label).update(f"✅ PDF saved!")

    def annotate_pdf(self, file_dir, file_name, text, rect):
        doc = fitz.open(f"{file_dir}/{file_name}.pdf")
        page = doc[0]
        width = page.rect.width
        point = fitz.Point(width / 2, 25)
        page.insert_text(point, text, fontname="helvetica-bold")
        highlights = page.search_for(text)
        page.add_highlight_annot(highlights)
        output_path = os.path.join(FILE_DIR, "marked_pdf", f"{file_name}.pdf")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        doc.save(output_path)
        doc.close()

    @on(Button.Pressed, "#cancel")
    def cancel_form(self):
        self.exit()

if __name__ == "__main__":
    end_path = os.path.join(FILE_DIR,"marked_pdf")
    if not os.path.exists(end_path):
        os.mkdir(end_path)
    PDFMarkerApp().run()
