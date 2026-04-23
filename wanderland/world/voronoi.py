"""Simple Voronoi diagram generator."""
import random
import math
from PIL import Image, ImageDraw


def generate_voronoi(num_points: int, width: int, height: int, output: str = "assets/voronoi_map.png") -> None:
    """Generate a Voronoi diagram."""
    points = []
    for _ in range(num_points):
        x = random.randint(0, width - 1)
        y = random.randint(0, height - 1)
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)
        points.append((x, y, r, g, b))
    
    img = Image.new('RGBA', (width, height), (255, 255, 255, 0))
    px = img.load()
    
    for y in range(height):
        for x in range(width):
            min_dist = float('inf')
            closest = points[0]
            for px_x, px_y, r, g, b in points:
                dist = math.sqrt((x - px_x) ** 2 + (y - px_y) ** 2)
                if dist < min_dist:
                    min_dist = dist
                    closest = (px_x, px_y, r, g, b)
            
            # Use green as the "land" color for our processing
            if closest[4] > 128:
                px[x, y] = (0, 128, 0, 255)
            else:
                px[x, y] = (0, 128, 0, 255)
    
    img.save(output)
