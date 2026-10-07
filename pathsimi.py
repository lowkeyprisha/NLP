import nltk
from nltk.corpus import wordnet

nltk.download('wordnet')
nltk.download('omw-1.4')

word1 = input("Enter first word: ")
word2 = input("Enter second word: ")

synsets1 = wordnet.synsets(word1)
synsets2 = wordnet.synsets(word2)

print("\nSynsets of", word1, ":", synsets1)
print("Synsets of", word2, ":", synsets2)

if synsets1 and synsets2:
    print("\nPath Similarity:")

    for s1 in synsets1:
        for s2 in synsets2:
            similarity = s1.path_similarity(s2)
            print(s1.name(), "vs", s2.name(), "=", similarity)

    print("\nWu-Palmer Similarity:")

    for s1 in synsets1:
        for s2 in synsets2:
            similarity = s1.wup_similarity(s2)
            print(s1.name(), "vs", s2.name(), "=", similarity)

else:
    print("One or both words are not found in WordNet.")