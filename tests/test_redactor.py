import sys
import os
import nltk

# Add the parent directory to the system path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))#Possible reasons for pipenv failure
nltk.download('punkt_tab')
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('omw-1.4')


# Now you can import your functions from redactor.py
from redactor import address_redactor, name_redactor, date_redactor, phone_redactor, concept_redactor

def test_address_redactor():
    text = "I also ran into some friends of yours in Bermuda last month."
    expected_output = "I also ran into some friends of yours in ███████ last month."
    censored_text, count = address_redactor(text)
    assert censored_text == expected_output
    assert count == 1

def test_name_redactor():
    text = "Heather Lockhart Robertson, Director"
    expected_output = "██████████████████████████, Director"
    censored_text, count = name_redactor(text)
    assert censored_text == expected_output
    assert count == 0

def test_date_redactor():
    text = "Date: Mon, 24 Sep 2001 14:09:13 -0700 (PDT)"
    expected_output = "Date: Mon, ███████████ 14:09:13 -0700 (PDT)"
    censored_text, count = date_redactor(text)
    assert censored_text == expected_output
    assert count == 1

def test_phone_redactor():
    text = "T 858-942-7740"
    expected_output = "T ████████████"
    censored_text, count = phone_redactor(text)
    assert censored_text == expected_output
    assert count == 1

def test_concept_redactor():
    text = "1. Gary Vaynerchuk of the Wine Library has signed on to host a wine tasting dinner at Cafe Brand of Jersey City this Wednesday October 24 at ickly if you have interest."
    concept_words = ["wine"]
    expected_output = "██ █████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████"
    censored_text,count = concept_redactor(text, concept_words)
    assert censored_text == expected_output

