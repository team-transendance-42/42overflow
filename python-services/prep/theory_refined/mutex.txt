---
  What a lock is (start simple)
  
  Imagine a bathroom with one door. A lock on the door means:
  - One person goes in, locks the door
  - Everyone else waits outside
  - Person finishes, unlocks → next person goes in
  
  That's sync.Mutex. One at a time. Always. No exceptions.
====================================
  The problem with a bathroom analogy
  
  A bathroom makes sense — two people can't use it at once.

  But a library bookshelf is different:
  - 10 people can read the same book simultaneously — no problem
  - But if someone is writing notes in the book, nobody else should touch it

  This is the insight behind sync.RWMutex. R stands for Read.
======================
ync.Mutex vs sync.RWMutex

  sync.Mutex          sync.RWMutex
  ──────────────      ──────────────────────────────
  Lock()              Lock()    ← writer lock (exclusive, same as before)
  Unlock()            Unlock()  ← release writer lock

                      RLock()   ← reader lock (shared — many at once)
                      RUnlock() ← release reader lock

  RWMutex has two modes:

  ┌─────────────────────┬─────────────────────────┬─────────────────────────────────┐
  │        Mode         │      Who can enter      │         Who is blocked          │
  ├─────────────────────┼─────────────────────────┼─────────────────────────────────┤
  │ RLock() — read mode │ Many goroutines at once │ Anyone calling Lock() (writers) │
  ├─────────────────────┼─────────────────────────┼─────────────────────────────────┤
  │ Lock() — write mode │ Exactly one goroutine   │ Everyone — readers AND writers  │
  └─────────────────────┴─────────────────────────┴─────────────────────────────────┘
==========================
  What RLock / RUnlock mean

  ragCacheMu.RLock()       // "I want to READ — let me in if no writer is active"
  e, ok := ragCache[key]   // read the map — safe alongside other readers
  ragCacheMu.RUnlock()     // "I'm done reading — release my reader slot"

  R = Read. RLock = Read Lock. RUnlock = Read Unlock
=================================
  ▎ Use sync.Mutex when reads and writes are roughly equal.
  ▎ Use sync.RWMutex when reads vastly outnumber writes.

  A cache is the textbook case for RWMutex: thousands of reads per write. Once an answer is cached, it gets read
  by every user who asks the same question for the next hour — and Lock() would make all of them wait in line for
  no reason.

