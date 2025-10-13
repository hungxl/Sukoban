from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static
from textual.containers import Container
from rich.text import Text
from game_manager import GameMap
from base.Base import Position


class GameMapWidget(Static):
    """Widget to display the Sokoban game map using entity system"""
    
    def __init__(self, level_data: list[str]):
        super().__init__()
        self.game_map = GameMap(level_data)
        
    def render(self) -> Text:
        """Render the game map with entities"""
        lines = []
        
        for y in range(self.game_map.height):
            line = ""
            for x in range(self.game_map.width):
                position = Position(x, y)
                cell_render = self.game_map.render_cell(position)
                line += cell_render
            lines.append(line)
        
        return Text.from_markup("\n".join(lines))
    
    def move_player(self, direction: str) -> bool:
        """Move player in the given direction"""
        return self.game_map.move_player(direction)
    
    def is_level_complete(self) -> bool:
        """Check if all boxes are on docks"""
        return self.game_map.is_level_complete()
    
    def reset_level(self):
        """Reset the level to its original state"""
        self.game_map.reset_level()
    
    def get_moves(self) -> int:
        """Get player's move count"""
        return self.game_map.get_moves()
    
    def get_pushes(self) -> int:
        """Get player's push count"""
        return self.game_map.get_pushes()


class ScoreBar(Static):
    """Widget to display game statistics"""
    
    def __init__(self, game_map_widget: GameMapWidget):
        super().__init__()
        self.game_map_widget = game_map_widget
        
    def render(self) -> Text:
        moves = self.game_map_widget.get_moves()
        pushes = self.game_map_widget.get_pushes()
        return Text.from_markup(
            f"[bold cyan]Moves: {moves}[/bold cyan]  "
            f"[bold magenta]Pushes: {pushes}[/bold magenta]"
        )


class PauseMenu(Static):
    """Pause menu overlay"""
    
    def __init__(self):
        super().__init__()
        self.visible = False
        
    def render(self) -> Text:
        if not self.visible:
            return Text("")
            
        return Text.from_markup(
            "\n[bold white on blue]        PAUSED        [/bold white on blue]\n"
            "[bold white on blue]                      [/bold white on blue]\n"
            "[bold white on blue]  R - Resume Game     [/bold white on blue]\n"
            "[bold white on blue]  N - Reset Level     [/bold white on blue]\n"
            "[bold white on blue]  Q - Quit Game       [/bold white on blue]\n"
            "[bold white on blue]                      [/bold white on blue]\n"
        )
    
    def toggle(self):
        self.visible = not self.visible


class SukobanApp(App):
    """Main Sokoban game application using entity-based architecture"""
    
    CSS = """
    Screen {
        background: $background;
    }
    
    .game-container {
        height: 100%;
        width: 100%;
        align: center middle;
    }
    
    .score-bar {
        dock: top;
        height: 3;
        background: $surface;
        text-align: center;
    }
    
    .game-map {
        margin: 1;
        text-align: center;
    }
    
    .pause-menu {
        dock: top;
        height: 8;
        text-align: center;
        layer: overlay;
    }
    """
    
    BINDINGS = [
        ("w,up", "move_up", "Move up"),
        ("s,down", "move_down", "Move down"),
        ("a,left", "move_left", "Move left"),
        ("d,right", "move_right", "Move right"),
        ("p,space", "pause", "Pause"),
        ("r", "reset", "Reset level"),
        ("q", "quit", "Quit"),
    ]
    
    def __init__(self):
        super().__init__()
        self.level_data = self.load_level_1()
        self.game_map_widget = GameMapWidget(self.level_data)
        self.score_bar = ScoreBar(self.game_map_widget)
        self.pause_menu = PauseMenu()
        self.paused = False
        
    def load_level_1(self) -> list[str]:
        """Load level 1 from the levels.txt file or use a default"""
        try:
            with open("levels.txt", "r") as f:
                content = f.read()
                lines = content.split('\n')
                
                # Find Level 1
                level_start = -1
                for i, line in enumerate(lines):
                    if line.strip() == "Level 1":
                        level_start = i + 1
                        break
                
                if level_start == -1:
                    return self.get_default_level()
                
                # Extract level data until empty line or next level
                level_lines = []
                for i in range(level_start, len(lines)):
                    line = lines[i]
                    if line.strip() == "" or line.startswith("Level "):
                        break
                    level_lines.append(line.rstrip())
                
                return level_lines if level_lines else self.get_default_level()
                
        except FileNotFoundError:
            return self.get_default_level()
    
    def get_default_level(self) -> list[str]:
        """Return a default level if file is not found"""
        return [
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
    
    def compose(self) -> ComposeResult:
        """Compose the UI layout"""
        yield Header()
        yield Container(
            self.pause_menu,
            self.score_bar,
            self.game_map_widget,
            classes="game-container"
        )
        yield Footer()
    
    def action_move_up(self):
        if not self.paused:
            self.move_player('up')
    
    def action_move_down(self):
        if not self.paused:
            self.move_player('down')
    
    def action_move_left(self):
        if not self.paused:
            self.move_player('left')
    
    def action_move_right(self):
        if not self.paused:
            self.move_player('right')
    
    def action_pause(self):
        self.paused = not self.paused
        self.pause_menu.toggle()
        self.refresh_widgets()
    
    def action_reset(self):
        self.game_map_widget.reset_level()
        self.refresh_widgets()
    
    def move_player(self, direction: str):
        """Handle player movement and game state updates"""
        if self.game_map_widget.move_player(direction):
            self.refresh_widgets()
            
            if self.game_map_widget.is_level_complete():
                self.notify("🎉 Level Complete! Congratulations!", severity="information")
    
    def refresh_widgets(self):
        """Refresh all widgets"""
        self.game_map_widget.refresh()
        self.score_bar.refresh()
        self.pause_menu.refresh()


if __name__ == "__main__":
    app = SukobanApp()
    app.run()