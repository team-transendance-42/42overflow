package services

import (
	"strings"
	"testing"
)

func TestBuildRAGPromptContainsOnlyConstraint(t *testing.T) {
	prompt := buildRAGPrompt("some context", "what is malloc?")
	if !strings.Contains(prompt, "ONLY") {
		t.Error("prompt must instruct model to answer ONLY from context")
	}
}

func TestBuildRAGPromptContainsDoNotGuess(t *testing.T) {
	prompt := buildRAGPrompt("some context", "what is malloc?")
	if !strings.Contains(prompt, "DO NOT guess") {
		t.Error("prompt must explicitly prohibit guessing")
	}
}

func TestBuildRAGPromptContainsDoNotUseTrainingKnowledge(t *testing.T) {
	prompt := buildRAGPrompt("some context", "what is malloc?")
	if !strings.Contains(prompt, "DO NOT use your training knowledge") {
		t.Error("prompt must prohibit use of training knowledge")
	}
}

func TestBuildRAGPromptContainsFallbackPhrase(t *testing.T) {
	prompt := buildRAGPrompt("some context", "what is malloc?")
	if !strings.Contains(prompt, "I don't have enough context to answer this.") {
		t.Error("prompt must include the exact fallback phrase the model should use")
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
