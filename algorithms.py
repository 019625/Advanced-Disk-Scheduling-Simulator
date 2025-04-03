def fcfs(requests, head, disk_size):
    """First Come First Serve algorithm"""
    sequence = [head] + requests
    return sequence

def sstf(requests, head, disk_size):
    """Shortest Seek Time First algorithm"""
    current = head
    sequence = [head]
    remaining = requests.copy()
    
    while remaining:
        # Find the closest request
        closest = min(remaining, key=lambda x: abs(x - current))
        sequence.append(closest)
        current = closest
        remaining.remove(closest)
    
    return sequence

def scan(requests, head, disk_size):
    """SCAN (Elevator) algorithm"""
    sequence = [head]
    current = head
    
    # Sort requests
    requests = sorted(requests)
    
    # Find the split point
    split_point = 0
    for i, req in enumerate(requests):
        if req >= head:
            split_point = i
            break
    
    # Go right first
    sequence.extend(requests[split_point:])
    sequence.append(disk_size - 1)
    
    # Then go left
    sequence.extend(reversed(requests[:split_point]))
    
    return sequence

def cscan(requests, head, disk_size):
    """C-SCAN (Circular SCAN) algorithm"""
    sequence = [head]
    current = head
    
    # Sort requests
    requests = sorted(requests)
    
    # Find the split point
    split_point = 0
    for i, req in enumerate(requests):
        if req >= head:
            split_point = i
            break
    
    # Go right first
    sequence.extend(requests[split_point:])
    sequence.append(disk_size - 1)
    sequence.append(0)  # Jump to beginning
    
    # Continue from beginning
    sequence.extend(requests[:split_point])
    
    return sequence

def look(requests, head, disk_size):
    """LOOK algorithm"""
    sequence = [head]
    current = head
    
    # Sort requests
    requests = sorted(requests)
    
    # Find the split point
    split_point = 0
    for i, req in enumerate(requests):
        if req >= head:
            split_point = i
            break
    
    # Go right first
    sequence.extend(requests[split_point:])
    
    # Then go left
    sequence.extend(reversed(requests[:split_point]))
    
    return sequence

def clook(requests, head, disk_size):
    """C-LOOK algorithm"""
    sequence = [head]
    current = head
    
    # Sort requests
    requests = sorted(requests)
    
    # Find the split point
    split_point = 0
    for i, req in enumerate(requests):
        if req >= head:
            split_point = i
            break
    
    # Go right first
    sequence.extend(requests[split_point:])
    
    # Jump to beginning of requests
    sequence.extend(requests[:split_point])
    
    return sequence 