from sync_queue import SyncQueue
import os

main_path = "./data/guild_info.txt"

# guild id: guild_priority_list
priorities = {}

try:
    with open(main_path, "rt") as file:
        lines = file.readlines()
        for i in lines:
            parts = i.split()

            priorities[guild_id] = SyncQueue()

            guild_id = int(parts[0])
            name_priorities = parts[1:]
            for i in name_priorities:
                priorities[guild_id].append(i)
except FileNotFoundError:
    open(main_path, "x")

def get_priorities(id_of: int) -> SyncQueue:
    if id_of not in priorities:
        priorities[id_of] = SyncQueue()
    return priorities[id_of]

def set_priorities(id_of: int, p: SyncQueue):
    priorities[id_of] = p

def save_to_file():
    with open(main_path, "wt") as output:
        outputs = []
        for id_of in priorities:
            outputs.append(" ".join([str(id_of)] + list(priorities[id_of].main)))
        output.write("\n".join(outputs))
