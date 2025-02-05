import re

# Helper function to convert "75rb" to "75000"
def parse_amount(amount_text):
    if not amount_text:
        return 0
    compiled = re.compile(re.escape("rb"), re.IGNORECASE)
    is_rb_match = compiled.search(amount_text)
    amount_text = compiled.sub('', amount_text)
    int_amount = int(amount_text.replace('.', '').replace(' ', ''))
    if(is_rb_match):
        int_amount = int_amount*1000
    return int_amount

def add_sum(df):
    df_sum = df.sum()
    df_sum.name = 'Total'
    # Assign sum of all rows of DataFrame as a new row
    return df._append(df_sum.transpose())
    

date_pattern = re.compile(r"(\d{2})/(\d{2})/(\d{4}), (\d{2}):(\d{2})")  # Matches dd/mm/yyyy