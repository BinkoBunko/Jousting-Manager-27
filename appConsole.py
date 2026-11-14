#testing ground for development

import db
from npc import Npc


npcs = []
for i in range(1000):
    npc = Npc(None, None, None)
    npcs.append(npc)

db.add_npcs(npcs)
print("\n".join(str(npc) for npc in npcs))
#display min and max of each stat
print(f"Min Strength: {min(npc.stats['strength'] for npc in npcs)}")
print(f"Max Strength: {max(npc.stats['strength'] for npc in npcs)}")
print(f"Min Animal Handling: {min(npc.stats['animalHandling'] for npc in npcs)}")
print(f"Max Animal Handling: {max(npc.stats['animalHandling'] for npc in npcs)}")
print(f"Min AC: {min(npc.stats['ac'] for npc in npcs)}")
print(f"Max AC: {max(npc.stats['ac'] for npc in npcs)}")