
# Implementation Plan

- [x] 1. Fix core character extraction logic in WorkingUniversalProcessor
  - Add content type detection to prevent extracting random words as characters
  - Implement logic to distinguish between narrative fiction, philosophical content, and character descriptions
  - Add fallback to create conceptual characters when no narrative characters exist
  - _Requirements: 1.1, 1.2, 1.3, 1.4_

- [x] 2. Enhance character analysis for conceptual content processing
- [x] 2.1 Add content type detection to EnhancedCharacterAnalyzer
  - Modify analyze_character_text method to detect content type before processing
  - Add logic to handle explicit character descriptions without extraction attempts
  - Implement conceptual character creation from philosophical themes and concepts
  - _Requirements: 2.1, 2.2, 2.3, 2.4_

- [x] 2.2 Extend StandardCharacterProfile with optional conceptual fields
  - Add backward-compatible fields for conceptual_basis, content_type, processing_notes
  - Implement helper methods to identify conceptual vs narrative characters
  - Ensure existing functionality remains unchanged
  - _Requirements: 2.2, 2.3_

- [x] 3. Consolidate and fix album generation tools
- [x] 3.1 Merge overlapping album generation functions in server.py
  - Consolidate create_story_integrated_album, create_character_album into single robust tool
  - Remove redundant album creation functions to reduce code bloat
  - Implement proper narrative progression logic for track generation
  - _Requirements: 3.1, 3.2, 3.3, 3.4_

- [x] 3.2 Fix track title and content generation
  - Replace generic track titles (Track 1, Song 2) with meaningful, thematic titles
  - Implement unique lyrical content generation for each track
  - Add narrative progression validation to ensure story arc coherence
  - _Requirements: 3.2, 3.3, 3.4_

- [x] 4. Enhance emotional and thematic analysis depth
- [x] 4.1 Improve emotional analysis in existing character analyzer
  - Replace superficial emotion detection with deeper psychological analysis
  - Add connection logic between philosophical concepts and emotional states
  - Implement complex emotional state tracking across album tracks
  - _Requirements: 4.1, 4.2, 4.3, 4.4_

- [x] 4.2 Add thematic coherence validation
  - Implement validation logic to ensure thematic consistency across album
  - Add quality checks for character voice and perspective maintenance
  - Create coherence scoring system for generated content
  - _Requirements: 4.2, 4.3, 7.1, 7.2, 7.3, 7.4_

- [x] 5. Improve middleware coordination and error handling
- [x] 5.1 Enhance MCPToolsIntegration workflow coordination
  - Improve tool sequencing and state management between character analysis and album generation
  - Add better error recovery strategies when character extraction fails
  - Implement fallback processing modes for different content types
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 9.1, 9.2, 9.3, 9.4_

- [x] 5.2 Consolidate error handling and validation logic
  - Merge redundant error handling code across multiple files
  - Enhance existing validation in mcp_data_validation.py with content type validation
  - Improve fallback strategies in mcp_error_recovery.py for conceptual processing
  - _Requirements: 6.1, 6.2, 6.3, 6.4_

- [x] 6. Add genre-specific production intelligence
- [x] 6.1 Enhance Suno command generation with accurate genre handling
  - Fix genre defaulting issues (electronic drum & bass vs alternative)
  - Add genre-specific production techniques and instrumentation suggestions
  - Implement proper tempo, rhythm, and style tag generation for requested genres
  - _Requirements: 5.1, 5.2, 5.3, 5.4_

- [x] 6.2 Align artist personas with requested musical genres
  - Ensure generated artist personas match the requested genre characteristics
  - Add genre-appropriate vocal styles, instrumental preferences, and artistic influences
  - Validate persona-genre alignment in album generation workflow
  - _Requirements: 5.2, 5.3, 5.4_

- [x] 7. Implement flexible input processing strategies
- [x] 7.1 Add input format detection and routing
  - Implement logic to detect and route different input formats appropriately
  - Add support for explicit character descriptions, concept outlines, philosophical excerpts
  - Create processing strategy selection based on input content analysis
  - _Requirements: 8.1, 8.2, 8.3, 8.4_

- [x] 7.2 Add user clarification prompts for ambiguous input
  - Implement clarification request system when input type is unclear
  - Add interactive prompts to guide users toward appropriate processing modes
  - Create fallback options when automatic content detection fails
  - _Requirements: 8.4, 6.2, 6.4_

- [x] 8. Code cleanup and consolidation
- [x] 8.1 Remove redundant and unused functions
  - Audit codebase for overlapping functionality and remove duplicates
  - Consolidate similar validation and error handling logic
  - Remove unused imports and dead code paths
  - _Requirements: 9.4_

- [x] 8.2 Improve existing test coverage for refactored functionality
  - Update existing tests to cover new content type detection logic
  - Add test cases for conceptual character creation and album generation
  - Validate that existing narrative fiction processing still works correctly
  - _Requirements: 7.1, 7.2, 7.3, 7.4_

- [x] 9. Integration testing and validation
- [x] 9.1 Test end-to-end workflow with different content types
  - Validate philosophical content processing creates meaningful characters and albums
  - Test explicit character description handling produces consistent results
  - Ensure narrative fiction processing remains functional
  - _Requirements: 1.1, 1.2, 1.3, 2.1, 2.2, 2.3_

- [x] 9.2 Validate album coherence and quality improvements
  - Test that generated albums have meaningful track progression and unique content
  - Validate character consistency across all tracks in generated albums
  - Ensure genre-specific elements are properly applied to generated content
  - _Requirements: 3.1, 3.2, 3.3, 5.1, 5.2, 7.1, 7.2, 7.3_