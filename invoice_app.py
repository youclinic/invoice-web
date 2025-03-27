from flask import Flask, render_template, request, send_file
from fpdf import FPDF
import os
import tempfile
from datetime import datetime

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        invoice_type = request.form.get('invoice_type', 'Invoice')
        billed_by_name = request.form.get('billed_by_name', '')
        billed_by_country = request.form.get('billed_by_country', '')
        billed_to_name = request.form.get('billed_to_name', '')
        billed_to_country = request.form.get('billed_to_country', '')
        currency_symbol = request.form.get('currency', '$')
        show_quantity = request.form.get('show_quantity') == 'on'
        show_rate = request.form.get('show_rate') == 'on'

        items = []
        total = 0
        for i in range(1, 11):
            item = request.form.get(f'item_{i}')
            quantity = request.form.get(f'quantity_{i}')
            rate = request.form.get(f'rate_{i}')
            note = request.form.get(f'note_{i}')
            if item:
                quantity = int(quantity) if quantity else 1
                rate = float(rate) if rate else 0
                amount = quantity * rate
                total += amount
                items.append({
                    'name': item,
                    'quantity': quantity,
                    'rate': rate,
                    'amount': amount
                    'note': note
                })

        pdf = FPDF()
        pdf.add_page()
        pdf.image("template_clean.jpg", x=0, y=0, w=210, h=297)

        pdf.set_y(35)
        pdf.set_font("Arial", "B", 16)
        pdf.set_text_color(0, 51, 102)
        pdf.cell(0, 10, f"Proforma Invoice" if invoice_type == "Proforma" else "Invoice", ln=True, align="C")

        pdf.set_font("Arial", size=10)
        pdf.set_y(45)
        pdf.cell(0, 10, f"Invoice No: A{datetime.now().strftime('%y%m%d%H%M')}", ln=True)
        pdf.set_y(40)
        pdf.cell(0, 10, f"Date: {datetime.now().strftime('%Y-%m-%d')}", ln=True)

        pdf.set_y(60)
        pdf.set_font("Arial", "B", 10)
        pdf.cell(95, 7, "Billed By:", 1)
        pdf.cell(95, 7, "Billed To:", 1, ln=True)

        pdf.set_font("Arial", size=10)
        pdf.cell(95, 7, billed_by_name, 1)
        pdf.cell(95, 7, billed_to_name, 1, ln=True)
        pdf.cell(95, 7, billed_by_country, 1)
        pdf.cell(95, 7, billed_to_country, 1, ln=True)

        pdf.set_y(pdf.get_y() + 10)
        pdf.set_font("Arial", "B", 10)
        pdf.set_fill_color(80, 100, 200)
        pdf.set_text_color(255)

        col_widths = [90]
        headers = ["Item"]
        if show_quantity:
            headers.append("Quantity")
            col_widths.append(25)
        if show_rate:
            headers.append("Rate")
            col_widths.append(35)
        headers.append("Amount")
        col_widths.append(40)

        for i, header in enumerate(headers):
            pdf.cell(col_widths[i], 8, header, 1, 0, 'C', True)
        pdf.ln()

        pdf.set_text_color(0)
        pdf.set_font("Arial", size=10)
        for item in items:
            pdf.cell(col_widths[0], 8, item['name'], 1)
            col_idx = 1
            if show_quantity:
                pdf.cell(col_widths[col_idx], 8, str(item['quantity']), 1, 0, 'C')
                col_idx += 1
            if show_rate:
                pdf.cell(col_widths[col_idx], 8, f"{currency_symbol}{item['rate']:.2f}", 1, 0, 'C')
                col_idx += 1
            pdf.cell(col_widths[col_idx], 8, f"{currency_symbol}{item['amount']:.2f}", 1, 0, 'C')
            pdf.ln()
            if item.get('note'):
                pdf.set_font("Arial", "I", 9)
                pdf.set_text_color(80)
                pdf.multi_cell(0, 6, f"   {item['note']}", border=0)
                pdf.set_font("Arial", size=10)
                pdf.set_text_color(0)

        pdf.set_font("Arial", "B", 10)
        pdf.cell(sum(col_widths[:-1]), 8, "Total", 1)
        pdf.cell(col_widths[-1], 8, f"{currency_symbol}{total:.2f}", 1, ln=True)

        temp_dir = tempfile.gettempdir()
        filename = os.path.join(temp_dir, f"invoice_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf")
        pdf.output(filename)
        return send_file(filename, as_attachment=True)

    return render_template('invoice_form.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
