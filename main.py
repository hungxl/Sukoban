from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static
from textual.containers import Container
from rich.text import Text
from src.game_manager import GameMap
from src.base import Position
from src.log import get_logger
from random import randint
from pathlib import Path
from src.algorithms import SokobanBot, TIME_LIMIT_DEFAULT
from src.levels.level import get_level_count, get_level_info, get_level, list_available_levels
import time
import asyncio

LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

# Clean up old log files (ignore if files are locked by another process)
for file in LOG_DIR.glob("*.log"):
    try:
        file.unlink()
    except (PermissionError, OSError):
        pass  # File is in use by another process, skip it
        
for file in LOG_DIR.glob("*.zip"):
    try:
        file.unlink()
    except (PermissionError, OSError):
        pass  # File is in use by another process, skip it
    
# Get logger for this module
log = get_logger(__name__)


class GameMapWidget(Static):
    """Widget to display the Sokoban game map using entity system"""
    
    def __init__(self, level_data: list[str]):
        super().__init__()
        log.info(f"Initializing GameMapWidget with level size {len(level_data)}x{len(level_data[0]) if level_data else 0}")
        self.game_map = GameMap(level_data)
        self.bot = SokobanBot()
        log.info("GameMapWidget initialization complete")
        
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
        log.debug(f"Moving player in direction: {direction}")
        success = self.game_map.move_player(direction)
        if success:
            log.info(f"Player moved {direction} successfully")
        else:
            log.warning(f"Player could not move {direction}")
        return success
    
    def auto_solve(self, algorithm: str = "auto"):
        """Use bot to automatically solve the puzzle - returns result dict"""
        try:
            log.info(f"🤖 Starting auto-solve with {algorithm} algorithm")
            
            # Use the bot to solve with current game state
            if algorithm == "auto":
                result = self.bot.auto_solve(self.game_map)
            else:
                result = self.bot.solve(self.game_map, algorithm)
            
            return result
                
        except Exception as e:
            log.error(f"❌ Auto-solve failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def execute_solution(self, moves: list[str]) -> bool:
        """Execute a series of moves"""
        try:
            for move in moves:
                if not self.move_player(move):
                    log.warning(f"Failed to execute move: {move}")
                    return False
                time.sleep(0.1)  # Small delay for visibility
            return True
        except Exception as e:
            log.error(f"Failed to execute solution: {e}")
            return False
    
    async def execute_solution_animated(self, moves: list[str], app_callback) -> bool:
        """Execute a series of moves with animation"""
        try:
            for i, move in enumerate(moves):
                if not self.move_player(move):
                    log.warning(f"Failed to execute move: {move}")
                    return False
                
                # Update UI through callback
                await app_callback(i + 1, len(moves))
                
                # Delay for animation
                await asyncio.sleep(0.3)
            return True
        except Exception as e:
            log.error(f"Failed to execute animated solution: {e}")
            return False
    
    def reset_level(self):
        """Reset the level to its original state"""
        self.game_map.reset_level()
        
    def is_level_complete(self) -> bool:
        """Check if the level is complete"""
        return self.game_map.is_level_complete()
        
    def get_moves(self) -> int:
        """Get the number of moves made"""
        return self.game_map.get_moves()
        
    def get_pushes(self) -> int:
        """Get the number of box pushes made"""
        return self.game_map.get_pushes()


class ScoreBar(Static):
    """Widget to display game statistics"""
    
    def __init__(self, game_map_widget: GameMapWidget):
        super().__init__()
        self.game_map_widget = game_map_widget
        self.bot_status = ""
        self.last_solve_time = None

    def set_bot_status(self, status: str, solve_time: float | None = None):
        """Set bot status and timing information"""
        self.bot_status = status
        if solve_time is not None:
            self.last_solve_time = solve_time
        
    def render(self) -> Text:
        moves = self.game_map_widget.get_moves()
        pushes = self.game_map_widget.get_pushes()
        
        status_text = f"[bold cyan]Moves: {moves}[/bold cyan]  [bold magenta]Pushes: {pushes}[/bold magenta]"
        
        if self.bot_status:
            status_text += f"  [bold yellow]{self.bot_status}[/bold yellow]"
            
        if self.last_solve_time is not None:
            status_text += f"  [bold green]Solved in {self.last_solve_time:.2f}s[/bold green]"
            
        return Text.from_markup(status_text)


class SolutionDisplay(Static):
    """Display solution details after bot solving"""    
    def __init__(self):
        super().__init__()
        self.visible = False
        self.solution_data = None
        
    def show_solution(self, result: dict):
        self.solution_data = result
        self.visible = True
        
    def hide(self):
        self.visible = False
        self.solution_data = None
        
    def render(self) -> Text:
        if not self.visible or not self.solution_data:
            return Text("")
        
        data = self.solution_data
        algo = data.get('algorithm', 'Unknown')
        moves = data.get('move_count', 0)
        time_taken = data.get('solve_time', 0.0)
        iterations = data.get('iterations_used', 0)
        optimal = data.get('optimal', False)
        
        content = "\n[bold white on green]           🎯 SOLUTION FOUND!            [/bold white on green]\n"
        content += "[bold white on green]                                         [/bold white on green]\n"
        content += f"[bold white on green]  Algorithm: {algo:27}[/bold white on green]\n"
        content += f"[bold white on green]  Moves: {moves:32}[/bold white on green]\n"
        content += f"[bold white on green]  Iterations: {iterations:28}[/bold white on green]\n"
        content += f"[bold white on green]  Time: {time_taken:.2f}s{' ' * (31 - len(f'{time_taken:.2f}s'))}[/bold white on green]\n"
        
        if optimal:
            content += "[bold white on green]  ⭐ Optimal Solution              [/bold white on green]\n"
        
        content += "[bold white on green]                                         [/bold white on green]\n"
        content += "[bold white on green]  ▶ Press SPACE to Auto-Play Solution   [/bold white on green]\n"
        content += "[bold white on green]  ⏭  Press ENTER to Skip                [/bold white on green]\n"
        content += "[bold white on green]                                         [/bold white on green]\n"
        
        return Text.from_markup(content)


class CountdownTimer(Static):
    """Display countdown timer during bot solving"""
    
    def __init__(self):
        super().__init__()
        self.visible = False
        self.time_limit = TIME_LIMIT_DEFAULT
        self.elapsed_time = 0.0
        self.start_time = None
        self.algorithm_name = "Bot"
        
    def start(self, time_limit: float, algorithm_name: str = "Bot"):
        """Start the countdown timer"""
        self.time_limit = time_limit
        self.elapsed_time = 0.0
        self.start_time = time.time()
        self.algorithm_name = algorithm_name
        self.visible = True
        
    def stop(self):
        """Stop the countdown timer"""
        self.visible = False
        self.start_time = None
        
    def update_time(self):
        """Update elapsed time"""
        if self.start_time:
            self.elapsed_time = time.time() - self.start_time
            
    def get_progress_bar(self, width: int = 40) -> str:
        """Generate a progress bar showing time remaining"""
        if self.time_limit <= 0:
            return ""
            
        remaining = max(0, self.time_limit - self.elapsed_time)
        progress = min(1.0, self.elapsed_time / self.time_limit)
        
        filled = int(progress * width)
        empty = width - filled
        
        bar = "█" * filled + "░" * empty
        
        # Color based on time remaining
        if remaining < self.time_limit / 6:
            color = "red"
        elif remaining < self.time_limit / 2:
            color = "yellow"
        else:
            color = "green"
            
        return f"[{color}]{bar}[/{color}]"
        
    def render(self) -> Text:
        if not self.visible:
            return Text("")
        
        self.update_time()
        
        remaining = max(0, self.time_limit - self.elapsed_time)
        minutes = int(remaining // 60)
        seconds = int(remaining % 60)
        
        progress_bar = self.get_progress_bar(40)
        time_str = f"{minutes:02d}:{seconds:02d}"
        
        # Color the time based on urgency
        if remaining < 10:
            time_color = "bold red"
        elif remaining < 30:
            time_color = "bold yellow"
        else:
            time_color = "bold green"
        
        content = "\n[bold white on blue]        🤖 BOT SOLVING IN PROGRESS 🤖        [/bold white on blue]\n"
        content += "[bold white on blue]                                             [/bold white on blue]\n"
        content += f"[bold white on blue]  Algorithm: {self.algorithm_name:30}[/bold white on blue]\n"
        content += f"[bold white on blue]  Time Remaining: [{time_color}]{time_str}[/{time_color}]{' ' * (24 - len(time_str))}[/bold white on blue]\n"
        content += f"[bold white on blue]  {progress_bar}  [/bold white on blue]\n"
        content += "[bold white on blue]                                             [/bold white on blue]\n"
        content += "[bold white on blue]     Please wait while the bot finds a solution...  [/bold white on blue]\n"
        content += "[bold white on blue]                                             [/bold white on blue]\n"
        
        return Text.from_markup(content)


class HelpMenu(Static):
    """Help menu overlay"""
    
    def __init__(self):
        super().__init__()
        self.visible = False
        
    def render(self) -> Text:
        if not self.visible:
            return Text("")
            
        return Text.from_markup(
            "\n[bold white on green]          HELP - SOKOBAN CONTROLS          [/bold white on green]\n"
            "[bold white on green]                                            [/bold white on green]\n"
            "[bold white on green]  🎮 MOVEMENT:                             [/bold white on green]\n"
            "[bold white on green]     W/↑ - Move Up     S/↓ - Move Down     [/bold white on green]\n"
            "[bold white on green]     A/← - Move Left   D/→ - Move Right    [/bold white on green]\n"
            "[bold white on green]                                            [/bold white on green]\n"
            "[bold white on green]  🎯 GAME CONTROLS:                        [/bold white on green]\n"
            "[bold white on green]     P/Space - Pause   R - Reset Level     [/bold white on green]\n"
            "[bold white on green]     N - Next Level    L - Level Selection [/bold white on green]\n"
            "[bold white on green]     Q - Quit Game                         [/bold white on green]\n"
            "[bold white on green]                                            [/bold white on green]\n"
            "[bold white on green]  📋 MENU NAVIGATION:                      [/bold white on green]\n"
            "[bold white on green]     ↑↓ - Navigate     Enter - Select      [/bold white on green]\n"
            "[bold white on green]     ←→ - Change Page (Level Menu)         [/bold white on green]\n"
            "[bold white on green]                                            [/bold white on green]\n"
            "[bold white on green]  🤖 AI BOT:                               [/bold white on green]\n"
            "[bold white on green]     B - Bot Menu      H - This Help       [/bold white on green]\n"
            "[bold white on green]                                            [/bold white on green]\n"
            "[bold white on green]  🎲 GOAL: Push all boxes ($) onto docks (.)  [/bold white on green]\n"
            "[bold white on green]                                            [/bold white on green]\n"
            "[bold white on green]          Press H again to close help      [/bold white on green]\n"
            "[bold white on green]                                            [/bold white on green]\n"
        )
    
    def toggle(self):
        self.visible = not self.visible


class BotMenu(Static):
    """Bot selection menu overlay"""
    
    def __init__(self):
        super().__init__()
        self.visible = False
        self.selected_option = 0
        self.algorithms = []
        self._load_algorithms()
        
    def _load_algorithms(self):
        """Load available algorithms from SokobanBot"""
        try:
            from src.algorithms import SokobanBot
            bot = SokobanBot()
            
            self.algorithms = []
            for key, info in bot.algorithms.items():
                self.algorithms.append((key, info['name'], info['description']))
            
            # Add auto and back options
            self.algorithms.append(("auto", "Auto (Best Choice)", "Automatically selects best algorithm"))
            self.algorithms.append(("back", "Back to Game", "Return to the game"))
            
        except Exception as e:
            log.error(f"Failed to load algorithms: {e}")
            # Fallback algorithms
            self.algorithms = [
                ("bfs", "BFS (Optimal Solution)", "Guarantees shortest path"),
                ("astar", "A* (Fast & Smart)", "Heuristic-based solving"),
                ("auto", "Auto (Best Choice)", "Automatically selects best algorithm"),
                ("back", "Back to Game", "Return to the game")
            ]
        
    def render(self) -> Text:
        if not self.visible:
            return Text("")
        
        content = "\n[bold white on magenta]        🤖 AI BOT SOLVER        [/bold white on magenta]\n"
        content += "[bold white on magenta]                                [/bold white on magenta]\n"
        content += "[bold white on magenta]  Choose an algorithm:          [/bold white on magenta]\n"
        content += "[bold white on magenta]                                [/bold white on magenta]\n"
        
        for i, (key, title, desc) in enumerate(self.algorithms):
            if i == self.selected_option:
                content += f"[bold black on white]  {title:<26}  [/bold black on white]\n"
                content += f"[bold white on magenta]  {desc:<26}  [/bold white on magenta]\n"
            else:
                content += f"[bold white on magenta]  {title:<26}  [/bold white on magenta]\n"
                content += f"[bold white on magenta]  {desc:<26}  [/bold white on magenta]\n"
            content += "[bold white on magenta]                                [/bold white on magenta]\n"
        
        content += "[bold white on magenta]  ↑↓ Navigate  Enter - Select    [/bold white on magenta]\n"
        content += "[bold white on magenta]                                [/bold white on magenta]\n"
            
        return Text.from_markup(content)
    
    def toggle(self):
        self.visible = not self.visible
        if self.visible:
            self.selected_option = 0
            
    def move_up(self):
        if self.selected_option > 0:
            self.selected_option -= 1
        else:
            self.selected_option = len(self.algorithms) - 1
            
    def move_down(self):
        if self.selected_option < len(self.algorithms) - 1:
            self.selected_option += 1
        else:
            self.selected_option = 0
            
    def get_selected_action(self):
        return self.algorithms[self.selected_option][0]
    
    def get_selected_algorithm_name(self):
        return self.algorithms[self.selected_option][1]


class PauseMenu(Static):
    """Pause menu overlay"""
    
    def __init__(self):
        super().__init__()
        self.visible = False
        self.selected_option = 0
        self.options = [
            ("p", "Resume Game", "Continue playing"),
            ("n", "Next Level", "Load next level"),
            ("r", "Reset Level", "Restart current level"),
            ("l", "Level Selection", "Choose a specific level"),
            ("b", "Bot Menu", "AI solver options"),
            ("h", "Help & Controls", "Show game help"),
            ("q", "Quit Game", "Exit the game")
        ]
        
    def render(self) -> Text:
        if not self.visible:
            return Text("")
        
        content = "\n[bold white on blue]        PAUSED        [/bold white on blue]\n"
        content += "[bold white on blue]                      [/bold white on blue]\n"
        
        for i, (key, title, desc) in enumerate(self.options):
            if i == self.selected_option:
                content += f"[bold black on white]  {key.upper()} - {title:<15}  [/bold black on white]\n"
            else:
                content += f"[bold white on blue]  {key.upper()} - {title:<15}  [/bold white on blue]\n"
        
        content += "[bold white on blue]                      [/bold white on blue]\n"
        content += "[bold white on blue]  ↑↓ Navigate  Enter - Select  [/bold white on blue]\n"
        content += "[bold white on blue]                      [/bold white on blue]\n"
            
        return Text.from_markup(content)
    
    def toggle(self):
        self.visible = not self.visible
        if self.visible:
            self.selected_option = 0
            
    def move_up(self):
        if self.selected_option > 0:
            self.selected_option -= 1
        else:
            self.selected_option = len(self.options) - 1
            
    def move_down(self):
        if self.selected_option < len(self.options) - 1:
            self.selected_option += 1
        else:
            self.selected_option = 0
            
    def get_selected_action(self):
        return self.options[self.selected_option][0]


class LevelMenu(Static):
    """Level selection menu overlay"""
    
    def __init__(self):
        super().__init__()
        self.visible = False
        self.current_page = 1
        self.levels_per_page = 10
        self.selected_level = 0  # 0-based index within current page
        
    def render(self) -> Text:
        if not self.visible:
            return Text("")
        
        total_levels = get_level_count()
        if total_levels == 0:
            return Text.from_markup(
                "\n[bold white on red]        LEVEL SELECTION        [/bold white on red]\n"
                "[bold white on red]                               [/bold white on red]\n"
                "[bold white on red]  No levels available!        [/bold white on red]\n"
                "[bold white on red]                               [/bold white on red]\n"
                "[bold white on red]  L - Back to Game             [/bold white on red]\n"
                "[bold white on red]                               [/bold white on red]\n"
            )
        
        max_pages = (total_levels + self.levels_per_page - 1) // self.levels_per_page
        levels = list_available_levels(self.current_page, self.levels_per_page)
        
        header = f"[bold white on cyan]        LEVEL SELECTION (Page {self.current_page}/{max_pages})        [/bold white on cyan]\n"
        header += f"[bold white on cyan]        Total Levels: {total_levels}                    [/bold white on cyan]\n"
        header += "[bold white on cyan]                                                [/bold white on cyan]\n"
        
        content = ""
        start_num = (self.current_page - 1) * self.levels_per_page + 1
        for i, level_info in enumerate(levels):
            level_num = start_num + i
            if i == self.selected_level:
                content += f"[bold black on white]  {level_num:2d} - {level_info:<40}  [/bold black on white]\n"
            else:
                content += f"[bold white on cyan]  {level_num:2d} - {level_info:<40}  [/bold white on cyan]\n"
        
        # Pad with empty lines if needed
        while len(levels) < self.levels_per_page:
            content += "[bold white on cyan]                                                [/bold white on cyan]\n"
            levels.append("")
        
        footer = "[bold white on cyan]                                                [/bold white on cyan]\n"
        footer += "[bold white on cyan]  ↑↓ Navigate  Enter - Select Level          [/bold white on cyan]\n"
        footer += "[bold white on cyan]  ← Prev Page  → Next Page  L - Back        [/bold white on cyan]\n"
        footer += "[bold white on cyan]                                                [/bold white on cyan]\n"
        
        return Text.from_markup("\n" + header + content + footer)
    
    def toggle(self):
        self.visible = not self.visible
        if self.visible:
            self.selected_level = 0
        
    def move_up(self):
        if self.selected_level > 0:
            self.selected_level -= 1
        else:
            # Go to previous page and select last level
            if self.prev_page():
                total_levels = get_level_count()
                levels_on_page = min(self.levels_per_page, total_levels - (self.current_page - 1) * self.levels_per_page)
                self.selected_level = levels_on_page - 1
            
    def move_down(self):
        total_levels = get_level_count()
        levels_on_page = min(self.levels_per_page, total_levels - (self.current_page - 1) * self.levels_per_page)
        
        if self.selected_level < levels_on_page - 1:
            self.selected_level += 1
        else:
            # Go to next page and select first level
            if self.next_page():
                self.selected_level = 0
        
    def next_page(self):
        total_levels = get_level_count()
        max_pages = (total_levels + self.levels_per_page - 1) // self.levels_per_page
        if self.current_page < max_pages:
            self.current_page += 1
            return True
        else: 
            self.current_page = 1
            return True
    
    def prev_page(self):
        total_levels = get_level_count()
        max_pages = (total_levels + self.levels_per_page - 1) // self.levels_per_page
        if self.current_page > 1:
            self.current_page -= 1
            return True
        else:
            self.current_page = max_pages
            return True
            
    def get_selected_level_number(self):
        """Get the actual level number (1-based) of the selected level"""
        return (self.current_page - 1) * self.levels_per_page + self.selected_level + 1


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
        height: 10;
        text-align: center;
        layer: overlay;
    }
    
    .help-menu {
        dock: top;
        height: 18;
        text-align: center;
        layer: overlay;
    }
    
    .bot-menu {
        dock: top;
        height: 16;
        text-align: center;
        layer: overlay;
    }
    
    .level-menu {
        dock: top;
        height: 18;
        text-align: center;
        layer: overlay;
    }
    
    .solution-display {
        dock: top;
        height: 12;
        text-align: center;
        layer: overlay;
    }
    
    .countdown-timer {
        dock: top;
        height: 10;
        text-align: center;
        layer: overlay;
    }
    """
    
    BINDINGS = [
        ("w,up", "move_up", "Move up"),
        ("s,down", "move_down", "Move down"),
        ("a,left", "move_left", "Move left"),
        ("d,right", "move_right", "Move right"),
        ("enter", "select", "Select menu item"),
        ("p,space", "pause", "Pause"),
        ("r", "reset", "Reset level"),
        ("n", "new_level", "Next level"),
        ("l", "level_menu", "Level selection"),
        ("b", "bot_menu", "Show bot menu"),
        ("h", "help", "Show help"),
        ("a", "auto_solve", "Auto solve"),
        ("q", "quit", "Quit"),
    ]
    
    def __init__(self):
        super().__init__()
        log.info("🎮 Starting Sokoban game application...")
        self.current_level = 1  # Track current level number
        self.level_data = self.load_level(self.current_level)
        self.game_map_widget = GameMapWidget(self.level_data)
        self.score_bar = ScoreBar(self.game_map_widget)
        self.pause_menu = PauseMenu()
        self.help_menu = HelpMenu()
        self.bot_menu = BotMenu()
        self.level_menu = LevelMenu()
        self.solution_display = SolutionDisplay()
        self.countdown_timer = CountdownTimer()
        self.paused = False
        self.help_shown = False
        self.bot_menu_shown = False
        self.level_menu_shown = False
        self.solution_shown = False
        self.current_solution = None
        self.is_autoplaying = False
        log.success("✅ Sokoban application initialized successfully!")
        
    def load_level(self, level_number: int = 1) -> list[str]:
        """Load a specific level from the collection"""
        log.info(f"� Loading level {level_number}...")
        try:
            from src.levels.level import generate_sokoban_level
            
            # Load the specified level
            level_data = generate_sokoban_level(10, 10, 3, level_number)
            
            if level_data and len(level_data) > 0:
                log.success(f"✅ Level {level_number} loaded successfully ({len(level_data)} lines)")
                return level_data
            else:
                log.warning(f"⚠️ Level {level_number} not found, using fallback level")
                return self.get_default_level()
                
        except Exception as e:
            log.error(f"❌ Level loading error: {e}")
            log.info("🔄 Falling back to default level")
            return self.get_default_level()
    
    def get_default_level(self) -> list[str]:
        """Return a default level if file is not found"""
        log.info("🎮 Loading default level...")
        return [
            "####",
            "#  ###",
            "#    #",
            "# $  #",
            "### ###",
            "#   $ #",
            "#. @..#",
            "#  $  #",
            "###  ##",
            "  ####"
        ]
    
    def compose(self) -> ComposeResult:
        """Compose the UI layout"""
        yield Header()
        yield Container(
            self.help_menu,
            self.bot_menu,
            self.level_menu,
            self.solution_display,
            self.countdown_timer,
            self.pause_menu,
            self.score_bar,
            self.game_map_widget,
            classes="game-container"
        )
        yield Footer()
    
    def action_move_up(self):
        if self.paused:
            self.pause_menu.move_up()
            self.refresh_widgets()
        elif self.bot_menu_shown:
            self.bot_menu.move_up()
            self.refresh_widgets()
        elif self.level_menu_shown:
            self.level_menu.move_up()
            self.refresh_widgets()
        elif not self.help_shown:
            self.move_player('up')
    
    def action_move_down(self):
        if self.paused:
            self.pause_menu.move_down()
            self.refresh_widgets()
        elif self.bot_menu_shown:
            self.bot_menu.move_down()
            self.refresh_widgets()
        elif self.level_menu_shown:
            self.level_menu.move_down()
            self.refresh_widgets()
        elif not self.help_shown:
            self.move_player('down')
    
    def action_move_left(self):
        if self.level_menu_shown:
            self.level_menu.prev_page()
            self.refresh_widgets()
        elif not self.paused and not self.help_shown and not self.bot_menu_shown:
            self.move_player('left')
    
    def action_move_right(self):
        if self.level_menu_shown:
            self.level_menu.next_page()
            self.refresh_widgets()
        elif not self.paused and not self.help_shown and not self.bot_menu_shown:
            self.move_player('right')
    
    def action_select(self):
        """Handle Enter key to select menu items"""
        if self.solution_shown:
            # Enter skips solution display
            self.solution_shown = False
            self.solution_display.hide()
            self.refresh_widgets()
        elif self.paused:
            action = self.pause_menu.get_selected_action()
            self._execute_menu_action(action)
        elif self.bot_menu_shown:
            action = self.bot_menu.get_selected_action()
            self._execute_menu_action(action)
        elif self.level_menu_shown:
            level_number = self.level_menu.get_selected_level_number()
            self.load_specific_level(level_number)
    
    def _execute_menu_action(self, action):
        """Execute the action selected from a menu"""
        if action == "p":
            self.action_pause()
        elif action == "n":
            self.action_new_level()
        elif action == "r":
            self.action_reset()
        elif action == "l":
            self.action_level_menu()
        elif action == "b" or action == "back":
            self.action_bot_menu()
        elif action == "h":
            self.action_help()
        elif action == "q":
            self.exit()
        elif action == "auto":
            self.action_auto_solve()
        elif action in ["bfs", "astar"]:
            self.action_solve_algorithm(action)
        else:
            # Try to handle it as an algorithm action
            self.action_solve_algorithm(action)
    
    def action_pause(self):
        if self.solution_shown:
            # Space triggers autoplay when solution is shown
            self.run_worker(self.autoplay_solution())
        elif self.help_shown:
            self.help_shown = False
            self.help_menu.toggle()
        elif self.bot_menu_shown:
            self.bot_menu_shown = False
            self.bot_menu.toggle()
        elif self.level_menu_shown:
            self.level_menu_shown = False
            self.level_menu.toggle()
        else:
            self.paused = not self.paused
            self.pause_menu.toggle()
        self.refresh_widgets()
    
    def action_help(self):
        if self.bot_menu_shown:
            self.bot_menu_shown = False
            self.bot_menu.toggle()
        elif self.level_menu_shown:
            self.level_menu_shown = False
            self.level_menu.toggle()
        
        self.help_shown = not self.help_shown
        self.help_menu.toggle()
        self.refresh_widgets()
    
    def action_bot_menu(self):
        if self.help_shown:
            self.help_shown = False
            self.help_menu.toggle()
        elif self.level_menu_shown:
            self.level_menu_shown = False
            self.level_menu.toggle()
        
        if self.paused:
            self.paused = False
            self.pause_menu.toggle()
            
        self.bot_menu_shown = not self.bot_menu_shown
        self.bot_menu.toggle()
        self.refresh_widgets()
    
    def action_level_menu(self):
        """Show/hide level selection menu"""
        if self.help_shown:
            self.help_shown = False
            self.help_menu.toggle()
        elif self.bot_menu_shown:
            self.bot_menu_shown = False
            self.bot_menu.toggle()
        
        if self.paused:
            self.paused = False
            self.pause_menu.toggle()
            
        self.level_menu_shown = not self.level_menu_shown
        self.level_menu.toggle()
        self.refresh_widgets()
    
    def action_reset(self):
        self.game_map_widget.reset_level()
        self.score_bar.set_bot_status("")  # Clear bot status
        self.refresh_widgets()
    
    def action_new_level(self):
        """Load the next level in sequence"""
        try:
            # Move to next level
            total_levels = get_level_count()
            if total_levels > 0:
                self.current_level = (self.current_level % total_levels) + 1
                log.info(f"🎮 Moving to level {self.current_level}")
                
                # Load new level
                new_level_data = self.load_level(self.current_level)
                
                # Get the container and replace the game widget
                container = self.query_one(".game-container")
                
                # Remove old widget
                old_widget = self.game_map_widget
                container.remove_children([old_widget])
                
                # Create new widget
                self.game_map_widget = GameMapWidget(new_level_data)
                self.score_bar.game_map_widget = self.game_map_widget
                
                # Add new widget
                container.mount(self.game_map_widget)
                
                log.success(f"✅ Level {self.current_level} loaded successfully!")
                self.refresh_widgets()
            else:
                log.warning("⚠️ No levels available")
                
        except Exception as e:
            log.error(f"❌ Error loading next level: {e}")
            
    def load_specific_level(self, level_number: int):
        """Load a specific level by number"""
        try:
            total_levels = get_level_count()
            if 1 <= level_number <= total_levels:
                self.current_level = level_number
                log.info(f"🎮 Loading level {level_number}")
                
                # Load new level
                new_level_data = self.load_level(level_number)
                
                # Get the container and replace the game widget
                container = self.query_one(".game-container")
                
                # Remove old widget
                old_widget = self.game_map_widget
                container.remove_children([old_widget])
                
                # Create new widget
                self.game_map_widget = GameMapWidget(new_level_data)
                self.score_bar.game_map_widget = self.game_map_widget
                
                # Add new widget
                container.mount(self.game_map_widget)
                
                # Close level menu
                if self.level_menu_shown:
                    self.level_menu_shown = False
                    self.level_menu.toggle()
                
                log.success(f"✅ Level {level_number} loaded successfully!")
                self.refresh_widgets()
            else:
                log.warning(f"⚠️ Level {level_number} not available (1-{total_levels})")
                
        except Exception as e:
            log.error(f"❌ Error loading level {level_number}: {e}")
    
    def move_player(self, direction: str):
        """Handle player movement and game state updates"""
        if self.game_map_widget.move_player(direction):
            self.refresh_widgets()
            moves = self.game_map_widget.get_moves()
            pushes = self.game_map_widget.get_pushes()
            log.debug(f"Game state updated - Moves: {moves}, Pushes: {pushes}")
            
            if self.game_map_widget.is_level_complete():
                log.success(f"🎉 Level completed in {moves} moves and {pushes} pushes!")
                self.notify("🎉 Level Complete! Congratulations!", severity="information")
    
    async def autoplay_solution(self):
        """Automatically play the found solution with animation"""
        if not self.current_solution or not self.current_solution.get('moves'):
            return
        
        self.is_autoplaying = True
        self.solution_shown = False
        self.solution_display.hide()
        
        moves = self.current_solution['moves']
        total_moves = len(moves)
        
        try:
            for i, move in enumerate(moves):
                if not self.is_autoplaying:  # Allow cancellation
                    break
                
                # Update status
                self.score_bar.set_bot_status(f"⏵ Autoplay: {i+1}/{total_moves}")
                self.refresh_widgets()
                
                # Execute move
                if not self.game_map_widget.move_player(move):
                    log.warning(f"Failed to execute move: {move}")
                    break
                
                # Delay for animation
                await asyncio.sleep(0.3)
            
            # Clear status
            self.score_bar.set_bot_status("")
            self.is_autoplaying = False
            self.refresh_widgets()
            
        except Exception as e:
            log.error(f"Autoplay error: {e}")
            self.is_autoplaying = False
            self.score_bar.set_bot_status("❌ Autoplay error")
            self.refresh_widgets()
    
    def action_auto_solve(self):
        """Auto solve using the best algorithm for the puzzle"""
        self._close_all_menus()
        self.run_worker(self._async_auto_solve(), exclusive=True)
    
    async def _async_auto_solve(self):
        """Async auto solve with countdown timer"""
        try:
            log.info("🤖 Starting auto-solve...")
            self.score_bar.set_bot_status("🤖 Auto-solving...")
            
            # Get time limit from bot configuration
            bot_info = self.game_map_widget.bot.get_algorithm_info()
            # Auto-solve will try multiple algorithms, use longest time limit
            time_limit = max(algo['time_limit'] for algo in bot_info.values())
            
            # Start countdown timer with actual time limit
            self.countdown_timer.start(time_limit, "Auto-Solver")
            self.refresh_widgets()
            
            # Run solver in executor to not block UI
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                # Start solver
                future = executor.submit(self.game_map_widget.auto_solve, "auto")
                
                # Update timer while solving
                while not future.done():
                    await asyncio.sleep(0.1)
                    self.countdown_timer.update_time()
                    self.refresh_widgets()
                
                result = future.result()
            
            # Stop countdown timer
            self.countdown_timer.stop()
            
            if result and result.get('success'):
                # Store solution and show display
                self.current_solution = result
                self.solution_shown = True
                self.solution_display.show_solution(result)
                self.score_bar.set_bot_status("✅ Solution found!", result.get('solve_time'))
                self.notify("🎯 Solution found! Press SPACE to autoplay or ENTER to skip", severity="information")
            else:
                self.score_bar.set_bot_status("❌ Auto-solve failed")
                self.notify("❌ Bot couldn't solve this puzzle", severity="error")
                
        except Exception as e:
            log.error(f"Auto-solve error: {e}")
            self.countdown_timer.stop()
            self.score_bar.set_bot_status("❌ Auto-solve error")
            self.notify(f"❌ Auto-solve failed: {e}", severity="error")
        finally:
            self.refresh_widgets()
    
    def action_solve_algorithm(self, algorithm_key):
        """Solve using the specified algorithm"""
        self._close_all_menus()
        self.run_worker(self._async_solve_algorithm(algorithm_key), exclusive=True)
    
    async def _async_solve_algorithm(self, algorithm_key):
        """Async solve with specific algorithm and countdown timer"""
        # Map algorithm keys to names and icons
        algorithm_info = {
            "bfs": {"name": "BFS", "display": "Breadth-First Search", "icon": "🔍", "emoji": "🎯"},
            "astar": {"name": "A*", "display": "A* Search", "icon": "🎯", "emoji": "🎯"},
        }
        
        if algorithm_key not in algorithm_info:
            log.error(f"Unknown algorithm: {algorithm_key}")
            self.notify(f"❌ Unknown algorithm: {algorithm_key}", severity="error")
            return
            
        info = algorithm_info[algorithm_key]
        
        try:
            log.info(f"🤖 Starting {info['display']} solver...")
            self.score_bar.set_bot_status(f"{info['icon']} {info['name']} solving...")
            
            # Get time limit from bot configuration for this specific algorithm
            bot_algo_info = self.game_map_widget.bot.get_algorithm_info(algorithm_key)
            time_limit = bot_algo_info.get('time_limit', 60.0)
            
            # Start countdown timer with algorithm's actual time limit
            self.countdown_timer.start(time_limit, info['display'])
            self.refresh_widgets()
            
            # Run solver in executor to not block UI
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                # Start solver
                future = executor.submit(self.game_map_widget.auto_solve, algorithm_key)
                
                # Update timer while solving
                while not future.done():
                    await asyncio.sleep(0.1)
                    self.countdown_timer.update_time()
                    self.refresh_widgets()
                
                result = future.result()
            
            # Stop countdown timer
            self.countdown_timer.stop()
            
            if result and result.get('success'):
                # Store solution and show display
                self.current_solution = result
                self.solution_shown = True
                self.solution_display.show_solution(result)
                self.score_bar.set_bot_status(f"✅ {info['name']} solved!", result.get('solve_time'))
                self.notify(f"{info['emoji']} Solution found! Press SPACE to autoplay or ENTER to skip", severity="information")
            else:
                self.score_bar.set_bot_status(f"❌ {info['name']} failed")
                self.notify(f"❌ {info['display']} couldn't solve this puzzle", severity="error")
                
        except Exception as e:
            log.error(f"{info['display']} solve error: {e}")
            self.countdown_timer.stop()
            self.score_bar.set_bot_status(f"❌ {info['name']} error")
            self.notify(f"❌ {info['display']} solve failed: {e}", severity="error")
        finally:
            self.refresh_widgets()

    def _close_all_menus(self):
        """Close all open menus"""
        if self.paused:
            self.paused = False
            self.pause_menu.toggle()
        if self.help_shown:
            self.help_shown = False
            self.help_menu.toggle()
        if self.bot_menu_shown:
            self.bot_menu_shown = False
            self.bot_menu.toggle()
        if self.level_menu_shown:
            self.level_menu_shown = False
            self.level_menu.toggle()
        if self.solution_shown:
            self.solution_shown = False
            self.solution_display.hide()
    
    def on_key(self, event):
        """Handle key events for level selection"""
        # Only process numeric keys when level menu is shown
        if self.level_menu_shown and event.key.isdigit():
            self._handle_level_number_input(event.key)
            event.prevent_default()
    
    def _handle_level_number_input(self, key):
        """Handle numeric key input for level selection"""
        if not hasattr(self, '_level_input_buffer'):
            self._level_input_buffer = ""
            
        self._level_input_buffer += key
        
        # Try to parse as level number
        try:
            level_number = int(self._level_input_buffer)
            total_levels = get_level_count()
            
            # If it's a valid single digit level, load it immediately
            if 1 <= level_number <= min(9, total_levels):
                self.load_specific_level(level_number)
                self._level_input_buffer = ""
            # If it's a two-digit number and valid, load it
            elif len(self._level_input_buffer) >= 2 and 1 <= level_number <= total_levels:
                self.load_specific_level(level_number)
                self._level_input_buffer = ""
            # If buffer is getting too long or invalid, reset
            elif len(self._level_input_buffer) >= 3 or level_number > total_levels:
                self._level_input_buffer = ""
                
        except ValueError:
            self._level_input_buffer = ""
    
    def refresh_widgets(self):
        """Refresh all widgets"""
        self.game_map_widget.refresh()
        self.score_bar.refresh()
        self.pause_menu.refresh()
        self.help_menu.refresh()
        self.bot_menu.refresh()
        self.level_menu.refresh()
        self.solution_display.refresh()
        self.countdown_timer.refresh()


if __name__ == "__main__":
    app = SukobanApp()
    app.run()