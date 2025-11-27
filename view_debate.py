"""View saved debate output."""

import json
from pathlib import Path

debate_file = Path("data/debates/debate_20251126_085509.json")

with open(debate_file, "r", encoding="utf-8") as f:
    debate = json.load(f)

print("=" * 80)
print("DEBATE SUMMARY")
print("=" * 80)
print(f"Debate ID: {debate['debate_id']}")
print(f"Timestamp: {debate['timestamp']}")
print(f"Total Messages: {len(debate['messages'])}")
print()

print("=" * 80)
print("DEBATE TRANSCRIPT")
print("=" * 80)

for i, msg in enumerate(debate["messages"], 1):
    print(f"\n[Message {i}] {msg['type']} - {msg['from_agent']} (Round {msg['round_number']})")
    print("-" * 80)
    content = msg["content"]
    # Show first 300 chars
    if len(content) > 300:
        print(content[:300] + "...")
    else:
        print(content)
    print()

print("=" * 80)
print("MESSAGE BREAKDOWN")
print("=" * 80)
from collections import Counter

types = Counter(msg["type"] for msg in debate["messages"])
agents = Counter(msg["from_agent"] for msg in debate["messages"])

print(f"\nBy Type:")
for msg_type, count in types.items():
    print(f"  {msg_type}: {count}")

print(f"\nBy Agent:")
for agent, count in agents.items():
    print(f"  {agent}: {count}")
