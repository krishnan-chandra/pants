# Copyright 2021 Pants project contributors (see CONTRIBUTORS.md).
# Licensed under the Apache License, Version 2.0 (see LICENSE).

# mypy: disable-error-code="import-untyped"
#   Disables checking of the `pkg_resources` below which was awkward to figure out how to disable
#   with a `# type: ignore[import-untyped]` comment.

from __future__ import annotations

import logging
import urllib.parse

import pkg_resources
from pkg_resources.extern.packaging.requirements import InvalidRequirement

logger = logging.getLogger(__name__)


class PipRequirement:
    """A Pip-style requirement."""

    @classmethod
    def parse(cls, line: str, description_of_origin: str = "") -> PipRequirement:
        try:
            return cls(pkg_resources.Requirement.parse(line))
        except InvalidRequirement as e:
            scheme, netloc, path, query, fragment = urllib.parse.urlsplit(line, scheme="file")
            if fragment:
                # Try converting a pip VCS-style requirement into a PEP-440 one that can be
                # parsed as a Requirement. E.g.,
                # git+https://github.com/django/django.git@stable/2.1.x#egg=Django
                # into
                # Django@ git+https://github.com/django/django.git@stable/2.1.x#egg=Django

                # Note: In pip VCS urls the fragment is a query-style string.
                fragment_params = urllib.parse.parse_qs(fragment)
                egg = fragment_params.get("egg")
                if egg:
                    # parse_qs() ignores params with empty values by default, so we're guaranteed
                    # that there is at least one value in this list.
                    project = egg[0]
                    # We recompose the URL to force the default file:// scheme to be explicit.
                    full_url = urllib.parse.urlunsplit((scheme, netloc, path, query, fragment))
                    pep_440_req_str = f"{project}@ {full_url}"
                    try:
                        return cls(pkg_resources.Requirement.parse(pep_440_req_str))
                    except InvalidRequirement:
                        # If parsing the converted URL fails for some reason, it's probably less
                        # confusing to the user if we raise the original error instead of one for
                        # a synthetic requirement string they don't directly know about.
                        pass
            origin_str = f" in {description_of_origin}" if description_of_origin else ""
            raise ValueError(f"Invalid requirement '{line}'{origin_str}: {e}")

    def __init__(self, req: pkg_resources.Requirement):
        self._req = req

    def as_pkg_resources_requirement(self) -> pkg_resources.Requirement:
        return self._req

    @property
    def project_name(self) -> str:
        return self._req.project_name

    @property
    def specs(self):
        return self._req.specs

    @property
    def url(self):
        return self._req.url

    def __hash__(self):
        return hash(self._req)

    def __eq__(self, other):
        # Semantic equality requires parsing the specifier (since order in it doesn't matter).
        if not isinstance(other, self.__class__):
            return False
        return self._req == other._req

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._req})"

    def __str__(self):
        return str(self._req)
