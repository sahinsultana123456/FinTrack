import csv
import os
from datetime import datetime
from services import get_user_transactions

def generate_report(user_id):
    """
    Generate a CSV report of all transactions for a given user_id.
    Returns the path to the generated CSV file.
    """
    transactions = get_user_transactions(user_id)
    if not transactions:
        return None  # or raise Exception("No transactions to report")

    # Create a reports directory if not exists
    reports_dir = 'reports'
    os.makedirs(reports_dir, exist_ok=True)

    # Filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"user_{user_id}_transactions_{timestamp}.csv"
    filepath = os.path.join(reports_dir, filename)

    # Write CSV file
    with open(filepath, mode='w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        # Write header
        writer.writerow(['Category', 'Amount', 'Day', 'Month', 'Year', 'Notes'])
        # Write transaction rows
        for row in transactions:
            writer.writerow(row)

    return filepath


