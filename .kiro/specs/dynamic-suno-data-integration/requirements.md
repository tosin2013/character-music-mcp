# Requirements Document

## Introduction

This feature will enhance the Character Music MCP by integrating dynamic data from the Suno AI Wiki to provide more comprehensive and up-to-date genre mappings, meta tags, and musical knowledge. Instead of relying on static hardcoded mappings, the system will fetch and utilize the extensive genre lists and meta tag information from sunoaiwiki.com.

## Requirements

### Requirement 1

**User Story:** As a music generation system, I want to access comprehensive genre information from Suno AI Wiki, so that I can provide more accurate and diverse genre mappings for character personas.

#### Acceptance Criteria

1. WHEN the system needs genre information THEN it SHALL read data from locally downloaded copy of https://sunoaiwiki.com/resources/2024-05-03-list-of-music-genres-and-styles/
2. WHEN genre data is parsed THEN the system SHALL extract and structure it for use in character-to-genre mapping
3. WHEN genre mapping occurs THEN the system SHALL use the comprehensive wiki data instead of hardcoded mappings
4. IF the wiki is unavailable THEN the system SHALL fall back to existing hardcoded mappings

### Requirement 2

**User Story:** As a music generation system, I want to access comprehensive meta tag information from Suno AI Wiki, so that I can generate more sophisticated and accurate Suno commands with proper meta tags.

#### Acceptance Criteria

1. WHEN the system needs meta tag information THEN it SHALL read data from locally downloaded copy of https://sunoaiwiki.com/resources/2024-05-13-list-of-metatags/
2. WHEN meta tag data is parsed THEN the system SHALL extract and categorize tags by type (structural, emotional, instrumental, etc.)
3. WHEN generating Suno commands THEN the system SHALL use wiki-sourced meta tags for enhanced command generation
4. IF the wiki is unavailable THEN the system SHALL fall back to existing hardcoded meta tags

### Requirement 2.1

**User Story:** As a music generation system, I want to access Suno AI tips and techniques from the wiki, so that I can apply advanced prompt optimization and production techniques.

#### Acceptance Criteria

1. WHEN the system needs prompt optimization guidance THEN it SHALL read from locally downloaded tip pages including:
   - https://sunoaiwiki.com/tips/2024-05-02-how-to-enhance-song-production-using-suno-ai/
   - https://sunoaiwiki.com/tips/2024-04-16-how-to-make-suno-ai-sing-with-spoken-word/
   - https://sunoaiwiki.com/tips/2024-05-04-how-to-structure-prompts-for-suno-ai/
   - https://sunoaiwiki.com/tips/2024-05-04-how-to-use-meta-tags-in-suno-ai-for-song-creation/
   - https://sunoaiwiki.com/tips/2024-05-07-how-to-get-specific-vocal-styles-in-suno-ai/
   - https://sunoaiwiki.com/tips/2024-05-08-how-to-bypass-explicit-lyric-restrictions/
   - https://sunoaiwiki.com/tips/2024-05-09-how-to-end-a-song-naturally/
   - https://sunoaiwiki.com/tips/2024-05-18-how-to-optimize-prompts-in-suno-ai-with-letter-case/
   - https://sunoaiwiki.com/tips/2024-05-22-how-to-prompt-suno-ai-to-use-animal-sounds-and-noises/
   - https://sunoaiwiki.com/tips/2024-05-22-how-to-solve-suno-ai-sampling-detection-issues/
   - https://sunoaiwiki.com/tips/2024-05-25-how-to-handle-producer-tags-in-suno-ai/
   - https://sunoaiwiki.com/tips/2024-07-08-how-to-create-better-lyrics-for-suno/
   - https://sunoaiwiki.com/tips/2024-07-08-improve-suno-hiphop-rap-trap/
2. WHEN generating commands THEN the system SHALL apply techniques from tip pages for better results
3. WHEN handling specific scenarios THEN the system SHALL reference relevant tip pages for best practices
4. WHEN tip pages are parsed THEN the system SHALL extract actionable techniques and patterns

### Requirement 3

**User Story:** As a system administrator, I want the wiki pages to be downloaded and stored locally with download metadata, so that the system has reliable access to data and can track when updates are needed.

#### Acceptance Criteria

1. WHEN wiki pages are downloaded THEN the system SHALL save the full HTML content locally with download timestamps
2. WHEN local wiki files exist THEN the system SHALL parse data from local files instead of making web requests
3. WHEN local files are older than configured refresh interval THEN the system SHALL attempt to download fresh copies
4. WHEN downloads fail THEN the system SHALL continue using existing local files if available

### Requirement 4

**User Story:** As a developer, I want the wiki integration to be configurable, so that I can control data sources, download locations, and update frequencies based on deployment needs.

#### Acceptance Criteria

1. WHEN the system starts THEN it SHALL read configuration for wiki integration settings including local storage paths
2. WHEN wiki integration is disabled in config THEN the system SHALL use only hardcoded data
3. WHEN download refresh intervals are configured THEN the system SHALL respect those settings
4. WHEN wiki URLs are configured THEN the system SHALL use the specified endpoints for downloads
5. WHEN new wiki pages are added to configuration THEN the system SHALL download and integrate them automatically

### Requirement 5

**User Story:** As a music generation system, I want to intelligently match character traits to wiki genres, so that I can provide more nuanced and accurate genre selections.

#### Acceptance Criteria

1. WHEN character traits are analyzed THEN the system SHALL map them to appropriate wiki genres using semantic matching
2. WHEN multiple genres match character traits THEN the system SHALL rank them by relevance and confidence
3. WHEN wiki genres include subgenres THEN the system SHALL consider hierarchical relationships in matching
4. WHEN no direct matches exist THEN the system SHALL use similarity algorithms to find closest genre matches

### Requirement 6

**User Story:** As a music generation system, I want to use wiki meta tags contextually, so that I can generate more sophisticated and genre-appropriate Suno commands.

#### Acceptance Criteria

1. WHEN generating commands for specific genres THEN the system SHALL select appropriate meta tags from wiki data
2. WHEN character emotions are analyzed THEN the system SHALL map them to relevant emotional meta tags from the wiki
3. WHEN instrumental preferences are determined THEN the system SHALL use corresponding instrumental meta tags from the wiki
4. WHEN combining meta tags THEN the system SHALL ensure compatibility and avoid conflicting tags

### Requirement 7

**User Story:** As a developer, I want clear instructions on how to add new wiki pages to the system, so that I can easily extend the knowledge base with new Suno AI resources.

#### Acceptance Criteria

1. WHEN adding new wiki pages THEN the system SHALL provide configuration format documentation
2. WHEN new pages are configured THEN the system SHALL validate URLs and download content
3. WHEN page types are specified THEN the system SHALL apply appropriate parsing logic
4. WHEN documentation is provided THEN it SHALL include examples of adding different page types (resources, tips, guides)

### Requirement 8

**User Story:** As an LLM processing album generation requests, I want to receive source URLs along with wiki content, so that I can provide transparent references and understand the context of the information.

#### Acceptance Criteria

1. WHEN wiki content is included in LLM context THEN the system SHALL include the original source URL
2. WHEN multiple wiki sources are referenced THEN the system SHALL clearly attribute each piece of information to its source
3. WHEN building album context THEN the system SHALL include relevant wiki URLs for genres, meta tags, and techniques being used
4. WHEN LLM responses reference wiki information THEN they SHALL include the source URLs for user reference