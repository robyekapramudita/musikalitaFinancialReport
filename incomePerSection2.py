import pandas as pd
import re
from util import parse_amount, add_sum, getFilePath, date_pattern
from datetime import datetime
from collections import defaultdict

section_patterns = {
    "LES": re.compile(r"(?i)\s*PEMASUKAN LES\s*"),
    "STUDIO": re.compile(r"(?i)\s*PEMASUKAN STUDIO\s*"),
    "JUALAN": re.compile(r"(?i)\s*PEMASUKAN JUALAN\s*")
}

end_section = re.compile(r"(?i)\s*TOTAL PEMASUKAN\s*")

amount_pattern = re.compile(r"(?i)(?:•|-)?\s*.*?(\d{1,3}(?:\.\d{3})*\s*rb)(?:\s+\w+)*\s+(cash|gopay|qris|bca)", re.IGNORECASE)

current_month = None
yearList = set()

def process_chat(chat_file):
    monthly_data = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
    should_check_amount = False
    current_section = None
    daily_section = defaultdict(int)

    with open(chat_file, 'r', encoding='utf-8') as file:
        for line in file:
            date_match = date_pattern.search(line)
            if date_match:
                day, month, year, hour, minute = date_match.groups()
                yearList.add(year)
                current_month = datetime(int(year), int(month), 1).strftime("%B %Y")
                date_str = datetime(int(year), int(month), int(day), int(hour), int(minute)).strftime("%d %B %Y %H:%M")
                
                daily_data = defaultdict(lambda: defaultdict(int))
                daily_section = defaultdict(int)
                daily_total = 0
            
            for method, pattern in section_patterns.items():
                if pattern.search(line):
                    if current_section:
                        daily_data.update(daily_section)
                    should_check_amount = True
                    daily_section = defaultdict(int)
                    current_section = method

            if end_section.search(line):
                should_check_amount = False
                daily_data.update(daily_section)
                current_section = None
            
            if should_check_amount:
                matches = amount_pattern.findall(line)
                for match in matches:
                    amount, payment_method = match
                    amount_value = parse_amount(amount)
                    payment_method = payment_method.upper() if payment_method else "UNKNOWN"
                    key = f"{current_section} - {payment_method}"
                    daily_section[key] += amount_value
                    daily_total += amount_value
            daily_data["TOTAL"] = daily_total
            monthly_data[current_month][date_str] = daily_data
    
    return monthly_data


def write_to_excel(data):
    writer = pd.ExcelWriter(f'sectionReport2{yearList.pop()}.xlsx')
    summary = defaultdict(lambda: defaultdict(int))
    
    for sheet, data in data.items():
        df = pd.DataFrame(data).T.fillna(0)
        df_sum = df.sum()
        df = add_sum(df)
        summary[sheet] = df_sum.to_dict()
        df.to_excel(writer, sheet_name=sheet, index=True)
    
    summary_df = pd.DataFrame(summary).T
    summary_df = add_sum(summary_df)
    summary_df.to_excel(writer, sheet_name="summary", index=True)
    writer.close()


def main():
    chat_file = getFilePath()  # Path to your exported WhatsApp chat file
    processed_data = process_chat(chat_file)
    write_to_excel(processed_data)


if __name__ == "__main__":
    main()
