package services

import (
	"strings"
	"testing"
)

func TestBuildRAGPromptContainsOnlyConstraint(t *testing.T) {
	prompt := buildRAGPrompt("some context", "what is malloc?")
	if !strings.Contains(prompt, "ONLY") {
		t.Error("prompt must instruct model to answer ONLY from posts")
	}
}

func TestBuildRAGPromptContainsDoNotInclude(t *testing.T) {
	prompt := buildRAGPrompt("some context", "what is malloc?")
	if !strings.Contains(prompt, "do NOT include that sentence") {
		t.Error("prompt must explicitly prohibit the fallback phrase when an answer exists")
	}
}

func TestBuildRAGPromptContainsFallbackPhrase(t *testing.T) {
	prompt := buildRAGPrompt("some context", "what is malloc?")
	if !strings.Contains(prompt, "The community hasn't covered this yet") {
		t.Error("prompt must include the fallback phrase for the model to use")
	}
}

func TestBuildRAGPromptEmbeddsQuestion(t *testing.T) {
	prompt := buildRAGPrompt("some context", "what is malloc?")
	if !strings.Contains(prompt, "what is malloc?") {
		t.Error("prompt must include the user question")
	}
}

func TestBuildRAGPromptEmbeddsContext(t *testing.T) {
	prompt := buildRAGPrompt("malloc allocates heap memory", "what is malloc?")
	if !strings.Contains(prompt, "malloc allocates heap memory") {
		t.Error("prompt must include the context block")
	}
}
