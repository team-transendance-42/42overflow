package services

import (
	"strings"
	"sync"
	"time"
)

const ragCacheTTL = time.Hour

type ragCacheEntry struct {
	answer    string
	expiresAt time.Time
}

var (
	ragCache   = make(map[string]ragCacheEntry)
	ragCacheMu sync.RWMutex
)

func ragCacheKey(question string) string {
	return strings.ToLower(strings.TrimSpace(question))
}

func ragCacheGet(question string) (string, bool) {
	key := ragCacheKey(question)

	ragCacheMu.RLock()
	e, ok := ragCache[key]
	ragCacheMu.RUnlock()

	if !ok {
		return "", false
	}
	if !time.Now().After(e.expiresAt) {
		return e.answer, true
	}

	// Entry is expired: upgrade to write lock to delete it.
	// Re-check after acquiring the write lock — another goroutine may have
	// already deleted or replaced this entry between RUnlock and Lock.
	ragCacheMu.Lock()
	defer ragCacheMu.Unlock()
	if current, still := ragCache[key]; still && time.Now().After(current.expiresAt) {
		delete(ragCache, key)
	}
	return "", false
}

func ragCacheSet(question, answer string) {
	if strings.TrimSpace(answer) == "" {
		return
	}
	ragCacheMu.Lock()
	defer ragCacheMu.Unlock()
	ragCache[ragCacheKey(question)] = ragCacheEntry{
		answer:    answer,
		expiresAt: time.Now().Add(ragCacheTTL),
	}
}
