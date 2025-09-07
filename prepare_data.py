from main import AutoCompleteEngine
from pathlib import Path

if __name__ == "__main__":
    engine = AutoCompleteEngine()
    engine.load_corpus_from_zip(r"C:\Users\This User\Downloads\final\Archive.zip")

    engine.build_index()
    engine.save_index(Path("corpus.pkl"))
