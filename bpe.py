import nltk
from nltk.tokenize import word_tokenize
from collections import defaultdict
nltk.download('punkt')
corpus = {
    "lower": 5,
    "lowest": 2,
    "widest": 6,
    "newest": 3
}

text = " ".join(corpus.keys())
words = word_tokenize(text)
vocab = {}

for word in words:
    vocab[" ".join(list(word))] = corpus[word]
global_vocab = set()

for word in vocab:
    for symbol in word.split():
        global_vocab.add(symbol)

print("Initial Vocabulary:")
print(sorted(global_vocab))
print("-" * 60)
merge_rules = []
def get_pair_freq(vocab):
    pair_freq = defaultdict(int)

    for word, freq in vocab.items():
        symbols = word.split()

        for i in range(len(symbols) - 1):
            pair = (symbols[i], symbols[i + 1])
            pair_freq[pair] += freq

    return pair_freq

def merge_pair(pair, vocab):
    merged_vocab = {}

    bigram = " ".join(pair)
    replacement = "".join(pair)

    for word in vocab:
        new_word = word.replace(bigram, replacement)
        merged_vocab[new_word] = vocab[word]

    return merged_vocab


iterations = int(input("Enter number of iterations: "))

for itr in range(1, iterations + 1):

    pair_freq = get_pair_freq(vocab)

    if not pair_freq:
        break

    best_pair = max(pair_freq, key=pair_freq.get)

    print(f"\nIteration {itr}")
    print("Best Pair :", best_pair)
    print("Frequency :", pair_freq[best_pair])

    merge_rules.append(best_pair)
    global_vocab.add("".join(best_pair))

    vocab = merge_pair(best_pair, vocab)

    print("\nUpdated Vocabulary:")
    print(sorted(global_vocab))

    print("\nUpdated Words:")
    for word in vocab:
        print(word.split())

    print("-" * 60)


print("\nFinal Global Vocabulary:")
print(sorted(global_vocab))

print("\nMerge Rules Learned:")
for rule in merge_rules:
    print(rule)


def tokenize_new_word(word, merge_rules):

    tokens = list(word)

    for pair in merge_rules:

        i = 0

        while i < len(tokens) - 1:

            if tokens[i] == pair[0] and tokens[i + 1] == pair[1]:
                tokens[i:i + 2] = ["".join(pair)]

            else:
                i += 1

    return tokens


new_word = input("\nEnter a new word: ")

tokens = tokenize_new_word(new_word, merge_rules)

print("\nTokenized Output:")
print(tokens) 