from asyncio import Event, LifoQueue

# TODO: Consider defininig a new object to store screenshots and memory
# Resources shared across all threads
screenshots_stack: LifoQueue = LifoQueue(maxsize=10)
inferred_memory_stack: LifoQueue = LifoQueue(maxsize=10)

# Event object for determining when the application is ready to exit
exit_event = Event()

# Function to clear the oldest n elements from the LifoQueue
async def clear_oldest_from_lifoqueue(q:LifoQueue, n:int):
    """
    This will only work so long as there is a single producer, 
    with more than one producer I can imagine a race condition could exist
    when trying to clear the stack while another producer inserts a new entity.
    At the very least it will jeapordize the order of the stack. 
    TODO: Consider defining a custom queue class that can be used for this purpose
    """
    if n > q.qsize():
        raise IndexError("Cannot remove more items than are present")
    
    # Temporary list to hold elements
    temp_list = []

    # Transfer elements from LifoQueue to the list
    while not q.empty():
        temp_item = await q.get()
        temp_list.append(temp_item)

    # Remove the oldest elements (the last ones in the list)
    if temp_list:
        for i in range(n-1):
            temp_list.pop()

    # Transfer the remaining elements back to the LifoQueue
    for item in reversed(temp_list):
        await q.put(item)