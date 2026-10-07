import nltk
from nltk.corpus import wordnet

nltk.download('wordnet')
nltk.download('omw-1.4')

word1 = input("Enter first word: ")
word2 = input("Enter second word: ")

synsets1 = wordnet.synsets(word1)
synsets2 = wordnet.synsets(word2)

print("\n========== SENSES OF", word1.upper(), "==========")

for i, syn in enumerate(synsets1, start=1):
    print("\nSense", i)
    print("Synset :", syn.name())
    print("Gloss  :", syn.definition())
    print("Examples:", syn.examples())

print("\n========== SENSES OF", word2.upper(), "==========")

for i, syn in enumerate(synsets2, start=1):
    print("\nSense", i)
    print("Synset :", syn.name())
    print("Gloss  :", syn.definition())
    print("Examples:", syn.examples())

choice1 = int(input("\nSelect the sense number for " + word1 + ": "))
choice2 = int(input("Select the sense number for " + word2 + ": "))

sense1 = synsets1[choice1 - 1]
sense2 = synsets2[choice2 - 1]

print("\n========== SELECTED SENSES ==========")

print("\n", word1, "->", sense1.name())
print("Gloss:", sense1.definition())

print("\n", word2, "->", sense2.name())
print("Gloss:", sense2.definition())

path_similarity = sense1.path_similarity(sense2)
wup_similarity = sense1.wup_similarity(sense2)

print("\n========== SIMILARITY RESULTS ==========")

print("Path Similarity      :", path_similarity)
print("Wu-Palmer Similarity :", wup_similarity)