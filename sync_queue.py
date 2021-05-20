from collections import deque


class SyncQueue:
    main = deque()

    def append(self, to_add):
        self.main.append(to_add)

    def popleft(self):
        return self.main.popleft()

    def move_to_front(self, element):
        self.main.remove(element)
        self.main.append(element)

    def sync(self, sync_to: set):
        in_guild = deque()
        while len(self.main) > 0:
            thing = self.main.popleft()
            if thing in sync_to:
                in_guild.append(thing)
                sync_to.remove(thing)

        full_queue = deque(sync_to)
        while len(in_guild) > 0:
            full_queue.append(in_guild.popleft())

        self.main = full_queue
