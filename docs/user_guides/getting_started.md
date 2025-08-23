# Getting Started with Character-Driven Music Generation

Welcome to the Character-Driven Music Generation MCP Server! This guide will help you set up and start creating music from narrative content in minutes.

## What This System Does

Transform any narrative text into complete musical compositions by:
1. **Analyzing characters** using advanced three-layer psychology methodology
2. **Creating musical personas** that authentically represent your characters
3. **Generating authentic lyrics** that reflect character voice and psychology
4. **Creating optimized Suno AI commands** with embedded lyrics for professional-quality music production

## Quick Setup

### Prerequisites
- Python 3.10 or higher
- [uv](https://docs.astral.sh/uv/) package manager (recommended)
- A text editor or IDE with MCP support (like Claude Desktop)

### Installation Steps

1. **Clone or download the project files**
   ```bash
   git clone [repository-url]
   cd character-music-mcp
   ```

2. **Make the run script executable**
   ```bash
   chmod +x run.sh
   ```

3. **Test the installation**
   ```bash
   ./run.sh
   ```
   The server will automatically install dependencies on first run.

### MCP Client Configuration

#### Claude Desktop Setup
Add to your Claude Desktop MCP configuration file:

```json
{
  "mcpServers": {
    "character-music": {
      "command": "sh",
      "args": ["/path/to/character-music-mcp/run.sh"]
    }
  }
}
```

Replace `/path/to/character-music-mcp/` with your actual project path.

## Your First Music Generation

### Step 1: Prepare Your Text
Start with any narrative content containing characters:
- Novel excerpts
- Short stories
- Character descriptions
- Screenplay scenes
- Personal narratives

**Example text:**
```
Emma stood at the crossroads, her heart heavy with the weight of her decision. 
She had always been the responsible one, the sister who held everything together 
when their parents divorced. But now, at twenty-five, she felt trapped by 
everyone's expectations. The job offer in Tokyo represented freedom, but it 
also meant leaving behind her younger brother who still needed her guidance.
```

### Step 2: Analyze Characters
Use the `analyze_character_text` tool:

```python
result = await analyze_character_text("""
Emma stood at the crossroads, her heart heavy with the weight of her decision...
""")
```

This will return detailed character profiles with psychological analysis.

### Step 3: Generate Musical Personas
Transform characters into musical artists:

```python
personas = await generate_artist_personas(result)
```

### Step 4: Generate Complete Songs with Lyrics
Create full songs with character-driven lyrics:

```python
song_result = await process_universal_content("""
Your narrative text here...
""")
```

This provides:
- Complete formatted lyrics
- Character interpretation
- Suno-ready commands with embedded lyrics

### Step 5: Use in Suno AI
Copy the generated commands (with lyrics included) into Suno AI and create your music!

## Quick Start with Complete Workflow

For rapid prototyping, use the complete workflow tool:

```python
complete_result = await complete_workflow("""
Your narrative text here...
""")
```

This executes all steps in one operation and provides:
- Character analysis
- Musical personas
- **Complete song lyrics** in character voice
- Multiple Suno command variations with embedded lyrics
- Production notes and recommendations

For even more comprehensive lyric generation, try:

```python
lyric_result = await process_universal_content("""
Your narrative text here...
""")
```

This provides detailed lyrical content with character interpretation and authentic voice.

## Understanding the Output

### Character Analysis
- **Confidence Score**: Higher scores (>0.7) indicate strong character analysis
- **Importance Score**: Ranks characters by narrative significance
- **Three-Layer Analysis**: Skin (observable), Flesh (background), Core (psychology)

### Musical Personas
- **Genre Mapping**: Psychological traits mapped to musical styles
- **Vocal Style**: Determined from character speech patterns
- **Thematic Content**: Derived from character motivations and conflicts

### Suno Commands
- **Simple Prompts**: Natural language descriptions
- **Custom Mode**: Structured parameter specifications
- **Bracket Notation**: Precise element control using Suno's syntax
- **Effectiveness Scores**: Quality ratings for each command variation

## Best Practices for Beginners

### Text Selection
- **Length**: 200-2000 words works best for initial attempts
- **Character Focus**: Ensure your text contains clear character descriptions
- **Emotional Content**: Include character emotions and internal thoughts
- **Avoid**: Pure dialogue without character context

### Interpreting Results
- Start with highest-confidence characters
- Use commands with effectiveness scores >0.8
- Try multiple command variations for creative options
- Read the rationales to understand the musical choices

### Common First-Time Issues

**"No characters detected"**
- Add more character description and internal thoughts
- Include character names and relationships
- Describe character emotions and motivations

**"Generic musical output"**
- Use more specific character psychology in your text
- Include unique character traits and conflicts
- Add character backstory and formative experiences

**"Commands don't work in Suno"**
- Try the simple prompt format first
- Remove complex meta tags if needed
- Use the troubleshooting guide for specific issues

## Next Steps

Once you're comfortable with basic generation:

1. **Read the Lyric Generation Guide** for detailed lyric creation techniques
2. **Read the Album Creation Guide** for multi-song projects
3. **Explore Prompt Engineering** for optimized results
4. **Try Creative Mode** for abstract concept music
5. **Use the Producer Tools** for advanced production guidance

## Getting Help

- **Troubleshooting Guide**: Common issues and solutions
- **Example Workflows**: Complete examples with expected outputs
- **Prompt Templates**: Reusable templates for different scenarios
- **Community Resources**: Tips and techniques from other users

## System Requirements

### Minimum
- 4GB RAM
- Python 3.10+
- Internet connection for Suno AI

### Recommended
- 8GB RAM for large text processing
- SSD storage for faster loading
- Multiple CPU cores for concurrent processing

---

**Ready to create music from your stories?** Start with a simple character description and watch your narrative come alive through sound!