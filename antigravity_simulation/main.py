import pygame
import sys
import math

# Initialize pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Antigravity Engine Simulation")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)

# Antigravity engine properties
class AntigravityEngine:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.strength = 50
        self.radius = 30
        self.active = True

    def draw(self, surface):
        # Draw the engine
        pygame.draw.circle(surface, BLUE, (self.x, self.y), self.radius)
        
        # Draw the force field
        if self.active:
            for i in range(1, 5):
                alpha = 50 - (i * 10)
                radius = self.radius + (i * 20)
                color = (0, 0, 255, alpha)
                pygame.draw.circle(surface, color, (self.x, self.y), radius)

    def apply_force(self, obj):
        if not self.active:
            return
        
        dx = obj.x - self.x
        dy = obj.y - self.y
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance < self.radius + obj.radius:
            # Calculate force direction
            if distance == 0:
                distance = 0.1  # Avoid division by zero
            
            force_magnitude = self.strength / (distance**2)
            force_x = (dx / distance) * force_magnitude
            force_y = (dy / distance) * force_magnitude
            
            # Apply the force to the object
            obj.vx += force_x
            obj.vy += force_y

# Floating object
class FloatingObject:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 20
        self.vx = 0
        self.vy = 0
        self.color = RED

    def update(self):
        # Apply gravity
        self.vy += 0.1
        
        # Update position
        self.x += self.vx
        self.y += self.vy
        
        # Apply friction
        self.vx *= 0.99
        self.vy *= 0.99
        
        # Boundary checking
        if self.x < self.radius:
            self.x = self.radius
            self.vx *= -0.5
        elif self.x > WIDTH - self.radius:
            self.x = WIDTH - self.radius
            self.vx *= -0.5
        
        if self.y < self.radius:
            self.y = self.radius
            self.vy *= -0.5
        elif self.y > HEIGHT - self.radius:
            self.y = HEIGHT - self.radius
            self.vy *= -0.5

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)

# Main function
def main():
    clock = pygame.time.Clock()
    
    # Create antigravity engine
    engine = AntigravityEngine(WIDTH // 2, HEIGHT // 2)
    
    # Create floating objects
    objects = [
        FloatingObject(100, 100),
        FloatingObject(200, 200),
        FloatingObject(300, 300)
    ]
    
    # UI elements
    font = pygame.font.SysFont(None, 24)
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    engine.active = not engine.active
                elif event.key == pygame.K_UP:
                    engine.strength += 10
                elif event.key == pygame.K_DOWN:
                    engine.strength = max(10, engine.strength - 10)

        # Update objects
        for obj in objects:
            engine.apply_force(obj)
            obj.update()
        
        # Draw everything
        screen.fill(BLACK)
        engine.draw(screen)
        for obj in objects:
            obj.draw(screen)
        
        # Draw UI
        strength_text = font.render(f"Strength: {engine.strength}", True, WHITE)
        screen.blit(strength_text, (10, 10))
        status_text = font.render(f"Status: {'ON' if engine.active else 'OFF'}", True, WHITE)
        screen.blit(status_text, (10, 40))
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()