## MODIFIED Requirements

### Requirement: Article content download
The system SHALL download and parse article content using Newspaper4k by creating a `newspaper.Article` instance configured with a 30-second timeout and a standard browser user agent.

#### Scenario: Successful download
- **WHEN** an article URL is accessible
- **THEN** the system calls `article.download()` and `article.parse()` to retrieve and extract content

#### Scenario: Network timeout
- **WHEN** a download request times out after 30 seconds
- **THEN** the system MUST log a warning and skip that article

#### Scenario: HTTP error status
- **WHEN** the server returns 404, 403, or 5xx status codes
- **THEN** the system MUST log a warning and skip that article

### Requirement: Content extraction
The system SHALL use Newspaper4k to extract clean article text from the downloaded HTML content.

#### Scenario: Successful extraction
- **WHEN** Newspaper4k successfully parses content from the URL
- **THEN** the system uses `article.text` for NLP processing

#### Scenario: Extraction failure
- **WHEN** Newspaper4k cannot extract meaningful text (article.text is empty)
- **THEN** the system MUST log a warning and skip that article

### Requirement: Summary generation
The system SHALL generate a summary using Newspaper4k's built-in NLP by calling `article.nlp()` and reading `article.summary`.

#### Scenario: NLP summary available
- **WHEN** `article.nlp()` produces a non-empty `article.summary`
- **THEN** the system uses `article.summary` as the stored summary

#### Scenario: NLP summary empty with text available
- **WHEN** `article.summary` is empty but `article.text` is non-empty
- **THEN** the system truncates `article.text` to approximately 300 words and uses that as the summary

#### Scenario: Article shorter than 300 words
- **WHEN** extracted text contains fewer than 300 words
- **THEN** the system uses the entire text as the summary

### Requirement: NLTK tokenizer availability
The system SHALL ensure the NLTK `punkt_tab` tokenizer is available before calling `article.nlp()`.

#### Scenario: Tokenizer downloaded at startup
- **WHEN** the pipeline script starts
- **THEN** the system calls `nltk.download('punkt_tab', quiet=True)` before processing any articles

### Requirement: Summary storage format
The system SHALL store summaries as plain text without HTML markup.

#### Scenario: Clean text summary
- **WHEN** a summary is generated
- **THEN** it MUST NOT contain HTML tags, scripts, or style elements

## REMOVED Requirements

### Requirement: Word counting
**Reason**: Manual word counting was only needed for the word-truncation summary approach. Newspaper4k's NLP summary replaces this; the fallback truncation uses Python's `str.split()` inline without a dedicated word-count function.
**Migration**: Remove any standalone word-count utility. Use `len(text.split())` inline if a word count is needed for the fallback truncation path.
