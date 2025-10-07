# Utility functions for the hand gesture control system

def normalize_coordinates(x, y, width, height):
    """Normalize pixel coordinates to 0-1 range."""
    return x / width, y / height

def denormalize_coordinates(norm_x, norm_y, width, height):
    """Convert normalized coordinates back to pixels."""
    return int(norm_x * width), int(norm_y * height)

def calculate_distance(point1, point2):
    """Calculate Euclidean distance between two points."""
    import math
    return math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)