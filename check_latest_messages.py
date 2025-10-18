#!/usr/bin/env python
"""Check the latest messages in database"""
import sqlite3
from datetime import datetime, timedelta

conn = sqlite3.connect('data/bot.db')
cursor = conn.cursor()

# Get messages from last 5 minutes (web chat messages)
time_threshold = (datetime.now() - timedelta(minutes=5)).strftime('%Y-%m-%d %H:%M:%S')

cursor.execute("""
    SELECT m.id, m.user_id, u.username, m.role, m.content, m.created_at
    FROM messages m
    JOIN users u ON m.user_id = u.user_id
    WHERE m.user_id < 0
    AND m.created_at > ?
    ORDER BY m.created_at DESC
    LIMIT 20
""", (time_threshold,))

rows = cursor.fetchall()

print("\n" + "="*80)
print("RECENT WEB CHAT MESSAGES (Last 5 minutes)")
print("="*80 + "\n")

if rows:
    for row in rows:
        msg_id, user_id, username, role, content, created_at = row
        # Truncate long messages for display
        display_content = content[:70] + "..." if len(content) > 70 else content

        # Clean content for display (handle encoding)
        try:
            display_content = display_content.encode('ascii', 'ignore').decode('ascii')
        except:
            display_content = "[content with special chars]"

        print(f"Message ID: {msg_id}")
        print(f"  User: {username} (ID: {user_id})")
        print(f"  Role: {role}")
        print(f"  Content: {display_content}")
        print(f"  Time: {created_at}")
        print()

    # Summary
    user_msgs = sum(1 for r in rows if r[3] == 'user')
    assistant_msgs = sum(1 for r in rows if r[3] == 'assistant')

    print("="*80)
    print(f"Total messages: {len(rows)}")
    print(f"  - User messages: {user_msgs}")
    print(f"  - Assistant messages: {assistant_msgs}")
    print("="*80)

    if assistant_msgs == 0 and user_msgs > 0:
        print("\n✅ CORRECT: Only user messages are being saved!")
    elif assistant_msgs > 0:
        print("\n⚠️  WARNING: Assistant messages are being saved (should NOT be saved)")
else:
    print("No recent web chat messages found.")
    print("Please send some messages through the web UI first.")

print()
conn.close()

