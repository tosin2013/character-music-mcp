# Requirements Document

## Introduction

This feature will systematically fix the critical issues identified in the MCP tools diagnostic report. The MCP tools currently suffer from format mismatches, hardcoded content, generic output, and function errors that prevent them from working as intended. This spec will address each tool's specific issues to restore proper functionality.

## Requirements

### Requirement 1

**User Story:** As a user of the analyze_character_text tool, I want accurate character analysis with proper three-layer analysis, so that I can get meaningful character insights instead of empty or incorrect results.

#### Acceptance Criteria

1. WHEN character text is analyzed THEN the system SHALL return populated characters array with detected characters
2. WHEN narrative themes are identified THEN the system SHALL provide accurate themes beyond just "friendship"
3. WHEN emotional arcs are analyzed THEN the system SHALL provide varied emotional states, not just "neutral"
4. WHEN character analysis is performed THEN the system SHALL include skin/flesh/core layer analysis as described
5. WHEN character descriptions are clear THEN the system SHALL extract and structure character information properly

### Requirement 2

**User Story:** As a user of the generate_artist_personas tool, I want the tool to accept the correct character profile format, so that I can generate artist personas without format errors.

#### Acceptance Criteria

1. WHEN character profiles are submitted THEN the system SHALL accept the expected JSON format without 'skin' parameter errors
2. WHEN CharacterProfile is initialized THEN it SHALL use the correct parameter names and structure
3. WHEN artist personas are generated THEN the system SHALL return valid persona data
4. WHEN the tool processes input THEN it SHALL handle all expected character profile fields correctly

### Requirement 3

**User Story:** As a user of the creative_music_generation tool, I want meaningful creative variations and practical Suno commands, so that I can get useful music production guidance instead of generic repetition.

#### Acceptance Criteria

1. WHEN music concepts are processed THEN the system SHALL generate creative variations, not just repeat the input
2. WHEN production commands are created THEN they SHALL be practical and usable with Suno AI
3. WHEN creative generation occurs THEN the output SHALL provide meaningful musical insights and suggestions
4. WHEN different concepts are input THEN the system SHALL produce varied and contextually appropriate responses

### Requirement 4

**User Story:** As a user of the complete_workflow tool, I want the workflow to execute without function errors, so that I can run complete music generation workflows successfully.

#### Acceptance Criteria

1. WHEN the complete workflow is triggered THEN the system SHALL execute without 'FunctionTool' object not callable errors
2. WHEN workflow steps are processed THEN each step SHALL complete successfully
3. WHEN internal functions are called THEN they SHALL be properly callable and functional
4. WHEN the workflow completes THEN it SHALL return meaningful results for the entire process

### Requirement 5

**User Story:** As a user of the process_universal_content tool, I want content processing that respects my input parameters, so that I get relevant output instead of hardcoded Bristol backstories.

#### Acceptance Criteria

1. WHEN character descriptions are provided THEN the system SHALL use the provided character, not hardcoded "Marcus" or Bristol references
2. WHEN genre specifications are given THEN the system SHALL generate content in the requested genre, not always alternative/philosophical
3. WHEN content is processed THEN the output SHALL reflect the input parameters, not predetermined backstories
4. WHEN different characters are specified THEN the system SHALL generate unique content for each character

### Requirement 6

**User Story:** As a user of the create_character_album tool, I want unique tracks that reflect my character and genre specifications, so that I get diverse album content instead of identical tracks.

#### Acceptance Criteria

1. WHEN albums are created THEN each track SHALL have unique lyrics and content
2. WHEN character descriptions are provided THEN the album SHALL reflect the specified character, not hardcoded personas
3. WHEN genres are specified THEN the music SHALL match the requested genre (e.g., Memphis hip-hop), not default to alternative
4. WHEN albums are generated THEN the character description SHALL be used throughout, not ignored

### Requirement 7

**User Story:** As a user of the create_story_integrated_album tool, I want proper character detection from narratives, so that I can create story-based albums without character detection failures.

#### Acceptance Criteria

1. WHEN narratives with explicit characters are provided THEN the system SHALL detect and extract character information
2. WHEN character detection runs THEN it SHALL not fail with "No characters found" errors for clear character descriptions
3. WHEN story integration occurs THEN the system SHALL properly parse character details from narrative text
4. WHEN albums are created THEN they SHALL incorporate the detected characters into the musical content

### Requirement 8

**User Story:** As a user of the analyze_artist_psychology tool, I want the tool to accept correct character profile formats, so that I can analyze artist psychology without format errors.

#### Acceptance Criteria

1. WHEN character profiles are analyzed THEN the system SHALL accept profiles without 'age' parameter errors
2. WHEN CharacterProfile objects are created THEN they SHALL use the correct initialization parameters
3. WHEN psychology analysis occurs THEN it SHALL process character data and return meaningful psychological insights
4. WHEN the tool runs THEN it SHALL handle all expected character profile fields correctly

### Requirement 9

**User Story:** As a user of the crawl_suno_wiki_best_practices tool, I want actual wiki data and Suno specifications, so that I get useful information instead of empty data fields.

#### Acceptance Criteria

1. WHEN wiki crawling occurs THEN the system SHALL return populated data fields, not empty results
2. WHEN Suno specifications are requested THEN the system SHALL provide actual Suno AI guidelines and best practices
3. WHEN crawling completes THEN it SHALL return meaningful wiki content, not just integration notes
4. WHEN best practices are gathered THEN they SHALL be actionable and specific to Suno AI usage

### Requirement 10

**User Story:** As a user of the create_suno_commands tool, I want the tool to accept correct persona data formats, so that I can generate Suno commands without format errors.

#### Acceptance Criteria

1. WHEN persona data is submitted THEN the system SHALL accept the expected JSON format without format errors
2. WHEN Suno commands are generated THEN they SHALL be based on valid persona data processing
3. WHEN the tool processes input THEN it SHALL handle persona data structure correctly
4. WHEN commands are created THEN they SHALL be practical and usable with Suno AI

### Requirement 11

**User Story:** As a user of the understand_topic_with_emotions tool, I want meaningful emotional analysis and varied output, so that I get useful insights instead of repetitive generic responses.

#### Acceptance Criteria

1. WHEN topics are analyzed THEN the system SHALL provide actual emotional analysis, not just repeat input text
2. WHEN emotional understanding occurs THEN it SHALL generate varied emotional insights, not always "contemplative"
3. WHEN beat patterns are requested THEN they SHALL be meaningful and genre-appropriate, not generic
4. WHEN different topics are processed THEN the system SHALL produce contextually appropriate emotional responses

### Requirement 12

**User Story:** As a developer maintaining the MCP tools, I want comprehensive error logging and debugging information, so that I can quickly identify and fix issues when they occur.

#### Acceptance Criteria

1. WHEN tools encounter errors THEN they SHALL log detailed error information including stack traces
2. WHEN format mismatches occur THEN the system SHALL provide clear information about expected vs actual formats
3. WHEN tools fail THEN they SHALL return helpful error messages that aid in debugging
4. WHEN debugging is needed THEN comprehensive logging SHALL be available for all tool operations

### Requirement 13

**User Story:** As a developer extending the MCP tools, I want consistent data models and interfaces, so that I can easily add new functionality without format conflicts.

#### Acceptance Criteria

1. WHEN new tools are added THEN they SHALL use consistent character profile formats across all tools
2. WHEN data models are defined THEN they SHALL be shared and reused to prevent format mismatches
3. WHEN interfaces are created THEN they SHALL follow consistent patterns for input validation and error handling
4. WHEN tools interact THEN they SHALL use compatible data structures and formats