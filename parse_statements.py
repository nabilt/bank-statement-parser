from datetime import datetime
import re
import sys

def parse_line(line, current_year):
    # Regular expression to extract the dates, description, and price (positive or negative)
    pattern = r"(\b[A-Z]{3} \d{1,2}\b)\s+(\b[A-Z]{3} \d{1,2}\b)\s+(.*?)\s+(-?\$\d{1,3}(?:,\d{3})*(?:\.\d{2})?)"
    match = re.search(pattern, line)
    if match:
        transaction_date = f"{match.group(1)} {current_year}"
        posting_date = f"{match.group(2)} {current_year}"
        description = match.group(3)
        price_str = match.group(4).replace(',', '')  # Remove commas from the price
        price = float(price_str.replace('$', ''))  # Convert to float
        # Convert dates to datetime objects
        transaction_date_obj = datetime.strptime(transaction_date, "%b %d %Y")
        posting_date_obj = datetime.strptime(posting_date, "%b %d %Y")
        return transaction_date_obj, posting_date_obj, description, price
    return None

def process_file(input_file):
    transactions = []
    total_balance = 0.0
    current_year = None

    with open(input_file, 'r') as file:
        for line in file:
            line = line.strip()
            if line.startswith("Date:"):
                month_year = re.search(r'Date:\s*(\w+)\s*(\d{4})', line)
                if month_year:
                    current_month = month_year.group(1)
                    current_year = int(month_year.group(2))
            else:
                if current_year:
                    parsed_line = parse_line(line, current_year)
                    if parsed_line:
                        transaction_date, posting_date, description, price = parsed_line
                        # Adjust year based on month logic
                        transaction_month = transaction_date.strftime("%b")
                        if current_month == "Dec" and transaction_month in ["Jan", "Feb"]:
                            adjusted_year = current_year + 1
                        elif current_month == "Jan" and transaction_month in ["Nov", "Dec"]:
                            adjusted_year = current_year - 1
                        else:
                            adjusted_year = current_year
                        transaction_date = transaction_date.replace(year=adjusted_year)
                        posting_date = posting_date.replace(year=adjusted_year)
                        
                        transactions.append({
                            "transaction_date": transaction_date,
                            "posting_date": posting_date,
                            "description": description,
                            "price": price
                        })
                        total_balance += price

    return transactions, total_balance

def main():
    if len(sys.argv) != 2:
        print("Usage: python process_statements.py <input_file>")
        sys.exit(1)
    
    input_file = sys.argv[1]

    transactions, total_balance = process_file(input_file)

    # Sort transactions by transaction_date
    transactions.sort(key=lambda t: t['transaction_date'], reverse=True)

    # Print sorted transactions
    for t in transactions:
        print(
            f"{t['transaction_date'].strftime('%b %d %Y')};{t['posting_date'].strftime('%b %d %Y')};{t['description']};{t['price']}"
        )

if __name__ == "__main__":
    main()
