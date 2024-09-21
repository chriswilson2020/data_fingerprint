import pandas as pd
import hashlib
import sys
import os
import csv
import warnings

def detect_decimal_separator(file_path, delimiter):
    """
    Detects the decimal separator in a CSV file by sampling numeric data.
    """
    decimal_separators = [',', '.']
    decimal_counts = {',': 0, '.': 0}

    with open(file_path, 'r', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile, delimiter=delimiter)
        # Skip header
        headers = next(reader, None)
        for _ in range(10):  # Sample first 10 data rows
            try:
                row = next(reader)
            except StopIteration:
                break
            if row:
                for value in row:
                    # Remove any non-digit characters except decimal separators
                    value_no_sep = ''.join(c for c in value if c.isdigit() or c in decimal_separators)
                    for sep in decimal_separators:
                        if sep in value_no_sep:
                            # Count decimal separators that are not thousands separators
                            parts = value_no_sep.split(sep)
                            if len(parts) == 2 and all(part.isdigit() for part in parts):
                                decimal_counts[sep] += 1
        # Determine the most frequent decimal separator
        if decimal_counts[','] > decimal_counts['.']:
            detected_decimal = ','
        else:
            detected_decimal = '.'
        print(f"Detected decimal separator: '{detected_decimal}'")
        return detected_decimal

def load_data(file_path):
    """
    Attempts to load a dataset from the given file path, trying multiple file formats.
    """
    df = None
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()
    try:
        if ext == '.csv':
            # Read a sample of the file to detect the delimiter
            with open(file_path, 'r', encoding='utf-8') as csvfile:
                sample = csvfile.read(2048)
                # Use Sniffer to detect the delimiter
                sniffer = csv.Sniffer()
                try:
                    dialect = sniffer.sniff(sample, delimiters=[',', ';', '\t', '|'])
                    delimiter = dialect.delimiter
                    print(f"Detected delimiter: '{delimiter}'")
                except csv.Error:
                    # Default to comma if Sniffer fails
                    delimiter = ','
                    print("Could not detect delimiter. Defaulting to comma.")

            # Detect decimal separator
            decimal_sep = detect_decimal_separator(file_path, delimiter)

            # Read the CSV with the detected delimiter and decimal separator
            df = pd.read_csv(file_path, delimiter=delimiter, decimal=decimal_sep)
            print(f"Loaded CSV with '{delimiter}' as delimiter and '{decimal_sep}' as decimal separator.")
        elif ext in ['.xlsx', '.xls']:
            df = pd.read_excel(file_path, decimal=',')
            print("Loaded Excel file.")
        elif ext == '.json':
            df = pd.read_json(file_path, convert_dates=False)
            print("Loaded JSON file.")
        elif ext == '.parquet':
            df = pd.read_parquet(file_path)
            print("Loaded Parquet file.")
        elif ext == '.feather':
            df = pd.read_feather(file_path)
            print("Loaded Feather file.")
        elif ext in ['.h5', '.hdf', '.hdf5']:
            df = pd.read_hdf(file_path)
            print("Loaded HDF5 file.")
        elif ext in ['.pkl', '.pickle']:
            df = pd.read_pickle(file_path)
            print("Loaded Pickle file.")
        elif ext == '.dta':
            df = pd.read_stata(file_path)
            print("Loaded Stata file.")
        elif ext == '.sas7bdat':
            df = pd.read_sas(file_path) # I can't test this without sas so I need help
            print("Loaded SAS file.")
        elif ext == '.sav':
            df = pd.read_spss(file_path)
            print("Loaded SPSS file.")
        elif ext == '.xml':
            df = pd.read_xml(file_path)
            print("Loaded XML file.")
        elif ext == '.html':
            df_list = pd.read_html(file_path)
            if df_list:
                df = df_list[0]
                print("Loaded HTML file.")
            else:
                raise ValueError("No tables found in HTML file.")
        else:
            # If extension is unknown, try to load it using common formats
            print("Unknown file extension. Attempting to read the file in common formats...")
            df = try_loading_with_guesses(file_path)
    except Exception as e:
        print(f"Error loading file based on extension: {e}")
        # If failed, try loading with guesses
        df = try_loading_with_guesses(file_path)
    if df is None:
        raise ValueError("Could not read the data file in any known format.")

    print(df.head())
    return df

def try_loading_with_guesses(file_path):
    """
    Try loading the file as various formats if the extension is unknown or incorrect.
    """
    loaders = [
        ("CSV", pd.read_csv),
        ("Excel", pd.read_excel),
        ("JSON", pd.read_json),
        ("XML", pd.read_xml),
        ("Parquet", pd.read_parquet),
        ("Feather", pd.read_feather),
        ("HDF5", pd.read_hdf),
        ("Pickle", pd.read_pickle),
        ("Stata", pd.read_stata),
        ("SAS", pd.read_sas),
        ("SPSS", pd.read_spss),
        ("HTML", lambda f: pd.read_html(f)[0] if pd.read_html(f) else None)
    ]

    for format_name, loader in loaders:
        try:
            if format_name == "CSV":
                # Use default delimiter and decimal
                df = pd.read_csv(file_path)
            elif format_name == "Excel":
                df = pd.read_excel(file_path, decimal=',')
            else:
                df = loader(file_path)
            if df is not None:
                print(f"Successfully loaded file as {format_name}.")
                return df
        except Exception as e:
            print(f"Failed to load file as {format_name}: {e}")
    return None

def standardize_datetime_columns(df, date_only=False):
    """
    Identifies datetime columns and standardizes their format.
    If date_only is True, formats to 'YYYY-MM-DD'. Otherwise, includes time.
    """
    # Identify columns with datetime data types
    datetime_cols = df.select_dtypes(include=['datetime', 'datetime64[ns]', 'datetimetz']).columns.tolist()

    # For object columns, attempt to parse as datetime
    object_cols = df.select_dtypes(include=['object']).columns.tolist()
    potential_datetime_cols = []

    # Define possible datetime formats
    datetime_formats = [
        '%Y-%m-%d %H:%M:%S',
        '%d-%m-%Y %H:%M:%S',
        '%Y-%m-%d %H:%M',
        '%d-%m-%Y %H:%M',
        '%Y-%m-%d',
        '%d-%m-%Y'
    ]

    # Attempt to parse object columns as datetime
    for col in object_cols:
        parsed_col = None
        for fmt in datetime_formats:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", category=UserWarning)
                try:
                    parsed_col = pd.to_datetime(df[col], format=fmt, errors='raise')
                    df[col] = parsed_col
                    potential_datetime_cols.append(col)
                    print(f"Parsed '{col}' as datetime with format '{fmt}'.")
                    break  # Stop if parsing is successful
                except Exception:
                    continue
        if parsed_col is None:
            # Try to parse without specifying the format
            parsed_col = pd.to_datetime(df[col], errors='coerce')
            if parsed_col.notnull().mean() >= 0.8:
                df[col] = parsed_col
                potential_datetime_cols.append(col)
                print(f"Parsed '{col}' as datetime using default inference.")

    # Combine detected datetime columns
    datetime_cols.extend(potential_datetime_cols)
    datetime_cols = list(set(datetime_cols))  # Remove duplicates if any

    # Standardize datetime formats
    date_format = '%Y-%m-%d' if date_only else '%Y-%m-%d %H:%M:%S'
    for col in datetime_cols:
        df[col] = df[col].dt.strftime(date_format)
        print(f"Standardized datetime column: {col}")

    return df

def generate_order_dependent_fingerprint(df):
    """
    Generates an order-dependent fingerprint of the DataFrame.
    """
    # Standardize datetime columns
    df = standardize_datetime_columns(df)
    # Ensure consistent column order
    df = df.reindex(sorted(df.columns), axis=1)
    # Reset index
    df = df.reset_index(drop=True)
    # Strip whitespace from string columns
    string_cols = df.select_dtypes(include=['object']).columns
    df[string_cols] = df[string_cols].apply(lambda x: x.str.strip())
    # Round numeric columns
    numeric_cols = df.select_dtypes(include=['float64', 'float32', 'int64', 'int32']).columns
    df[numeric_cols] = df[numeric_cols].round(6)
    # Convert all data to strings
    df = df.fillna('').astype(str)
    # Serialize data without index and header
    data_string = df.to_csv(index=False, header=False, lineterminator='\n')
    # Hash the serialized data using SHA-256
    hash_object = hashlib.sha256(data_string.encode('utf-8'))
    fingerprint = hash_object.hexdigest()
    return fingerprint

def generate_order_independent_fingerprint(df):
    """
    Generates an order-independent fingerprint of the DataFrame.
    """
    # Standardize datetime columns
    df = standardize_datetime_columns(df)
    # Reset index and sort columns to ensure consistent order
    df = df.reindex(sorted(df.columns), axis=1)
    df = df.reset_index(drop=True)
    # Strip whitespace from string columns
    string_cols = df.select_dtypes(include=['object']).columns
    df[string_cols] = df[string_cols].apply(lambda x: x.str.strip())
    # Round numeric columns
    numeric_cols = df.select_dtypes(include=['float64', 'float32', 'int64', 'int32']).columns
    df[numeric_cols] = df[numeric_cols].round(6)
    # Handle NaN values and convert all data to strings
    df = df.fillna('').astype(str)
    # Serialize each row into a string
    row_strings = df.apply(lambda row: ','.join(row.values), axis=1)
    # Hash each row individually
    row_hashes = row_strings.apply(lambda x: hashlib.sha256(x.encode('utf-8')).hexdigest())
    # Sort row hashes to ensure order-independence
    row_hashes = sorted(row_hashes)
    # Concatenate all row hashes
    concatenated_hashes = ''.join(row_hashes)
    # Generate final fingerprint
    final_hash = hashlib.sha256(concatenated_hashes.encode('utf-8')).hexdigest()
    return final_hash

def process_file_with_order_dependent_fingerprint(file_path):
    """
    Processes a file and returns its order-dependent fingerprint.
    """
    df = load_data(file_path)
    fingerprint = generate_order_dependent_fingerprint(df)
    return fingerprint

def process_file_with_order_independent_fingerprint(file_path):
    """
    Processes a file and returns its order-independent fingerprint.
    """
    df = load_data(file_path)
    fingerprint = generate_order_independent_fingerprint(df)
    return fingerprint

def main():
    print("Select fingerprinting mode:")
    print("1. Order-Dependent")
    print("2. Order-Independent")
    choice = input("Enter your choice (1 or 2): ")
    if choice not in ['1', '2']:
        print("Invalid choice.")
        sys.exit(1)
    file_path = input("Enter the file path of the dataset: ").strip()
    if not os.path.exists(file_path):
        print("File does not exist.")
        sys.exit(1)
    try:
        if choice == '1':
            fingerprint = process_file_with_order_dependent_fingerprint(file_path)
            print("Order-dependent fingerprint:", fingerprint)
        else:
            fingerprint = process_file_with_order_independent_fingerprint(file_path)
            print("Order-independent fingerprint:", fingerprint)
    except Exception as e:
        print("Error processing file:", e)
        sys.exit(1)

if __name__ == "__main__":
    main()
