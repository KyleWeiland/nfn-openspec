## REMOVED Requirements

### Requirement: Google Alerts redirect detection
**Reason**: gnews returns direct article URLs. There are no Google Alerts redirect URLs to detect or parse.
**Migration**: Remove all redirect-detection logic. Pass gnews `result['url']` directly to the article processing stage.

### Requirement: URL parameter extraction
**Reason**: No longer applicable — gnews does not produce redirect URLs with query parameters.
**Migration**: Delete the URL parameter extraction function. Article URLs come pre-resolved from gnews.

### Requirement: URL decoding
**Reason**: gnews returns fully-decoded, direct article URLs. No URL-decoding step is needed.
**Migration**: Remove URL decoding logic from the pipeline.

### Requirement: Extracted URL validation
**Reason**: Basic URL validation (HTTP/HTTPS scheme) is now handled implicitly by Newspaper4k — it will raise or return empty content for malformed URLs, which is caught by the existing download failure handler.
**Migration**: Remove explicit URL validation. Rely on Newspaper4k's download error handling to catch invalid URLs.
