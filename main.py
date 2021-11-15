# Python
import os
from random import randint

# Third-party
from simple_term_menu import TerminalMenu

DISPLAY_MINES = os.getenv('DISPLAY_MINES', None)

# TODO:
# - Add multiple mines on the random generating
# - Maybe make sure the robot and the exit is not on the same line and row


class Level:
    def __init__(self, selected_level=None, random=False):
        self.random = random
        self.selected_level = selected_level
        self.generated_level = []
        self.amount_of_rows = 0
        self.amount_of_columns = 0
        self.robot_position = []
        self.level_exit = []
    
    def generate_level(self):
        # Use one of the predefined levels
        # A level is always selected, and for random levels we still use that size
        level_file_path = os.path.join('levels', self.selected_level['file_name'])
        with open(level_file_path, 'r') as level_file:
            level = level_file.read().splitlines()
            self.amount_of_rows = len(level)
            self.amount_of_columns = len(level[0])
            if not self.random:
                self.generated_level = level
            else:
                self.generated_level = self.generate_random_level()

    def generate_random_level(self):
        # Generate outer level
        top_and_bottom_row = ['#' for x in range(self.amount_of_columns)]
        middle_row = ['#']
        for column in range(self.amount_of_columns - 2):
            middle_row.append('o')
        middle_row.append('#')
  
        level = []
        for i in range(self.amount_of_rows):
            if i == 0 or i == (self.amount_of_rows - 1):
                level.append(top_and_bottom_row.copy())
            else:
                level.append(middle_row.copy())
        
        # Add Robot [R]
        found_valid_robot_position = False

        while not found_valid_robot_position:
            random_row = randint(0, self.amount_of_rows - 1)
            random_column = randint(0, self.amount_of_columns - 1)
            if level[random_row][random_column] == '#':
                if random_row != 0 and random_row != (self.amount_of_rows - 1):
                    self.robot_position = [random_row, random_column]
                    level[random_row][random_column] = "R"
                    found_valid_robot_position = True
                else:
                    if random_column != 0 and random_column != (self.amount_of_columns - 1):
                        self.robot_position = [random_row, random_column]
                        level[random_row][random_column] = "R"
                        found_valid_robot_position = True
        
        found_valid_exit_position = False

        while not found_valid_exit_position:
            random_row = randint(0, self.amount_of_rows - 1)
            random_column = randint(0, self.amount_of_columns - 1)
            if level[random_row][random_column] == '#':
                if random_row != 0 and random_row != (self.amount_of_rows - 1):
                    found_valid_exit_position = True
                    if level[random_row - 1][random_column] != 'R' and level[random_row + 1][random_column] != 'R':
                        level[random_row][random_column] = "E"
                        found_valid_exit_position = True
                else:
                    if random_column != 0 and random_column != (self.amount_of_columns - 1):
                        if level[random_row][random_column - 1] != 'R' and level[random_row][random_column + 1] != 'R':
                            level[random_row][random_column] = "E"
                            found_valid_exit_position = True

        found_valid_mine_position = False

        while not found_valid_mine_position:
            random_row = randint(0, self.amount_of_rows - 1)
            random_column = randint(0, self.amount_of_columns - 1)
            not_allowed = ['R', 'E']
            if level[random_row][random_column] == 'o':
                if level[random_row][random_column - 1] not in not_allowed and level[random_row][random_column + 1] not in not_allowed:
                    if level[random_row - 1][random_column] not in not_allowed and level[random_row + 1][random_column] not in not_allowed:
                        level[random_row][random_column] = "*"
                        found_valid_mine_position = True

        return level

    def show_generated_level(self):
        print('\n')
        print('-----------------------------------------------------------------------------')
        print(f'You have selected the {self.selected_level["type"]} level. Navigate your way through the following level:')
        self.show_level_example()


    def show_level_example(self):
        level_copy = self.generated_level.copy()
        for index, line in enumerate(level_copy):
            if DISPLAY_MINES:
                level_copy[index] = ''.join([x for x in line])
            else:
                level_copy[index] = ''.join([x if x != '*' else 'o' for x in line])

        print(f"\n{self.selected_level['type']} level\n")
        for line in level_copy:
            print(line)
        print('\n')
 

class Game:
    def __init__(self):
        self.predefined_levels = [
            {
                'file_name': 'level_small.txt',
                'type': 'small'
            },
            {
                'file_name': 'level_medium.txt',
                'type': 'medium'
            },
            {
                'file_name': 'level_large.txt',
                'type': 'large'
            },
        ]
        self.random_level_type = False
        self.selected_field = None
        self.random_generated_field = []
        self.player_strategy = ''
        self.game_over = False


    def get_robot_position(self, level):
        for index, line in enumerate(level):
            if 'R' in line:
                # x, y
                return [line.index('R'), index]


    def load_random_field(self):
        print('\n')
        print('-----------------------------------------------------------------------------')
        print(f'You have selected a random {self.selected_field[1]} field')

    def retrieve_level_selection(self):
        print('Select what type of level you want to play')
        # We're adding [{index}] to also provide the user with an option to 
        # select by simply pressing a number
        terminal_menu = TerminalMenu(
            [f'[{index}] {level["type"]}' for index, level in enumerate(self.predefined_levels)],
            # Add Spindle specific colors
            menu_cursor_style=('fg_yellow', 'bold'),
            shortcut_key_highlight_style=('fg_yellow', 'bold')
        )
        menu_entry_index = terminal_menu.show()
        return self.predefined_levels[menu_entry_index]
    

    def retrieve_player_strategy(self):
        print('-----------------------------------------------------------------------------')
        print('Select the strategy you want to use to navigate the field')
        print('-----------------------------------------------------------------------------')
        print('Commands')
        print('[U] - UP | [D] - DOWN | [L] - LEFT | [R] - RIGHT')
        print('-----------------------------------------------------------------------------')
        return input()


    def handle_player_strategy(self, level):
        # TODO: Get it from level
        self.robot_position = self.get_robot_position(level)

        # We need to handle the strategy, we start from the R and navigate through our list
        # We let the player know if they hit any mines during their way to the exit
        for command in self.player_strategy:
            if not self.game_over:
                if command == 'U':
                    expected_move = [self.robot_position[0], self.robot_position[1] - 1]
                if command == 'D':
                    expected_move = [self.robot_position[0], self.robot_position[1] + 1]
                if command == 'L':
                    expected_move = [self.robot_position[0] - 1, self.robot_position[1]]
                if command == 'R':
                    expected_move = [self.robot_position[0] + 1, self.robot_position[1]]

                intersect_with = level[expected_move[1]][expected_move[0]]

                if intersect_with != '#' and intersect_with != '*':
                    self.robot_position = expected_move
                else:
                    if intersect_with == '*':
                        self.game_over = True
        
        if level[self.robot_position[1]][self.robot_position[0]] == 'E':
            self.game_over = False
        else:
            self.game_over = True

    def level_selection(self):
        print('--------------------------------------------------------------------------------------------------------------------')
        print('Would you like to play a level created by Spindle (optimized for ultimate fun!) or random levels (changes everytime)?')
        print('--------------------------------------------------------------------------------------------------------------------')
        options = ['[0] Level by Spindle', '[1] Random level']
        terminal_menu = TerminalMenu(
            options,
            # Add Spindle specific colors
            menu_cursor_style=('fg_yellow', 'bold'),
            shortcut_key_highlight_style=('fg_yellow', 'bold')
        )
        menu_entry_index = terminal_menu.show()
        if menu_entry_index == 0:
            return False
        return True

    def show_level_example(self, level):
        level_file_path = os.path.join('levels', level['file_name'])
        with open(level_file_path, 'r') as level_file:
            # Create a copy
            level_lines = level_file.read().splitlines().copy()
            for index, line in enumerate(level_lines):
                level_lines[index] = ''.join([x if x != '*' else 'o' for x in line])

            print(f"\n{level['type']} field\n")
            for line in level_lines:
                print(line)
            print('\n')

    def show_level_examples(self):
        for level in self.predefined_levels:
            self.show_level_example(level)

    def start(self):
        print('-----------------------------------------------------------------------------')
        print('Spindle Mine Dodger v1.0')
        print('Navigate your robot [R] through the mine field [o] without hitting any mines.')
        self.random_level_type = self.level_selection()
        print('-----------------------------------------------------------------------------')
        print('Legend')
        print('[#] - Wall | [o] - Field | [R] - Robot | [E] - Exit')
        print('-----------------------------------------------------------------------------')
        self.show_level_examples()
        self.selected_level = self.retrieve_level_selection()
        level = Level(self.selected_level, random=self.random_level_type)
        level.generate_level()
        level.show_generated_level()
        self.player_strategy = self.retrieve_player_strategy()
        self.handle_player_strategy(level.generated_level)

        if self.game_over:
            print('-----------------------------------------------------------------------------')
            print('GAME OVER. PLEASE TRY AGAIN.')
            print('-----------------------------------------------------------------------------')
        else:
            print('-----------------------------------------------------------------------------')
            print('YAY YOU MADE IT! WELL DONE!')
            print('-----------------------------------------------------------------------------')

if __name__ == "__main__":
    spindle_game = Game()
    spindle_game.start()