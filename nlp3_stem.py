import nltk
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize

nltk.download('punkt')

stemmer = PorterStemmer()

text = input("Enter your text: ")

words = word_tokenize(text)

stemmed_words = []

for word in words:
    stemmed_words.append(stemmer.stem(word))

print("\nOriginal words:")
print(words)

print("\nStemmed words:")
print(stemmed_words)

