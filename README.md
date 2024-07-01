# TD Canada Credit Card Statement Parser

This project consists of two Python scripts to parse TD Canada credit card statements from PDF files and convert them into a CSV file. The scripts have been tested only on TD Canada credit card statements.

## Disclaimer

This project was created using ChatGPT and has undergone minimal testing for accuracy. Use it at your own risk and verify the results for accuracy.

## How It Works

1. **parse_pdf.py**: This script processes all PDF statements in a specified folder and extracts the transaction data.
    - The PDF files contain readable text, so no OCR is needed.
    - The script searches each page for transaction data and creates a bounding box around the relevant section.
    - It then finds the row separators within the bounding box to identify individual transactions.
    - The date is extracted from the filename and is used by the other script to reconstruct the year for each transaction.

2. **parse_statements.py**: This script takes the extracted transaction data from a text file, parses it, and outputs a semicolon-delimited CSV file.
    - The script reads the input file and parses the transaction lines.
    - It extracts the transaction date, posting date, description, and amount.
    - The extracted dates are combined with the year parsed from the text file to form complete date fields.
    - The transactions are sorted by transaction date before being written to the output CSV file.

## Usage

1. **Extract data from PDF statements**

    ```sh
    python parse_pdf.py <folder> > statements.txt
    ```

    - `<folder>`: Path to the folder containing the PDF statements.
    - `statements.txt`: Output file where the extracted transaction data will be saved.

    Note: You may need to modifiy the filename parser code if your filenames are different.
    
2. **Convert extracted data to CSV**

    ```sh
    python parse_statements.py statements.txt > statements.csv
    ```

    - `statements.txt`: Input file containing the extracted transaction data.
    - `statements.csv`: Output CSV file with semicolon delimiter.

## Example

1. Extract data from PDF statements in the `statements` folder:

    ```sh
    python parse_pdf.py statements > statements.txt
    ```

2. Convert the extracted data to a semicolon-delimited CSV file:

    ```sh
    python parse_statements.py statements.txt > statements.csv
    ```

## Note

- The CSV file is semicolon (`;`) delimited to ensure that descriptions containing commas do not interfere with the column separation.

## Requirements

- Python 3.x
- PyMuPDF (fitz)

## Installation

You can install the required Python packages using pip:

```sh
pip install PyMuPDF
