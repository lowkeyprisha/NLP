import nltk
from nltk.corpus import wordnet

nltk.download('wordnet')
nltk.download('omw-1.4')

word = input("Enter a word: ")

synonyms = set()
antonyms = set()

for syn in wordnet.synsets(word):
    print("\nMeaning:", syn.definition())
    print("Example:", syn.examples())

    for lemma in syn.lemmas():
        synonyms.add(lemma.name())

        if lemma.antonyms():
            for antonym in lemma.antonyms():
                antonyms.add(antonym.name())

print("\nSynonyms:", synonyms)
print("Antonyms:", antonyms)