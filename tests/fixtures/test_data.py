#!/usr/bin/env python3
"""
Test Data Manager for Character-Driven Music Generation

Provides centralized management of test data and fixtures for all test suites.
"""

import pytest
import json
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any, Union
from pathlib import Path

# Import data models from the main server
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from server import CharacterProfile, ArtistPersona, SunoCommand


@dataclass
class ScenarioData:
    """Test scenario with expected inputs and outputs"""
    name: str
    description: str
    narrative_text: str
    expected_character_count: int
    expected_primary_character: str
    expected_genres: List[str]
    complexity_level: str  # "simple", "medium", "complex"


class TestDataManager:
    """Centralized management of test data and fixtures"""
    
    def __init__(self):
        self.scenarios = self._initialize_scenarios()
        self.expected_characters = self._initialize_expected_characters()
        self.expected_personas = self._initialize_expected_personas()
        self.expected_commands = self._initialize_expected_commands()
    
    # Prevent pytest from treating this as a test class
    __test__ = False
    
    def _initialize_scenarios(self) -> Dict[str, ScenarioData]:
        """Initialize test scenarios with different complexity levels"""
        return {
            "single_character_simple": ScenarioData(
                name="single_character_simple",
                description="Simple narrative with one clear character",
                narrative_text="""
                Sarah Chen stood at the edge of the rooftop, tears streaming down her face. 
                At twenty-seven, she had spent her entire life meeting everyone else's expectations. 
                The perfect daughter, the perfect student, the perfect employee. But tonight, 
                after losing the job she never wanted, she finally felt free to be herself.
                """,
                expected_character_count=1,
                expected_primary_character="Sarah Chen",
                expected_genres=["indie", "alternative"],
                complexity_level="simple"
            ),
            
            "multi_character_medium": ScenarioData(
                name="multi_character_medium",
                description="Medium complexity with multiple characters and relationships",
                narrative_text="""
                Elena Rodriguez stood in her cramped studio apartment, paintbrush trembling 
                in her hand as she stared at the blank canvas. At twenty-eight, she had already 
                given up three different career paths, each time running when success seemed within reach.
                
                The phone rang, startling her from her thoughts. It was David, her best friend 
                since art school and the only person who truly understood her creative struggles. 
                "Still avoiding the gallery opening?" he asked, his voice gentle but knowing.
                
                Elena sighed, setting down her brush. David had always been the confident one, 
                the artist who embraced fame while she shrank from it. His paintings hung in 
                galleries across the city while hers gathered dust in storage.
                """,
                expected_character_count=2,
                expected_primary_character="Elena Rodriguez",
                expected_genres=["indie", "folk", "alternative"],
                complexity_level="medium"
            ),
            
            "concept_album_complex": ScenarioData(
                name="concept_album_complex",
                description="Complex philosophical narrative for concept album",
                narrative_text="""
                The Philosopher sat in his study, surrounded by the weight of centuries of human thought. 
                Nietzsche's words echoed in his mind: "God is dead, and we have killed him." But what 
                comes after the death of absolute meaning? What fills the void left by collapsed certainties?
                
                He had spent decades wrestling with existential questions, moving through phases of 
                nihilistic despair, absurdist acceptance, and finally arriving at something resembling 
                hope. Not the naive hope of youth, but the hard-won hope of someone who has stared 
                into the abyss and chosen to create meaning anyway.
                
                The manuscript before him represented his life's work: a treatise on finding purpose 
                in a purposeless universe. Each chapter was a movement in a symphony of human struggle, 
                from the initial shock of meaninglessness to the gradual construction of personal values.
                """,
                expected_character_count=1,
                expected_primary_character="The Philosopher",
                expected_genres=["progressive rock", "ambient", "post-rock"],
                complexity_level="complex"
            ),
            
            "minimal_character_edge": ScenarioData(
                name="minimal_character_edge",
                description="Edge case with minimal character information",
                narrative_text="""
                Someone walked through the rain. They thought about things. It was difficult.
                """,
                expected_character_count=1,
                expected_primary_character="Someone",
                expected_genres=["ambient", "experimental"],
                complexity_level="simple"
            ),
            
            "emotional_intensity_high": ScenarioData(
                name="emotional_intensity_high",
                description="High emotional intensity for testing emotional framework",
                narrative_text="""
                Marcus collapsed to his knees in the hospital corridor, the doctor's words 
                still echoing in his mind. "I'm sorry, we did everything we could." His wife 
                of thirty years, his anchor, his reason for breathing, was gone.
                
                The rage came first, hot and consuming. How dare the universe take her now, 
                just as they were planning their retirement, their golden years together? 
                Then came the bargaining, the desperate prayers to a God he'd never believed in. 
                Finally, the crushing weight of absolute emptiness settled over him like a shroud.
                
                But in that darkness, something unexpected stirred. A memory of her laugh, 
                the way she hummed while cooking, her fierce love for their children. 
                She wouldn't want him to disappear into grief. She would want him to live, 
                to carry their love forward into whatever time he had left.
                """,
                expected_character_count=1,
                expected_primary_character="Marcus",
                expected_genres=["blues", "soul", "gospel"],
                complexity_level="complex"
            ),
            
            "sci_fi_adventure": ScenarioData(
                name="sci_fi_adventure",
                description="Science fiction narrative with adventure elements",
                narrative_text="""
                Captain Zara Okafor floated in the observation deck of the starship Meridian, 
                watching the swirling nebula that had trapped them for three weeks. Her crew 
                looked to her for answers she didn't have, for hope she struggled to maintain.
                
                At thirty-five, she had commanded vessels across seven star systems, but nothing 
                had prepared her for this. The nebula's electromagnetic storms had disabled their 
                jump drive, and their supplies were running dangerously low. Worse, the strange 
                energy readings suggested they weren't alone in this cosmic maze.
                
                "Captain," came the voice of her first officer, Lieutenant Chen. "We're detecting 
                movement in sector seven. It's... it's not natural." Zara straightened, her hand 
                instinctively moving to her sidearm. Whatever was out there, she would face it 
                head-on. Her crew depended on her courage, even when she felt none herself.
                """,
                expected_character_count=2,
                expected_primary_character="Captain Zara Okafor",
                expected_genres=["electronic", "synthwave", "ambient"],
                complexity_level="medium"
            ),
            
            "romance_contemporary": ScenarioData(
                name="romance_contemporary",
                description="Contemporary romance with emotional depth",
                narrative_text="""
                Maya Patel closed her laptop with a sigh, another day of remote work blending 
                into the endless stream of video calls and deadlines. At twenty-nine, she had 
                built a successful career in digital marketing, but the pandemic had left her 
                feeling more isolated than ever.
                
                The coffee shop across from her apartment had become her lifeline to the outside 
                world. Every morning at 8:15, she would see him - the man with kind eyes who 
                always ordered a simple black coffee and sat by the window with a worn paperback.
                
                Today, their eyes met through the glass. He smiled, raising his coffee cup in 
                a small salute. Maya felt her heart skip, a warmth spreading through her chest 
                that had nothing to do with her morning latte. Maybe it was time to be brave, 
                to step outside her carefully constructed comfort zone and take a chance on connection.
                """,
                expected_character_count=2,
                expected_primary_character="Maya Patel",
                expected_genres=["indie pop", "folk", "singer-songwriter"],
                complexity_level="simple"
            ),
            
            "historical_drama": ScenarioData(
                name="historical_drama",
                description="Historical narrative with period-specific challenges",
                narrative_text="""
                Amelia Hartwell adjusted her corset with practiced efficiency, preparing for 
                another day of pretending to be the perfect Victorian lady. But beneath the 
                layers of silk and propriety, her mind raced with equations and theories that 
                would scandalize London society.
                
                At twenty-four, she had already made groundbreaking discoveries in mathematics, 
                publishing her work under her brother's name to avoid the scandal of a woman 
                in academia. The Royal Society would never accept her contributions directly, 
                but she refused to let societal constraints silence her brilliant mind.
                
                Tonight, she would attend another tedious social gathering, smiling demurely 
                while men half her intellectual equal discussed politics and science. But in 
                her private study, surrounded by forbidden books and hidden calculations, 
                she was building a legacy that would outlast all their narrow prejudices.
                """,
                expected_character_count=1,
                expected_primary_character="Amelia Hartwell",
                expected_genres=["classical", "orchestral", "chamber music"],
                complexity_level="medium"
            ),
            
            "urban_fantasy": ScenarioData(
                name="urban_fantasy",
                description="Urban fantasy with supernatural elements",
                narrative_text="""
                Detective Riley Santos had seen enough crime scenes to last three lifetimes, 
                but nothing had prepared her for this. The victim lay in the alley, completely 
                drained of blood, with strange symbols carved into the brick wall above.
                
                What the other cops didn't know - what she could never tell them - was that 
                Riley could see the lingering traces of magic around the body. Wisps of dark 
                energy that spoke of ancient powers and modern malevolence.
                
                Her grandmother's warnings echoed in her mind: "Mija, the old ways never truly 
                died. They just learned to hide in the shadows of the city." Riley had spent 
                years suppressing her inherited sight, trying to live a normal life. But now, 
                with bodies piling up and the supernatural bleeding into her mundane world, 
                she would have to embrace the very gifts she had tried so hard to deny.
                """,
                expected_character_count=1,
                expected_primary_character="Detective Riley Santos",
                expected_genres=["dark electronic", "industrial", "gothic"],
                complexity_level="complex"
            ),
            
            "coming_of_age": ScenarioData(
                name="coming_of_age",
                description="Coming-of-age story with universal themes",
                narrative_text="""
                Sixteen-year-old Alex Kim stared at the acceptance letter from the prestigious 
                music conservatory, the paper trembling in their hands. This was everything 
                they had worked for, dreamed of, sacrificed for. So why did it feel like a 
                prison sentence?
                
                Their parents had immigrated from Seoul with nothing but hope and determination, 
                building a successful restaurant business through decades of eighteen-hour days. 
                They saw Alex's musical talent as validation of their sacrifices, proof that 
                the American dream was real.
                
                But Alex's heart pulled in a different direction. The underground music scene 
                downtown, where kids like them created raw, honest sounds that spoke to their 
                generation's struggles. Classical training felt like wearing someone else's 
                clothes - technically perfect but emotionally hollow. The choice ahead would 
                define not just their career, but their very identity.
                """,
                expected_character_count=1,
                expected_primary_character="Alex Kim",
                expected_genres=["indie rock", "alternative", "lo-fi"],
                complexity_level="medium"
            ),
            
            "psychological_thriller": ScenarioData(
                name="psychological_thriller",
                description="Psychological thriller with unreliable narrator",
                narrative_text="""
                Dr. Catherine Wells reviewed her patient notes for the third time, but the 
                words kept shifting on the page. Or maybe that was just the medication. She 
                couldn't be sure anymore what was real and what was a symptom of her own 
                unraveling mind.
                
                The irony wasn't lost on her - a psychiatrist losing her grip on reality. 
                For fifteen years, she had helped others navigate their darkest thoughts, 
                but now she was drowning in her own psychological maze. The line between 
                doctor and patient had blurred beyond recognition.
                
                Her reflection in the office window looked wrong somehow, the features 
                subtly distorted. Was someone watching her, or was paranoia finally claiming 
                the last vestiges of her sanity? The truth felt like quicksand - the harder 
                she grasped for it, the deeper she sank into uncertainty.
                """,
                expected_character_count=1,
                expected_primary_character="Dr. Catherine Wells",
                expected_genres=["dark ambient", "experimental", "minimalist"],
                complexity_level="complex"
            ),
            
            "family_saga": ScenarioData(
                name="family_saga",
                description="Multi-generational family story",
                narrative_text="""
                Rosa Delgado stood in the kitchen where four generations of women had kneaded 
                bread and shared secrets. At sixty-eight, she was the keeper of family stories, 
                the bridge between her grandmother's Mexico and her granddaughter's America.
                
                Her granddaughter Sofia, twenty-two and fresh from college, sat at the worn 
                wooden table, laptop open, trying to document the family recipes before they 
                were lost forever. But Rosa knew that recipes were just the beginning - each 
                dish carried the weight of history, love, and survival.
                
                "Mija," Rosa said, her weathered hands shaping masa with practiced ease, "the 
                secret ingredient isn't in any cookbook. It's the stories we tell while we cook, 
                the love we knead into every tortilla, the prayers we whisper over every pot." 
                Sofia looked up from her screen, finally understanding that she was documenting 
                more than food - she was preserving the soul of her family.
                """,
                expected_character_count=2,
                expected_primary_character="Rosa Delgado",
                expected_genres=["folk", "world music", "acoustic"],
                complexity_level="medium"
            )
        }
    
    def _initialize_expected_characters(self) -> Dict[str, CharacterProfile]:
        """Initialize expected character profiles for validation"""
        return {
            "Sarah Chen": CharacterProfile(
                name="Sarah Chen",
                aliases=["Sarah"],
                physical_description="27-year-old woman standing on rooftop",
                mannerisms=["tears streaming", "standing at edge"],
                speech_patterns=["internal monologue", "self-reflection"],
                behavioral_traits=["perfectionist", "people-pleaser", "breaking free"],
                backstory="Lifetime of meeting others' expectations, perfect daughter role",
                relationships=["family expectations", "societal pressures"],
                formative_experiences=["constant pressure for perfection", "job loss"],
                social_connections=["family", "work environment"],
                motivations=["authenticity", "self-discovery", "freedom"],
                fears=["disappointing others", "being judged", "vulnerability"],
                desires=["to be herself", "authentic expression", "emotional freedom"],
                conflicts=["perfection vs authenticity", "others' expectations vs own needs"],
                personality_drivers=["need for authenticity", "desire for freedom"],
                confidence_score=0.85,
                text_references=["Sarah Chen stood at the edge"],
                first_appearance="Sarah Chen stood at the edge of the rooftop",
                importance_score=1.0
            ),
            
            "Elena Rodriguez": CharacterProfile(
                name="Elena Rodriguez",
                aliases=["Elena", "El"],
                physical_description="28-year-old artist with trembling hands",
                mannerisms=["trembling hands", "nervous gestures", "sighing"],
                speech_patterns=["hesitant admissions", "self-doubt"],
                behavioral_traits=["fearful", "creative", "self-sabotaging"],
                backstory="Given up three career paths, struggling artist",
                relationships=["David - supportive best friend"],
                formative_experiences=["art school", "career failures", "creative struggles"],
                social_connections=["David - best friend since art school"],
                motivations=["create meaningful art", "overcome fear", "artistic recognition"],
                fears=["success", "failure", "judgment", "vulnerability"],
                desires=["artistic fulfillment", "self-acceptance", "creative courage"],
                conflicts=["fear vs ambition", "self-sabotage vs success"],
                personality_drivers=["creative drive", "fear of exposure"],
                confidence_score=0.75,
                text_references=["Elena Rodriguez stood in her cramped studio"],
                first_appearance="Elena Rodriguez stood in her cramped studio apartment",
                importance_score=1.0
            ),
            
            "The Philosopher": CharacterProfile(
                name="The Philosopher",
                aliases=["Philosopher"],
                physical_description="Contemplative figure surrounded by books and manuscripts",
                mannerisms=["deep contemplation", "manuscript reviewing", "philosophical reflection"],
                speech_patterns=["philosophical discourse", "existential questioning"],
                behavioral_traits=["intellectual", "introspective", "meaning-seeking"],
                backstory="Decades wrestling with existential questions, phases of despair to hope",
                relationships=["centuries of human thought", "philosophical tradition"],
                formative_experiences=["nihilistic despair", "absurdist acceptance", "meaning creation"],
                social_connections=["philosophical community", "academic world"],
                motivations=["find purpose", "create meaning", "help others navigate meaninglessness"],
                fears=["absolute meaninglessness", "nihilistic void", "intellectual isolation"],
                desires=["construct personal values", "share wisdom", "transcend despair"],
                conflicts=["meaninglessness vs purpose", "despair vs hope", "isolation vs connection"],
                personality_drivers=["quest for meaning", "intellectual courage"],
                confidence_score=0.9,
                text_references=["The Philosopher sat in his study"],
                first_appearance="The Philosopher sat in his study, surrounded by the weight of centuries",
                importance_score=1.0
            ),
            
            "Marcus": CharacterProfile(
                name="Marcus",
                aliases=["Marcus"],
                physical_description="Man collapsed in hospital corridor, overwhelmed by grief",
                mannerisms=["collapsing to knees", "desperate prayers", "memory recall"],
                speech_patterns=["internal anguish", "bargaining with universe"],
                behavioral_traits=["grieving", "loving", "resilient"],
                backstory="Thirty years of marriage, planning retirement with beloved wife",
                relationships=["deceased wife - anchor and love", "children - shared love"],
                formative_experiences=["wife's death", "thirty years of marriage", "raising children"],
                social_connections=["family", "medical staff", "community of grief"],
                motivations=["honor wife's memory", "continue living", "carry love forward"],
                fears=["disappearing into grief", "forgetting her", "meaningless existence"],
                desires=["preserve their love", "find reason to live", "honor her wishes"],
                conflicts=["grief vs living", "despair vs hope", "past vs future"],
                personality_drivers=["love transcending death", "commitment to life"],
                confidence_score=0.8,
                text_references=["Marcus collapsed to his knees"],
                first_appearance="Marcus collapsed to his knees in the hospital corridor",
                importance_score=1.0
            ),
            
            "Captain Zara Okafor": CharacterProfile(
                name="Captain Zara Okafor",
                aliases=["Captain Okafor", "Zara", "Captain"],
                physical_description="35-year-old starship captain floating in observation deck",
                mannerisms=["hand to sidearm", "straightening posture", "observing nebula"],
                speech_patterns=["command authority", "measured responses", "tactical thinking"],
                behavioral_traits=["courageous", "responsible", "strategic"],
                backstory="Commanded vessels across seven star systems, experienced space captain",
                relationships=["crew dependency", "Lieutenant Chen - first officer"],
                formative_experiences=["commanding multiple vessels", "space exploration", "current crisis"],
                social_connections=["starship crew", "space command", "interstellar community"],
                motivations=["protect crew", "find escape route", "maintain hope"],
                fears=["crew death", "mission failure", "unknown threats"],
                desires=["safe passage home", "crew survival", "successful command"],
                conflicts=["confidence vs uncertainty", "leadership vs fear", "known vs unknown"],
                personality_drivers=["duty to crew", "courage under pressure"],
                confidence_score=0.85,
                text_references=["Captain Zara Okafor floated in the observation deck"],
                first_appearance="Captain Zara Okafor floated in the observation deck of the starship Meridian",
                importance_score=1.0
            ),
            
            "Maya Patel": CharacterProfile(
                name="Maya Patel",
                aliases=["Maya"],
                physical_description="29-year-old remote worker, isolated but hopeful",
                mannerisms=["laptop closing", "sighing", "heart skipping", "window gazing"],
                speech_patterns=["internal monologue", "romantic hope", "self-encouragement"],
                behavioral_traits=["isolated", "career-focused", "romantically hopeful"],
                backstory="Successful digital marketing career, pandemic isolation",
                relationships=["mysterious coffee shop man", "work colleagues (remote)"],
                formative_experiences=["pandemic isolation", "career building", "daily coffee shop routine"],
                social_connections=["coffee shop community", "work network", "potential romance"],
                motivations=["human connection", "break isolation", "find love"],
                fears=["continued isolation", "rejection", "vulnerability"],
                desires=["meaningful connection", "romantic relationship", "emotional warmth"],
                conflicts=["isolation vs connection", "safety vs risk", "routine vs change"],
                personality_drivers=["need for connection", "romantic optimism"],
                confidence_score=0.7,
                text_references=["Maya Patel closed her laptop"],
                first_appearance="Maya Patel closed her laptop with a sigh",
                importance_score=1.0
            ),
            
            "Amelia Hartwell": CharacterProfile(
                name="Amelia Hartwell",
                aliases=["Amelia", "Miss Hartwell"],
                physical_description="24-year-old Victorian woman, brilliant mathematician in disguise",
                mannerisms=["corset adjusting", "demure smiling", "hidden calculations"],
                speech_patterns=["proper Victorian speech", "hidden intellectual discourse"],
                behavioral_traits=["brilliant", "constrained", "rebellious", "secretive"],
                backstory="Groundbreaking mathematician publishing under brother's name",
                relationships=["brother - publishing proxy", "Royal Society - exclusionary"],
                formative_experiences=["mathematical discoveries", "societal constraints", "academic exclusion"],
                social_connections=["London society", "academic circles", "family"],
                motivations=["advance mathematics", "gain recognition", "break barriers"],
                fears=["discovery", "scandal", "intellectual suppression"],
                desires=["direct recognition", "academic acceptance", "intellectual freedom"],
                conflicts=["genius vs gender roles", "truth vs propriety", "ambition vs safety"],
                personality_drivers=["intellectual brilliance", "determination to contribute"],
                confidence_score=0.9,
                text_references=["Amelia Hartwell adjusted her corset"],
                first_appearance="Amelia Hartwell adjusted her corset with practiced efficiency",
                importance_score=1.0
            ),
            
            "Detective Riley Santos": CharacterProfile(
                name="Detective Riley Santos",
                aliases=["Riley", "Detective Santos", "Santos"],
                physical_description="Experienced detective with supernatural sight",
                mannerisms=["crime scene analysis", "suppressing magical sight", "grandmother's wisdom recall"],
                speech_patterns=["police procedural", "internal supernatural conflict"],
                behavioral_traits=["experienced", "conflicted", "intuitive", "suppressed"],
                backstory="Years suppressing inherited magical sight, trying to live normally",
                relationships=["grandmother - magical mentor", "police colleagues", "supernatural community"],
                formative_experiences=["inherited magical abilities", "police training", "supernatural suppression"],
                social_connections=["police department", "family magical tradition", "crime victims"],
                motivations=["solve supernatural crimes", "protect innocents", "embrace heritage"],
                fears=["exposure", "losing sanity", "supernatural threats"],
                desires=["balance both worlds", "use gifts effectively", "protect community"],
                conflicts=["normal vs supernatural", "duty vs heritage", "hiding vs revealing"],
                personality_drivers=["duty to justice", "inherited magical responsibility"],
                confidence_score=0.8,
                text_references=["Detective Riley Santos had seen enough crime scenes"],
                first_appearance="Detective Riley Santos had seen enough crime scenes to last three lifetimes",
                importance_score=1.0
            ),
            
            "Alex Kim": CharacterProfile(
                name="Alex Kim",
                aliases=["Alex"],
                physical_description="16-year-old with trembling hands holding acceptance letter",
                mannerisms=["paper trembling", "staring at letter", "internal conflict"],
                speech_patterns=["teenage uncertainty", "cultural identity struggle"],
                behavioral_traits=["talented", "conflicted", "identity-seeking", "pressured"],
                backstory="Musical prodigy from immigrant family, multiple sacrifices for success",
                relationships=["immigrant parents - sacrificing", "underground music scene"],
                formative_experiences=["musical training", "cultural expectations", "identity formation"],
                social_connections=["family", "music conservatory", "underground scene"],
                motivations=["authentic expression", "honor parents", "find identity"],
                fears=["disappointing parents", "losing authenticity", "wrong choice"],
                desires=["musical authenticity", "cultural balance", "personal fulfillment"],
                conflicts=["classical vs contemporary", "family vs self", "tradition vs innovation"],
                personality_drivers=["musical authenticity", "cultural identity"],
                confidence_score=0.65,
                text_references=["Sixteen-year-old Alex Kim stared at the acceptance letter"],
                first_appearance="Sixteen-year-old Alex Kim stared at the acceptance letter",
                importance_score=1.0
            ),
            
            "Dr. Catherine Wells": CharacterProfile(
                name="Dr. Catherine Wells",
                aliases=["Dr. Wells", "Catherine"],
                physical_description="Psychiatrist losing grip on reality, distorted reflection",
                mannerisms=["reviewing notes repeatedly", "reality checking", "paranoid observation"],
                speech_patterns=["clinical analysis", "self-doubt", "reality questioning"],
                behavioral_traits=["analytical", "unraveling", "paranoid", "self-aware"],
                backstory="Fifteen years helping others, now losing own sanity",
                relationships=["patients - role reversal", "medical colleagues"],
                formative_experiences=["psychiatric training", "helping others", "mental deterioration"],
                social_connections=["medical community", "patient relationships", "professional network"],
                motivations=["maintain sanity", "continue helping", "find truth"],
                fears=["complete breakdown", "harming patients", "losing identity"],
                desires=["mental clarity", "professional competence", "reality anchor"],
                conflicts=["doctor vs patient", "sanity vs madness", "help vs harm"],
                personality_drivers=["professional duty", "self-preservation"],
                confidence_score=0.4,
                text_references=["Dr. Catherine Wells reviewed her patient notes"],
                first_appearance="Dr. Catherine Wells reviewed her patient notes for the third time",
                importance_score=1.0
            ),
            
            "Rosa Delgado": CharacterProfile(
                name="Rosa Delgado",
                aliases=["Rosa", "Abuela"],
                physical_description="68-year-old keeper of family traditions, weathered hands",
                mannerisms=["bread kneading", "story telling", "masa shaping", "prayer whispering"],
                speech_patterns=["wisdom sharing", "cultural preservation", "loving guidance"],
                behavioral_traits=["wise", "nurturing", "traditional", "bridge-building"],
                backstory="Four generations of family cooking, bridge between Mexico and America",
                relationships=["granddaughter Sofia", "family generations", "cultural heritage"],
                formative_experiences=["generational cooking", "cultural preservation", "family guidance"],
                social_connections=["extended family", "cultural community", "neighborhood"],
                motivations=["preserve traditions", "guide granddaughter", "share wisdom"],
                fears=["lost traditions", "cultural disconnection", "family separation"],
                desires=["cultural continuity", "family unity", "wisdom transfer"],
                conflicts=["tradition vs modernity", "preservation vs change", "past vs future"],
                personality_drivers=["cultural preservation", "family love"],
                confidence_score=0.95,
                text_references=["Rosa Delgado stood in the kitchen"],
                first_appearance="Rosa Delgado stood in the kitchen where four generations of women had kneaded bread",
                importance_score=1.0
            )
        }
    
    def _initialize_expected_personas(self) -> Dict[str, ArtistPersona]:
        """Initialize expected artist personas for validation"""
        return {
            "Sarah Chen": ArtistPersona(
                character_name="Sarah Chen",
                artist_name="Fragile Freedom",
                primary_genre="indie",
                secondary_genres=["alternative", "singer-songwriter"],
                vocal_style="vulnerable and raw emotional delivery",
                instrumental_preferences=["acoustic guitar", "minimal piano", "ambient textures"],
                lyrical_themes=["authenticity vs facade", "breaking free", "self-discovery"],
                emotional_palette=["vulnerability", "liberation", "raw honesty", "hope"],
                artistic_influences=["Phoebe Bridgers", "Sufjan Stevens", "Sharon Van Etten"],
                collaboration_style="intimate and selective",
                character_mapping_confidence=0.9,
                genre_justification="Indie's raw authenticity matches her journey from perfection to truth",
                persona_description="An artist emerging from perfectionist constraints to authentic expression"
            ),
            
            "Elena Rodriguez": ArtistPersona(
                character_name="Elena Rodriguez",
                artist_name="Canvas Dreams",
                primary_genre="folk",
                secondary_genres=["indie", "alternative"],
                vocal_style="soft, introspective with trembling vulnerability",
                instrumental_preferences=["acoustic guitar", "piano", "strings"],
                lyrical_themes=["artistic struggle", "fear of success", "creative courage"],
                emotional_palette=["fear", "hope", "vulnerability", "artistic passion"],
                artistic_influences=["Joni Mitchell", "Nick Drake", "Bon Iver"],
                collaboration_style="cautious but meaningful connections",
                character_mapping_confidence=0.85,
                genre_justification="Folk's intimate storytelling suits her introspective artistic journey",
                persona_description="A fearful artist learning to embrace her creative voice"
            ),
            
            "The Philosopher": ArtistPersona(
                character_name="The Philosopher",
                artist_name="Existential Architect",
                primary_genre="progressive rock",
                secondary_genres=["ambient", "post-rock", "experimental"],
                vocal_style="contemplative spoken word with melodic interludes",
                instrumental_preferences=["synthesizers", "orchestral arrangements", "complex rhythms"],
                lyrical_themes=["existential meaning", "philosophical inquiry", "hope from despair"],
                emotional_palette=["contemplation", "intellectual passion", "hard-won hope", "cosmic perspective"],
                artistic_influences=["Pink Floyd", "King Crimson", "Godspeed You! Black Emperor"],
                collaboration_style="philosophical dialogue through music",
                character_mapping_confidence=0.95,
                genre_justification="Progressive rock's complexity mirrors philosophical depth and conceptual thinking",
                persona_description="A philosophical mind creating meaning through complex musical architecture"
            ),
            
            "Marcus": ArtistPersona(
                character_name="Marcus",
                artist_name="Eternal Love",
                primary_genre="blues",
                secondary_genres=["soul", "gospel", "americana"],
                vocal_style="deep, weathered voice carrying decades of love and loss",
                instrumental_preferences=["guitar", "harmonica", "organ", "strings"],
                lyrical_themes=["enduring love", "grief transformation", "memory preservation"],
                emotional_palette=["profound grief", "transcendent love", "spiritual resilience", "hope"],
                artistic_influences=["B.B. King", "Otis Redding", "Mahalia Jackson"],
                collaboration_style="community-centered, healing through shared music",
                character_mapping_confidence=0.9,
                genre_justification="Blues tradition of transforming pain into beauty matches his grief journey",
                persona_description="A man transforming devastating loss into eternal love through music"
            ),
            
            "Captain Zara Okafor": ArtistPersona(
                character_name="Captain Zara Okafor",
                artist_name="Stellar Command",
                primary_genre="electronic",
                secondary_genres=["synthwave", "ambient", "space music"],
                vocal_style="commanding presence with ethereal harmonies",
                instrumental_preferences=["synthesizers", "electronic drums", "space effects", "orchestral elements"],
                lyrical_themes=["cosmic exploration", "leadership under pressure", "unknown frontiers"],
                emotional_palette=["determination", "cosmic wonder", "protective instinct", "courage"],
                artistic_influences=["Vangelis", "Jean-Michel Jarre", "Daft Punk"],
                collaboration_style="strategic coordination with crew-like ensemble",
                character_mapping_confidence=0.85,
                genre_justification="Electronic music's futuristic soundscapes match space exploration themes",
                persona_description="A space commander channeling cosmic adventure through electronic soundscapes"
            ),
            
            "Maya Patel": ArtistPersona(
                character_name="Maya Patel",
                artist_name="Coffee Shop Dreams",
                primary_genre="indie pop",
                secondary_genres=["folk", "singer-songwriter", "bedroom pop"],
                vocal_style="warm, intimate vocals with hopeful undertones",
                instrumental_preferences=["acoustic guitar", "soft synths", "gentle percussion", "strings"],
                lyrical_themes=["modern romance", "connection in isolation", "digital age loneliness"],
                emotional_palette=["longing", "hope", "warmth", "romantic optimism"],
                artistic_influences=["Clairo", "Rex Orange County", "Kali Uchis"],
                collaboration_style="intimate duets and gentle harmonies",
                character_mapping_confidence=0.8,
                genre_justification="Indie pop's warm accessibility matches her hopeful romantic journey",
                persona_description="A modern romantic finding connection through gentle, hopeful melodies"
            ),
            
            "Amelia Hartwell": ArtistPersona(
                character_name="Amelia Hartwell",
                artist_name="Hidden Equations",
                primary_genre="classical",
                secondary_genres=["chamber music", "orchestral", "neoclassical"],
                vocal_style="precise, mathematical phrasing with hidden passion",
                instrumental_preferences=["piano", "string quartet", "harpsichord", "full orchestra"],
                lyrical_themes=["hidden brilliance", "societal constraints", "intellectual freedom"],
                emotional_palette=["suppressed genius", "rebellious spirit", "mathematical beauty", "liberation"],
                artistic_influences=["Bach", "Clara Schumann", "Max Richter"],
                collaboration_style="formal structure hiding revolutionary content",
                character_mapping_confidence=0.9,
                genre_justification="Classical music's mathematical precision mirrors her hidden mathematical genius",
                persona_description="A Victorian genius encoding rebellion and brilliance in classical forms"
            ),
            
            "Detective Riley Santos": ArtistPersona(
                character_name="Detective Riley Santos",
                artist_name="Shadow Walker",
                primary_genre="dark electronic",
                secondary_genres=["industrial", "gothic", "dark ambient"],
                vocal_style="haunting vocals layered with supernatural undertones",
                instrumental_preferences=["dark synths", "industrial percussion", "atmospheric effects", "distorted guitars"],
                lyrical_themes=["supernatural investigation", "hidden worlds", "inherited power"],
                emotional_palette=["mystery", "supernatural dread", "ancestral wisdom", "protective duty"],
                artistic_influences=["Nine Inch Nails", "Portishead", "Massive Attack"],
                collaboration_style="solitary creation with occasional mystical guidance",
                character_mapping_confidence=0.85,
                genre_justification="Dark electronic's atmospheric tension matches supernatural crime investigation",
                persona_description="A supernatural detective channeling otherworldly investigations through dark soundscapes"
            ),
            
            "Alex Kim": ArtistPersona(
                character_name="Alex Kim",
                artist_name="Cultural Crossroads",
                primary_genre="indie rock",
                secondary_genres=["alternative", "lo-fi", "k-indie"],
                vocal_style="youthful uncertainty blending cultural influences",
                instrumental_preferences=["electric guitar", "synthesizers", "traditional instruments", "bedroom recording"],
                lyrical_themes=["cultural identity", "generational expectations", "authentic expression"],
                emotional_palette=["identity confusion", "cultural pride", "rebellious spirit", "coming-of-age"],
                artistic_influences=["Mitski", "Japanese Breakfast", "The Strokes"],
                collaboration_style="cross-cultural fusion with peer musicians",
                character_mapping_confidence=0.8,
                genre_justification="Indie rock's DIY authenticity matches their search for genuine cultural expression",
                persona_description="A young artist navigating cultural identity through authentic indie expression"
            ),
            
            "Dr. Catherine Wells": ArtistPersona(
                character_name="Dr. Catherine Wells",
                artist_name="Fractured Mind",
                primary_genre="dark ambient",
                secondary_genres=["experimental", "minimalist", "drone"],
                vocal_style="fragmented whispers and clinical observations",
                instrumental_preferences=["field recordings", "processed sounds", "minimal electronics", "found sounds"],
                lyrical_themes=["reality distortion", "professional identity crisis", "sanity boundaries"],
                emotional_palette=["paranoia", "clinical detachment", "existential fear", "fragmented consciousness"],
                artistic_influences=["Tim Hecker", "William Basinski", "The Caretaker"],
                collaboration_style="isolated creation with reality-checking collaborators",
                character_mapping_confidence=0.75,
                genre_justification="Dark ambient's disorienting soundscapes mirror psychological fragmentation",
                persona_description="A fractured psyche exploring the boundaries of sanity through experimental sound"
            ),
            
            "Rosa Delgado": ArtistPersona(
                character_name="Rosa Delgado",
                artist_name="Generational Wisdom",
                primary_genre="folk",
                secondary_genres=["world music", "acoustic", "traditional"],
                vocal_style="warm, storytelling voice carrying generational wisdom",
                instrumental_preferences=["acoustic guitar", "traditional instruments", "family harmonies", "kitchen sounds"],
                lyrical_themes=["family traditions", "cultural preservation", "intergenerational love"],
                emotional_palette=["maternal wisdom", "cultural pride", "nostalgic warmth", "protective love"],
                artistic_influences=["Lila Downs", "Natalia Lafourcade", "Mercedes Sosa"],
                collaboration_style="family ensemble with teaching moments",
                character_mapping_confidence=0.95,
                genre_justification="Folk's storytelling tradition perfectly preserves and shares cultural wisdom",
                persona_description="A cultural keeper weaving family stories and traditions through timeless folk melodies"
            )
        }
    
    def _initialize_expected_commands(self) -> Dict[str, List[SunoCommand]]:
        """Initialize expected Suno commands for validation"""
        return {
            "Sarah Chen": [
                SunoCommand(
                    command_type="simple",
                    prompt="An indie song about breaking free from perfectionist expectations, vulnerable female vocals",
                    style_tags=["indie", "alternative", "raw"],
                    structure_tags=["verse", "chorus", "bridge"],
                    sound_effect_tags=["intimate", "acoustic"],
                    vocal_tags=["vulnerable", "emotional"],
                    character_source="Sarah Chen",
                    artist_persona="Fragile Freedom",
                    command_rationale="Captures her journey from perfection to authenticity",
                    estimated_effectiveness=0.85,
                    variations=["acoustic version", "full band arrangement"]
                ),
                SunoCommand(
                    command_type="custom",
                    prompt="[Verse] Standing on the edge of everything I used to be [Chorus] Finally free to fall apart, finally free to be me [Bridge] Twenty-seven years of being perfect, now I'm perfectly broken",
                    style_tags=["indie", "emotional", "breakthrough"],
                    structure_tags=["[Verse]", "[Chorus]", "[Bridge]"],
                    sound_effect_tags=["rooftop ambience", "wind"],
                    vocal_tags=["raw emotion", "cathartic"],
                    character_source="Sarah Chen",
                    artist_persona="Fragile Freedom",
                    command_rationale="Direct lyrical interpretation of her rooftop revelation",
                    estimated_effectiveness=0.9,
                    variations=["stripped down", "orchestral build"]
                )
            ],
            
            "The Philosopher": [
                SunoCommand(
                    command_type="simple",
                    prompt="Progressive rock concept piece about finding meaning in a meaningless universe, philosophical spoken word",
                    style_tags=["progressive rock", "philosophical", "conceptual"],
                    structure_tags=["intro", "movement I", "movement II", "finale"],
                    sound_effect_tags=["cosmic", "contemplative", "orchestral"],
                    vocal_tags=["spoken word", "contemplative", "wise"],
                    character_source="The Philosopher",
                    artist_persona="Existential Architect",
                    command_rationale="Matches his philosophical journey from despair to meaning creation",
                    estimated_effectiveness=0.9,
                    variations=["full orchestral", "chamber ensemble", "electronic ambient"]
                ),
                SunoCommand(
                    command_type="bracket_notation",
                    prompt="[Contemplative intro] God is dead, and we have killed him [Building intensity] But what comes after the death of absolute meaning? [Climactic resolution] The hard-won hope of someone who has stared into the abyss and chosen to create meaning anyway",
                    style_tags=["progressive", "existential", "hopeful"],
                    structure_tags=["[Contemplative intro]", "[Building intensity]", "[Climactic resolution]"],
                    sound_effect_tags=["philosophical atmosphere", "cosmic reverb"],
                    vocal_tags=["philosophical discourse", "emotional build"],
                    character_source="The Philosopher",
                    artist_persona="Existential Architect",
                    command_rationale="Direct adaptation of his existential journey and manuscript themes",
                    estimated_effectiveness=0.95,
                    variations=["symphonic version", "minimalist arrangement"]
                )
            ],
            
            "Marcus": [
                SunoCommand(
                    command_type="simple",
                    prompt="Soulful blues about transforming grief into eternal love, deep weathered male vocals",
                    style_tags=["blues", "soul", "healing"],
                    structure_tags=["verse", "chorus", "bridge", "outro"],
                    sound_effect_tags=["warm", "intimate", "spiritual"],
                    vocal_tags=["weathered", "soulful", "healing"],
                    character_source="Marcus",
                    artist_persona="Eternal Love",
                    command_rationale="Captures his transformation of devastating loss into enduring love",
                    estimated_effectiveness=0.9,
                    variations=["gospel arrangement", "acoustic version", "full band"]
                ),
                SunoCommand(
                    command_type="custom",
                    prompt="[Verse] Thirty years of morning coffee, thirty years of goodnight kiss [Chorus] But love don't die when the body fails, love just learns a different way to live [Bridge] She wouldn't want me disappearing into grief, she'd want me carrying our love forward",
                    style_tags=["blues", "memorial", "love"],
                    structure_tags=["[Verse]", "[Chorus]", "[Bridge]"],
                    sound_effect_tags=["hospital ambience", "memory echoes"],
                    vocal_tags=["grief-stricken", "loving", "determined"],
                    character_source="Marcus",
                    artist_persona="Eternal Love",
                    command_rationale="Direct lyrical interpretation of his hospital corridor revelation",
                    estimated_effectiveness=0.95,
                    variations=["string arrangement", "harmonica solo"]
                )
            ],
            
            "Captain Zara Okafor": [
                SunoCommand(
                    command_type="simple",
                    prompt="Electronic space music about leadership in cosmic crisis, commanding female vocals with ethereal harmonies",
                    style_tags=["electronic", "space", "cinematic"],
                    structure_tags=["intro", "build", "climax", "resolution"],
                    sound_effect_tags=["cosmic", "nebula", "starship"],
                    vocal_tags=["commanding", "ethereal", "determined"],
                    character_source="Captain Zara Okafor",
                    artist_persona="Stellar Command",
                    command_rationale="Reflects her space command experience and current cosmic crisis",
                    estimated_effectiveness=0.85,
                    variations=["orchestral hybrid", "ambient version", "action sequence"]
                )
            ],
            
            "Maya Patel": [
                SunoCommand(
                    command_type="simple",
                    prompt="Warm indie pop about finding connection through coffee shop romance, hopeful female vocals",
                    style_tags=["indie pop", "romantic", "warm"],
                    structure_tags=["verse", "chorus", "bridge"],
                    sound_effect_tags=["coffee shop ambience", "intimate"],
                    vocal_tags=["hopeful", "warm", "romantic"],
                    character_source="Maya Patel",
                    artist_persona="Coffee Shop Dreams",
                    command_rationale="Captures her pandemic isolation and hopeful romantic connection",
                    estimated_effectiveness=0.8,
                    variations=["acoustic version", "bedroom pop style"]
                )
            ],
            
            "Amelia Hartwell": [
                SunoCommand(
                    command_type="simple",
                    prompt="Classical chamber piece encoding mathematical rebellion, precise piano with hidden passion",
                    style_tags=["classical", "mathematical", "rebellious"],
                    structure_tags=["exposition", "development", "recapitulation"],
                    sound_effect_tags=["Victorian parlor", "mathematical precision"],
                    vocal_tags=["precise", "hidden passion", "intellectual"],
                    character_source="Amelia Hartwell",
                    artist_persona="Hidden Equations",
                    command_rationale="Mathematical precision hiding revolutionary content matches her situation",
                    estimated_effectiveness=0.9,
                    variations=["full orchestra", "string quartet", "solo piano"]
                )
            ],
            
            "Detective Riley Santos": [
                SunoCommand(
                    command_type="simple",
                    prompt="Dark electronic investigation music with supernatural undertones, haunting female vocals",
                    style_tags=["dark electronic", "supernatural", "investigative"],
                    structure_tags=["intro", "investigation", "revelation", "resolution"],
                    sound_effect_tags=["crime scene", "supernatural energy", "urban night"],
                    vocal_tags=["haunting", "determined", "mystical"],
                    character_source="Detective Riley Santos",
                    artist_persona="Shadow Walker",
                    command_rationale="Dark atmosphere matches supernatural crime investigation",
                    estimated_effectiveness=0.85,
                    variations=["industrial version", "ambient investigation"]
                )
            ],
            
            "Alex Kim": [
                SunoCommand(
                    command_type="simple",
                    prompt="Indie rock about cultural identity and generational expectations, youthful vocals blending influences",
                    style_tags=["indie rock", "cultural", "coming-of-age"],
                    structure_tags=["verse", "chorus", "bridge"],
                    sound_effect_tags=["bedroom recording", "cultural fusion"],
                    vocal_tags=["youthful", "conflicted", "authentic"],
                    character_source="Alex Kim",
                    artist_persona="Cultural Crossroads",
                    command_rationale="DIY authenticity matches their search for genuine cultural expression",
                    estimated_effectiveness=0.8,
                    variations=["lo-fi version", "full band arrangement"]
                )
            ],
            
            "Rosa Delgado": [
                SunoCommand(
                    command_type="simple",
                    prompt="Traditional folk song about preserving family recipes and cultural wisdom, warm storytelling vocals",
                    style_tags=["folk", "traditional", "family"],
                    structure_tags=["verse", "chorus", "story bridge"],
                    sound_effect_tags=["kitchen sounds", "family gathering", "warm"],
                    vocal_tags=["storytelling", "wise", "nurturing"],
                    character_source="Rosa Delgado",
                    artist_persona="Generational Wisdom",
                    command_rationale="Folk storytelling tradition perfectly preserves cultural wisdom",
                    estimated_effectiveness=0.95,
                    variations=["family harmony", "acoustic guitar", "traditional instruments"]
                )
            ]
        }
    
    def get_sample_narrative(self, scenario: str) -> str:
        """Get sample narrative text for testing"""
        if scenario in self.scenarios:
            return self.scenarios[scenario].narrative_text
        raise ValueError(f"Unknown scenario: {scenario}")
    
    def get_expected_character(self, character_name: str) -> CharacterProfile:
        """Get expected character profile for validation"""
        if character_name in self.expected_characters:
            return self.expected_characters[character_name]
        raise ValueError(f"Unknown character: {character_name}")
    
    def get_expected_persona(self, character_name: str) -> ArtistPersona:
        """Get expected artist persona for validation"""
        if character_name in self.expected_personas:
            return self.expected_personas[character_name]
        raise ValueError(f"Unknown persona: {character_name}")
    
    def get_expected_commands(self, character_name: str) -> List[SunoCommand]:
        """Get expected Suno commands for validation"""
        if character_name in self.expected_commands:
            return self.expected_commands[character_name]
        raise ValueError(f"Unknown commands for: {character_name}")
    
    def get_test_scenario(self, scenario_name: str) -> ScenarioData:
        """Get complete test scenario"""
        if scenario_name in self.scenarios:
            return self.scenarios[scenario_name]
        raise ValueError(f"Unknown scenario: {scenario_name}")
    
    def list_scenarios(self) -> List[str]:
        """List all available test scenarios"""
        return list(self.scenarios.keys())
    
    def get_scenarios_by_complexity(self, complexity: str) -> List[ScenarioData]:
        """Get scenarios filtered by complexity level"""
        return [scenario for scenario in self.scenarios.values() 
                if scenario.complexity_level == complexity]
    
    def export_test_data(self, filepath: str) -> None:
        """Export test data to JSON file for external use"""
        data = {
            "scenarios": {name: asdict(scenario) for name, scenario in self.scenarios.items()},
            "expected_characters": {name: char.to_dict() for name, char in self.expected_characters.items()},
            "expected_personas": {name: persona.to_dict() for name, persona in self.expected_personas.items()},
            "expected_commands": {
                name: [cmd.to_dict() for cmd in commands] 
                for name, commands in self.expected_commands.items()
            }
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def validate_character_against_expected(self, actual: CharacterProfile, expected_name: str) -> Dict[str, Any]:
        """Validate actual character against expected profile"""
        expected = self.get_expected_character(expected_name)
        
        validation_results = {
            "name_match": actual.name == expected.name,
            "confidence_acceptable": actual.confidence_score >= 0.7,
            "has_required_fields": all([
                actual.backstory,
                actual.motivations,
                actual.fears,
                actual.desires,
                actual.conflicts
            ]),
            "theme_alignment": self._check_theme_alignment(actual, expected),
            "completeness_score": self._calculate_completeness(actual)
        }
        
        return validation_results
    
    def _check_theme_alignment(self, actual: CharacterProfile, expected: CharacterProfile) -> float:
        """Check thematic alignment between actual and expected characters"""
        # Simple keyword matching for themes
        expected_themes = set()
        actual_themes = set()
        
        # Extract themes from various fields
        for field in ['motivations', 'fears', 'desires', 'conflicts']:
            expected_themes.update(getattr(expected, field, []))
            actual_themes.update(getattr(actual, field, []))
        
        if not expected_themes:
            return 1.0
        
        # Calculate overlap
        overlap = len(expected_themes.intersection(actual_themes))
        return overlap / len(expected_themes)
    
    def _calculate_completeness(self, character: CharacterProfile) -> float:
        """Calculate completeness score for character profile"""
        required_fields = [
            'name', 'backstory', 'motivations', 'fears', 'desires', 'conflicts',
            'personality_drivers', 'physical_description'
        ]
        
        completed_fields = 0
        for field in required_fields:
            value = getattr(character, field, None)
            if value and (isinstance(value, str) and value.strip() or 
                         isinstance(value, list) and len(value) > 0):
                completed_fields += 1
        
        return completed_fields / len(required_fields)
    
    def validate_persona_against_expected(self, actual: ArtistPersona, expected_name: str) -> Dict[str, Any]:
        """Validate actual persona against expected persona"""
        expected = self.get_expected_persona(expected_name)
        
        validation_results = {
            "character_name_match": actual.character_name == expected.character_name,
            "genre_alignment": self._check_genre_alignment(actual, expected),
            "confidence_acceptable": actual.character_mapping_confidence >= 0.7,
            "has_required_fields": all([
                actual.primary_genre,
                actual.vocal_style,
                actual.lyrical_themes,
                actual.emotional_palette
            ]),
            "persona_completeness": self._calculate_persona_completeness(actual),
            "artistic_coherence": self._check_artistic_coherence(actual)
        }
        
        return validation_results
    
    def _check_genre_alignment(self, actual: ArtistPersona, expected: ArtistPersona) -> float:
        """Check genre alignment between actual and expected personas"""
        # Primary genre match is most important
        primary_match = 1.0 if actual.primary_genre == expected.primary_genre else 0.0
        
        # Secondary genre overlap
        actual_genres = set([actual.primary_genre] + actual.secondary_genres)
        expected_genres = set([expected.primary_genre] + expected.secondary_genres)
        
        if not expected_genres:
            return primary_match
        
        overlap = len(actual_genres.intersection(expected_genres))
        secondary_match = overlap / len(expected_genres)
        
        # Weight primary genre more heavily
        return (primary_match * 0.7) + (secondary_match * 0.3)
    
    def _calculate_persona_completeness(self, persona: ArtistPersona) -> float:
        """Calculate completeness score for artist persona"""
        required_fields = [
            'character_name', 'artist_name', 'primary_genre', 'vocal_style',
            'lyrical_themes', 'emotional_palette', 'persona_description'
        ]
        
        completed_fields = 0
        for field in required_fields:
            value = getattr(persona, field, None)
            if value and (isinstance(value, str) and value.strip() or 
                         isinstance(value, list) and len(value) > 0):
                completed_fields += 1
        
        return completed_fields / len(required_fields)
    
    def _check_artistic_coherence(self, persona: ArtistPersona) -> float:
        """Check artistic coherence within persona"""
        # Simple coherence check based on genre-style alignment
        coherence_score = 0.0
        
        # Check if vocal style matches genre expectations
        genre_vocal_map = {
            "indie": ["vulnerable", "raw", "intimate"],
            "folk": ["storytelling", "warm", "acoustic"],
            "blues": ["soulful", "weathered", "emotional"],
            "electronic": ["ethereal", "processed", "atmospheric"],
            "classical": ["precise", "trained", "formal"],
            "progressive rock": ["complex", "conceptual", "dynamic"]
        }
        
        expected_vocal_styles = genre_vocal_map.get(persona.primary_genre, [])
        if any(style in persona.vocal_style.lower() for style in expected_vocal_styles):
            coherence_score += 0.5
        
        # Check if lyrical themes align with emotional palette
        theme_emotion_alignment = len(set(persona.lyrical_themes).intersection(set(persona.emotional_palette)))
        if theme_emotion_alignment > 0:
            coherence_score += 0.5
        
        return min(coherence_score, 1.0)
    
    def validate_suno_command_against_expected(self, actual: SunoCommand, character_name: str, command_index: int = 0) -> Dict[str, Any]:
        """Validate actual Suno command against expected command"""
        expected_commands = self.get_expected_commands(character_name)
        
        if command_index >= len(expected_commands):
            return {"error": f"No expected command at index {command_index}"}
        
        expected = expected_commands[command_index]
        
        validation_results = {
            "command_type_match": actual.command_type == expected.command_type,
            "character_source_match": actual.character_source == expected.character_source,
            "effectiveness_acceptable": actual.estimated_effectiveness >= 0.7,
            "has_required_tags": all([
                actual.style_tags,
                actual.vocal_tags,
                actual.prompt
            ]),
            "tag_alignment": self._check_tag_alignment(actual, expected),
            "command_completeness": self._calculate_command_completeness(actual)
        }
        
        return validation_results
    
    def _check_tag_alignment(self, actual: SunoCommand, expected: SunoCommand) -> float:
        """Check tag alignment between actual and expected commands"""
        alignments = []
        
        # Check style tags alignment
        actual_style = set(actual.style_tags)
        expected_style = set(expected.style_tags)
        if expected_style:
            style_alignment = len(actual_style.intersection(expected_style)) / len(expected_style)
            alignments.append(style_alignment)
        
        # Check vocal tags alignment
        actual_vocal = set(actual.vocal_tags)
        expected_vocal = set(expected.vocal_tags)
        if expected_vocal:
            vocal_alignment = len(actual_vocal.intersection(expected_vocal)) / len(expected_vocal)
            alignments.append(vocal_alignment)
        
        return sum(alignments) / len(alignments) if alignments else 1.0
    
    def _calculate_command_completeness(self, command: SunoCommand) -> float:
        """Calculate completeness score for Suno command"""
        required_fields = [
            'command_type', 'prompt', 'style_tags', 'vocal_tags',
            'character_source', 'artist_persona', 'command_rationale'
        ]
        
        completed_fields = 0
        for field in required_fields:
            value = getattr(command, field, None)
            if value and (isinstance(value, str) and value.strip() or 
                         isinstance(value, list) and len(value) > 0):
                completed_fields += 1
        
        return completed_fields / len(required_fields)
    
    def create_album_test_fixture(self, scenario_name: str, track_count: int = 6) -> Dict[str, Any]:
        """Create a complete album test fixture for validation"""
        scenario = self.get_test_scenario(scenario_name)
        character_name = scenario.expected_primary_character
        
        # Get expected outputs
        expected_character = self.get_expected_character(character_name)
        expected_persona = self.get_expected_persona(character_name)
        expected_commands = self.get_expected_commands(character_name)
        
        # Create album fixture
        album_fixture = {
            "scenario": scenario,
            "album_metadata": {
                "title": f"{character_name} - Complete Album",
                "track_count": track_count,
                "concept": f"Musical exploration of {scenario.description}",
                "expected_themes": expected_persona.lyrical_themes,
                "expected_genres": [expected_persona.primary_genre] + expected_persona.secondary_genres
            },
            "expected_character": expected_character,
            "expected_persona": expected_persona,
            "expected_track_structure": self._generate_track_structure(expected_commands, track_count),
            "validation_criteria": {
                "thematic_consistency": 0.8,
                "character_authenticity": 0.85,
                "genre_coherence": 0.8,
                "lyrical_quality": 0.75,
                "command_effectiveness": 0.8
            }
        }
        
        return album_fixture
    
    def _generate_track_structure(self, base_commands: List[SunoCommand], track_count: int) -> List[Dict[str, Any]]:
        """Generate expected track structure for album"""
        track_structure = []
        
        # Track themes based on narrative arc
        track_themes = [
            "Opening Statement", "Personal Reflection", "Deeper Questions",
            "Emotional Core", "Conflict Resolution", "Final Understanding",
            "Bonus Exploration", "Alternative Perspective", "Instrumental Meditation",
            "Collaborative Vision", "Extended Journey", "Ultimate Synthesis"
        ]
        
        for i in range(track_count):
            theme = track_themes[i] if i < len(track_themes) else f"Track {i+1}"
            
            # Use base command as template, modify for track theme
            base_command = base_commands[0] if base_commands else None
            
            track_info = {
                "track_number": i + 1,
                "theme": theme,
                "expected_command_type": base_command.command_type if base_command else "simple",
                "expected_style_tags": base_command.style_tags if base_command else [],
                "expected_effectiveness_range": [0.7, 0.95],
                "thematic_variation": f"Explores {theme.lower()} aspect of character journey"
            }
            
            track_structure.append(track_info)
        
        return track_structure
    
    def get_edge_case_scenarios(self) -> List[ScenarioData]:
        """Get scenarios specifically designed for edge case testing"""
        edge_cases = []
        
        for scenario in self.scenarios.values():
            if (scenario.name == "minimal_character_edge" or 
                "edge" in scenario.description.lower() or
                scenario.expected_character_count == 0):
                edge_cases.append(scenario)
        
        return edge_cases
    
    def get_performance_test_scenarios(self) -> List[ScenarioData]:
        """Get scenarios suitable for performance testing"""
        performance_scenarios = []
        
        for scenario in self.scenarios.values():
            # Long narratives or complex scenarios for performance testing
            if (len(scenario.narrative_text) > 1000 or 
                scenario.complexity_level == "complex" or
                scenario.expected_character_count > 2):
                performance_scenarios.append(scenario)
        
        return performance_scenarios
    
    def create_batch_test_data(self, scenario_names: List[str]) -> Dict[str, Any]:
        """Create batch test data for multiple scenarios"""
        batch_data = {
            "batch_id": f"batch_{len(scenario_names)}_scenarios",
            "scenario_count": len(scenario_names),
            "scenarios": {},
            "expected_results": {},
            "validation_summary": {
                "total_characters": 0,
                "total_personas": 0,
                "total_commands": 0,
                "complexity_distribution": {"simple": 0, "medium": 0, "complex": 0}
            }
        }
        
        for scenario_name in scenario_names:
            if scenario_name in self.scenarios:
                scenario = self.scenarios[scenario_name]
                batch_data["scenarios"][scenario_name] = scenario
                
                # Add expected results
                character_name = scenario.expected_primary_character
                batch_data["expected_results"][scenario_name] = {
                    "character": self.expected_characters.get(character_name),
                    "persona": self.expected_personas.get(character_name),
                    "commands": self.expected_commands.get(character_name, [])
                }
                
                # Update summary
                batch_data["validation_summary"]["total_characters"] += scenario.expected_character_count
                batch_data["validation_summary"]["total_personas"] += 1
                batch_data["validation_summary"]["total_commands"] += len(self.expected_commands.get(character_name, []))
                batch_data["validation_summary"]["complexity_distribution"][scenario.complexity_level] += 1
        
        return batch_data


# Global instance for easy access
test_data_manager = TestDataManager()


# Additional validation utilities and test fixtures

@dataclass
class ValidationResult:
    """Result of validation test"""
    test_name: str
    passed: bool
    score: float
    details: Dict[str, Any]
    error_message: Optional[str] = None


@dataclass
class AlbumValidationResult:
    """Result of album validation test"""
    album_title: str
    track_count: int
    overall_score: float
    track_results: List[ValidationResult]
    thematic_consistency: float
    character_authenticity: float
    genre_coherence: float


class ComprehensiveValidator:
    """Comprehensive validation system for all test fixtures"""
    
    def __init__(self, test_data_manager: TestDataManager):
        self.test_data = test_data_manager
    
    def validate_complete_workflow(self, 
                                 scenario_name: str,
                                 actual_character: CharacterProfile,
                                 actual_persona: ArtistPersona,
                                 actual_commands: List[SunoCommand]) -> Dict[str, ValidationResult]:
        """Validate complete workflow output against expected results"""
        
        results = {}
        
        # Validate character
        character_validation = self.test_data.validate_character_against_expected(
            actual_character, actual_character.name
        )
        results["character"] = ValidationResult(
            test_name="character_validation",
            passed=all(character_validation.values()),
            score=sum(1 for v in character_validation.values() if v) / len(character_validation),
            details=character_validation
        )
        
        # Validate persona
        persona_validation = self.test_data.validate_persona_against_expected(
            actual_persona, actual_persona.character_name
        )
        results["persona"] = ValidationResult(
            test_name="persona_validation",
            passed=all(persona_validation.values()),
            score=sum(1 for v in persona_validation.values() if v) / len(persona_validation),
            details=persona_validation
        )
        
        # Validate commands
        command_results = []
        for i, command in enumerate(actual_commands):
            command_validation = self.test_data.validate_suno_command_against_expected(
                command, actual_character.name, i
            )
            command_results.append(ValidationResult(
                test_name=f"command_{i}_validation",
                passed=all(v for k, v in command_validation.items() if k != "error"),
                score=sum(1 for k, v in command_validation.items() if k != "error" and v) / max(1, len([k for k in command_validation.keys() if k != "error"])),
                details=command_validation
            ))
        
        results["commands"] = command_results
        
        return results
    
    def validate_album_creation(self,
                              scenario_name: str,
                              album_tracks: List[Dict[str, Any]]) -> AlbumValidationResult:
        """Validate complete album creation against expected structure"""
        
        album_fixture = self.test_data.create_album_test_fixture(scenario_name, len(album_tracks))
        expected_structure = album_fixture["expected_track_structure"]
        validation_criteria = album_fixture["validation_criteria"]
        
        track_results = []
        thematic_scores = []
        authenticity_scores = []
        genre_scores = []
        
        for i, track in enumerate(album_tracks):
            expected_track = expected_structure[i] if i < len(expected_structure) else expected_structure[0]
            
            # Validate individual track
            track_validation = self._validate_album_track(track, expected_track, album_fixture)
            track_results.append(track_validation)
            
            # Collect scores for album-level metrics
            thematic_scores.append(track_validation.score)
            authenticity_scores.append(track_validation.score)  # Simplified for now
            genre_scores.append(track_validation.score)  # Simplified for now
        
        # Calculate album-level scores
        thematic_consistency = sum(thematic_scores) / len(thematic_scores) if thematic_scores else 0
        character_authenticity = sum(authenticity_scores) / len(authenticity_scores) if authenticity_scores else 0
        genre_coherence = sum(genre_scores) / len(genre_scores) if genre_scores else 0
        
        overall_score = (thematic_consistency + character_authenticity + genre_coherence) / 3
        
        return AlbumValidationResult(
            album_title=album_fixture["album_metadata"]["title"],
            track_count=len(album_tracks),
            overall_score=overall_score,
            track_results=track_results,
            thematic_consistency=thematic_consistency,
            character_authenticity=character_authenticity,
            genre_coherence=genre_coherence
        )
    
    def _validate_album_track(self, 
                            actual_track: Dict[str, Any], 
                            expected_track: Dict[str, Any],
                            album_fixture: Dict[str, Any]) -> ValidationResult:
        """Validate individual album track"""
        
        validation_details = {}
        
        # Check if track has required fields
        required_fields = ["track_number", "title", "suno_command"]
        for field in required_fields:
            validation_details[f"has_{field}"] = field in actual_track
        
        # Check thematic alignment
        if "theme" in actual_track and "theme" in expected_track:
            validation_details["theme_alignment"] = expected_track["theme"].lower() in actual_track.get("title", "").lower()
        
        # Check command effectiveness if available
        if "suno_command" in actual_track:
            command_data = actual_track["suno_command"]
            if isinstance(command_data, dict) and "estimated_effectiveness" in command_data:
                effectiveness = command_data["estimated_effectiveness"]
                validation_details["effectiveness_acceptable"] = effectiveness >= expected_track.get("expected_effectiveness_range", [0.7, 1.0])[0]
        
        # Calculate overall track score
        passed_checks = sum(1 for v in validation_details.values() if v)
        total_checks = len(validation_details)
        score = passed_checks / total_checks if total_checks > 0 else 0
        
        return ValidationResult(
            test_name=f"track_{actual_track.get('track_number', 'unknown')}_validation",
            passed=score >= 0.7,
            score=score,
            details=validation_details
        )
    
    def create_performance_benchmark(self, scenario_names: List[str]) -> Dict[str, Any]:
        """Create performance benchmark data for testing"""
        
        benchmark_data = {
            "benchmark_id": f"perf_benchmark_{len(scenario_names)}_scenarios",
            "scenario_count": len(scenario_names),
            "expected_performance": {
                "character_analysis_time": {"max": 5.0, "target": 2.0},  # seconds
                "persona_generation_time": {"max": 3.0, "target": 1.5},
                "command_generation_time": {"max": 2.0, "target": 1.0},
                "total_workflow_time": {"max": 10.0, "target": 5.0},
                "memory_usage": {"max": 500, "target": 200},  # MB
                "concurrent_requests": {"max": 10, "target": 5}
            },
            "test_scenarios": [],
            "validation_thresholds": {
                "character_confidence": 0.7,
                "persona_confidence": 0.7,
                "command_effectiveness": 0.7,
                "overall_quality": 0.75
            }
        }
        
        for scenario_name in scenario_names:
            if scenario_name in self.test_data.scenarios:
                scenario = self.test_data.scenarios[scenario_name]
                benchmark_data["test_scenarios"].append({
                    "scenario_name": scenario_name,
                    "narrative_length": len(scenario.narrative_text),
                    "complexity_level": scenario.complexity_level,
                    "expected_character_count": scenario.expected_character_count,
                    "expected_processing_time": self._estimate_processing_time(scenario)
                })
        
        return benchmark_data
    
    def _estimate_processing_time(self, scenario: ScenarioData) -> float:
        """Estimate processing time based on scenario complexity"""
        base_time = 1.0  # Base processing time in seconds
        
        # Adjust for narrative length
        length_factor = len(scenario.narrative_text) / 1000  # Per 1000 characters
        
        # Adjust for complexity
        complexity_multiplier = {
            "simple": 1.0,
            "medium": 1.5,
            "complex": 2.0
        }.get(scenario.complexity_level, 1.0)
        
        # Adjust for character count
        character_factor = scenario.expected_character_count * 0.5
        
        estimated_time = base_time + length_factor + character_factor
        return estimated_time * complexity_multiplier


# Create global validator instance
comprehensive_validator = ComprehensiveValidator(test_data_manager)


# Utility functions for test data creation

def create_test_suite_data(suite_name: str, scenario_names: List[str]) -> Dict[str, Any]:
    """Create complete test suite data package"""
    
    suite_data = {
        "suite_name": suite_name,
        "created_at": "2024-01-01T00:00:00Z",  # Would be datetime.now() in real implementation
        "scenario_count": len(scenario_names),
        "scenarios": {},
        "expected_outputs": {},
        "validation_config": {
            "character_validation": True,
            "persona_validation": True,
            "command_validation": True,
            "album_validation": True,
            "performance_validation": True
        },
        "test_metadata": {
            "total_narratives": len(scenario_names),
            "complexity_distribution": {},
            "genre_distribution": {},
            "character_count_distribution": {}
        }
    }
    
    # Populate scenarios and expected outputs
    for scenario_name in scenario_names:
        if scenario_name in test_data_manager.scenarios:
            scenario = test_data_manager.scenarios[scenario_name]
            suite_data["scenarios"][scenario_name] = asdict(scenario)
            
            # Add expected outputs
            character_name = scenario.expected_primary_character
            suite_data["expected_outputs"][scenario_name] = {
                "character": test_data_manager.expected_characters.get(character_name, {}).to_dict() if character_name in test_data_manager.expected_characters else {},
                "persona": test_data_manager.expected_personas.get(character_name, {}).to_dict() if character_name in test_data_manager.expected_personas else {},
                "commands": [cmd.to_dict() for cmd in test_data_manager.expected_commands.get(character_name, [])]
            }
            
            # Update metadata
            complexity = scenario.complexity_level
            suite_data["test_metadata"]["complexity_distribution"][complexity] = suite_data["test_metadata"]["complexity_distribution"].get(complexity, 0) + 1
            
            for genre in scenario.expected_genres:
                suite_data["test_metadata"]["genre_distribution"][genre] = suite_data["test_metadata"]["genre_distribution"].get(genre, 0) + 1
            
            char_count = scenario.expected_character_count
            suite_data["test_metadata"]["character_count_distribution"][str(char_count)] = suite_data["test_metadata"]["character_count_distribution"].get(str(char_count), 0) + 1
    
    return suite_data


def export_test_fixtures(output_dir: str = "test_fixtures_export") -> None:
    """Export all test fixtures to files for external use"""
    import os
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Export main test data
    test_data_manager.export_test_data(os.path.join(output_dir, "test_data.json"))
    
    # Export test suites
    all_scenarios = list(test_data_manager.scenarios.keys())
    
    # Unit test suite
    unit_scenarios = [s for s in all_scenarios if test_data_manager.scenarios[s].complexity_level == "simple"]
    unit_suite = create_test_suite_data("unit_tests", unit_scenarios)
    with open(os.path.join(output_dir, "unit_test_suite.json"), 'w') as f:
        json.dump(unit_suite, f, indent=2)
    
    # Integration test suite
    integration_scenarios = [s for s in all_scenarios if test_data_manager.scenarios[s].complexity_level in ["medium", "complex"]]
    integration_suite = create_test_suite_data("integration_tests", integration_scenarios)
    with open(os.path.join(output_dir, "integration_test_suite.json"), 'w') as f:
        json.dump(integration_suite, f, indent=2)
    
    # Performance test suite
    performance_scenarios = [s for s in all_scenarios if len(test_data_manager.scenarios[s].narrative_text) > 500]
    performance_suite = create_test_suite_data("performance_tests", performance_scenarios)
    with open(os.path.join(output_dir, "performance_test_suite.json"), 'w') as f:
        json.dump(performance_suite, f, indent=2)
    
    print(f"Test fixtures exported to {output_dir}/")
    print(f"- Main test data: test_data.json")
    print(f"- Unit test suite: unit_test_suite.json ({len(unit_scenarios)} scenarios)")
    print(f"- Integration test suite: integration_test_suite.json ({len(integration_scenarios)} scenarios)")
    print(f"- Performance test suite: performance_test_suite.json ({len(performance_scenarios)} scenarios)")


# Example usage and testing functions
if __name__ == "__main__":
    # Test the comprehensive test data system
    print("🧪 COMPREHENSIVE TEST DATA SYSTEM")
    print("=" * 50)
    
    # Test basic functionality
    print(f"📊 Available scenarios: {len(test_data_manager.scenarios)}")
    print(f"👥 Expected characters: {len(test_data_manager.expected_characters)}")
    print(f"🎭 Expected personas: {len(test_data_manager.expected_personas)}")
    print(f"🎵 Expected command sets: {len(test_data_manager.expected_commands)}")
    
    # Test scenario retrieval
    print(f"\n📖 Sample scenario: {test_data_manager.scenarios['single_character_simple'].name}")
    print(f"   Description: {test_data_manager.scenarios['single_character_simple'].description}")
    print(f"   Complexity: {test_data_manager.scenarios['single_character_simple'].complexity_level}")
    
    # Test validation
    sarah_character = test_data_manager.get_expected_character("Sarah Chen")
    validation_result = test_data_manager.validate_character_against_expected(sarah_character, "Sarah Chen")
    print(f"\n✅ Character validation test: {validation_result}")
    
    # Test album fixture creation
    album_fixture = test_data_manager.create_album_test_fixture("single_character_simple", 4)
    print(f"\n🎵 Album fixture created: {album_fixture['album_metadata']['title']}")
    print(f"   Tracks: {album_fixture['album_metadata']['track_count']}")
    
    # Test batch data creation
    batch_scenarios = ["single_character_simple", "multi_character_medium", "concept_album_complex"]
    batch_data = test_data_manager.create_batch_test_data(batch_scenarios)
    print(f"\n📦 Batch test data: {batch_data['batch_id']}")
    print(f"   Total characters: {batch_data['validation_summary']['total_characters']}")
    print(f"   Complexity distribution: {batch_data['validation_summary']['complexity_distribution']}")
    
    print(f"\n🎯 COMPREHENSIVE TEST DATA SYSTEM READY!")
    print("• Realistic narrative scenarios ✅")
    print("• Expected character profiles ✅")
    print("• Expected artist personas ✅")
    print("• Expected Suno commands ✅")
    print("• Validation framework ✅")
    print("• Album creation fixtures ✅")
    print("• Performance benchmarks ✅")
    print("• Batch testing support ✅")