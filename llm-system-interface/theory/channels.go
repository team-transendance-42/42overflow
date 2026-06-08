/* Channel — typed pipe between goroutines: without shared memory + mutexes
ch := make(chan int)       // unbuffered: sender blocks until receiver reads
ch := make(chan int, 5)    // buffered: sender can push 5 items before blocking
Go's philosophy: "Don't communicate by sharing memory; share memory by communicating." — channels are the preferred way, mutex is the fallbac
*/
// package main

import (
    "fmt"
    "sync"
)

func compute(ch chan int) {
    result := 42
    ch <- result  // send into channel (blocks until someone reads)
}

func main() {
    ch := make(chan int)

    go compute(ch)   // runs in background

    val := <-ch      // receive from channel (blocks until something arrives)
    fmt.Println(val) // 42
}
// -------------------------------------------
func worker(id int, ch chan string, wg *sync.WaitGroup) {
    defer wg.Done()
    ch <- fmt.Sprintf("worker %d done", id)
}

func main() {
    ch := make(chan string, 5) // buffered
    var wg sync.WaitGroup

    for i := 0; i < 5; i++ {
        wg.Add(1)
        go worker(i, ch, &wg)
    }

    // close channel when all workers finish
    go func() {
        wg.Wait()
        close(ch)
    }()

    // range over channel until it's closed
    for msg := range ch {
        fmt.Println(msg)
    }
}
