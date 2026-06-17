package tests

import (
	"context"
	"strings"
	"testing"
	"time"

	"llm-system-interface/services"
)

// TestForwardAndAccumulate_DeliversAllChunks verifies that all tokens from
// rawCh are forwarded to outCh and the full text is passed to onDone.
func TestForwardAndAccumulate_DeliversAllChunks(t *testing.T) {
	ctx := context.Background()
	rawCh := make(chan string, 3)
	outCh := make(chan string, 3)

	rawCh <- "hello"
	rawCh <- " "
	rawCh <- "world"
	close(rawCh)

	var accumulated string
	go services.ForwardAndAccumulate(ctx, rawCh, outCh, func(full string) {
		accumulated = full
	})

	var received []string
	for chunk := range outCh {
		received = append(received, chunk)
	}

	if got := strings.Join(received, ""); got != "hello world" {
		t.Errorf("forwarded = %q, want %q", got, "hello world")
	}
	if accumulated != "hello world" {
		t.Errorf("accumulated = %q, want %q", accumulated, "hello world")
	}
}

// TestForwardAndAccumulate_ExitsOnCancel is the regression test for the goroutine
// leak: when the client disconnects (ctx cancelled) and nobody reads outCh,
// the goroutine must exit instead of blocking on outCh <- chunk forever.
func TestForwardAndAccumulate_ExitsOnCancel(t *testing.T) {
	ctx, cancel := context.WithCancel(context.Background())

	rawCh := make(chan string, 10)
	outCh := make(chan string) // unbuffered, no reader — simulates disconnected client

	rawCh <- "chunk1"
	rawCh <- "chunk2"

	done := make(chan struct{})
	go func() {
		defer close(done)
		services.ForwardAndAccumulate(ctx, rawCh, outCh, func(string) {})
	}()

	cancel() // disconnect — nobody reads outCh

	select {
	case <-done:
		// goroutine exited cleanly
	case <-time.After(2 * time.Second):
		t.Fatal("goroutine blocked after context cancel — goroutine leak detected")
	}
}

// TestForwardAndAccumulate_OnDoneNotCalledOnCancel verifies that a partial
// answer is not cached when the stream is cut short by cancellation.
func TestForwardAndAccumulate_OnDoneNotCalledOnCancel(t *testing.T) {
	ctx, cancel := context.WithCancel(context.Background())

	rawCh := make(chan string, 2)
	outCh := make(chan string) // unbuffered, no reader

	rawCh <- "partial"

	called := false
	done := make(chan struct{})
	go func() {
		defer close(done)
		services.ForwardAndAccumulate(ctx, rawCh, outCh, func(string) { called = true })
	}()

	cancel()
	<-done

	if called {
		t.Error("onDone must not be called on cancel — partial answers must not be cached")
	}
}

// TestForwardAndAccumulate_EmptyStream verifies a closed empty rawCh triggers
// onDone with an empty string and outCh closes cleanly.
func TestForwardAndAccumulate_EmptyStream(t *testing.T) {
	ctx := context.Background()
	rawCh := make(chan string)
	outCh := make(chan string, 1)

	close(rawCh)

	var accumulated string
	go services.ForwardAndAccumulate(ctx, rawCh, outCh, func(full string) {
		accumulated = full
	})

	for range outCh {
	}

	if accumulated != "" {
		t.Errorf("expected empty accumulation, got %q", accumulated)
	}
}
