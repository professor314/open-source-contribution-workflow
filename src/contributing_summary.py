"""Contributing summary module.

Summarizes CONTRIBUTING.md content into a concise summary of no more than 200 words.
"""

import re


def summarize_contributing(text: str) -> str:
    """Summarize CONTRIBUTING.md text content into at most 200 words.

    Args:
        text: Raw CONTRIBUTING.md file content.

    Returns:
        A summary string of no more than 200 words. If the input is empty
        or whitespace-only, returns a notice that no guidelines were found.
    """
    if not text or not text.strip():
        return "No formal contribution guidelines were found."

    # Strip markdown formatting characters
    cleaned = _strip_markdown(text)

    # Split into sentences
    sentences = _split_sentences(cleaned)

    # Filter to the most relevant sentences about contribution process
    relevant = _filter_relevant_sentences(sentences)

    # If no relevant sentences found, fall back to taking first sentences
    if not relevant:
        relevant = sentences

    # Take sentences that fit within 200 words
    summary = _fit_within_word_limit(relevant, max_words=200)

    return summary


def _strip_markdown(text: str) -> str:
    """Remove markdown formatting characters for cleaner output."""
    # Remove # characters at line starts (keep the header text)
    text = re.sub(r'^#{1,6}\s*', '', text, flags=re.MULTILINE)
    # Remove bold/italic markers
    text = re.sub(r'\*{1,3}', '', text)
    # Remove inline code backticks
    text = re.sub(r'`{1,3}', '', text)
    # Remove link syntax [text](url) -> text
    text = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', text)
    # Remove image syntax ![alt](url)
    text = re.sub(r'!\[([^\]]*)\]\([^)]*\)', r'\1', text)
    # Remove blockquote markers
    text = re.sub(r'^>\s*', '', text, flags=re.MULTILINE)
    # Remove horizontal rules
    text = re.sub(r'^[-*_]{3,}\s*$', '', text, flags=re.MULTILINE)
    # Remove list markers (- * + and numbered)
    text = re.sub(r'^\s*[-*+]\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*\d+\.\s+', '', text, flags=re.MULTILINE)
    # Collapse multiple whitespace/newlines into single spaces
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def _split_sentences(text: str) -> list:
    """Split text into sentences."""
    # Split on sentence-ending punctuation followed by space or end
    sentences = re.split(r'(?<=[.!?])\s+', text)
    # Filter out empty strings and very short fragments
    return [s.strip() for s in sentences if s.strip() and len(s.strip()) > 5]


def _filter_relevant_sentences(sentences: list) -> list:
    """Filter sentences to those most relevant to contribution guidelines."""
    keywords = [
        'pull request', 'pr', 'submit', 'branch', 'fork',
        'code style', 'format', 'lint', 'style guide',
        'test', 'testing', 'pytest', 'unittest',
        'issue', 'bug report', 'feature request',
        'slack', 'discord', 'chat', 'mailing list', 'communication',
        'review', 'merge', 'commit', 'convention',
        'contribute', 'contribution', 'guidelines',
    ]

    relevant = []
    for sentence in sentences:
        lower = sentence.lower()
        if any(kw in lower for kw in keywords):
            relevant.append(sentence)

    return relevant


def _fit_within_word_limit(sentences: list, max_words: int = 200) -> str:
    """Take sentences that fit within the word limit."""
    result_sentences = []
    word_count = 0

    for sentence in sentences:
        sentence_words = sentence.split()
        if word_count + len(sentence_words) <= max_words:
            result_sentences.append(sentence)
            word_count += len(sentence_words)
        else:
            # If we haven't added anything yet, truncate the first sentence
            if not result_sentences:
                truncated = ' '.join(sentence_words[:max_words])
                result_sentences.append(truncated)
            break

    return ' '.join(result_sentences)
