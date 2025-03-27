
from flask import Flask, render_template, request, send_file
from fpdf import FPDF
import os
import tempfile
import datetime

app = Flask(__name__)

def get_next_invoice_number():
    file_path = "invoice_counter.txt"
    if not os.path.exists(file_path):
        with open(file_path, "w") as f:
            f.write("A013000")
    with open(file_path, "r") as f:
        current = f.read().strip()
    prefix = current[:1]
    number = int(current[1:]) + 1
    new_number = f"{prefix}{number:06}"
    with open(file_path, "w") as f:
        f.write(new_number)
    return new_number

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        invoice_no = get_next_invoice_number()
        invoice_date = datetime.date.today().strftime("%Y-%m-%d")
        invoice_title = request.form.get("invoice_title")
        billed_by = request.form.get("billed_by")
        billed_to = request.form.get("billed_to")
        currency = request.form.get("currency")
        show_quantity = "show_quantity" in request.form
        show_rate = "show_rate" in request.form
        show_amount = "show_amount" in request.form

        items = []
        total = 0.0
        for i in range(1, 11):  # Up to 10 items
            item = request.form.get(f"item_{i}")
            quantity = request.form.get(f"quantity_{i}", type=float, default=0)
            rate = request.form.get(f"rate_{i}", type=float, default=0)
            note = request.form.get(f"note_{i}", "")
            if item:
                amount = quantity * rate
                total += amount
                items.append({
                    "item": item,
                    "quantity": quantity,
                    "rate": rate,
                    "amount": amount,
                    "note": note
                })

        class PDF(FPDF):
            def header(self):
                self.image("template_clean.jpg", x=0, y=0, w=210, h=297)

        pdf = PDF()
        pdf.add_page()
        pdf.set_y(35)
        pdf.set_font("Arial", "B", 16)
        pdf.set_text_color(0, 51, 102)
        pdf.cell(0, 10, f"{invoice_title} Invoice", ln=True, align="C")

        pdf.set_font("Arial", "B", 10)
        pdf.set_text_color(0)
        pdf.cell(0, 8, f"Invoice No: {invoice_no}", ln=True)
        pdf.cell(0, 8, f"Date: {invoice_date}", ln=True)

        pdf.set_y(pdf.get_y() + 5)
        pdf.set_fill_color(235, 235, 235)
        pdf.set_font("Arial", "B", 10)
        pdf.cell(95, 8, "Billed By", 1, 0, "C", True)
        pdf.cell(95, 8, "Billed To", 1, 1, "C", True)
        pdf.set_font("Arial", "", 10)
        pdf.multi_cell(95, 8, billed_by, border=1)
        x = pdf.get_x()
        y = pdf.get_y() - 16
        pdf.set_xy(x + 95, y)
        pdf.multi_cell(95, 8, billed_to, border=1)

        pdf.set_y(pdf.get_y() + 10)
        headers = ["Item"]
        if show_quantity: headers.append("Qty")
        if show_rate: headers.append("Rate")
        if show_amount: headers.append("Amount")

        col_width = 180 / len(headers)
        pdf.set_font("Arial", "B", 11)
        pdf.set_fill_color(220, 230, 250)
        for h in headers:
            pdf.cell(col_width, 8, h, 1, 0, "C", True)
        pdf.ln()

        pdf.set_font("Arial", "", 10)
        for idx, entry in enumerate(items, 1):
            row = [entry["item"]]
            if show_quantity: row.append(str(entry["quantity"]))
            if show_rate: row.append(f"{currency}{entry['rate']:.2f}")
            if show_amount: row.append(f"{currency}{entry['amount']:.2f}")
            for value in row:
                pdf.cell(col_width, 8, value, 1)
            pdf.ln()
            if entry["note"]:
                pdf.set_font("Arial", "I", 9)
                pdf.set_text_color(100)
                pdf.multi_cell(180, 6, f"   {entry['note']}", border=0)
                pdf.set_font("Arial", "", 10)
                pdf.set_text_color(0)

        pdf.set_y(pdf.get_y() + 5)
        pdf.set_font("Arial", "B", 11)
        pdf.cell(0, 10, f"Total: {currency}{total:.2f}", ln=True, align="R")
        pdf.set_font("Arial", "I", 9)
        pdf.set_text_color(80)
        pdf.cell(0, 6, "This invoice is valid for cash payment only.", ln=True, align="R")

        temp_path = tempfile.gettempdir()
        filename = os.path.join(temp_path, f"invoice_{invoice_no}.pdf")
        pdf.output(filename)
        return send_file(filename, as_attachment=True)

    return render_template("invoice_form.html")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
