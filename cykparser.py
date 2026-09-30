def cky(grammar, sentence, start="S"):
    words = sentence.split()
    n = len(words)

    # CKY table
    table = [[set() for _ in range(n)] for _ in range(n)]

    # Fill diagonal
    for i, word in enumerate(words):
        for lhs, rhs in grammar:
            if len(rhs) == 1 and rhs[0] == word:
                table[i][i].add(lhs)

    # Fill the table
    for length in range(2, n + 1):
        for i in range(n - length + 1):
            j = i + length - 1

            for k in range(i, j):
                for lhs, rhs in grammar:
                    if len(rhs) == 2:
                        B, C = rhs

                        if B in table[i][k] and C in table[k + 1][j]:
                            table[i][j].add(lhs)

    return start in table[0][n - 1]


# Input grammar
grammar = [
    ("S", ["NP", "VP"]),
    ("NP", ["Det", "N"]),
    ("VP", ["V", "NP"]),
    ("Det", ["the"]),
    ("N", ["cat"]),
    ("N", ["dog"]),
    ("V", ["sees"])
]

sentence = input("Enter sentence: ")

print(cky(grammar, sentence))