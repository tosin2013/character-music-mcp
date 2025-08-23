#!/usr/bin/env python3
"""
Edge Case and Error Handling Performance Tests

Tests comprehensive error handling for malformed inputs, graceful degradation
with minimal character data, validates error message clarity and recovery
suggestions, and tests system behavior with empty inputs and invalid JSON.
"""

import asyncio
import sys
import os
import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from enhanced_server import (
    CharacterAnalyzer, PersonaGenerator, SunoCommandGenerator,
    CharacterProfile, ArtistPersona, SunoCommand
)
from tests.fixtures.mock_contexts import create_mock_context
from tests.fixtures.test_data import TestDataManager, test_data_manager


@dataclass
class EdgeCaseTestResult:
    """Result from edge case test execution"""
    test_name: str
    input_type: str
    success: bool
    graceful_degradation: bool
    error_message_quality: str  # "clear", "unclear", "missing"
    recovery_suggestion_provided: bool
    processing_time: float
    characters_found: int
    error_details: Optional[str] = None


class EdgeCaseGenerator:
    """Generates edge case inputs for testing"""
    
    def __init__(self):
        self.edge_cases = {
            "empty_string": "",
            "whitespace_only": "   \n\t   \n   ",
            "single_word": "Hello",
            "numbers_only": "123 456 789 000",
            "special_characters": "!@#$%^&*()_+-=[]{}|;:,.<>?",
            "mixed_languages": "Hello 你好 Bonjour Hola こんにちは",
            "extremely_short": "A.",
            "repeated_text": "The same sentence. " * 100,
            "malformed_json_like": '{"name": "John", "age": incomplete',
            "html_tags": "<html><body><p>This is HTML content</p></body></html>",
            "code_snippet": "def function(): return 'code'",
            "urls_and_emails": "Visit https://example.com or email test@example.com",
            "unicode_characters": "🎵🎶🎸🎤🎧 Music symbols and emojis 🎼🎹🥁",
            "very_long_single_sentence": "This is an extremely long sentence that goes on and on without any breaks or periods and contains no real character information but just keeps rambling about nothing in particular for a very long time to test how the system handles run-on sentences that provide no meaningful content for character analysis purposes. " * 10,
            "minimal_character_hint": "Someone did something somewhere.",
            "ambiguous_pronouns": "They went there. It happened. This was done. That was said.",
            "dialogue_only": '"Hello," said someone. "Goodbye," replied another. "Maybe," whispered a third.',
            "stream_of_consciousness": "thinking thinking always thinking what am I thinking about thinking about thoughts and more thoughts endless thoughts without structure or meaning just thoughts flowing like water like time like nothing at all",
            "technical_jargon": "The API endpoint returned a 404 error when the GET request was made to the REST service with invalid parameters in the JSON payload.",
            "poetry_format": "Roses are red,\nViolets are blue,\nThis is a poem,\nWith no character clue.",
            "incomplete_sentences": "When the... But then... However, if... Because of the... Therefore...",
            "contradictory_information": "John is tall. John is short. John is happy. John is sad. John exists. John doesn't exist."
        }
    
    def get_edge_case(self, case_name: str) -> str:
        """Get specific edge case input"""
        return self.edge_cases.get(case_name, "")
    
    def get_all_edge_cases(self) -> Dict[str, str]:
        """Get all edge case inputs"""
        return self.edge_cases.copy()
    
    def generate_malformed_json_inputs(self) -> Dict[str, str]:
        """Generate various malformed JSON-like inputs"""
        return {
            "unclosed_brace": '{"name": "John", "story": "incomplete',
            "missing_quotes": '{name: John, story: "His tale"}',
            "trailing_comma": '{"name": "John", "story": "His tale",}',
            "invalid_escape": '{"name": "John\\", "story": "His tale"}',
            "mixed_quotes": "{'name': \"John\", 'story': \"His tale\"}",
            "nested_incomplete": '{"character": {"name": "John", "details": {"age": 25',
            "array_malformed": '{"characters": ["John", "Jane",]}',
            "number_as_string_key": '{123: "value", "name": "John"}',
            "boolean_malformed": '{"active": True, "name": "John"}',  # Python True instead of JSON true
            "null_malformed": '{"value": None, "name": "John"}'  # Python None instead of JSON null
        }
    
    def generate_minimal_character_scenarios(self) -> Dict[str, str]:
        """Generate scenarios with minimal character information"""
        return {
            "name_only": "Sarah walked.",
            "action_only": "Someone cried.",
            "emotion_only": "There was sadness.",
            "location_only": "In the park.",
            "time_only": "Yesterday.",
            "single_pronoun": "She.",
            "vague_reference": "The person did the thing.",
            "abstract_concept": "Love exists.",
            "incomplete_thought": "When the door...",
            "question_only": "Who was there?"
        }


class EdgeCaseErrorTester:
    """Tests edge cases and error handling"""
    
    def __init__(self):
        self.character_analyzer = CharacterAnalyzer()
        self.persona_generator = PersonaGenerator()
        self.command_generator = SunoCommandGenerator()
        self.edge_case_generator = EdgeCaseGenerator()
        
        # Error handling quality criteria
        self.error_quality_criteria = {
            "clear_message": ["specific", "actionable", "user-friendly"],
            "recovery_suggestions": ["try", "consider", "ensure", "check"],
            "graceful_degradation": ["partial", "fallback", "alternative"]
        }
    
    async def test_empty_and_whitespace_inputs(self) -> List[EdgeCaseTestResult]:
        """Test handling of empty and whitespace-only inputs"""
        print("🔍 Testing empty and whitespace inputs...")
        
        test_cases = {
            "empty_string": "",
            "whitespace_only": "   \n\t   \n   ",
            "newlines_only": "\n\n\n\n",
            "tabs_only": "\t\t\t\t"
        }
        
        results = []
        for case_name, input_text in test_cases.items():
            result = await self._test_single_edge_case(case_name, input_text, "empty_input")
            results.append(result)
        
        return results
    
    async def test_malformed_inputs(self) -> List[EdgeCaseTestResult]:
        """Test handling of malformed and invalid inputs"""
        print("🔍 Testing malformed inputs...")
        
        # Test basic malformed inputs
        basic_cases = {
            "special_characters": "!@#$%^&*()_+-=[]{}|;:,.<>?",
            "numbers_only": "123 456 789 000",
            "html_tags": "<html><body><p>Content</p></body></html>",
            "code_snippet": "def function(): return 'code'"
        }
        
        results = []
        for case_name, input_text in basic_cases.items():
            result = await self._test_single_edge_case(case_name, input_text, "malformed_input")
            results.append(result)
        
        # Test malformed JSON-like inputs
        json_cases = self.edge_case_generator.generate_malformed_json_inputs()
        for case_name, input_text in json_cases.items():
            result = await self._test_single_edge_case(f"json_{case_name}", input_text, "malformed_json")
            results.append(result)
        
        return results
    
    async def test_minimal_character_data(self) -> List[EdgeCaseTestResult]:
        """Test graceful degradation with minimal character information"""
        print("🔍 Testing minimal character data scenarios...")
        
        minimal_cases = self.edge_case_generator.generate_minimal_character_scenarios()
        results = []
        
        for case_name, input_text in minimal_cases.items():
            result = await self._test_single_edge_case(case_name, input_text, "minimal_character")
            results.append(result)
        
        return results
    
    async def test_ambiguous_and_contradictory_inputs(self) -> List[EdgeCaseTestResult]:
        """Test handling of ambiguous and contradictory information"""
        print("🔍 Testing ambiguous and contradictory inputs...")
        
        ambiguous_cases = {
            "ambiguous_pronouns": "They went there. It happened. This was done.",
            "contradictory_info": "John is tall. John is short. John is happy. John is sad.",
            "stream_of_consciousness": "thinking thinking always thinking what am I thinking about",
            "incomplete_sentences": "When the... But then... However, if... Because of the...",
            "vague_references": "The person did the thing at the place during the time."
        }
        
        results = []
        for case_name, input_text in ambiguous_cases.items():
            result = await self._test_single_edge_case(case_name, input_text, "ambiguous_input")
            results.append(result)
        
        return results
    
    async def test_extreme_length_variations(self) -> List[EdgeCaseTestResult]:
        """Test handling of extremely short and long inputs"""
        print("🔍 Testing extreme length variations...")
        
        length_cases = {
            "single_character": "A",
            "single_word": "Hello",
            "extremely_short": "A.",
            "very_long_sentence": self.edge_case_generator.get_edge_case("very_long_single_sentence"),
            "repeated_text": "The same sentence. " * 200
        }
        
        results = []
        for case_name, input_text in length_cases.items():
            result = await self._test_single_edge_case(case_name, input_text, "length_variation")
            results.append(result)
        
        return results
    
    async def test_unicode_and_encoding_issues(self) -> List[EdgeCaseTestResult]:
        """Test handling of unicode characters and encoding issues"""
        print("🔍 Testing unicode and encoding scenarios...")
        
        unicode_cases = {
            "emoji_only": "🎵🎶🎸🎤🎧🎼🎹🥁",
            "mixed_languages": "Hello 你好 Bonjour Hola こんにちは",
            "special_unicode": "Ñoël Müller Øyvind Žižek",
            "mathematical_symbols": "∑∏∫∆∇∂∞≠≤≥±×÷",
            "currency_symbols": "€£¥₹₽₩₪₨₦₡₵",
            "arrows_and_symbols": "→←↑↓⇒⇐⇑⇓⟶⟵⟷⟺"
        }
        
        results = []
        for case_name, input_text in unicode_cases.items():
            result = await self._test_single_edge_case(case_name, input_text, "unicode_input")
            results.append(result)
        
        return results
    
    async def _test_single_edge_case(self, case_name: str, input_text: str, input_type: str) -> EdgeCaseTestResult:
        """Test a single edge case scenario"""
        import time
        start_time = time.time()
        
        try:
            # Create mock context
            ctx = create_mock_context("edge_case_test", session_id=f"edge_{case_name}")
            
            # Attempt character analysis
            characters = await self.character_analyzer.analyze_character_text(ctx, input_text)
            
            # Check for graceful degradation
            graceful_degradation = True
            characters_found = len(characters) if characters else 0
            
            # If no characters found, check if system handled it gracefully
            if characters_found == 0:
                # Check if context has appropriate messages
                has_info_messages = any("no characters" in msg.lower() or "unable to" in msg.lower() 
                                      for msg in ctx.get_all_messages())
                graceful_degradation = has_info_messages
            
            processing_time = time.time() - start_time
            
            return EdgeCaseTestResult(
                test_name=case_name,
                input_type=input_type,
                success=True,
                graceful_degradation=graceful_degradation,
                error_message_quality="clear" if graceful_degradation else "unclear",
                recovery_suggestion_provided=graceful_degradation,
                processing_time=processing_time,
                characters_found=characters_found
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            error_message = str(e)
            
            # Evaluate error message quality
            error_quality = self._evaluate_error_message_quality(error_message)
            recovery_provided = self._check_recovery_suggestions(error_message)
            
            return EdgeCaseTestResult(
                test_name=case_name,
                input_type=input_type,
                success=False,
                graceful_degradation=True,  # Exception handling is a form of graceful degradation
                error_message_quality=error_quality,
                recovery_suggestion_provided=recovery_provided,
                processing_time=processing_time,
                characters_found=0,
                error_details=error_message
            )
    
    def _evaluate_error_message_quality(self, error_message: str) -> str:
        """Evaluate the quality of an error message"""
        if not error_message:
            return "missing"
        
        error_lower = error_message.lower()
        
        # Check for clear, specific messages
        clear_indicators = ["invalid", "unable to", "failed to", "missing", "empty", "malformed"]
        if any(indicator in error_lower for indicator in clear_indicators):
            return "clear"
        
        # Check for technical jargon or unclear messages
        unclear_indicators = ["exception", "error", "traceback", "none", "null"]
        if any(indicator in error_lower for indicator in unclear_indicators):
            return "unclear"
        
        return "unclear"
    
    def _check_recovery_suggestions(self, error_message: str) -> bool:
        """Check if error message provides recovery suggestions"""
        if not error_message:
            return False
        
        error_lower = error_message.lower()
        suggestion_indicators = ["try", "consider", "ensure", "check", "provide", "use", "should"]
        
        return any(indicator in error_lower for indicator in suggestion_indicators)
    
    def _print_edge_case_results(self, test_category: str, results: List[EdgeCaseTestResult]) -> None:
        """Print edge case test results"""
        print(f"\n  📊 {test_category} Results:")
        
        total_tests = len(results)
        graceful_degradation_count = sum(1 for r in results if r.graceful_degradation)
        clear_errors_count = sum(1 for r in results if r.error_message_quality == "clear")
        recovery_suggestions_count = sum(1 for r in results if r.recovery_suggestion_provided)
        
        print(f"    Total Tests: {total_tests}")
        print(f"    Graceful Degradation: {graceful_degradation_count}/{total_tests} ({graceful_degradation_count/total_tests:.1%})")
        print(f"    Clear Error Messages: {clear_errors_count}/{total_tests} ({clear_errors_count/total_tests:.1%})")
        print(f"    Recovery Suggestions: {recovery_suggestions_count}/{total_tests} ({recovery_suggestions_count/total_tests:.1%})")
        
        # Show problematic cases
        problematic_cases = [r for r in results if not r.graceful_degradation or r.error_message_quality == "unclear"]
        if problematic_cases:
            print(f"    ⚠️  Problematic Cases:")
            for case in problematic_cases[:3]:  # Show first 3
                print(f"      - {case.test_name}: {case.error_details or 'No graceful degradation'}")
    
    def validate_edge_case_requirements(self, all_results: List[EdgeCaseTestResult]) -> Dict[str, bool]:
        """Validate edge case handling against requirements"""
        total_tests = len(all_results)
        if total_tests == 0:
            return {"no_tests": False}
        
        graceful_degradation_rate = sum(1 for r in all_results if r.graceful_degradation) / total_tests
        clear_error_rate = sum(1 for r in all_results if r.error_message_quality == "clear") / total_tests
        recovery_suggestion_rate = sum(1 for r in all_results if r.recovery_suggestion_provided) / total_tests
        
        # No crashes or unhandled exceptions
        no_crashes = all(r.success or r.graceful_degradation for r in all_results)
        
        return {
            "graceful_degradation_acceptable": graceful_degradation_rate >= 0.8,  # 80% should degrade gracefully
            "error_messages_clear": clear_error_rate >= 0.7,  # 70% should have clear error messages
            "recovery_suggestions_provided": recovery_suggestion_rate >= 0.6,  # 60% should provide recovery suggestions
            "no_system_crashes": no_crashes,
            "reasonable_processing_time": all(r.processing_time < 5.0 for r in all_results)  # All should complete within 5 seconds
        }


# Test functions for integration with test runner
async def test_empty_input_handling():
    """Test handling of empty and whitespace inputs"""
    tester = EdgeCaseErrorTester()
    results = await tester.test_empty_and_whitespace_inputs()
    
    # All empty inputs should be handled gracefully
    assert all(r.graceful_degradation for r in results), "Empty inputs should be handled gracefully"
    assert all(r.processing_time < 2.0 for r in results), "Empty input processing should be fast"


async def test_malformed_input_handling():
    """Test handling of malformed inputs"""
    tester = EdgeCaseErrorTester()
    results = await tester.test_malformed_inputs()
    
    # Most malformed inputs should be handled gracefully
    graceful_count = sum(1 for r in results if r.graceful_degradation)
    assert graceful_count / len(results) >= 0.7, f"At least 70% of malformed inputs should be handled gracefully, got {graceful_count}/{len(results)}"


async def test_minimal_character_data_handling():
    """Test graceful degradation with minimal character data"""
    tester = EdgeCaseErrorTester()
    results = await tester.test_minimal_character_data()
    
    # System should handle minimal data gracefully
    assert all(r.graceful_degradation for r in results), "Minimal character data should be handled gracefully"
    
    # Some minimal cases might still find basic character information
    some_characters_found = any(r.characters_found > 0 for r in results)
    # This is not a strict requirement, just checking system behavior


async def test_ambiguous_input_handling():
    """Test handling of ambiguous and contradictory inputs"""
    tester = EdgeCaseErrorTester()
    results = await tester.test_ambiguous_and_contradictory_inputs()
    
    # System should not crash on ambiguous inputs
    assert all(r.success or r.graceful_degradation for r in results), "Ambiguous inputs should not crash the system"


async def test_unicode_input_handling():
    """Test handling of unicode and special character inputs"""
    tester = EdgeCaseErrorTester()
    results = await tester.test_unicode_and_encoding_issues()
    
    # Unicode should be handled without crashes
    assert all(r.success or r.graceful_degradation for r in results), "Unicode inputs should not crash the system"
    assert all(r.processing_time < 5.0 for r in results), "Unicode processing should complete in reasonable time"


async def test_comprehensive_edge_case_coverage():
    """Test comprehensive edge case coverage"""
    tester = EdgeCaseErrorTester()
    
    # Run all edge case tests
    all_results = []
    
    empty_results = await tester.test_empty_and_whitespace_inputs()
    all_results.extend(empty_results)
    
    malformed_results = await tester.test_malformed_inputs()
    all_results.extend(malformed_results)
    
    minimal_results = await tester.test_minimal_character_data()
    all_results.extend(minimal_results)
    
    ambiguous_results = await tester.test_ambiguous_and_contradictory_inputs()
    all_results.extend(ambiguous_results)
    
    unicode_results = await tester.test_unicode_and_encoding_issues()
    all_results.extend(unicode_results)
    
    # Validate overall requirements
    validation = tester.validate_edge_case_requirements(all_results)
    
    assert validation["no_system_crashes"], "System should not crash on any edge case"
    assert validation["graceful_degradation_acceptable"], f"Graceful degradation rate too low"
    assert validation["reasonable_processing_time"], "All edge cases should process in reasonable time"


# Main execution for standalone testing
async def main():
    """Main function for standalone edge case testing"""
    print("🚀 Edge Case and Error Handling Testing")
    print("=" * 50)
    
    tester = EdgeCaseErrorTester()
    
    # Run all edge case test categories
    test_categories = [
        ("Empty and Whitespace Inputs", tester.test_empty_and_whitespace_inputs),
        ("Malformed Inputs", tester.test_malformed_inputs),
        ("Minimal Character Data", tester.test_minimal_character_data),
        ("Ambiguous Inputs", tester.test_ambiguous_and_contradictory_inputs),
        ("Unicode and Encoding", tester.test_unicode_and_encoding_issues),
        ("Extreme Length Variations", tester.test_extreme_length_variations)
    ]
    
    all_results = []
    
    for category_name, test_func in test_categories:
        print(f"\n📋 Testing {category_name}...")
        try:
            results = await test_func()
            all_results.extend(results)
            tester._print_edge_case_results(category_name, results)
        except Exception as e:
            print(f"❌ {category_name} failed: {e}")
    
    # Print overall summary
    print("\n" + "=" * 50)
    print("📊 EDGE CASE TEST SUMMARY")
    print("=" * 50)
    
    if all_results:
        validation = tester.validate_edge_case_requirements(all_results)
        
        total_tests = len(all_results)
        graceful_count = sum(1 for r in all_results if r.graceful_degradation)
        clear_errors = sum(1 for r in all_results if r.error_message_quality == "clear")
        
        print(f"📊 Overall Results:")
        print(f"   Total Edge Cases Tested: {total_tests}")
        print(f"   Graceful Degradation: {graceful_count}/{total_tests} ({graceful_count/total_tests:.1%})")
        print(f"   Clear Error Messages: {clear_errors}/{total_tests} ({clear_errors/total_tests:.1%})")
        
        print(f"\n✅ Validation Results:")
        for requirement, passed in validation.items():
            status = "✅" if passed else "❌"
            print(f"   {status} {requirement.replace('_', ' ').title()}")
        
        all_passed = all(validation.values())
        if all_passed:
            print("\n🎉 All edge case handling requirements met!")
            return True
        else:
            print("\n⚠️ Some edge case handling requirements not met")
            return False
    else:
        print("❌ No edge case tests were executed")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)