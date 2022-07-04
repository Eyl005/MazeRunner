import json
import os
import sys
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

from a3_support import AbstractGrid
from a2_solution import *
from constants import GAME_FILE, TASK
from math import *
from typing import *

# Name, student number and email address.
__author__ = "<Yanran Li>, <s4722469>"
__email__ = "<yanran.li1@uqconnect.edu.au>"


# Write your classes here
class Candy(Food):
    """ Candy decreases the players hunger. """
    _id = CANDY

    def apply(self, player: 'Player') -> None:
        """ Changes player's hunger to 0; Decrease player's health 2. """
        player._hunger = 0
        player.change_health(-2)


class LevelView(AbstractGrid):
    """The view of level in the game."""

    def __init__(self, master: Union[tk.Tk, tk.Frame],
                 dimensions: tuple[int, int], size: tuple[int, int], **kwargs):
        """
        Set up the level.

        Parameters:
            master: The master frame for this Canvas.
            dimensions: (#rows, #columns)
            size: (width in pixels, height in pixels)
        """
        super().__init__(master, dimensions, size, **kwargs)

    def _draw_level(self, tiles: list[list[Tile]]) -> None:
        """
        Draw the tiles in the level.

        Parameters:
            tiles: The tiles in this level.
        """
        row_num, col_num = self._dimensions
        for row in range(row_num):
            for column in range(col_num):
                x_min, y_min, x_max, y_max = self.get_bbox((row, column))
                tile = tiles[row][column].get_id()
                self.create_rectangle(x_min, y_min, x_max, y_max,
                                      fill=TILE_COLOURS[tile])

    def _draw_items(self, items: dict[tuple[int, int], Item]) -> None:
        """
        Draw the items in the level.

        Parameters:
            items: Maps locations to the items currently at those locations.
        """
        for position, item in items.items():
            x_min, y_min, x_max, y_max = self.get_bbox(position)
            item = item.get_id()
            self.create_oval(x_min, y_min, x_max, y_max,
                             fill=ENTITY_COLOURS[item])
            self.annotate_position(position, item)

    def _draw_player(self, player_pos: tuple[int, int]) -> None:
        """
        Draw the player in the level.

        Parameters:
            player_pos: The current position of the player
        """
        x_min, y_min, x_max, y_max = self.get_bbox(player_pos)
        self.create_oval(x_min, y_min, x_max, y_max,
                         fill=ENTITY_COLOURS[PLAYER])
        self.annotate_position(player_pos, PLAYER)

    def draw(self,
             tiles: list[list[Tile]],
             items: dict[tuple[int, int], Item],
             player_pos: tuple[int, int]) -> None:
        """
        Clears and redraws the entire level (maze and entities).

        Parameters:
            tiles: The tiles in this level.
            items: Maps locations to the items currently at those locations.
            player_pos: The current position of the player
        """
        self.clear()

        self._draw_level(tiles)
        self._draw_items(items)
        self._draw_player(player_pos)


class StatsView(AbstractGrid):
    """The view of player's status."""

    def __init__(self, master: Union[tk.Tk, tk.Frame],
                 width: int, **kwargs) -> None:
        """
        Sets up a new StatsView in the master frame with the given width.

        Parameters:
            master: The master frame for this Canvas.
            width: The width of this Canvas.
        """
        super().__init__(master, (2, 4), (width, STATS_HEIGHT), **kwargs)
        self.config(background=THEME_COLOUR)

    def draw_stats(self, player_stats: tuple[int, int, int]) -> None:
        """
        Draws the player’s stats (hp, hunger, thirst).

        Parameters:
            player_stats: hp, hunger, thirst.
        """
        HP, Hunger, Thirst = player_stats
        self.annotate_position((0, 0), 'HP')
        self.annotate_position((1, 0), str(HP))
        self.annotate_position((0, 1), 'Hunger')
        self.annotate_position((1, 1), str(Hunger))
        self.annotate_position((0, 2), 'Thirst')
        self.annotate_position((1, 2), str(Thirst))

    def draw_coins(self, num_coins: int) -> None:
        """
        Draws the number of coins.

        Parameters:
            num_coins: the number of coins.
        """
        self.annotate_position((0, 3), 'Coins')
        self.annotate_position((1, 3), str(num_coins))


class InventoryView(tk.Frame):
    """The view of inventory."""

    def __init__(self, master: Union[tk.Tk, tk.Frame], **kwargs) -> None:
        """
        Creates a new InventoryView within master.

        Parameters:
            master: The master frame.
        """
        super().__init__(master, **kwargs)
        self._callback = None

    def set_click_callback(self, callback: Callable[[str], None]) -> None:
        """Sets the function to be called when an item is clicked. """
        self._callback = callback

    def clear(self) -> None:
        """Clears all child widgets from this InventoryView"""
        for child in self.winfo_children():
            child.destroy()

    def _draw_item(self, name: str, num: int, colour: str) -> None:
        """
        Creates and binds a single tk.Label in the InventoryView frame.

        Parameters:
            name: the name of the item.
            num: the quantity currently in the users inventory.
            colour: the background colour for this item label.
        """
        item = tk.Label(self, text=name + ': ' + str(num),
                        background=colour, relief='raised')
        item.pack(fill="both", ipady=10)
        if self._callback:
            item.bind('<Button-1>', lambda event: self._callback(name))

    def draw_inventory(self, inventory: Inventory) -> None:
        """
        Draws any non-coin inventory items with their quantities
        and binds the callback for each.

        Parameters:
            inventory: non-coin inventory items.
        """
        tk.Label(self, text='Inventory', font=HEADING_FONT).pack(fill="both")

        for name, items in inventory.get_items().items():
            if name != Coin.__name__:
                self._draw_item(name, len(items),
                                ENTITY_COLOURS[items[0].get_id()])


class ImageLevelView(LevelView):
    """The view of level use image."""

    def __init__(self, master, dimensions, size, **kwargs):
        """
        Set up the level.

        Parameters:
            master: The master frame.
            dimensions: (#rows, #columns)
            size: (width in pixels, height in pixels)
        """
        super().__init__(master, dimensions, size, **kwargs)
        self._photos = {}
        self._size = size

    def _draw_level(self, tiles: list[list[Tile]]) -> None:
        """
        Draw the tiles in the level.

        Parameters:
            tiles: The tiles in this level.
        """
        num_rows, num_cols = self._dimensions

        for row in range(num_rows):
            for column in range(num_cols):
                tile = tiles[row][column].get_id()
                image = Image.open('images/' + TILE_IMAGES[tile])
                image = image.resize(self.get_cell_size())
                photo = ImageTk.PhotoImage(image)
                self._photos[(row, column)] = photo
                self.create_image(self.get_midpoint((row, column)),
                                  image=photo)

    def _draw_items(self, items: dict[tuple[int, int], Item]) -> None:
        """
        Draw the items in the level.

        Parameters:
            items: Maps locations to the items currently at those locations.
        """
        for position, item in items.items():
            item = item.get_id()
            image = Image.open('images/' + ENTITY_IMAGES[item])
            image = image.resize(self.get_cell_size())
            photo = ImageTk.PhotoImage(image)
            self._photos[position + (item,)] = photo
            self.create_image(self.get_midpoint(position), image=photo)

    def _draw_player(self, player_pos: tuple[int, int]) -> None:
        """
        Draw the player in the level.

        Parameters:
            player_pos: The current position of the player
        """
        image = Image.open('images/' + ENTITY_IMAGES[PLAYER])
        image = image.resize(self.get_cell_size())
        photo = ImageTk.PhotoImage(image)
        self._photos[player_pos + (PLAYER,)] = photo
        self.create_image(self.get_midpoint(player_pos), image=photo)

    def clear(self):
        """clear the level."""
        super().clear()
        self._photos = {}


class ShopView(tk.Frame):
    """The view of shop."""

    # Items and value in the shop.
    _shop_items1 = [HONEY, APPLE, WATER]
    _shop_items2 = [POTION, CANDY]
    _value = {APPLE: 1, WATER: 1, HONEY: 2, POTION: 2, CANDY: 3}

    def __init__(self, master: Union[tk.Tk, tk.Frame, tk.Toplevel], buy_item,
                 **kwargs) -> None:
        """
        Set up the view of shop.

        Parameters:
            master: The master frame.
            buy_item: the function to buy the item in the shop.
        """
        super().__init__(master, **kwargs)
        self._buy = buy_item
        self._images = {}

        # Divide the frame into two part.
        tk.Label(master, text="Shop", font=BANNER_FONT,
                 background=THEME_COLOUR).pack(fill="x")
        self._level1 = tk.Frame(master)
        self._level1.pack(side=tk.TOP)
        self._level2 = tk.Frame(master)
        self._level2.pack()

    def draw_shop(self) -> None:
        """Draw the two part of shop."""
        self._draw_shop_item(self._level1, self._shop_items1)
        self._draw_shop_item(self._level2, self._shop_items2)

    def _draw_shop_item(self, master, items) -> None:
        """
        Draw every item in the shop.

        Parameters:
            master: The master frame.
            items: The item in this row.
        """
        for item in items:
            self._draw_item_photo(master, item)

    def _draw_item_photo(self, master, item) -> None:
        """
        Draw and bind the item in the frame.

        Parameters:
            master: The master frame.
            item: the item which need to be drawn.
        """
        photo_cell = (120, 120)
        image = Image.open('images/' + ENTITY_IMAGES[item])
        image = image.resize(photo_cell)
        photo = ImageTk.PhotoImage(image)
        self._images[item] = photo

        value = self._value[item]

        item_photo = tk.Label(master, text=str(value) + '$', image=photo,
                              relief='raised', compound=tk.TOP)
        if master == self._level2:
            item_photo.pack(fill="both", side=tk.LEFT, padx=20)
        else:
            item_photo.pack(fill="both", side=tk.LEFT)

        # Bind label to buy function.
        item_photo.bind('<Button-1>', lambda e: self._buy(item, value))


class MenuBar(tk.Menu):
    """The view of menu bar."""

    def __init__(self, master,
                 restart_game,
                 save_game,
                 load_game,
                 quit):
        """
        Set up the view of menu.

        Parameters:
            master: The master frame.
            restart_game: The function to restart function.
            save_game: The function to save game.
            load_game: The function to load game.
            quit: The function to quit the window.
        """
        super().__init__(master)
        fileMenu = tk.Menu(self, tearoff=False)
        self.add_cascade(label='File', menu=fileMenu)
        fileMenu.add_command(label='Save game', command=save_game)
        fileMenu.add_command(label='Load game', command=load_game)
        fileMenu.add_command(label='Restart game', command=restart_game)
        fileMenu.add_separator()
        fileMenu.add_command(label='Quit', command=quit)


class ControlsFrame(tk.Frame):
    """The view of control game."""

    def __init__(self, master: Union[tk.Tk, tk.Frame],
                 new_game, re_start, shop, **kwargs) -> None:
        """
        Set up the view of control frame.

        Parameters:
            master: The master frame.
            new_game: The function to start a new game.
            re_start: The function to restart game.
            shop: The function to set up the shop.
        """
        super().__init__(master, **kwargs)
        self.master = master

        if TASK == 3:
            shopGame = tk.Button(self, text='Shop',
                                 command=shop)
            shopGame.pack(side='left', padx=65, expand=True)

        # Set the button.
        new_game = tk.Button(self, text='New game', command=new_game)
        new_game.pack(side='left', padx=65, expand=True)

        Restart_game = tk.Button(self, text='Restart game', command=re_start)
        Restart_game.pack(side='left', padx=65, expand=True)

        Frame_timer = tk.Frame(self)
        Frame_timer.pack(side='left', padx=65, expand=True)
        tk.Label(Frame_timer, text='Timer').pack()
        self.time_label = tk.Label(Frame_timer, text='0m 0s')
        self.time_label.pack()


class GraphicalInterface(UserInterface):
    """A MazeRunner interface that uses ascii to present information."""

    def __init__(self, master: tk.Tk) -> None:
        """
        Creates a new GraphicalInterface with master frame master.

        Parameters:
            master: The master frame for root.
        """
        self.frame = None
        self.control_view = None
        self.status_view = None
        self.inventory_view = None
        self.menubar = None
        self.level_view = None
        self.master = master

        self.master.title('MazeRunner')
        tk.Label(self.master, text="MazeRunner",
                 font=BANNER_FONT,
                 background=THEME_COLOUR).pack(fill="both")
        self.frame = tk.Frame(self.master)
        self.frame.pack(fill="both")

    def create_interface(self, dimensions: tuple[int, int]) -> None:
        """
        Creates the components in the master frame for this interface.

        Parameters:
            dimensions:  (row, column)
        """
        self.level_view = LevelView(self.frame, dimensions,
                                    (MAZE_WIDTH, MAZE_HEIGHT))
        self.level_view.pack(side=tk.LEFT)

        self.inventory_view = InventoryView(self.frame)
        self.inventory_view.pack(fill="both", expand=True)

        self.status_view = StatsView(self.master, MAZE_WIDTH + INVENTORY_WIDTH)
        self.status_view.pack()

    def advanced_create_interface(self, dimensions: tuple[int, int],
                                  restart_game, new_game, save_game,
                                  load_game, shop, quit) -> None:
        """
        Creates the components in the master frame for this interface.

        Parameters:
            dimensions:  (row, column)
            restart_game: restart function
            new_game: new game function
            save_game: save game function
            load_game: load game function
            shop: shop function
            quit: The function to quit the window.
        """
        self.level_view = ImageLevelView(self.frame, dimensions,
                                         (MAZE_WIDTH, MAZE_HEIGHT))
        self.menubar = MenuBar(self.master, restart_game,
                               save_game, load_game, quit)
        self.master.config(menu=self.menubar)
        self.level_view.pack(side=tk.LEFT)

        self.inventory_view = InventoryView(self.frame)
        self.inventory_view.pack(fill="both", expand=True)

        self.status_view = StatsView(self.master, MAZE_WIDTH + INVENTORY_WIDTH)
        self.status_view.pack()

        self.control_view = ControlsFrame(self.master, new_game,
                                          restart_game, shop)
        self.control_view.pack(expand=True)

    def clear_all(self) -> None:
        """Clears each of the three major components."""
        self.level_view.clear()
        self.inventory_view.clear()
        self.status_view.clear()

    def set_maze_dimensions(self, dimensions: tuple[int, int]) -> None:
        """Updates the dimensions of the maze in the level to dimensions."""
        self.level_view.set_dimensions(dimensions)

    def bind_keypress(self, command: Callable[[tk.Event], None]) -> None:
        """Binds the given command to the general keypress event."""
        self.master.bind('<Key>', command)

    def set_inventory_callback(self, callback: Callable[[str], None]) -> None:
        """Sets the function to be called when an item is clicked
        in the inventory view to be callback."""
        self.inventory_view.set_click_callback(callback)

    def draw_inventory(self, inventory: Inventory) -> None:
        """Draws any non-coin inventory items with their quantities
        and binds the callback for each"""
        self.inventory_view.draw_inventory(inventory)

    def draw(self, maze: Maze, items: dict[tuple[int, int], Item],
             player_position: tuple[int, int],
             inventory: Inventory,
             player_stats: tuple[int, int, int]) -> None:
        """
        The draw method as per the docstring.

        Parameters:
            maze: The current maze for the level
            items: Maps locations to the items currently at those locations.
            player_position: The current position of the player
            inventory: The current inventory of the player
            player_stats: The current stats of the player
        """
        self.clear_all()

        self._draw_level(maze, items, player_position)
        self._draw_inventory(inventory)
        self._draw_player_stats(player_stats)

    def _draw_inventory(self, inventory: Inventory) -> None:
        """Implement the draw inventory method"""
        self.draw_inventory(inventory)
        self.status_view.draw_coins(len(inventory.get_items().
                                        get(Coin.__name__, [])))

    def _draw_level(self, maze: Maze, items: dict[tuple[int, int], Item],
                    player_position: tuple[int, int]) -> None:
        """Implement the draw level method"""
        self.level_view.draw(maze.get_tiles(), items, player_position)

    def _draw_player_stats(self, player_stats: tuple[int, int, int]) -> None:
        """Implement the draw player stats method"""
        self.status_view.draw_stats(player_stats)


class GraphicalMazeRunner(MazeRunner):
    def __init__(self, game_file: str, root: tk.Tk) -> None:
        """
        Creates a new GraphicalMazeRunner game.

        Parameters:
            game_file: The game_file of games.
            root: root of frame.
        """
        self.root = root
        self.game_file = game_file
        self._model = Model(game_file)
        self.gui = GraphicalInterface(self.root)

    def _handle_keypress(self, event: tk.Event) -> None:
        """
        Handles a keypress.

        Parameters:
            event: event.
        """
        if not self._model.has_won():
            if event.char in MOVE_DELTAS:
                self._model.move_player(MOVE_DELTAS.get(event.char))

            if self._model.did_level_up():
                self.gui.set_maze_dimensions(
                    self._model.get_level().get_dimensions())

        if self._model.has_won():
            messagebox.showinfo("WIN", WIN_MESSAGE)
        elif self._model.has_lost():
            messagebox.showinfo("LOSS", LOSS_MESSAGE)
        else:
            self._draw()

    def _draw(self):
        """draw the gui."""
        level = self._model.get_level()
        items = level.get_items()
        self.player = self._model.get_player()
        self.inventory = self.player.get_inventory()

        self.gui.draw(level.get_maze(),
                      items,
                      self.player.get_position(),
                      self.inventory,
                      self._model.get_player_stats())

    def _apply_item(self, item_name: str) -> None:
        """
        Attempts to apply an item with the given name to the player.

        Parameters:
            item_name: The item name.
        """
        item = self._model.get_player().get_inventory().remove_item(item_name)
        if item is not None:
            item.apply(self._model.get_player())
            self._draw()

    def play(self) -> None:
        """ Called to cause gameplay to occur."""
        self.gui.bind_keypress(self._handle_keypress)
        self.gui.create_interface(self._model.
                                  get_current_maze().get_dimensions(), )
        self.gui.set_inventory_callback(self._apply_item)

        self._draw()


class AdvancedGraphicalMazeRunner(GraphicalMazeRunner):
    """ Controller class for a game of MazeRunner """
    ENTITIES = {
        COIN: Coin,
        POTION: Potion,
        APPLE: Apple,
        HONEY: Honey,
        WATER: Water,
        CANDY: Candy,
    }

    def __init__(self, game_file: str, root: tk.Tk):

        super().__init__(game_file, root)
        self.timer = 0
        self.root.after(1000, self._time_count)

    def _time_count(self):
        """Count the time"""
        self.timer += 1
        self.root.after(1000, self._time_count)
        self.gui.control_view.time_label.config(text=f'{self.timer // 60}m '
                                                     f'{self.timer % 60}s')

    def _quit(self):
        """Quit function to exit the game."""
        answer = messagebox.askokcancel('Reminder', 'Are sure to quit?')
        if answer:
            sys.exit(0)

    def _restart(self):
        """Restart the game."""
        self._model = Model(self.game_file)
        control = self.gui.control_view
        self.timer = 0
        control.time_label.config(text=f'{self.timer // 60}m '
                                       f'{self.timer % 60}s')
        self.gui.set_maze_dimensions(
            self._model.get_current_maze().get_dimensions())
        self._draw()

    def _new_game(self):
        """Start a new game."""
        self.window = tk.Toplevel(self.root)
        tk.Label(self.window, text="Enter your game file").pack()
        self.input = tk.Entry(self.window)
        self.input.pack()
        tk.Button(self.window, text="Submit", command=self._submit).pack()

    def _submit(self):
        """The button event to submit the game file in new_game"""
        try:
            self.game_file = self.input.get()
            self._model = Model(self.game_file)
            self.window.destroy()

            self.timer = 0
            self.gui.set_maze_dimensions(
                self._model.get_current_maze().get_dimensions())
            self._draw()
        except:
            messagebox.showerror(title="Warning", message="Wrong input")
            self.window.destroy()

    def _save_game(self):
        """Save the game in a txt document."""
        level_items = self._model.get_level().get_items()
        Hp, Hunger, Thirst = self._model.get_player_stats()
        inventory = self._model.get_player_inventory().get_items()
        row, column = self._model.get_player().get_position()

        with open('save.txt', 'w') as f:
            f.write(f'Game File: {self.game_file}\n')
            f.write(f'Level_num: {self._model._level_num}\n')
            f.write(f'Level_items: {level_items}\n')
            f.write(f'Player_move: {self._model._num_moves}\n')
            f.write(f'Hp: {Hp}\n')
            f.write(f'Hunger: {Hunger}\n')
            f.write(f'Thirst: {Thirst}\n')
            f.write(f'Inventory: {inventory}\n')
            f.write(f'Row: {row}\n')
            f.write(f'Column: {column}\n')
            f.write(f'Time: {self.timer}')

        messagebox.showinfo(title="Save information",
                            message="It's saved in 'save.txt'")

    def _load_game(self):
        """Load the game from document."""
        messagebox.showinfo(title="Load information",
                            message="It's saved in 'save.txt'")

        with open('save.txt', 'r') as file:
            for line in file:
                line = line.strip()
                if line.startswith('Game File'):
                    self.game_file = line[11:]
                    self._model = Model(self.game_file)
                elif line.startswith('Level_num'):
                    self._model._level_num = int(line[10:])
                elif line.startswith('Level_items'):
                    self._model.get_level()._items = eval(line[13:])
                elif line.startswith('Player_move'):
                    self._model._num_moves = int(line[13:])
                elif line.startswith('Hp'):
                    self._model.get_player()._health = int(line[4:])
                elif line.startswith('Hunger'):
                    self._model.get_player()._hunger = int(line[8:])
                elif line.startswith('Thirst'):
                    self._model.get_player()._thirst = int(line[8:])
                elif line.startswith('Row'):
                    row = int(line[5:])
                elif line.startswith('Column'):
                    column = int(line[8:])
                elif line.startswith('Inventory'):
                    self._model.get_player_inventory()._items = eval(line[11:])
                elif line.startswith('Time'):
                    self.timer = int(line[6:])

            # Set the status of game.
            self._model.get_player().set_position((row, column))
            self.gui.set_maze_dimensions(
                self._model.get_current_maze().get_dimensions())
            self._draw()

    def _shop(self):
        """Buy the items from the shop."""
        self.window = tk.Toplevel(self.root)
        self.shop_view = ShopView(self.window, self._buy_item)
        self.shop_view.draw_shop()
        self.shop_view.pack()

        done = tk.Button(self.window, text="Done", command=self.window.destroy)
        done.pack()

    def _buy_item(self, item, value):
        """Specify buy function, compare the coin and item."""
        position = (0, 0)
        coin_num = len(self.inventory.get_items().get(Coin.__name__, []))

        if coin_num >= value:
            for times in range(value):
                self._model.get_player().get_inventory().remove_item('Coin')
            item_new = self.ENTITIES.get(item)(position)
            self._model.get_player().add_item(item_new)
        else:
            messagebox.showinfo("Error", "You don't have enough coins.")

        self._draw()

    def play(self) -> None:
        """ Called to cause gameplay to occur."""
        self.gui.bind_keypress(self._handle_keypress)
        self.gui.advanced_create_interface(self._model.
                                           get_current_maze().get_dimensions(),
                                           self._restart,
                                           self._new_game,
                                           self._save_game,
                                           self._load_game,
                                           self._shop,
                                           self._quit)
        self.gui.set_inventory_callback(self._apply_item)

        self._draw()


def play_game(root: tk.Tk):
    """Construct the controller instance."""
    if TASK == 1:
        play_game = GraphicalMazeRunner(GAME_FILE, root)
    else:
        play_game = AdvancedGraphicalMazeRunner(GAME_FILE, root)
    play_game.play()
    root.mainloop()


def main():
    """ Entry-point to gameplay """
    root = tk.Tk()
    play_game(root)


if __name__ == '__main__':
    main()
