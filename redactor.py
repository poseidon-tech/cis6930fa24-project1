import spacy
import argparse
import glob
import re
import os
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
sbert_model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
import sys

#Possible reasons for pipenv failure
nltk.download('punkt_tab')
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('omw-1.4')


FULL_BLOCK = '█'
nlp = spacy.load("en_core_web_md")
pattern = r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
x_to_pattern = r'X-To:\s*([A-Za-z.,-]+) \s*([A-Za-z.,-]*)'
location_pattern = r'(?:\d+\s+([A-Za-z]+(?:\s[A-Za-z]+)*)\s*(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr|Way|Terrace|Terr|Court|Ct|Place|Pl|Square|Sq|Parkway|Pkwy|Circle|Cir)?)?\s*(?:,\s*\d+[A-Za-z\s]*)?\s*(?:,\s*[A-Za-z\s]+)?\s*(?:,\s*[A-Z]{2}\s*\d{5})?$'
x_from_pattern = r'X-From:\s*([A-Za-z.,-]+) \s*([A-Za-z.,-]*)'
email_pattern = r'([A-Za-z0-9_%+-]+)(?:\.([A-Za-z0-9._%+-]+))?@([A-Za-z0-9.-]+\.[A-Z|a-z]{2,7})'
from_pattern = r'^From:\s*"?([A-Za-z]+)\s*,\s*([A-Za-z]+"?)'
to_pattern = r'To:\s*([A-Za-z]+)\s*,\s*([A-Za-z]+)'
x_filename_pattern = r'X-FileName:\s*(.+)'
x_origin_pattern = r'X-Origin:\s*(.+)'
x_folder_pattern = r'X-Folder:\s*\\([a-zA-Z]+_[a-zA-Z]*)'
week_pattern = r'[a-zA-Z]* (week|monday|tuesday|wednesday|thursday|friday|saturday|sunday)'
date_pattern = r'\b(0[1-9]|1[0-2])/(0[1-9]|[12][0-9]|3[01])/(\d{4}|\d{2})\b'
days_pattern = r'[0-9A-Za-z]+ ?(day\'s|days?|days)'
#location_pattern = r'\d{1,5}\s[A-Za-z0-9\s.,\-]+(?:Apt\.?\s?\d+|Suite\s?\d+|#\d+)?\s*,?\s*[A-Za-z\s]+,\s*[A-Z]{2}\s*\d{5}(?:-\d{4})?'
non_specific_dates = ['her week','all week','week','next week', 'next month', 'tomorrow', 'yesterday', 'today', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']



def main(args):
    txt_files = glob.glob(args.input, recursive=True)
    for txt_file in txt_files:
        stats = {
            'names': 0,
            'dates': 0,
            'phones': 0,
            'addresses': 0,
            'concepts': 0,
        }
        content = readData(txt_file)
        if args.address:
            content, stat = address_redactor(content)
            stats['addresses'] = stat
        if args.names:
            content,stat = name_redactor(content)
            stats['names'] = stat
        if args.phones:
            content,stat= phone_redactor(content)
            stats['phones'] = stat
        if args.dates:
            content,stat = date_redactor(content)
            stats['dates'] = stat
        if args.concept:
            content,stat = concept_redactor(content,args.concept)
            stats['concepts'] = stat
        if args.output:
            file_path = os.path.join(args.output, txt_file + '.censored')
            os.makedirs(args.output, exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(content)
        stats_summary = [
            "File Name: "+ txt_file,
            f"Names redacted: {stats['names']}",
            f"Dates redacted: {stats['dates']}",
            f"Phone numbers redacted: {stats['phones']}",
            f"Addresses redacted: {stats['addresses']}",
            f"Concepts redacted: {stats['concepts']}",
        ]
        stats_text = "\n".join(stats_summary)
        if args.stats == 'stderr':
            sys.stderr.write(stats_text + "\n")
        elif args.stats == 'stdout':
            sys.stdout.write(stats_text + "\n")
        elif(args.stats):
            with open(args.stats, 'a', encoding='utf-8') as output_file:
                output_file.write("\n" +stats_text)


def readData(txt_file):
    with open(txt_file, encoding='utf-8') as file:
        content = file.read()
    return content

def address_redactor(text):
    censorAddress = 0
    censored_text, count = re.subn(location_pattern, replace_with_blocks, text, flags=re.VERBOSE | re.IGNORECASE)
    doc = nlp(censored_text)
    for ent in doc.ents:
        if ent.label_ in ['FAC', 'GPE', 'LOC']:
            censored_text = censored_text[:ent.start_char] + FULL_BLOCK * (ent.end_char - ent.start_char) + censored_text[ent.end_char:]
            censorAddress += 1
    return censored_text, censorAddress

def name_redactor(text):
    censor_name=0
    text,count = re.subn(email_pattern,email_redactor,text)
    censor_name+=count
    text,count = from_redactor(text)
    censor_name += count
    text,count = to_redactor(text)
    censor_name += count
    text, count = re.subn(x_to_pattern, replace_x_to, text)
    censor_name += count
    text, count = re.subn(x_from_pattern, replace_x_from, text)
    censor_name += count
    text, count = re.subn(x_filename_pattern, replace_x_filename, text)
    censor_name += count
    text, count = re.subn(x_origin_pattern, replace_x_origin, text)
    censor_name += count
    text, count = re.subn(x_folder_pattern, replace_x_folder, text)
    censor_name += count
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ == 'PERSON':
            text = text[:ent.start_char] + FULL_BLOCK * (ent.end_char - ent.start_char) + text[ent.end_char:]
            censor_name += count
    return text,censor_name

def phone_redactor(text):
    censorPhone =  0
    censored_text = text
    for match in re.finditer(pattern, text):
        censored_text = censored_text[:match.start()] + FULL_BLOCK * (match.end() - match.start()) + censored_text[match.end():]
        censorPhone += 1
    return censored_text, censorPhone

def date_redactor(text):
    censorDate = 0
    censored_text = re.sub(date_pattern, replacement, text)
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ == 'DATE':
            if ent.text.lower() not in non_specific_dates and not re.search(week_pattern, ent.text.lower()) and not re.search(days_pattern, ent.text.lower()):
                censored_text = censored_text[:ent.start_char] + FULL_BLOCK * (ent.end_char - ent.start_char) + censored_text[ent.end_char:]
                censorDate += 1
    return censored_text,censorDate

def concept_redactor(text,concepts):
    threshold = 0.1

    def zscore_threshold(cosine_similarities):
        """Compute the threshold based on z-scores for a given set of cosine similarities."""
        z_threshold = 0.1
        threshold = np.mean(cosine_similarities) + (z_threshold * np.std(cosine_similarities))
        return threshold

    def get_sentence_embedding(sentence_tokens):
        sentence = " ".join(sentence_tokens)  # Join tokens into a full sentence
        return sbert_model.encode([sentence])[0]  # Return the embedding

    def preprocess(text):
        text = text.replace('\n', '.')
        return sent_tokenize(text)

    def compute_similarity(sentence_tokens, concept_word):
        concept_embedding = sbert_model.encode([concept_word])[0]  # Get SBERT embedding for concept word
        sentence_embedding = get_sentence_embedding(word_tokenize(sentence_tokens))
        similarity = cosine_similarity([concept_embedding], [sentence_embedding])[0][0]
        return similarity

    def is_related_to_concept(sentence_tokens, concept_word):
        similarity = compute_similarity(sentence_tokens, concept_word)
        return similarity > threshold

    def redact_concepts(text, concept_words, new_text, sentences):
        count =0
        processed_sentences = preprocess(text)
        for i, sentence_tokens in enumerate(processed_sentences):
            for concept_word in concept_words:
                if is_related_to_concept(sentence_tokens, concept_word):
                    count+=1
                    new_text = new_text.replace(sentences[i], "█" * len("".join(sentence_tokens)))
                    break
        return new_text,count

    concept_words = concepts
    new_text = text
    sentences = preprocess(text)
    redacted_text,count = redact_concepts(text, concept_words, new_text, sentences)
    return redacted_text,count

def from_redactor(text):
    redaction_count = 0
    # Include newline after redacted output
    text, from_redactions = re.subn(
        from_pattern,
        lambda match: f'X-From: {"█" * len(match.group(1))} {match.group(2)}',
        text
    )
    redaction_count += from_redactions
    return text, redaction_count

def to_redactor(text):
    redaction_count = 0
    # Include newline after redacted output
    text, to_redactions = re.subn(
        to_pattern,
        lambda match: f'X-To: {"█" * len(match.group(1))} {match.group(2)}',
        text
    )
    redaction_count += to_redactions
    return text, redaction_count

def email_redactor(match):
    firstname = match.group(1)
    lastname = match.group(2) if match.group(2) else ''
    domain = match.group(3)
    redacted_email = (
            FULL_BLOCK * len(firstname) +
            (("." + FULL_BLOCK * len(lastname)) if lastname else "") +
            '@' + domain  # Keep the domain intact.
    )
    return redacted_email

def replace_x_to(match):
    first_name = match.group(1)
    last_name = match.group(2)
    redacted_name = ''.join([FULL_BLOCK * (len(first_name) + len(last_name))])
    return f'X-To: {redacted_name}'

def replace_x_folder(match):
    name = match.group(1)
    redacted_name = FULL_BLOCK * len(name)
    return f"X-Folder: \\{redacted_name}"

def replace_x_from(match):
    first_name = match.group(1)
    last_name = match.group(2)
    redacted_name = ''.join([FULL_BLOCK * (len(first_name)+len(last_name))])
    return f'X-From: {redacted_name}'

def replace_with_blocks(match):
        return "█" * len(match.group(0))

def replace_x_filename(match):
    filename = match.group()
    return 'X-FileName: ' + FULL_BLOCK * len(filename)

def replace_x_origin(match):
    origin = match.group(1)
    return 'X-Origin: ' + FULL_BLOCK * len(origin)

def replacement(match):
    return FULL_BLOCK * len(match.group(0))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, required=True)
    parser.add_argument("--names", action='store_true')
    parser.add_argument("--dates", action='store_true')
    parser.add_argument("--phones", action='store_true')
    parser.add_argument("--address", action='store_true')
    parser.add_argument('--concept', action='append')
    parser.add_argument("--output", type=str, required=True)
    parser.add_argument("--stats")
    args = parser.parse_args()
    main(args)