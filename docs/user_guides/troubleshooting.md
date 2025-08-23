# Troubleshooting Guide

Common issues and solutions for character-driven music generation. This guide helps you diagnose problems and optimize your results.

## Character Analysis Issues

### "No characters detected" or Low Confidence Scores

**Symptoms:**
- Empty character analysis results
- Confidence scores below 0.5
- Generic or missing character traits

**Common Causes:**
1. **Insufficient character description**: Text focuses on plot events without character psychology
2. **Pure dialogue**: Conversations without character context or internal thoughts
3. **Abstract content**: Philosophical or conceptual text without human characters
4. **Too brief**: Very short text snippets (under 200 words)

**Solutions:**

#### Add Character Psychology
**Instead of:**
```
"Let's go," John said. "We're late."
Mary nodded and grabbed her coat.
```

**Try:**
```
"Let's go," John said, his voice tight with the anxiety that always surfaced 
when schedules went awry. Mary recognized the tone—the same one he'd used 
during their wedding planning when every delay felt like a personal failure. 
She nodded and grabbed her coat, knowing that rushing would calm him more 
than any reassurance.
```

#### Include Internal Monologue
Add character thoughts and feelings:
```
Sarah stared at the job offer, her mind racing. Part of her—the part that 
sounded like her mother—whispered that she wasn't qualified enough. But 
another voice, newer and stronger, reminded her of every challenge she'd 
already overcome.
```

#### Provide Character Context
Include backstory and relationships:
```
Marcus approached the podium with the same steady confidence he'd learned 
in debate class, back when his stutter made every word a battle. Public 
speaking was still terrifying, but he'd discovered that preparation could 
overcome almost any fear.
```

### Characters Seem Generic or Stereotypical

**Symptoms:**
- Character analysis lacks depth
- Musical personas feel clichéd
- Similar results across different characters

**Solutions:**

#### Add Contradictions and Complexity
```
Elena was known as the office optimist, always ready with encouragement 
and solutions. What her colleagues didn't see were the 3 AM anxiety spirals, 
the way she practiced positive responses in the mirror, or how exhausting 
it was to be everyone else's source of hope when she struggled to find 
her own.
```

#### Include Specific Details
Replace general traits with specific behaviors:
```
Instead of: "He was organized."
Use: "David labeled everything—not just files and folders, but his emotions 
too. 'Productive anxiety,' he'd call the feeling before big presentations. 
'Nostalgic melancholy' for Sunday evenings. Naming things made them manageable."
```

#### Show Character Growth
Include how characters change or evolve:
```
The woman who now ran board meetings with quiet authority was the same person 
who used to hide in bathroom stalls during high school lunch periods. The 
transformation hadn't been sudden—it was built from a thousand small moments 
of choosing courage over comfort.
```

## Musical Generation Issues

### Suno Commands Don't Work or Produce Poor Results

**Symptoms:**
- Suno AI rejects commands
- Generated music doesn't match character
- Low effectiveness scores on commands

**Common Causes:**
1. **Overly complex commands**: Too many conflicting instructions
2. **Invalid Suno syntax**: Incorrect bracket notation or meta tags
3. **Genre mismatches**: Character psychology doesn't support chosen genre
4. **Unclear prompts**: Vague or contradictory musical directions

**Solutions:**

#### Start with Simple Commands
Use the highest-rated simple prompts first:
```
# Instead of complex custom commands, try:
"A melancholic indie folk song about finding strength in solitude, 
with gentle acoustic guitar and vulnerable female vocals"
```

#### Check Suno Syntax
Ensure bracket notation is correct:
```
# Correct format:
[Verse 1]
[Chorus]
[Bridge]
[Outro]

# Avoid:
(Verse 1) - incorrect parentheses
[Verse One] - spell out numbers
[Pre-Chorus] - use [Bridge] instead
```

#### Simplify Meta Tags
Remove conflicting or excessive tags:
```
# Too complex:
"indie folk rock electronic ambient experimental jazz fusion"

# Better:
"indie folk with subtle electronic elements"
```

#### Match Genre to Character Psychology
Ensure musical choices align with character analysis:
```
# If character analysis shows:
- Introspective, melancholic → indie folk, alternative
- Rebellious, intense → rock, punk
- Complex, layered thinking → electronic, experimental
- Traditional, storytelling → folk, country
```

### Generated Music Doesn't Match Character

**Symptoms:**
- Music feels disconnected from character
- Genre choices seem random
- Lyrics don't reflect character psychology
- Character voice doesn't come through in lyrical content

**Solutions:**

#### Review Character Analysis Quality
Ensure your input text provides clear psychological insights:
- Check confidence scores (aim for >0.7)
- Verify character traits are specific, not generic
- Confirm emotional depth is captured

#### Use Character-Informed Prompts
Incorporate specific character elements:
```
# Generic:
"A sad song about loss"

# Character-informed:
"A song capturing the quiet grief of someone who lost their father young, 
with the kind of restrained emotion that comes from being strong for others"
```

#### Try Multiple Command Variations
Use different command types for the same character:
- Simple prompts for accessibility
- Custom mode for specific control
- Bracket notation for structure

## Lyric Generation Issues

### Lyrics Feel Generic or Inauthentic

**Symptoms:**
- Generated lyrics could apply to anyone
- Character's unique voice doesn't come through
- Lyrics feel like templates rather than personal expression
- No connection between character psychology and lyrical content

**Solutions:**

#### Enhance Character Voice Details
Include specific speech patterns and expression styles:
```
Instead of: "John was quiet and thoughtful."
Use: "John spoke in careful, measured sentences, always pausing to consider 
his words. He had a habit of starting difficult conversations with 'I've 
been thinking about something...' and ending them with 'Does that make sense?'"
```

#### Add Character-Specific Imagery
Include unique metaphors and references from character's world:
```
For a mechanic character: "Life's like an engine - sometimes you need to 
take it apart to understand what's broken."

For a teacher character: "Every student is a story waiting to be written, 
and I'm just here to help them find their voice."
```

#### Include Internal Monologue Examples
Show how the character thinks and processes emotions:
```
"Sarah stared at the job offer, her mind racing between excitement and terror. 
'This is what you wanted,' she told herself, but her father's voice whispered 
back, 'People like us don't get opportunities like this.'"
```

### Lyrics Don't Match Musical Genre

**Symptoms:**
- Folk music with aggressive, confrontational lyrics
- Hip-hop with overly poetic, abstract language
- Rock music with gentle, contemplative themes that don't build energy

**Solutions:**

#### Align Character Traits with Genre Expectations
Ensure character psychology supports the musical style:
```
For Folk: Include storytelling nature, cultural connections, simple wisdom
For Rock: Include intensity, rebellion, emotional expression needs
For Hip-Hop: Include strong voice, social awareness, rhythmic speech patterns
```

#### Review Genre-Character Mapping
Use the genre-specific templates to ensure authentic alignment:
- Check if character naturally fits the suggested genre
- Consider if character has multiple facets that suggest genre blending
- Verify that character's emotional expression style matches genre conventions

### Lyrics Lack Emotional Depth

**Symptoms:**
- Surface-level emotional expression
- No progression or development within the song
- Missing the character's core psychological conflicts

**Solutions:**

#### Include Character's Internal Conflicts
Show competing desires and values:
```
"Part of me wants to run away and start over somewhere new, but another 
part knows that running never solved anything. I'm torn between the person 
I was raised to be and the person I'm becoming."
```

#### Add Specific Emotional Triggers
Include concrete experiences that create emotional responses:
```
"Every time I smell coffee brewing, I'm back in Mom's kitchen, listening 
to her hum while she made breakfast. Now the house is silent, and I don't 
know how to fill that space."
```

## Album Creation Issues

### Songs Don't Feel Connected

**Symptoms:**
- Album lacks cohesion
- Songs feel like random collection
- No clear narrative or thematic arc

**Solutions:**

#### Establish Musical Consistency
Use recurring elements across tracks:
```
# Consistent elements to maintain:
- Key relationships (related keys)
- Instrumentation palette
- Production style
- Vocal approach
- Tempo relationships
```

#### Create Character Continuity
Ensure each song explores different aspects of the same character:
```
Track 1: Character's public persona
Track 2: Private struggles
Track 3: Relationships and connections
Track 4: Past experiences that shaped them
Track 5: Growth and resolution
```

#### Plan Emotional Arc
Map the album's emotional journey:
```
Opening: Introduction and setup
Early tracks: Establish character and conflict
Middle tracks: Explore complexity and development
Later tracks: Climax and transformation
Closing: Resolution and new understanding
```

### Multi-Character Albums Feel Chaotic

**Symptoms:**
- Characters compete rather than complement
- No clear album structure
- Inconsistent musical styles

**Solutions:**

#### Choose a Unifying Approach
Select one structural method:

**Option 1: Character Per Track**
- Each song focuses on one character
- Maintain musical consistency across tracks
- Order songs to create narrative flow

**Option 2: Thematic Unity**
- All characters explore the same theme
- Show different perspectives on shared experience
- Use musical variations to distinguish characters

**Option 3: Relationship Focus**
- Songs explore character interactions
- Use musical dialogue and contrast
- Build toward resolution or understanding

#### Create Character Hierarchy
Establish primary and secondary characters:
```
Primary character: 3-4 songs exploring deep psychology
Secondary characters: 1-2 songs each, supporting main narrative
Ensemble pieces: 1-2 songs bringing characters together
```

## Technical Issues

### Server Connection Problems

**Symptoms:**
- MCP server won't start
- Connection timeouts
- Tool calls fail

**Solutions:**

#### Check Installation
Verify all dependencies are installed:
```bash
# Test server startup
./run.sh

# Check Python version
python --version  # Should be 3.10+

# Verify uv installation
uv --version
```

#### Review MCP Configuration
Check your MCP client configuration:
```json
{
  "mcpServers": {
    "character-music": {
      "command": "sh",
      "args": ["/full/path/to/character-music-mcp/run.sh"]
    }
  }
}
```

#### Check File Permissions
Ensure run script is executable:
```bash
chmod +x run.sh
```

### Performance Issues

**Symptoms:**
- Slow processing times
- Memory usage warnings
- Timeouts on large inputs

**Solutions:**

#### Optimize Input Size
For large texts, break into smaller sections:
```python
# Instead of processing 10,000+ word documents at once
# Break into character-focused sections of 1,000-2,000 words each
```

#### Use Incremental Processing
Process complex albums in stages:
```python
# Step 1: Analyze characters
characters = await analyze_character_text(narrative)

# Step 2: Generate personas for main characters only
main_personas = await generate_artist_personas(main_characters)

# Step 3: Create commands for priority tracks
priority_commands = await create_suno_commands(main_personas, characters)
```

#### Monitor Resource Usage
Check system resources during processing:
- RAM usage should stay under 4GB for typical workflows
- Processing time should be under 30 seconds for standard inputs
- Consider upgrading hardware for large-scale album projects

## Quality Optimization

### Improving Character Analysis Quality

#### Input Text Optimization
- **Length**: 500-2000 words optimal for single characters
- **Depth**: Include psychology, not just actions
- **Specificity**: Unique details rather than generic traits
- **Emotion**: Internal thoughts and feelings
- **Context**: Relationships and backstory

#### Iterative Refinement
1. Start with basic character description
2. Analyze results and identify gaps
3. Add specific details for missing elements
4. Re-analyze and compare improvements
5. Repeat until confidence scores >0.7

### Enhancing Musical Results

#### Command Selection Strategy
1. **Start simple**: Use highest-rated simple prompts
2. **Test variations**: Try different command types
3. **Refine based on results**: Adjust based on Suno output
4. **Maintain consistency**: Use similar approaches for album tracks

#### Genre Matching
Ensure musical choices align with character psychology:
- **Introspective characters** → indie, folk, alternative
- **Intense characters** → rock, electronic, experimental
- **Traditional characters** → country, folk, classical influences
- **Complex characters** → genre-blending approaches

## Getting Additional Help

### Diagnostic Information to Collect

When seeking help, provide:
1. **Input text sample** (anonymized if needed)
2. **Character analysis results** (confidence scores, traits detected)
3. **Generated commands** and their effectiveness scores
4. **Suno results** or error messages
5. **System information** (OS, Python version, available RAM)

### Community Resources

- **Example Workflows**: Study successful examples for patterns
- **Prompt Templates**: Use proven templates as starting points
- **User Forums**: Share experiences and solutions with other users
- **Documentation Updates**: Check for new features and improvements

### Advanced Troubleshooting

For complex issues:
1. **Isolate the problem**: Test with minimal examples
2. **Compare with working examples**: Use known-good inputs
3. **Check system logs**: Look for error messages or warnings
4. **Test incrementally**: Add complexity gradually
5. **Document solutions**: Keep notes on what works for future reference

---

**Still having issues?** The key to successful troubleshooting is systematic testing and incremental improvement. Start with simple, working examples and gradually add complexity until you identify the source of problems.