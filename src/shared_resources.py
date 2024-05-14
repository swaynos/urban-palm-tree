from asyncio import Event, LifoQueue

# Resources shared across all threads
screenshots_stack: LifoQueue = LifoQueue()
inferred_memory_stack: LifoQueue = LifoQueue()

# Event object for determining when the application is ready to exit
exit_event = Event()