import discord
import json

from games.mystery.status import gamestatus



async def select_event(ctx,event_id):
    with open("games/mystery/story/introduction.json", "r", encoding="utf-8") as f:
        story_data = json.load(f)
    event = story_data['events'][event_id]
    return event