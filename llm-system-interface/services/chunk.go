package services

import "strings"

// chunkSender tracks the last byte sent across chunks to detect missing word boundaries.
// If two consecutive chunks both start/end on an alphanumeric character, a space is injected
// between them — this fixes the "helloworld" gluing that happens when the LLM stream splits
// tokens at word boundaries without whitespace.
// One chunkSender per request — never share across goroutines.
type chunkSender struct {
	lastChar byte
}

func (s *chunkSender) send(ch chan string, text string) {
	if strings.TrimSpace(text) == "" {
		return
	}
	if s.lastChar != 0 && isAlnum(s.lastChar) && isAlnum(text[0]) {
		ch <- " "
	}
	s.lastChar = text[len(text)-1]
	ch <- text
}

// isAlnum reports whether c is an ASCII letter or digit.
func isAlnum(c byte) bool {
	return (c >= 'a' && c <= 'z') ||
		(c >= 'A' && c <= 'Z') ||
		(c >= '0' && c <= '9')
}