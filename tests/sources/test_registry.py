from pipeline.sources.registry import SOURCES


def test_sources_load_without_error():
    names = [source.name for source in SOURCES]
    assert names == ["tiktok", "smartrecruiters", "lever", "careers@gov", "workday"]


def test_every_source_has_at_least_one_slug():
    for source in SOURCES:
        assert len(source.slugs) >= 1, f"{source.name} has no slugs configured"
