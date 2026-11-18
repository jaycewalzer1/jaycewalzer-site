# Rent Roll OCR

As CTO of OM-Analyzer (May–Jul 2024) I built a commercial real estate platform in Python and Flask. Its core turned offering memorandums into a tenant comps database. Brokers' PDFs often hold the rent roll as a scanned image with no text to copy, laid out differently by every broker.

You drag a PDF into the web app. It goes to S3 through a presigned upload, then the server finds the rent-roll page. It renders that page at 300 dpi, sharpens it, boosts the contrast and runs Tesseract. A cleaning pass drops note and boilerplate lines and keeps the lines that carry a dollar amount. It splits those lines at known tenant names, with anchor tenants held to their own rent thresholds. Each row is rebuilt from the OCR fragments: "1" "850" becomes 1,850 square feet, the lease end is matched to a 3, 5 or 10-year term, and rent per square foot is checked against annual rent. Rows land in a per-user master Excel sheet, with the property's address checked against a US ZIP table.

In the demo, a scanned seven-tenant rent roll goes in and seven complete rows come out. The sample is synthetic, and it ran locally against mocked AWS.

stack: Python, Flask, Tesseract OCR, PyMuPDF, openpyxl, pandas, AWS S3 and Cognito, Stripe, Docker
links: https://github.com/jaycewalzer1/rr-tool2
