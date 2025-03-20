import re
import pandas as pd
from util import parse_amount, getFilePath, date_pattern
from datetime import datetime

# Regex patterns
keyword_pattern = re.compile(r"(?i)\b(konser|recording)\b")  # Matches "konser" or "recording"
amount_pattern = re.compile(r"(?i)(\d{1,3}(?:\.\d{3})*\s*rb)(?:\s+\w+)*\s+(cash|gopay|qris|bca)")
current_date = None  # Stores the last detected date

def extract_special_transactions(chat_file):
    special_data = []

    with open(chat_file, 'r', encoding='utf-8') as file:
        for line in file:
            date_match = date_pattern.search(line)
            if date_match:
                # Extract and format date
                day, month, year, _, _ = date_match.groups()
                current_date = datetime(int(year), int(month), int(day)).strftime("%d %B %Y")

            keyword_match = keyword_pattern.search(line)  # Find keyword: "konser" or "recording"
            amount_match = amount_pattern.search(line)   # Find amount + payment method
            
            if keyword_match and amount_match:
                keyword = keyword_match.group(1).capitalize()  # Get "Konser" or "Recording"
                amount, payment_method = amount_match.groups()
                amount_value = parse_amount(amount)

                # Structure data with separate columns for Konser & Recording
                special_data.append({
                    "Date": current_date,
                    "Description": line.strip(),
                    "Konser Amount" if keyword == "Konser" else "Recording Amount": amount_value,
                    "Konser Payment" if keyword == "Konser" else "Recording Payment": payment_method.upper()
                })

    return special_data

def save_to_excel(data):
    df = pd.DataFrame(data)

    # Ensure both "Konser" and "Recording" columns exist
    if "Konser Amount" not in df:
        df["Konser Amount"] = None
        df["Konser Payment"] = None
    if "Recording Amount" not in df:
        df["Recording Amount"] = None
        df["Recording Payment"] = None

    output_filename = "Konser_Recording_Report.xlsx"
    df.to_excel(output_filename, index=False)
    print(f"✅ Report saved as {output_filename}")

def main():
    chat_file = getFilePath()  # Get the path of the WhatsApp chat file
    special_transactions = extract_special_transactions(chat_file)
    
    if special_transactions:
        save_to_excel(special_transactions)
    else:
        print("No 'konser' or 'recording' transactions found.")

if __name__ == "__main__":
    main()