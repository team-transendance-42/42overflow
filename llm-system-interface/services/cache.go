package services

import (
	"strings"
	"sync"
	"time"
)

const (
	ragCacheTTL     = time.Hour
	ragCacheMaxSize = 500 // max entries; oldest evicted when exceeded
)

type ragCacheEntry struct {
	answer    string
	expiresAt time.Time
}

var (
	ragCache      = make(map[string]ragCacheEntry)
	ragCacheOrder []string // insertion order for FIFO eviction
	ragCacheMu    sync.RWMutex
)

func ragCacheKey(question string) string {
	return strings.ToLower(strings.TrimSpace(question))
}

func ragCacheGet(question string) (string, bool) {
	key := ragCacheKey(question)

	ragCacheMu.RLock() // allowed read only, no write
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
	key := ragCacheKey(question)
	ragCacheMu.Lock()
	defer ragCacheMu.Unlock()

	// Evict oldest entry when at capacity.
	// FIFO is sufficient here — answers don't get "hotter" from re-reads,
	// and TTL already handles staleness. True LRU would cost a write on
	// every read, which defeats the RWMutex read-concurrency we set up.
	if _, exists := ragCache[key]; !exists {
		// Trim ghost keys from the front: entries deleted by ragCacheGet (expired)
		// leave their key in ragCacheOrder but not in ragCache.  Without this trim,
		// ragCacheOrder grows beyond ragCacheMaxSize when entries expire faster than
		// new ones are inserted (ghost keys accumulate without bound).
		for len(ragCacheOrder) > 0 {
			if _, alive := ragCache[ragCacheOrder[0]]; alive {
				break
			}
			ragCacheOrder = ragCacheOrder[1:]
		}
		for len(ragCache) >= ragCacheMaxSize {
			oldest := ragCacheOrder[0]
			ragCacheOrder = ragCacheOrder[1:]
			delete(ragCache, oldest)
		}
		ragCacheOrder = append(ragCacheOrder, key)
	}

	ragCache[key] = ragCacheEntry{
		answer:    answer,
		expiresAt: time.Now().Add(ragCacheTTL),
	}
}
