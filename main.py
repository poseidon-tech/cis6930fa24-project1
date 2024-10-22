import requests
import tarfile
import spacy
import argparse
import glob
import re
import os

FULL_BLOCK = '█'
pattern = r'^\+{0,1}[0-9]{0,2} {0,1}[0-9]{3}-{0,1}[0-9]{3}-{0,1}[0-9]{3}$|^\+{0,1}[0-9]{0,2} {0,1}\(?[0-9]{3}\)?-{0,1}[0-9]{3}-{0,1}[0-9]{3}$|^\+{0,1}[0-9]{0,2} {0,1}[0-9]{3} {0,1}[0-9]{3} {0,1}[0-9]{3}$|^\+{0,1}[0-9]{0,2} {0,1}\(?[0-9]{3}\)? {0,1}[0-9]{3} {0,1}[0-9]{3}$'
location_pattern = r"\d+\s[A-Za-z]+\s[A-Za-z]+\s(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr|NW|NE|SW|SE|East|West|North|South)[,]?\s[A-Za-z\s]+[,]\s[A-Za-z]{2}[.]?\s\d{5}?"
nlp = spacy.load("en_core_web_lg")

def main(input_file_location, output_file_location, concepts=None):
    txt_files = glob.glob(input_file_location, recursive=True)
    for txt_file in txt_files:
        output_file_path = os.path.join(output_file_location, txt_file + '.censored')
        content = readData(txt_file)
        doc = nlp(content)

        # Redacting information and tracking stats
        redacted_doc, name_count = name_redactor(doc)
        redacted_doc, date_count = date_redactor(redacted_doc)
        redacted_doc, phone_count = phone_redactor(redacted_doc)
        redacted_doc, address_count = address_redactor(redacted_doc)

        concept_count = 0
        if concepts is not None:
            redacted_doc, concept_count = concept_redactor(redacted_doc, concepts)

        # Write the redacted output
        with open(output_file_path, 'w', encoding='utf-8') as file:
            file.write(redacted_doc)

        # Calculate stats for the current file
        stats(output_file_path, name_count, date_count, phone_count, address_count, concept_count)

def getData():
    res = requests.get("https://www.cs.cmu.edu/~enron/enron_mail_20150507.tar.gz", stream=True)
    if res.status_code == 200:
        with open("data.tar.gz", "wb") as file:
            file.write(res.content)
        with tarfile.open("data.tar.gz", "r:gz") as tar:
            tar.extractall(path="enron_data")

def readData(txt_file):
    with open(txt_file) as file:
        content = file.read()
    return content

def name_redactor(doc):
    token_list = []
    redaction_count = 0
    for token in doc:
        if token.ent_type_ == 'PERSON':
            token_list.append(FULL_BLOCK * len(token.text))
            redaction_count += 1
        else:
            token_list.append(token.text)
    return nlp(" ".join(token_list)), redaction_count

def date_redactor(doc):
    token_list = []
    redaction_count = 0
    for token in doc:
        if token.ent_type_ in ('DATE', 'TIME'):
            token_list.append(FULL_BLOCK * len(token.text))
            redaction_count += 1
        else:
            token_list.append(token.text)
    return nlp(" ".join(token_list)), redaction_count

def phone_redactor(doc):
    token_list = []
    redaction_count = 0
    for token in doc:
        if re.match(pattern, token.text):
            token_list.append(FULL_BLOCK * len(token.text))
            redaction_count += 1
        else:
            token_list.append(token.text)
    return nlp(" ".join(token_list)), redaction_count

def address_redactor(doc):
    token_list = []
    redaction_count = 0
    for token in doc:
        if re.match(location_pattern, token.text) or token.ent_type_ in ('LOC', 'GPE'):
            token_list.append(FULL_BLOCK * len(token.text))
            redaction_count += 1
        else:
            token_list.append(token.text)
    return nlp(" ".join(token_list)), redaction_count

def concept_redactor(doc, concepts):
    token_list = []
    concept_vectors = [nlp(concept).vector for concept in concepts]
    redaction_count = 0
    for token in doc:
        redact = False
        if token.text.lower() in concepts or token.lemma_.lower() in concepts:
            redact = True
        for concept_vector in concept_vectors:
            concept_vector_norm = concept_vector.dot(concept_vector) ** 0.5
            similarity = token.vector.dot(concept_vector) / (token.vector_norm * concept_vector_norm)
            if similarity > 0.7:
                redact = True
                break
        if redact:
            for child in token.children:
                token_list.append(FULL_BLOCK * len(child.text))
            for ancestor in token.ancestors:
                token_list.append(FULL_BLOCK * len(ancestor.text))
            token_list.append(FULL_BLOCK * len(token.text))
            redaction_count += 1
        else:
            token_list.append(token.text)
    return " ".join(token_list), redaction_count

def stats(output_file_path, name_count, date_count, phone_count, address_count, concept_count):
    """
    Prints or logs statistics of the redactions performed.
    """
    print(f"File: {output_file_path}")
    print(f"Names redacted: {name_count}")
    print(f"Dates redacted: {date_count}")
    print(f"Phone numbers redacted: {phone_count}")
    print(f"Addresses redacted: {address_count}")
    print(f"Concepts redacted: {concept_count}")
    print("-" * 40)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, required=True)
    parser.add_argument("--names", action='store_true', help="Flag to redact names")
    parser.add_argument("--dates", action='store_true', help="Flag to redact dates")
    parser.add_argument("--phones", action='store_true', help="Flag to redact phone numbers")
    parser.add_argument("--address", action='store_true', help="Flag to redact addresses")
    parser.add_argument('--concept', action='append', help='<Required> Set flag', required=True)
    parser.add_argument("--output", type=str, required=True)
    args = parser.parse_args()
    main(args.input, args.output, args.concept)
