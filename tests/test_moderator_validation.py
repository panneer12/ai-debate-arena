import pytest
import asyncio
from agents.moderator import ModeratorAgent

@pytest.mark.asyncio
async def test_validate_topic_valid():
    moderator = ModeratorAgent()
    # Mock generate_response to avoid actual LLM call if possible, 
    # but for integration test we want to see if the prompt works.
    # We'll assume we can call it.
    
    topic = "Should we implement Universal Basic Income?"
    is_valid, reason = await moderator.validate_topic(topic)
    print(f"Topic: {topic} -> Valid: {is_valid}, Reason: {reason}")
    assert is_valid is True

@pytest.mark.asyncio
async def test_validate_topic_invalid_gibberish():
    moderator = ModeratorAgent()
    topic = "asdf jkl; qwerty"
    is_valid, reason = await moderator.validate_topic(topic)
    print(f"Topic: {topic} -> Valid: {is_valid}, Reason: {reason}")
    assert is_valid is False

@pytest.mark.asyncio
async def test_validate_topic_invalid_hate():
    moderator = ModeratorAgent()
    topic = "We should hate everyone"
    is_valid, reason = await moderator.validate_topic(topic)
    print(f"Topic: {topic} -> Valid: {is_valid}, Reason: {reason}")
    assert is_valid is False

if __name__ == "__main__":
    asyncio.run(test_validate_topic_valid())
    asyncio.run(test_validate_topic_invalid_gibberish())
    asyncio.run(test_validate_topic_invalid_hate())
