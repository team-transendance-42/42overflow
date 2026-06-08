Go uses a garbage collector (GC) — you generally don't manage memory manually, but there are things worth knowing:

What Go handles for you
Allocation — new(), make(), struct literals, slices, maps all allocate automatically
Deallocation — GC frees memory when nothing references it anymore
Stack vs heap — the compiler decides; small, short-lived values go on the stack (fast, auto-freed), larger/escaping values go on the heap (GC-managed)
============================================

What you do need to think about
Goroutine leaks — a goroutine that never exits holds its stack forever:

go func() {
    for { /* no exit condition */ }  // leaks
}()
--------
Map/slice growth — these never shrink automatically
m := make(map[string]Entry)
// delete(m, key) removes the entry but the map's internal capacity remains, so memory isn't freed
// To reduce memory, you can create a new map and copy entries over:
newMap := make(map[string]Entry, len(m))
--------
Holding references longer than needed — if a large slice is kept alive by a small sub-slice

big := make([]byte, 1_000_000)
small := big[:10]  // big stays in memory as long as small is reachable
Fix: small := append([]byte{}, big[:10]...) (copy it to a new slice)
--------