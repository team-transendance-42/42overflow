c := make(chan int)

go func() { c <- 3 }() // Create a new goroutine that puts 3 to the channel

fmt.Println(<-c) // Take 3 from the channel and print it in the main thread
------------------------

// unbuffered
messages := make(chan string)
go func() { messages <- "ping" }()
msg := <-messages

// buffered (capacity 1)
messages := make(chan string, 1)
func() { messages <- "ping" }()
msg := <-messages