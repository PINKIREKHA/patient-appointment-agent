from app.validation import is_explicit_confirmation


def test_yes_is_confirmation():
    assert is_explicit_confirmation("yes") is True


def test_yes_please_is_confirmation():
    assert is_explicit_confirmation("Yes please") is True


def test_book_it_is_confirmation():
    assert is_explicit_confirmation("book it") is True


def test_maybe_is_not_confirmation():
    assert is_explicit_confirmation("maybe") is False


def test_question_is_not_confirmation():
    assert is_explicit_confirmation(
        "Is this appointment still available?"
    ) is False