# Copyright 2023 Pants project contributors (see CONTRIBUTORS.md).
# Licensed under the Apache License, Version 2.0 (see LICENSE).

from __future__ import annotations

import pytest
from pants_release.changelog import Category, Entry, format_notes, format_notes_by_category


@pytest.mark.parametrize("category", [*(c for c in Category if c is not Category.Internal), None])
def test_format_notes_by_category(category: None | Category) -> None:
    entries = [Entry(category=category, text="some entry")]
    heading = "Uncategorized" if category is None else category.heading()

    formatted = format_notes_by_category(entries)

    # we're testing the exact formatting, so no softwrap/dedent:
    assert (
        formatted
        == f"""\
## {heading}

some entry"""
    )


def test_format_notes() -> None:
    entries = [Entry(category=None, text="some entry")]
    formatted = format_notes(entries)
    # we're testing the exact formatting, so no softwrap/dedent:
    assert (
        formatted
        == """\
some entry"""
    )
