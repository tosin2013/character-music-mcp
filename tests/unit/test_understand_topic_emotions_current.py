import pytest

#!/usr/bin/env python3

"""
Test current understand_topic_with_emotions tool behavior to identify issues
"""

import asyncio
import json
import os
import sys

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from server import understand_topic_with_emotions


class MockContext:
    async def info(self, message):
        print(f"INFO: {message}")

    async def error(self, message):
        print(f"ERROR: {message}")

@pytest.mark.asyncio
async def test_current_behavior():
    """Test current understand_topic_with_emotions behavior"""

    ctx = MockContext()

    # Test 1: Simple topic
    print("=== Test 1: Simple topic ===")
    result1 = await understand_topic_with_emotions(
        topic_text="A story about a lonely musician who finds hope through creating music in an abandoned warehouse.",
        source_type="story",
        focus_areas=["emotional journey", "musical themes"],
        ctx=ctx
    )

    print("Result 1:")
    try:
        parsed = json.loads(result1)
        print(json.dumps(parsed, indent=2))
    except:
        print(result1)

    print("\n" + "="*50 + "\n")

    # Test 2: Different emotional content
    print("=== Test 2: Different emotional content ===")
    result2 = await understand_topic_with_emotions(
        topic_text="An intense thriller about a detective chasing a serial killer through dark city streets, filled with suspense and fear.",
        source_type="book",
        focus_areas=["tension", "psychological elements"],
        ctx=ctx
    )

    print("Result 2:")
    try:
        parsed = json.loads(result2)
        print(json.dumps(parsed, indent=2))
    except:
        print(result2)

    print("\n" + "="*50 + "\n")

    # Test 3: Philosophical content
    print("=== Test 3: Philosophical content ===")
    result3 = await understand_topic_with_emotions(
        topic_text="A philosophical exploration of the meaning of existence, questioning whether life has inherent purpose or if we must create our own meaning through our choices and relationships.",
        source_type="philosophy",
        focus_areas=["existential themes", "human condition"],
        ctx=ctx
    )

    print("Result 3:")
    try:
        parsed = json.loads(result3)
        print(json.dumps(parsed, indent=2))
    except:
        print(result3)

if __name__ == "__main__":
    asyncio.run(test_current_behavior())
