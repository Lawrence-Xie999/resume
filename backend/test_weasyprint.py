from weasyprint import HTML
print("Starting WeasyPrint test...")
try:
    print("Creating HTML object...")
    html_obj = HTML('https://weasyprint.org/')
    print("Writing PDF...")
    html_obj.write_pdf('/tmp/weasyprint-website.pdf')
    print("PDF created successfully!")
except Exception as e:
    print(f"Error: {e}")