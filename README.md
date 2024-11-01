# CIS6930FA24 -- Project 1

**Name:** Prajay Yalamanchili

## Project Description

- This project is a data redaction tool designed to identify and redact sensitive information from text files.
- It processes various types of sensitive data, including names, phone numbers, addresses, dates, and custom concepts, ensuring compliance with privacy standards.
- The following fields will be redacted from the text document - `Names` `Address` `Phone numbers` `Dates` ` Custom Concept`
- The redacted text will be replaced by Unicode full block character `█`



## How to Install

**For Windows:**

1. If Python is not already installed on your system, download and install Python version 3.12 from [here](https://www.python.org/downloads/).
2. Set your path in the environment variables. To learn how to set the path in environment variables, read this [article](https://www.liquidweb.com/help-docs/adding-python-path-to-windows-10-or-11-path-environment-variable/).
3. Download or clone this repository.
4. Navigate to the project directory on your local machine.
5. Run the following commands:

    ```bash
    pip install pipenv
    ```
    ```bash
    pipenv install
    ```

## How to Run

To execute the `redactor.py` file, use:
```bas
pipenv run python main.py --input PATH_TO_TEXT_FILES [--names] [--dates] [--phones] [--address] [--concept CONCEPT_WORDS] --output OUTPUT_DIRECTORY --stats STATS_FILE
```
To run tests, use:
```bash
pipenv run python -m pytest -v
```
or

```bash
pipenv run pytest
```


## Demo Program Execution



[watch]()



## Folder Structure
```
|   COLLABORATORS.md
|   LICENSE
|   Pipfile
|   Pipfile.lock
|   README.md
|   setup.cfg
|   setup.py
|   redactor.py
|
+---files
|       sample.txt.censored
|
\---tests
        test_redactor.py
```

- **COLLABORATORS.md:** Contains information about collaborators and a list of resources used for the assignment.
- **redactor.py:** This is the main python file where the business logic resides, it Processes command-line arguments to redact the text.
- **Pipfile:** Manages the Python virtual environment and lists all dependencies.
- **Pipfile.lock:** Specifies the versions of dependencies to ensure consistent environments.
- **README.md:** This file, which documents the assignment.
- **setup.cfg** and **setup.py:** Used for setting up the Python environment.
- **docs:** Contains documentation for the assignment.
- **LICENSE:** Contains licensing information, including copyright, publishing, and usage rights.
- **Files:** This folder stores output censored files, including `sample.txt.censored`, which is a sample file for testing. User can store the files in another directory by mentioning in outputs argument.
- **tests:** Contains test files. `test_redactor.py` is used for testing the redactor Python file.
- **stats:** This is a sample stats file. The format includes the file name and the count of each redacted entity. A sample stats file is as follows -
```bash
File Name: sample.txt
Names redacted: 3
Dates redacted: 2
Phone numbers redacted: 1
Addresses redacted: 1
Concepts redacted: 5

```
## `redactor.py`

**Functions in `redactor.py`:**

### `main(args)`
The main function serves as the central hub for the workflow of the Redactor tool. It manages the entire process by:
1. Processing Command-Line Arguments: It captures user inputs and configuration settings specified via command-line flags.
2. Reading Input Files: It identifies and reads all text files that match the input pattern provided by the user.
3. Applying Redaction Methods: Based on the specified flags, it applies various redaction techniques to the text content:
4. Generating Output Files: After redaction, it creates new files with the same names as the original ones, appending .censored to the filenames, and saves them in the specified output directory.

### `address_redactor(text)`
This function employs regex patterns and spaCy's entity recognition capabilities to identify and redact physical addresses within the text.

### `name_redactor(text)`
The name_redactor function identifies and redacts names mentioned in the text, including both proper names and email addresses. It specifically targets headers like "From" and "To" to obscure personal information, ensuring that sensitive names are effectively censored throughout the document.

### `phone_redactor(text)`
This function scans the text for phone number patterns in various formats (e.g., (123) 456-7890, 123-456-7890) and redacts them.

### `date_redactor(text)`
The date_redactor function is designed to recognize and redact specific date formats, including both full dates and abbreviations. It accounts for a range of date styles and ensures that even non-specific dates (e.g., "last week") are appropriately handled to prevent inadvertent exposure of sensitive temporal information.

### `concept_redactor(text, concepts)`
This function allows users to define custom concepts for redaction. It utilizes semantic similarity techniques, including sentence embeddings, to identify and redact sentences that reference user-defined concepts.
## `test_main.py`

**Functions in `test_redactor.py`:**
This file contains unit tests for the functions defined in redactor.py. The functions being tested are responsible for redacting sensitive information such as addresses, names, dates, phone numbers, and concepts from text.

### `test_address_redactor()`
In `test_address_redactor()`, the function `address_redactor()` is tested by providing it with a sentence that contains a location, specifically "Bermuda". The expected behavior is that the function will correctly identify and redact "Bermuda" by replacing it with a series of block characters (████). The test also checks that the function reports one redaction, reflecting that only one location was censored. 

### `test_name_redactor()`
The `test_name_redactor()` function validates the ability of `name_redactor()` to find and obscure names in the input text.

### `test_date_redactor()`
In `test_date_redactor()`, the function `date_redactor()` is tested to ensure it successfully identifies and redacts dates within a string. The input text contains a specific date, "24 Sep 2001", embedded in an email header. The function should replace the date with block characters and report that one date has been redacted.

### `test_phone_redactor()`
For `test_phone_redactor()`, the `phone_redactor()` function is tested on a simple sentence containing a phone number. The function is expected to recognize the format of the phone number and censor it.

### `test_concept_redactor()`
`test_concept_redactor()` evaluates the `concept_redactor()` function’s ability to redact sentences that relate to specific concepts. In this test, the input text includes a sentence about wine, and the word "wine" is passed to the function as the concept to be redacted. 

## Bugs and Assumptions

- The regular expressions used for detecting patterns like phone numbers, email addresses, names, and dates are specifically tailored to the structure and content of the Enron email dataset.
- The `concept_redactor()` function uses a threshold-based approach to identify sentences conceptually related to given keywords. However, this method depends heavily on the quality of sentence embeddings and the threshold values.
- The `name_redactor()` function is dependent on the Spacy Named Entity Recognition (NER) model, which may not always accurately detect names.
- The `address_redactor()` relies on regular expressions and NER to redact addresses. It may not identify all addresses.
- In some cases, the length of the redaction block (the series of █ characters) may not accurately match the length of the text being redacted.
