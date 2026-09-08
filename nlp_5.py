states = ["PRON", "VERB", "NOUN"]

start_probability = {
    "PRON": 0.6,
    "VERB": 0.0,
    "NOUN": 0.4
}

transition_probability = {
    "PRON": {"PRON": 0.0, "VERB": 0.7, "NOUN": 0.3},
    "VERB": {"PRON": 0.0, "VERB": 0.2, "NOUN": 0.8},
    "NOUN": {"PRON": 0.0, "VERB": 0.1, "NOUN": 0.9}
}

emission_probability = {
    "I": {"PRON": 0.9, "VERB": 0.01, "NOUN": 0.01},
    "eat": {"PRON": 0.01, "VERB": 0.8, "NOUN": 0.05},
    "fish": {"PRON": 0.01, "VERB": 0.1, "NOUN": 0.7}
}

def viterbi(words):
    viterbi = [{}]
    backpointer = [{}]

    for tag in states:
        viterbi[0][tag] = start_probability[tag] * emission_probability[words[0]][tag]
        backpointer[0][tag] = None

    for i in range(1, len(words)):
        viterbi.append({})
        backpointer.append({})

        for current_tag in states:
            best_probability = 0
            best_previous_tag = None

            for previous_tag in states:
                probability = (
                    viterbi[i - 1][previous_tag]
                    * transition_probability[previous_tag][current_tag]
                    * emission_probability[words[i]][current_tag]
                )

                if probability > best_probability:
                    best_probability = probability
                    best_previous_tag = previous_tag

            viterbi[i][current_tag] = best_probability
            backpointer[i][current_tag] = best_previous_tag

    best_last_tag = max(viterbi[-1], key=viterbi[-1].get)

    best_tags = [best_last_tag]

    for i in range(len(words) - 1, 0, -1):
        best_last_tag = backpointer[i][best_last_tag]
        best_tags.append(best_last_tag)

    best_tags.reverse()

    return list(zip(words, best_tags))

words = ["I", "eat", "fish"]

result = viterbi(words)

for word, tag in result:
    print(word, "->", tag)