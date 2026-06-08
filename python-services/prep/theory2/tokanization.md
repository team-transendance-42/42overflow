A token is a chunk of text, like a word, punctuation mark, or sometimes even a part of a word.
Example: The sentence “I’m happy!” might be split into tokens: [“I”, “’m”, “happy”, “!”].
2. How are tokens created?

The process of splitting text into tokens is called “tokenization.”
Simple tokenization: Split by spaces and punctuation. Example: “cat’s paw” → [“cat”, “’s”, “paw”].
Advanced tokenization: Some models (like GPT) use “subword” tokenization, breaking rare or long words into smaller pieces (e.g., “unhappiness” → [“un”, “happiness”]).
===============================

How is it decided what is a token?

Rules or algorithms decide what counts as a token:
By whitespace: Each word separated by a space is a token.
By punctuation: Punctuation can be its own token.
By subword units: For efficiency, rare words are split into common pieces.
The choice depends on the tokenizer used (e.g., whitespace, Byte-Pair Encoding, WordPiece).
4. Why do we use tokens?

Computers can’t understand whole sentences at once, so breaking text into tokens makes it easier to process, analyze, and learn patterns.
=================================

Summary:
A token is a basic unit of text chosen by rules in a tokenizer. It can be a word, part of a word, or punctuation, depending on the method used. The goal is to make text easier for computers to handle.
