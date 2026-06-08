// handlers/stream.go  ← new shared file
package handlers

import (
	"fmt"
	"net/http"
	"strings"
)

func streamSSE(w http.ResponseWriter, ch <-chan string) {
	flusher, ok := w.(http.Flusher)
	if !ok {
		http.Error(w, "Streaming not supported", http.StatusInternalServerError)
		return
	}
	for chunk := range ch {
		for _, line := range strings.Split(chunk, "\n") {
			fmt.Fprintf(w, "data: %s\n", line)
		}
		fmt.Fprint(w, "\n")
		flusher.Flush()
	}
	fmt.Fprintf(w, "event: end\ndata: \n\n")
	flusher.Flush()
}