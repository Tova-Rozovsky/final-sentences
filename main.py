import re
import zipfile
import string
import pickle
from pathlib import Path
import sys
class AutoCompleteData:
    def __init__(self, completed_sentence: str, source_text: str, offset: int, score: int = 0):
        self.completed_sentence = completed_sentence
        self.source_text = source_text
        self.offset = offset
        self.score = score
    def __repr__(self):
        return f"<AutoCompleteData(sentence='{self.completed_sentence[:30]}...', source='{self.source_text}', offset={self.offset}, score={self.score})>"


class AutoCompleteEngine:
    def __init__(self):
        self.sentences = []
        self.index = {}

    def normalize_text(self, text: str) -> str:

        text = text.lower()
        translator = str.maketrans('', '', string.punctuation)
        text = text.translate(translator)
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        return text

    def load_corpus_from_zip(self, zip_path: str):

        sentences_found = 0
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            for file_name in zip_ref.namelist():
                if file_name.endswith(".txt"):  # קורא רק קבצי טקסט
                    with zip_ref.open(file_name) as f:
                        for i, line in enumerate(f):
                            try:
                                line = line.decode('utf-8').strip()
                            except:
                                line = line.decode('latin1').strip()
                            if line:
                                normalized = self.normalize_text(line)
                                self.sentences.append(
                                    AutoCompleteData(
                                        completed_sentence=normalized,
                                        source_text=line,
                                        offset=i + 1
                                    )
                                )
                                sentences_found += 1
        print(f"{sentences_found} sentences")

    def save_index(self, path):
        path = Path(path)
        with path.open("wb") as f:
            pickle.dump(self.index, f, protocol=pickle.HIGHEST_PROTOCOL)
        print(f"💾  index is saved: {path.resolve()}")

    def load_index(self, path):
        path = Path(path)
        with path.open("rb") as f:
            self.index = pickle.load(f)
        print(f"⚡ index is loaded: {path.resolve()}")

    def calculate_score(self, query: str, sentence: str) -> int:
        best_score = 0
        query_len = len(query)

        for i in range(len(sentence)):
            # חלון מקסימום: אורך השאילתה +1 (להוספה מותרת)
            for j in range(i + 1, min(len(sentence) + 1, i + query_len + 2)):
                substring = sentence[i:j]
                sub_len = len(substring)

                # יותר מתיקון אחד? לא חוקי
                if abs(sub_len - query_len) > 1:
                    continue

                edit_distance = None

                # החלפה אחת
                if sub_len == query_len:
                    diff_count = sum(1 for a, b in zip(query, substring) if a != b)
                    if diff_count > 1:
                        continue
                    edit_distance = diff_count

                # הוספה אחת
                elif sub_len == query_len + 1:
                    temp_idx = 0
                    diff_count = 0
                    for c in substring:
                        if temp_idx < query_len and c == query[temp_idx]:
                            temp_idx += 1
                        else:
                            diff_count += 1
                    if diff_count != 1 or temp_idx != query_len:
                        continue
                    edit_distance = 1

                # מחיקה אחת
                elif sub_len == query_len - 1:
                    temp_idx = 0
                    diff_count = 0
                    for c in query:
                        if temp_idx < sub_len and c == substring[temp_idx]:
                            temp_idx += 1
                        else:
                            diff_count += 1
                    if diff_count != 1 or temp_idx != sub_len:
                        continue
                    edit_distance = 1

                else:
                    continue

                # חישוב ניקוד
                base_score = 2 * query_len
                penalty = 0

                if edit_distance == 1:
                    # החלפה
                    if sub_len == query_len:
                        for k in range(query_len):
                            if query[k] != substring[k]:
                                penalty = [5, 4, 3, 2][k] if k < 4 else 1
                                break
                    # הוספה או מחיקה
                    else:
                        penalty = [10, 8, 6, 4][0] if min(query_len, sub_len) > 0 else 2

                current_score = base_score - penalty
                best_score = max(best_score, current_score)

        return best_score

    def build_index(self):

        from collections import defaultdict
        self.index = defaultdict(list)

        for data in self.sentences:
            words = set(data.completed_sentence.split())
            for w in words:
                self.index[w].append(data)
        print("index build works")

    def autocomplete(self, query: str, max_results: int = 5):
        results = []
        query_norm = self.normalize_text(query)

        first_word = query_norm.split()[0]

        candidates = self.index.get(first_word, [])
        if not candidates:
            candidates = self.sentences

        for data in candidates:
            score = self.calculate_score(query_norm, data.completed_sentence)
            if score > 0:
                data.score = score
                results.append(data)

        results.sort(key=lambda x: x.score, reverse=True)
        return results[:max_results]



