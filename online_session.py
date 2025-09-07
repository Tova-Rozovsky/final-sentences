from main import AutoCompleteEngine


def online_loop():
    engine = AutoCompleteEngine()
    engine.load_index("corpus.pkl")

    buffer = ""

    print('Enter your sentence')
    print('press # if you want to start from the beginning.\n')

    while True:
        user = input("Text> ").strip()

        if user == "#":
            buffer = ""
            continue

        buffer = (buffer + " " + user).strip()

        suggestions = engine.autocomplete(buffer, max_results=5)

        if not suggestions:
            print("— No suggestions —\n")
            continue

        print("\nLeading suggestions:")
        for i, s in enumerate(suggestions, start=1):
            src = f"| {s.source_text}" if s.source_text else ""
            print(f"{i}. {src} {s.completed_sentence}\n   (offset: {s.offset}, score: {s.score})")
        print()


if __name__ == "__main__":
    online_loop()
