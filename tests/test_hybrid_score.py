import pytest

from backend.services.hybrid_search_service import HybridSearchService


def test_calculate_final_score():
    score = HybridSearchService._calculate_final_score(
        keyword_score=1.0,
        semantic_score=0.5,
    )

    assert score == pytest.approx(0.7)