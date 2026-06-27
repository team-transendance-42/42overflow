import time
import pytest
from metrics import Metrics


def test_metrics_default_counters_are_zero():
    m = Metrics()
    assert m.retrieve_total == 0
    assert m.retrieve_errors == 0
    assert m.bm25_only_fallbacks == 0
    assert m.corpus_size == 0
    assert m.last_sync_at is None


def test_metrics_uptime_increases_over_time():
    m = Metrics()
    time.sleep(0.05)
    assert m.uptime_seconds() >= 0.05


def test_metrics_uptime_is_rounded():
    m = Metrics()
    result = m.uptime_seconds()
    assert result == round(result, 1)


def test_metrics_counters_increment():
    m = Metrics()
    m.retrieve_total += 1
    m.retrieve_errors += 1
    m.bm25_only_fallbacks += 1
    assert m.retrieve_total == 1
    assert m.retrieve_errors == 1
    assert m.bm25_only_fallbacks == 1


def test_metrics_corpus_size_and_sync_at():
    m = Metrics()
    m.corpus_size = 142
    m.last_sync_at = 1750000000.0
    assert m.corpus_size == 142
    assert m.last_sync_at == 1750000000.0
