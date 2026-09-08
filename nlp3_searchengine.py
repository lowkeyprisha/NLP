import re
import string

MAX_DOCS = 10
MAX_TERMS = 20

STOPWORDS = {
    "a", "an", "the", "is", "are", "was", "were", "in", "on", "at",
    "of", "to", "and", "or", "for", "with", "this", "that", "it",
    "as", "by", "be", "from", "has", "have", "had"
}


def simple_stem(word: str) -> str:
    for suffix in ("ing", "edly", "ies", "ied", "es", "ed", "s"):
        if word.endswith(suffix) and len(word) - len(suffix) > 2:
            return word[: -len(suffix)]
    return word


def tokenize(text: str):
    return re.findall(r"[a-zA-Z]+", text)


def normalize(tokens):
    return [t.lower().strip(string.punctuation) for t in tokens]


def remove_stopwords(tokens):
    return [t for t in tokens if t not in STOPWORDS]


def stem(tokens):
    return [simple_stem(t) for t in tokens]


def preprocess(text: str):
    tokens = tokenize(text)
    tokens = normalize(tokens)
    tokens = stem(tokens)
    tokens = remove_stopwords(tokens)
    return tokens


class InvertedIndex:
    def __init__(self, max_terms=MAX_TERMS):
        self.index = {}          # term -> set/list of doc_ids
        self.docs = {}           # doc_id -> original text
        self.max_terms = max_terms
        self.term_labels = {}    # term -> "T1", "T2", ... (like your notes)

    def add_document(self, doc_id: int, text: str):
        self.docs[doc_id] = text
        for term in preprocess(text):
            if term not in self.index:
                if len(self.index) >= self.max_terms:
                    continue  # vocabulary full (cap at T1..T20), skip new terms
                self.index[term] = set()
            self.index[term].add(doc_id)

    def build(self):
        self.index = {term: sorted(ids) for term, ids in self.index.items()}
        # assign T1, T2, ... T20 labels like the notes diagram
        self.term_labels = {
            term: f"T{i+1}" for i, term in enumerate(self.index.keys())
        }

    def search_term(self, term: str):
        term = simple_stem(term.lower().strip(string.punctuation))
        return self.index.get(term, "Not present")

    def and_query(self, term1: str, term2: str):
        p1 = self.search_term(term1)
        p2 = self.search_term(term2)
        if p1 == "Not present" or p2 == "Not present":
            return "Not present"
        result, i, j = [], 0, 0
        while i < len(p1) and j < len(p2):
            if p1[i] == p2[j]:
                result.append(p1[i]); i += 1; j += 1
            elif p1[i] < p2[j]:
                i += 1
            else:
                j += 1
        return result

    def print_vocabulary(self):
        print(f"\n=== Vocabulary (max {self.max_terms} terms) ===")
        for term, label in self.term_labels.items():
            print(f"  {label}: {term:<15} -> docs {self.index[term]}")

def get_documents_from_user():
    engine = InvertedIndex(max_terms=MAX_TERMS)
    doc_id = 1
    print(f"=== Enter your documents (max {MAX_DOCS}, D1-D{MAX_DOCS}) ===")
    print("Type an empty line to stop early.\n")

    while doc_id <= MAX_DOCS:
        text = input(f"Document D{doc_id}: ").strip()
        if text == "":
            break
        engine.add_document(doc_id, text)
        doc_id += 1

    if doc_id == MAX_DOCS + 1:
        print(f"\nReached the limit of {MAX_DOCS} documents.")

    if len(engine.docs) == 0:
        print("\nNo documents entered. Exiting.")
        return None

    engine.build()
    return engine


def run_query_loop(engine: InvertedIndex):
    engine.print_vocabulary()

    print("\n=== Query mode ===")
    print("Commands:")
    print("  <word>              -> single-term search")
    print("  <word1> AND <word2> -> intersection (merge) search")
    print("  exit                -> quit\n")

    while True:
        query = input("Query: ").strip()
        if query.lower() == "exit":
            print("Goodbye!")
            break
        if not query:
            continue

        if " AND " in query.upper():
            parts = re.split(r"\s+AND\s+", query, flags=re.IGNORECASE)
            if len(parts) != 2:
                print("  -> Please use exactly: word1 AND word2")
                continue
            term1, term2 = parts[0].strip(), parts[1].strip()
            result = engine.and_query(term1, term2)
            print(f"  -> {term1} AND {term2} : {result}")
        else:
            result = engine.search_term(query)
            print(f"  -> {result}")

        print()


if __name__ == "__main__":
    engine = get_documents_from_user()
    if engine:
        run_query_loop(engine)


