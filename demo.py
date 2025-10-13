#!/usr/bin/env python3
"""
Sokoban Game Demo - Text version for testing
Shows how the game logic works without the full TUI
"""

class SokobanDemo:
    def __init__(self):
        self.level_data = [
            "####",
            "#  ###",
            "#    #",
            "# $  #",
            "### ###",
            "# $ $ #",
            "#..@..#",
            "#  $  #",
            "###  ##",
            "  ####"
        ]
        self.level = [list(line) for line in self.level_data]
        self.player_pos = self.find_player()
        self.moves = 0
        self.pushes = 0
    
    def find_player(self):
        for y, row in enumerate(self.level):
            for x, cell in enumerate(row):
                if cell in ['@', '+']:
                    return (y, x)
        return (0, 0)
    
    def display(self):
        print(f"\nMoves: {self.moves} | Pushes: {self.pushes}")
        print("=" * 20)
        for row in self.level:
            line = ""
            for cell in row:
                if cell == '#':  # Wall
                    line += "█"
                elif cell == ' ':  # Floor
                    line += "·"
                elif cell == '@':  # Player on floor
                    line += "@"
                elif cell == '.':  # Dock
                    line += "."
                elif cell == '*':  # Box on dock
                    line += "☑"
                elif cell == '$':  # Box
                    line += "☐"
                elif cell == '+':  # Player on dock
                    line += "⊕"
                else:
                    line += cell
            print(line)
        print("=" * 20)
    
    def move_player(self, direction):
        y, x = self.player_pos
        moves = {
            'w': (-1, 0), 's': (1, 0), 
            'a': (0, -1), 'd': (0, 1)
        }
        
        if direction not in moves:
            return False
            
        dy, dx = moves[direction]
        new_y, new_x = y + dy, x + dx
        
        # Check bounds
        if (new_y < 0 or new_y >= len(self.level) or 
            new_x < 0 or new_x >= len(self.level[new_y])):
            return False
            
        target_cell = self.level[new_y][new_x]
        
        # Can't move into walls
        if target_cell == '#':
            return False
            
        # Check if trying to push a box
        if target_cell in ['$', '*']:
            box_new_y, box_new_x = new_y + dy, new_x + dx
            
            # Check if box can be moved
            if (box_new_y < 0 or box_new_y >= len(self.level) or 
                box_new_x < 0 or box_new_x >= len(self.level[box_new_y])):
                return False
                
            box_target = self.level[box_new_y][box_new_x]
            
            # Box can't be pushed into walls or other boxes
            if box_target in ['#', '$', '*']:
                return False
                
            # Move the box
            if box_target == '.':  # Box lands on dock
                self.level[box_new_y][box_new_x] = '*'
            else:  # Box lands on floor
                self.level[box_new_y][box_new_x] = '$'
                
            # Clear box's old position
            if target_cell == '*':  # Box was on dock
                self.level[new_y][new_x] = '.'
            else:  # Box was on floor
                self.level[new_y][new_x] = ' '
                
            self.pushes += 1
        
        # Move player
        current_cell = self.level[y][x]
        if current_cell == '+':  # Player was on dock
            self.level[y][x] = '.'
        else:  # Player was on floor
            self.level[y][x] = ' '
            
        # Place player in new position
        if target_cell in ['.', '*']:  # Moving onto dock
            self.level[new_y][new_x] = '+'
        else:  # Moving onto floor
            self.level[new_y][new_x] = '@'
            
        self.player_pos = (new_y, new_x)
        self.moves += 1
        
        return True
    
    def is_complete(self):
        for row in self.level:
            for cell in row:
                if cell == '$':  # Box not on dock
                    return False
        return True
    
    def play_demo(self):
        print("🎮 Sokoban Game Demo")
        print("\nLegend:")
        print("█ = Wall    · = Floor    @ = Player")
        print(". = Dock    ☐ = Box      ☑ = Box on Dock")
        print("⊕ = Player on Dock")
        print("\nCommands: w/a/s/d to move, q to quit, r to reset")
        
        self.display()
        
        moves_sequence = ['d', 's', 'd', 'd', 's', 's', 'a', 'a', 'a']
        print(f"\nDemo moves: {' -> '.join(moves_sequence)}")
        
        for i, move in enumerate(moves_sequence):
            input(f"\nPress Enter for move {i+1}: {move}")
            if self.move_player(move):
                self.display()
                if self.is_complete():
                    print("🎉 Level Complete!")
                    break
            else:
                print("Invalid move!")

if __name__ == "__main__":
    demo = SokobanDemo()
    demo.play_demo()