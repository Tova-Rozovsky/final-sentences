import pytest
from main import AutoCompleteEngine


@pytest.mark.parametrize("query,sentence,expected", [
    # התאמה מלאה
    ("hello world", "hello world", 22),
    ("this is", "to achieve a desired goal is called internetworking and this is where cisco", 14),
    ("this is", "to achieve a desired goal is called internetworking and this i where cisco", 13),
    ("open ai", "open ai", 14),
    ("open ai", "open xi", 13),
    ("abcd", "abxd", 2*4 - 3),
    ("abcd", "abcx", 2*4 - 2),
    ("abcd", "abxcd", 2*4 - 6),
    ("abcd", "abd", 2*3 - 6),
    ("world", "hello world", 10),
    ("open ai", "open xy", 0),
])
def test_calculate_score(query, sentence, expected):
    ace = AutoCompleteEngine()
    assert ace.calculate_score(query, sentence) == expected
