# User Onboarding Guide - Character-Driven Music Generation

## Welcome! 🎵

This guide will help you get started with the Character-Driven Music Generation system, which transforms narrative text into musical artist personas and Suno AI commands.

## Quick Start (5 minutes)

### 1. Basic Setup
```bash
# Ensure you have Python 3.8+ installed
python --version

# Navigate to the project directory
cd character-music-mcp

# Install dependencies (if not already done)
pip install -r requirements.txt
```

### 2. Your First Music Generation
Try this simple example:

```python
# Example narrative text
narrative = """
Sarah Chen stood at the edge of the rooftop, tears streaming down her face. 
At twenty-seven, she had spent her entire life meeting everyone else's expectations. 
The perfect daughter, the perfect student, the perfect employee. But tonight, 
after losing the job she never wanted, she finally felt free to be herself.
"""

# Run the complete workflow
python -c "
import asyncio
from server import complete_workflow
from tests.fixtures.mock_contexts import create_mock_context

async def test():
    ctx = create_mock_context('basic')
    result = await complete_workflow.__wrapped__('''$narrative''', ctx)
    print(result)

asyncio.run(test())
"
```

### 3. Understanding the Output
The system will generate:
- **Character Analysis**: Detailed character profiles with motivations, fears, and traits
- **Artist Personas**: Musical identities with genres, vocal styles, and themes
- **Suno Commands**: Ready-to-use commands for Suno AI music generation

## Core Concepts

### Character Analysis (3-Layer Methodology)
1. **Skin Layer**: Observable characteristics (appearance, mannerisms, speech)
2. **Flesh Layer**: Background and relationships (backstory, connections, experiences)
3. **Bone Layer**: Core psychology (motivations, fears, desires, conflicts)

### Artist Persona Generation
- Maps character psychology to musical expression
- Determines genres, vocal styles, and instrumental preferences
- Creates thematic content and emotional palettes

### Suno Command Optimization
- Generates multiple command variations
- Includes effectiveness scoring
- Provides meta tags and style guidance

## Common Use Cases

### 1. Single Character Album
**Input**: Detailed character narrative (500-2000 words)
**Output**: Complete album concept with 5-8 tracks
**Best For**: Character-driven storytelling, biographical albums

### 2. Concept Album Creation
**Input**: Abstract themes or philosophical concepts
**Output**: Thematic album with conceptual coherence
**Best For**: Progressive rock, ambient, experimental music

### 3. Genre-Specific Generation
**Input**: Character + genre preferences
**Output**: Genre-appropriate musical interpretation
**Best For**: Folk, electronic, indie, classical adaptations

## Step-by-Step Workflows

### Workflow 1: Complete Character-to-Music Pipeline
1. **Prepare Your Narrative** (10-15 minutes)
   - Write 500-2000 words about your character
   - Include background, personality, conflicts, and motivations
   - Add specific details about age, setting, and relationships

2. **Run Character Analysis** (2-3 minutes)
   ```bash
   python -m tests.integration.test_legacy_workflows
   ```

3. **Review Generated Personas** (5 minutes)
   - Check if genres match your vision
   - Verify vocal styles align with character
   - Adjust themes if needed

4. **Generate Suno Commands** (1-2 minutes)
   - Get multiple command variations
   - Choose highest effectiveness scores
   - Use provided meta tags

### Workflow 2: Album Creation Process
1. **Define Album Concept** (15-20 minutes)
   - Central theme or character arc
   - Target track count (5-12 songs)
   - Overall emotional journey

2. **Create Track Concepts** (10 minutes per track)
   - Individual song themes
   - Character development moments
   - Musical progression

3. **Generate Commands** (5 minutes total)
   - Run complete workflow for each track concept
   - Ensure thematic consistency
   - Optimize for album flow

## Testing Your Setup

### Run the Test Suite
```bash
# Run all tests to verify system functionality
python tests/test_runner.py

# Expected output: 88.9% success rate (16/18 tests passing)
```

### Validate Performance
```bash
# Run performance benchmarks
python scripts/run_benchmarks.py

# Expected: All benchmarks under threshold limits
```

### Check Documentation Examples
```bash
# Validate documentation examples
python scripts/validate_all.py

# Note: Some validation scripts may need refinement
```

## Troubleshooting

### Common Issues

#### 1. "No characters detected"
**Problem**: Input text too short or lacks character details
**Solution**: 
- Ensure narrative is at least 200 words
- Include character names, ages, and personality details
- Add emotional context and motivations

#### 2. "Generic musical output"
**Problem**: Character analysis too shallow
**Solution**:
- Add more specific character traits
- Include backstory and formative experiences
- Describe character's relationship to music/art

#### 3. "Low effectiveness scores"
**Problem**: Suno commands not optimized
**Solution**:
- Use more specific genre tags
- Include emotional descriptors
- Add production style preferences

### Getting Help

1. **Check the Documentation**:
   - `docs/user_guides/` - Comprehensive guides
   - `examples/` - Working examples
   - `docs/user_guides/troubleshooting.md` - Common issues

2. **Review Test Examples**:
   - `tests/fixtures/test_data.py` - Sample scenarios
   - `tests/integration/test_legacy_workflows.py` - Working code

3. **Performance Issues**:
   - Check `scripts/monitor_performance.py`
   - Review benchmark results
   - Optimize input text length

## Advanced Features

### Custom Persona Generation
```python
# Override default genre mapping
from server import MusicPersonaGenerator

generator = MusicPersonaGenerator()
# Customize generation parameters
```

### Batch Processing
```python
# Process multiple characters
from tests.fixtures.mock_contexts import MockBatchContext

ctx = MockBatchContext(batch_size=5)
# Process character batch
```

### Performance Monitoring
```python
# Track processing metrics
from tests.fixtures.mock_contexts import MockPerformanceContext

ctx = MockPerformanceContext()
# Monitor performance during generation
```

## Best Practices

### Input Optimization
- **Character Depth**: Include psychological complexity
- **Narrative Length**: 500-2000 words optimal
- **Specific Details**: Ages, locations, relationships
- **Emotional Context**: Conflicts, fears, desires

### Output Utilization
- **Review All Variations**: Don't just use the first command
- **Check Effectiveness Scores**: Higher scores = better results
- **Combine Elements**: Mix and match from different variations
- **Iterate**: Refine input based on output quality

### Workflow Efficiency
- **Start Simple**: Begin with single character scenarios
- **Build Complexity**: Gradually add multi-character narratives
- **Test Frequently**: Validate each step before proceeding
- **Document Results**: Keep track of successful patterns

## Example Templates

### Character Description Template
```
[Character Name] is a [age]-year-old [profession/role] who [current situation].

Background:
- [Key formative experience]
- [Important relationship]
- [Major life challenge]

Personality:
- [Core trait 1]: [specific example]
- [Core trait 2]: [specific example]
- [Core fear]: [how it manifests]
- [Primary motivation]: [what drives them]

Current Conflict:
[Describe the central tension or challenge they face]

Musical Connection:
[How they relate to music, art, or creative expression]
```

### Album Concept Template
```
Album Title: [Title]
Central Theme: [Main concept or character arc]
Target Genre: [Primary musical style]
Track Count: [5-12 songs]

Track Concepts:
1. [Opening theme/introduction]
2. [Character background/setup]
3. [Rising conflict/tension]
4. [Emotional climax]
5. [Resolution/transformation]
[Additional tracks as needed]

Overall Arc: [How the album tells a complete story]
```

## Success Metrics

### Quality Indicators
- **Character Analysis**: 3+ distinct personality traits identified
- **Genre Mapping**: Appropriate musical style selection
- **Command Effectiveness**: Scores above 7.0/10
- **Thematic Consistency**: Coherent album narrative

### Performance Targets
- **Processing Time**: Under 10 seconds for complete workflow
- **Memory Usage**: Under 500MB during generation
- **Success Rate**: 90%+ successful generations
- **User Satisfaction**: Clear, actionable Suno commands

## Next Steps

1. **Try the Examples**: Start with provided character scenarios
2. **Create Your Own**: Develop original character narratives
3. **Experiment with Genres**: Test different musical styles
4. **Build Albums**: Create complete musical projects
5. **Share Results**: Document successful workflows

## Support Resources

- **Documentation**: `docs/user_guides/`
- **Examples**: `examples/` directory
- **Test Cases**: `tests/fixtures/test_data.py`
- **Performance Tools**: `scripts/` directory

Welcome to character-driven music generation! 🎵✨

---

*This guide covers the essential onboarding process. For advanced features and detailed API documentation, see the complete documentation in the `docs/` directory.*