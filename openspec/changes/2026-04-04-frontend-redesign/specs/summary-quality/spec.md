## ADDED Requirements

### Requirement: Junk summary detection
The system SHALL detect summaries that contain non-article content such as cookie notices, security challenges, or privacy disclaimers.

#### Scenario: Cookie consent detection
- **WHEN** a summary contains phrases like "We use cookies", "cookie policy", or "by continuing you agree"
- **THEN** the summary MUST be flagged as junk

#### Scenario: Security wall detection
- **WHEN** a summary contains phrases like "establishing a secure connection", "checking your browser", or "security service to protect"
- **THEN** the summary MUST be flagged as junk

#### Scenario: Privacy disclaimer detection
- **WHEN** a summary contains phrases like "Your Privacy is Important", "Do Not Sell", or "review our Terms of Service"
- **THEN** the summary MUST be flagged as junk

#### Scenario: CAPTCHA detection
- **WHEN** a summary contains phrases like "prove you are human", "complete the CAPTCHA", or "verify you are not a robot"
- **THEN** the summary MUST be flagged as junk

### Requirement: Junk summary fallback
The system SHALL replace junk summaries with truncated article text when available.

#### Scenario: Article text available
- **WHEN** a summary is flagged as junk and article.text contains valid content
- **THEN** the summary MUST be replaced with article.text truncated to ~300 words

#### Scenario: No article text available
- **WHEN** a summary is flagged as junk and no alternative text is available
- **THEN** the summary MUST be set to an empty string

### Requirement: Junk detection logging
The system SHALL log when junk summaries are detected.

#### Scenario: Logging format
- **WHEN** a junk summary is detected
- **THEN** the system MUST log a warning with the article title and the matched anti-pattern
