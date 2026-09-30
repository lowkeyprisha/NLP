grammar = {
    "S": [("NP", "VP")],
    "NP": [("Det", "N"), ("dog",), ("cat",)],
    "VP": [("V", "NP")],
    "Det": [("the",)],
    "N": [("dog",), ("cat",)],
    "V": [("chased",)]
}

sentence = "the dog chased the cat".split()
n = len(sentence)

table = [[set() for _ in range(n)] for _ in range(n)]

# Step 1: Fill the diagonal using terminal productions
for i in range(n):
    word = sentence[i]

    for lhs, productions in grammar.items():
        for production in productions:
            if len(production) == 1 and production[0] == word:
                table[i][i].add(lhs)

# Step 2: Fill larger substrings
for length in range(2, n + 1):

    for i in range(n - length + 1):

        j = i + length - 1

        # Try every possible split
        for k in range(i, j):

            left = table[i][k]
            right = table[k + 1][j]

            # Try all grammar rules A -> BC
            for lhs, productions in grammar.items():

                for production in productions:

                    if len(production) == 2:

                        B, C = production

                        if B in left and C in right:
                            table[i][j].add(lhs)

# Print CYK table
print("CYK Table:")

for i in range(n):
    for j in range(i, n):
        print(
            f"{sentence[i:j+1]} : {table[i][j]}"
        )

# Check whether S is in the top-right cell
if "S" in table[0][n - 1]:
    print("\nSentence is accepted by the grammar.")
else:
    print("\nSentence is rejected by the grammar.")