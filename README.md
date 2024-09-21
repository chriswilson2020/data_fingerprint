## Dataset Fingerprint Generator

A Python script to generate unique fingerprints for datasets, supporting multiple file formats. The script can generate both order-dependent and order-independent fingerprints, allowing you to verify data integrity and detect changes in your datasets.

### Features:

* Supports Multiple File Formats: Automatically detects and loads data from various file formats.
* Standardizes Datetime Columns: Converts datetime columns to a consistent ISO 8601 format.
* Generates Unique Fingerprints:
* Order-Dependent: Sensitive to the order of rows and columns.
* Order-Independent: Independent of the order of rows and columns.

### Supported File Formats:

* CSV (comma-separated and semicolon-separated)
* Excel (`.xlsx`, `.xls`)
* JSON
* Parquet
* Feather
* HDF5 (`.h5`, `.hdf`, `.hdf5`)
* Pickle (`.pkl`, `.pickle`)
* Stata (`.dta`)
* SAS (`.sas7bdat`)
* SPSS (`.sav`)
* XML
* HTML

#### Validation Status:

##### Each file format is validated against five different senarios:

1. Standard csv file with `'` delimiter and `.` as decimal separator
2. European style csv file with `;` delimiter and `,` decimal separator
3. Mixed date formats throughout the file
4. Missing data points distribtuted throughout the file
5. No headers on the columns and a strange delimiter `^`

|File Format| Validation Status|Notes|
|---|---|---|
|.csv|Validated|All Pass|
|.xlsx|Validated|All Pass|
|.json|Validated|All Pass|
|.xml|Partial Validation|Fails without header (Expected behaviour)|
|.html|Fails Validation|Fails Mixed Date Formats|
|.h5|Fails Validation|All Pass|
|.dta|Fails Validation|All Pass|
|.feather|Fails Validation|All Pass|
|.parquet|Fails Validation|All Pass|
|.pkl|Fails Validation|All Pass|

*Note: .xml fails due to expected behaviours of the file format use with caution*

### Installation:

#### Prerequisites:
* Python 3.x
* pip (Python package installer)

Install Required Packages:
The script relies on several Python packages to handle different file formats. <br>
Install all required packages using the following command: `pip install pandas pyarrow tables pyreadstat lxml html5lib`

#### Package Breakdown:

* pandas: Main library for data manipulation and analysis.
* pyarrow: Required for reading Parquet and Feather files.
* tables: Needed for reading HDF5 files.
* pyreadstat: Enables reading of SAS, SPSS, and Stata files.
* lxml and html5lib: Required for reading XML and HTML files.

##### Additional Notes
csv, warnings, xml.etree.ElementTree, and pickle are part of Python's standard library and do not require installation.

### Installation Steps:
Clone the Repository or Download the Script:
```
git clone https://github.com/yourusername/dataset-fingerprint-generator.git
```

Navigate to the Directory
```
cd dataset-fingerprint-generator
```

#### Install Dependencies:
Install all the required Python packages:
```
pip install pandas pyarrow tables pyreadstat lxml html5lib
```

If you encounter permission issues, you may need to use --user or run the command with sudo (on Unix-based systems):
`pip install --user pandas pyarrow tables pyreadstat lxml html5lib`

### Usage:

Run the script from the command line:
```
python dataset_fingerprint.py
```

Follow the on-screen prompts:

#### Select Fingerprinting Mode:
Enter 1 for Order-Dependent fingerprint.
Enter 2 for Order-Independent fingerprint.
#### Enter the File Path:
Provide the path to your dataset file when prompted.

#### Example:
##### Step-by-Step Usage

Run the Script:
`python dataset_fingerprint.py`

Select Fingerprinting Mode
```
Select fingerprinting mode:
1. Order-Dependent
2. Order-Independent
Enter your choice (1 or 2):
```

Enter the File Path
```
Enter the file path of the dataset: data/sample_dataset.csv
```
Output
```
Loaded CSV with comma separator.
Standardized datetime column: date_column
Order-dependent fingerprint: a1b2c3d4e5f67890abcdef1234567890abcdef1234567890abcdef1234567890
```

### How It Works

#### Order-Dependent Fingerprint
Purpose: Detects any changes in the dataset, including the order of rows and columns.
##### Process:
Standardizes datetime columns to ISO 8601 format.
Serializes the DataFrame to a CSV string without headers and indexes.
Computes the SHA-256 hash of the serialized data.
#### Order-Independent Fingerprint
Purpose: Detects changes in data values, ignoring the order of rows and columns.
##### Process:
Resets index and sorts columns alphabetically.
Standardizes datetime columns to ISO 8601 format.
Fills NaN values and converts all data to strings.
Hashes each row individually using SHA-256.
Sorts the row hashes to ensure order independence.
Concatenates the sorted hashes and computes a final SHA-256 hash.

### Functions Explained

* `load_data(file_path)` <br>
Attempts to load the dataset from the provided file path, handling multiple file formats based on the file extension.
* `try_loading_with_guesses(file_path)` <br>
If the initial loading based on file extension fails, this function attempts to read the file using all supported formats.
* `standardize_datetime_columns(df)` <br>
Identifies and standardizes datetime columns to the ISO 8601 format (YYYY-MM-DD HH:MM:SS).
* `generate_order_dependent_fingerprint(df)` <br>
Generates an order-dependent fingerprint by hashing the serialized data of the DataFrame.
* `generate_order_independent_fingerprint(df)` <br>
Generates an order-independent fingerprint by hashing individual rows and then hashing the concatenated sorted row hashes.
* `process_file_with_order_dependent_fingerprint(file_path)` <br>
Loads the data and generates an order-dependent fingerprint.
* `process_file_with_order_independent_fingerprint(file_path)` <br>
Loads the data and generates an order-independent fingerprint.
* `main()` <br>
The entry point of the script. Handles user input and displays the resulting fingerprint.

### Limitations

Data Size: Processing very large datasets may consume significant memory and time.<br>
File Formats: Only supports the file formats listed above. Unsupported or corrupted files will result in errors.<br>
Datetime Parsing: Assumes that datetime columns can be parsed by `pandas.to_datetime`.

### Contributing

Contributions are welcome! Please follow these steps:

#### Fork the Repository
#### Create a Feature Branch
```
git checkout -b feature/YourFeature
```
#### Commit Your Changes
```
git commit -m "Add your message"
```
#### Push to Your Branch
```
git push origin feature/YourFeature
```
#### Open a Pull Request

### License

This project is licensed under the MIT License.

*Disclaimer: This script is provided "as is" without warranty of any kind. Use it at your own risk.* 

### Contact

For any questions or suggestions, please open an issue.

### Acknowledgments

Pandas Documentation
Python hashlib Library
PyArrow Documentation
PyTables Documentation
Pyreadstat Documentation

### Changelog

#### v1.1
Updated installation instructions to include additional dependencies.
Improved file format support by adding required packages.

#### v1.0
Initial release with support for multiple file formats.
Added order-dependent and order-independent fingerprinting modes.
Thank you for using the Dataset Fingerprint Generator! If you find this tool helpful, please give it a star ⭐ on GitHub.

### Additional Information

#### Troubleshooting
If you encounter issues while running the script, consider the following:

* Encoding Errors: For files with special character encodings, you may need to specify the encoding parameter in the load_data function.
* Permission Issues: Ensure you have the necessary permissions to read the dataset files.
 * Corrupted Files: Verify that your dataset files are not corrupted and are in the correct format.
Extending Functionality

**Feel free to modify the script to support additional file formats or to enhance its capabilities. Contributions that improve the script's functionality are highly appreciated.**

### Feedback

Your feedback is valuable to us. Please take a moment to share your thoughts or report any issues you encounter.
GitHub Issues: https://github.com/chriswilson2020/data_fingerprint/issues


