import tkinter as tk
from tkinter import ttk, filedialog
from tkcalendar import DateEntry
import fitz  # PyMuPDF
import os

FILE_DIR = "C:\\Users\\Loïc\\Downloads"

def add_text_box_and_highlight(pdf_path, file_name, text, rect):
    doc = fitz.open(f"{pdf_path}/{file_name}.pdf")
    page1 = doc[0]
    width = page1.rect.width  # Get the width of the page
    p = fitz.Point(width/2, 25)  # start point of 1st line
    page1.insert_text(p, text, fontname="helvetica-bold",)
    text_space = page1.search_for(text)
    page1.add_highlight_annot(text_space)
    doc.save(f"{FILE_DIR}\\marked_pdf\\{file_name}.pdf")
    doc.close()

def submit():
    # Gather data from the GUI
    file_name = pdf_path.split("/")[-1].split(".")[0]
    print(file_name)
    file_dir = pdf_path.rsplit("/", maxsplit=1)[0]
    print(file_dir)
    custom_text = text_input.get() if text_input_visible.get() else ""
    combo1_value = combo1.get()
    date_value = date_entry.get()
    combo3_value = combo3.get()
    opt_text = text_input2.get()
    
    # Example: Use the gathered data
    rect = fitz.Rect(100, 100, 300, 150)  # Define the rectangle for highlighting
    if combo1_value == "Remboursé":
        text = f"{file_name} \n{combo1_value} le {date_value} \nà {custom_text} \npar RIFT \nvia {combo3_value}"
    else:
        text = f"{file_name}\n {combo1_value} le {date_value} \npar RIFT \nvia {combo3_value}"
    if opt_text != "":
        text = text+f"\n{opt_text}"
    add_text_box_and_highlight(file_dir, file_name, text, rect)

    reset_fields()

def reset_fields():
    # Reset all input fields
    text_input.delete(0, tk.END)
    combo1.set('')
    date_entry.set_date('')
    combo3.set('')
    text_input.grid_remove()
    text_label.grid_remove()
    text_input_visible.set(False)
    text_input2.set('')

def select_file():
    global pdf_path
    pdf_path = filedialog.askopenfilename(title="Select PDF File", filetypes=[("PDF files", "*.pdf")], initialdir=FILE_DIR)
    file_label.config(text=pdf_path if pdf_path else "No file selected")

def on_combo1_change(event):
    # Show text input only if "Reimburse" is selected
    if combo1.get() == "Remboursé":
        text_input.grid(column=3, row=2)
        text_label.grid(column=2, row=2)
        text_input_visible.set(True)
    else:
        text_input.grid_remove()
        text_label.grid_remove()
        text_input_visible.set(False)


# Set up the main application window
root = tk.Tk()
root.title("PDF Annotation Tool")

# File selection
pdf_path = ""
file_button = ttk.Button(root, text="Select PDF File", command=select_file)
file_button.grid(column=0, row=0, columnspan=2)

file_label = ttk.Label(root, text="No file selected")
file_label.grid(column=0, row=1, columnspan=2)

# Text Input Setup
text_input_visible = tk.BooleanVar(value=False)
text_label = ttk.Label(root, text="à:")
text_input = tk.Entry(root, width=40)

# Paid/Reimbursed/... combo box
ttk.Label(root, text="Payé ou Remboursé:").grid(column=0, row=2)
combo1 = ttk.Combobox(root, values=["Payé", "Remboursé"])
combo1.grid(column=1, row=2)
combo1.bind("<<ComboboxSelected>>", on_combo1_change)

# Date Entry
ttk.Label(root, text="Date du payement:").grid(column=0, row=3)
date_entry = DateEntry(root)
date_entry.grid(column=1, row=3)

# Payment Method
ttk.Label(root, text="via:").grid(column=0, row=5)
combo3 = ttk.Combobox(root, values=["virement", "domiciliation", "VISA", "PayPal", "Liquide"])
combo3.grid(column=1, row=5)

# Text Input
ttk.Label(root, text="Autre Note:").grid(column=0, row=6)
text_input2 = tk.Entry(root, width=40)
text_input2.grid(column=1, row=6)

# Submit Button
submit_button = ttk.Button(root, text="Submit", command=submit)
submit_button.grid(column=0, row=7, columnspan=2)



if __name__ == "__main__":
    end_path = os.path.join(FILE_DIR,"marked_pdf")
    if not os.path.exists(end_path):
        os.mkdir(end_path)
    # Start the GUI event loop
    root.mainloop()
