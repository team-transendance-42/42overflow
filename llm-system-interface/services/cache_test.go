package services

import (
	"testing"
	"time"
)

func TestRagCacheMissForUnknownQuestion(t *testing.T) {
	_, ok := ragCacheGet("a question that was never stored xyzzy")
	if ok {
		t.Error("expected cache miss for unknown question")
	}
}

func TestRagCacheSetAndGet(t *testing.T) {
	ragCacheSet("what is malloc?", "malloc allocates heap memory")

	got, ok := ragCacheGet("what is malloc?")
	if !ok {
		t.Fatal("expected cache hit after set")
	}
	if got != "malloc allocates heap memory" {
		t.Errorf("unexpected cached value: %q", got)
	}
}

func TestRagCacheKeyNormalised(t *testing.T) {
	ragCacheSet("  What Is Free?  ", "free releases heap memory")

	got, ok := ragCacheGet("what is free?")
	if !ok {
		t.Fatal("expected cache hit with normalised key")
	}
	if got != "free releases heap memory" {
		t.Errorf("unexpected cached value: %q", got)
	}
}

func TestRagCacheExpiredEntryIsMiss(t *testing.T) {
	key := ragCacheKey("expiry test question abc")
	ragCacheMu.Lock()
	ragCache[key] = ragCacheEntry{
		answer:    "stale answer",
		expiresAt: time.Now().Add(-time.Second),
	}
	ragCacheMu.Unlock()

	_, ok := ragCacheGet("expiry test question abc")
	if ok {
		t.Error("expected expired entry to be a cache miss")
	}
}

func TestRagCacheDoesNotCacheEmptyAnswer(t *testing.T) {
	ragCacheSet("empty answer question xyz", "")

	_, ok := ragCacheGet("empty answer question xyz")
	if ok {
		t.Error("empty answers must not be stored in cache")
	}
}
