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
	ragCacheMu sync.Mutex
)

func ragCacheKey(question string) string {
	return strings.ToLower(strings.TrimSpace(question))
}

func ragCacheGet(question string) (string, bool) {
	key := ragCacheKey(question)
	ragCacheMu.Lock()
	defer ragCacheMu.Unlock()
	e, ok := ragCache[key]
	if !ok {
		return "", false
	}
	if time.Now().After(e.expiresAt) {
		delete(ragCache, key)
		return "", false
	}
	return e.answer, true
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
