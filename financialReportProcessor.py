import pandas as pd
import re
from util import parse_amount, add_sum, getFilePath, date_pattern
from datetime import datetime
from collections import defaultdict

# Regex patterns for dates and payment method lines
payment_patterns = {
    "BCA": re.compile(r"(?i)•\s*BCA\s*:\s*(\b\d{1,7}(?:\.\d{3})*(?:\s*rb)?\b)?\s*"),
    "QRIS": re.compile(r"(?i)•\s*QRIS\s*:\s*(\b\d{1,7}(?:\.\d{3})*(?:\s*rb)?\b)?\s*"),
    "CASH": re.compile(r"(?i)•\s*CASH\s*:\s*(\b\d{1,7}(?:\.\d{3})*(?:\s*rb)?\b)?\s*"),
    "GOPAY": re.compile(r"(?i)•\s*GOPAY\s*:\s*(\b\d{1,7}(?:\.\d{3})*(?:\s*rb)?\b)?\s*")
}

current_month = None
yearList = set()

# Function to process the chat data
def process_chat_data(chat_file):
    monthly_data = defaultdict(lambda: defaultdict(int))
    
    with open(chat_file, 'r', encoding='utf-8') as file:      
        for line in file:
            # Example line: "01/01/2023, TOTAL PEMASUKAN: BCA: 1000, QRIS: 2000, CASH: 3000, GOPAY: 4000"
            date_match = date_pattern.search(line)
            if date_match:
                day, month, year, hour, minute = date_match.groups()
                yearList.add(year)
                current_month = datetime(int(year), int(month), 1).strftime("%B %Y")
                date_str = datetime(int(year), int(month), int(day), int(hour), int(minute)).strftime("%d %B %Y %H:%M")

                daily_data = defaultdict(lambda: defaultdict(int))
                daily_total = 0

            for method, pattern in payment_patterns.items():
              match = pattern.search(line)
              if match:
                  amount_text = match.group(1)
                  amount_value = parse_amount(amount_text) if amount_text else 0
                  daily_data[method] = amount_value
                  daily_total += amount_value
              daily_data["TOTAL"] = daily_total
            monthly_data[current_month][date_str] = daily_data

    return monthly_data

# Function to write data to Excel
def write_to_excel(monthly_data):
    writer = pd.ExcelWriter(f'report{yearList.pop()}.xlsx')
    summary = defaultdict(lambda: defaultdict(int))
    for sheet,data in monthly_data.items():
        df = pd.DataFrame(data).T.iloc[:, [1, 2, 3, 4, 0]]
        df_sum = df.sum()
        # Assign sum of all rows of DataFrame as a new row
        df = add_sum(df)
        summary[sheet] = df_sum.to_dict()
        df.to_excel(writer, sheet_name=sheet,index=True)
    summary_df = pd.DataFrame(summary).T
    # Assign sum of all rows of DataFrame as a new row
    summary_df = add_sum(summary_df)
    summary_df.to_excel(writer, sheet_name="summary", index=True)
    writer.close()

# Main execution
if __name__ == "__main__":
    chat_file = getFilePath() # Path to your exported WhatsApp chat file
    monthly_data = process_chat_data(chat_file)
    # print(monthly_data)
    write_to_excel(monthly_data)