from flask import Flask, render_template, request, send_file
from fpdf import FPDF
import os
import tempfile
from datetime import datetime

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        invoice_type = request.form.get('invoice_type')
        billed_by = request.form.get('billed_by')
        billed_by_country = request.form.get('billed_by_country')
        billed_to = request.form.get('billed_to')
        billed_to_country = request.form.get('billed_to_country')
        invoice_no = request.form.get('invoice_no')
        invoice_date = request.form.get('invoice_date')
        currency = request.form.get('currency')

        items = []
        total = 0.0
        for i in range(1, 6):
            item = request.form.get(f'item_{i}')
            quantity = request.form.get(f'quantity_{i}')
            rate = request.form.get(f'rate_{i}')
            if item:
                quantity = int(quantity) if quantity else 0
                rate = float(rate) if rate else 0.0
                amount = quantity * rate if quantity and rate else 0.0
                total += amount
                items.append({
                    'item': item,
                    'quantity': quantity if quantity else '',
                    'rate': f"{currency}{rate:,.2f}" if rate else '',
                    'amount': f"{currency}{amount:,.2f}" if amount else ''
                })

        pdf = FPDF()
        pdf.add_page()
        pdf.image("template_clean.jpg", x=0, y=0, w=210, h=297)
        pdf.set_y(20)

        pdf.set_font("Arial", "B", 16)
        pdf.set_text_color(0, 51, 102)
        title = "Invoice" if invoice_type == "Invoice" else "Proforma Invoice"
        pdf.cell(0, 10, title, ln=True, align="C")

        pdf.set_font("Arial", size=10)
        pdf.set_y(35)
        pdf.cell(0, 10, f"Invoice No: {invoice_no}", ln=True)
        pdf.cell(0, 10, f"Date: {invoice_date}", ln=True)

        # Billed Info
        pdf.set_y(60)
        pdf.set_font("Arial", "B", 10)
        pdf.cell(95, 8, "Billed By:", border=1)
        pdf.cell(95, 8, "Billed To:", border=1, ln=True)

        pdf.set_font("Arial", size=10)
        pdf.cell(95, 8, billed_by, border=1)
        pdf.cell(95, 8, billed_to, border=1, ln=True)

        pdf.cell(95, 8, billed_by_country, border=1)
        pdf.cell(95, 8, billed_to_country, border=1, ln=True)

        # Table Header
        pdf.set_y(pdf.get_y() + 10)
        pdf.set_font("Arial", "B", 11)
        pdf.set_fill_color(87, 111, 230)
        pdf.set_text_color(255)
        pdf.cell(80, 8, "Item", border=1, fill=True)
        pdf.cell(30, 8, "Quantity", border=1, fill=True)
        pdf.cell(40, 8, "Rate", border=1, fill=True)
        pdf.cell(40, 8, "Amount", border=1, ln=True, fill=True)

        # Table Rows
        pdf.set_font("Arial", size=10)
        pdf.set_text_color(0)
        for row in items:
            pdf.cell(80, 8, row['item'], border=1)
            pdf.cell(30, 8, str(row['quantity']), border=1)
            pdf.cell(40, 8, row['rate'], border=1)
            pdf.cell(40, 8, row['amount'], border=1, ln=True)

        # Total
        pdf.set_font("Arial", "B", 11)
        pdf.cell(150, 8, "Total", border=1)
        pdf.cell(40, 8, f"{currency}{total:,.2f}", border=1, ln=True)

        # Footer Note
        pdf.set_font("Arial", "I", 9)
        pdf.set_text_color(80)
        pdf.cell(0, 6, "This invoice is valid for cash payment only.", ln=True, align="R")

        # Save PDF
        temp_dir = tempfile.gettempdir()
        filename = os.path.join(temp_dir, f"invoice_{invoice_no}.pdf")
        pdf.output(filename)
        return send_file(filename, as_attachment=True)

    return render_template('invoice_form.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
