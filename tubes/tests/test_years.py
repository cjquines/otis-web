from datetime import timedelta

import pytest
from django.utils import timezone

from tubes.factories import (
    OIMEProposalFactory,
    OIMESelectionFactory,
    OIMEYearFactory,
)
from tubes.models import OIMEProposal

PROPOSAL_DATA = {
    "title": "Squares",
    "statement": "Find all $x$ such that $x^2 = 4$.",
    "answer": 2,
    "solution": "Clearly $x = \\pm 2$.",
    "subject": "A",
    "difficulty": 1,
}


def closed_year(**kwargs):
    """A year whose proposal window closed yesterday."""
    now = timezone.now()
    return OIMEYearFactory.create(
        proposals_open_at=now - timedelta(days=30),
        proposals_close_at=now - timedelta(days=1),
        **kwargs,
    )


def released_year(**kwargs):
    return closed_year(release_at=timezone.now() - timedelta(hours=1), **kwargs)


# ---------------------------------------------------------------------------
# Pool, freezing and retirement
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_in_pool_excludes_only_retired():
    plain = OIMEProposalFactory.create()
    shortlisted = OIMESelectionFactory.create().proposal
    deferred_released = OIMESelectionFactory.create(
        year=released_year(), status="SEL_DEFERRED"
    ).proposal
    retired = OIMESelectionFactory.create(
        year=released_year(), status="SEL_DONE"
    ).proposal
    pool = set(OIMEProposal.in_pool())
    assert {plain, shortlisted, deferred_released} <= pool
    assert retired not in pool
    assert retired.is_retired is True
    assert deferred_released.is_retired is False
