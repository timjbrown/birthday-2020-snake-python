import pygame
import random

EMPTY_COLOR = (255, 255, 255)
BLOCK_COLOR = (0, 0, 0)
SNAKE_COLOR = (0, 255, 0)
APPLE_COLOR = (255, 0, 0)
CELL_SIZE = 30


class GameObject:
    def __init__(self, row, col, color):
        self.row = row
        self.col = col
        self.color = color

    def draw(self):
        pygame.draw.rect(
            screen, self.color,
            [CELL_SIZE * self.col, CELL_SIZE * self.row, CELL_SIZE, CELL_SIZE])

    def __repr__(self):
        return str(self.row) + ',' + str(self.col)

    def __str__(self):
        return self.__repr__()


class SnakeBlock(GameObject):
    def __init__(self, row, col, color):
        super(SnakeBlock, self).__init__(row, col, color)

    def copy(self):
        return SnakeBlock(self.row, self.col, self.color)


class Block(GameObject):
    def __init__(self, row, col, color):
        super(Block, self).__init__(row, col, color)


class Apple(GameObject):
    def __init__(self, row, col, color):
        super(Apple, self).__init__(row, col, color)


class Snake():
    def __init__(self):
        self.direction = 'd'
        self.segments = []

    def change_direction(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                self.direction = 'w'
            if event.key == pygame.K_a:
                self.direction = 'a'
            if event.key == pygame.K_s:
                self.direction = 's'
            if event.key == pygame.K_d:
                self.direction = 'd'

    def add_head(self, segment):
        self.segments.insert(0, segment)

    def add_tail(self, segment):
        self.segments.append(segment)

    def remove_tail(self):
        if len(self.segments) > 0:
            return self.segments.pop()

    def get_head(self):
        return self.segments[0]

    def __str__(self):
        return str(self.segments)


class Level:
    def __init__(self, filename):
        self.board = []
        self.snake = Snake()

        with open(filename, 'r') as f:
            for row, line in enumerate(f):
                line = line.strip()
                self.board.append([])
                for col, letter in enumerate(line):
                    cell = self.create_cell(letter, row, col)
                    if type(cell) == SnakeBlock:
                        self.snake.add_tail(cell)

                    self.board[row].append(cell)

        self.pix_width = len(self.board) * CELL_SIZE
        self.pix_height = len(self.board[0]) * CELL_SIZE
        self.spawn_apple()

    def create_cell(self, letter, row, col):
        if letter == ' ':
            return None
        elif letter == 'S':
            return SnakeBlock(row, col, SNAKE_COLOR)
        elif letter == 'X':
            return Block(row, col, BLOCK_COLOR)

    def draw(self):
        for row in self.board:
            for col in row:
                if col != None:
                    col.draw()

    def move_snake(self):
        # copy the old head into new head
        old_head = self.snake.get_head()
        new_head = old_head.copy()

        # remove old end of snake and update board
        removed_segment = self.snake.remove_tail()
        self.board[removed_segment.row][removed_segment.col] = None

        # move the position of the new head
        if self.snake.direction == 'w':
            new_head.row -= 1
        if self.snake.direction == 'a':
            new_head.col -= 1
        if self.snake.direction == 's':
            new_head.row += 1
        if self.snake.direction == 'd':
            new_head.col += 1

        got_apple = False
        # Check if the player got an apple
        if type(self.board[new_head.row][new_head.col]) == Apple:
            got_apple = True

        # Check if the player died
        elif self.board[new_head.row][new_head.col] != None:
            return True

        # add new head of snake and update board
        self.snake.add_head(new_head)
        self.board[new_head.row][new_head.col] = new_head

        if got_apple:
            self.spawn_apple()
            self.snake.add_tail(removed_segment)
            self.board[removed_segment.row][
                removed_segment.col] = removed_segment
            global score
            score += 1

        #print(self.snake)
        return False

    def spawn_apple(self):
        global delay
        while True:
            rand_row = random.randrange(len(self.board))
            rand_col = random.randrange(len(self.board[0]))
            if self.board[rand_row][rand_col] == None:
                self.board[rand_row][rand_col] = Apple(rand_row, rand_col,
                                                       APPLE_COLOR)
                delay -= delay * .1
                break


# Call this function so the Pygame library can initialize itself
pygame.init()

# Set the title of the window
pygame.display.set_caption('Snake Game')

# Set up the clock and delay to move the player
clock = pygame.time.Clock()

# Set up font for drawing text
font = pygame.font.SysFont('Arial', 20, True, False)

delay = 300
done = False
score = 0

while not done:
    for i in range(2):
        # Initialize the level
        level = Level('level{}.txt'.format(i))

        # Create the screen
        screen = pygame.display.set_mode(
            [CELL_SIZE * len(level.board[0]), CELL_SIZE * len(level.board)])

        delay = 220
        counter = 0
        score = 0
        pause = False

        while not done:
            # Process keyboard events since last frame
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = True
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        done = True
                    if event.key == pygame.K_SPACE:
                        pause = not pause

                level.snake.change_direction(event)

            if not pause:
                counter += clock.tick()
                if counter >= delay:
                    counter = 0
                    died = level.move_snake()
                    if died:
                        break

                # Draw empty screen
                screen.fill(EMPTY_COLOR)

                # Draw level
                level.draw()

                # Draw score
                text = font.render('Score: ' + str(score), True, BLOCK_COLOR)
                textx = level.pix_width / 2 - text.get_width() / 2
                texty = level.pix_height / 2 - text.get_height() / 2
                screen.blit(text, [textx, texty])

                # Flip screen
                pygame.display.flip()

pygame.quit()