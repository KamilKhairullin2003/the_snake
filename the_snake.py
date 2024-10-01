import pygame as pg
import random
from typing import Tuple, List

# Константы для размеров поля и сетки
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Направления движения
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Начальная позиция объекта
CENTER_POSITION = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

# Цвета
BOARD_BACKGROUND_COLOR = (0, 0, 0)
BORDER_COLOR = (93, 216, 228)
APPLE_COLOR = (255, 0, 0)
SNAKE_COLOR = (0, 255, 0)

# Скорость движения змейки (FPS)
SPEED = 10

# Инициализация Pygame
pg.init()

# Настройка игрового окна
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pg.display.set_caption('Нажми Esc, чтобы выйти')

# Настройка времени
clock = pg.time.Clock()

# Сопоставление клавиш с направлениями
KEY_DIRECTION_MAPPING = {
    pg.K_UP: UP,
    pg.K_DOWN: DOWN,
    pg.K_LEFT: LEFT,
    pg.K_RIGHT: RIGHT
}


class GameObject:
    """Родительский класс для игровых объектов."""

    def __init__(self, position: Tuple[int, int] = None,
                 body_color: Tuple[int, int, int] = None):
        """
        Инициализирует основные атрибуты игрового объекта.

         Позиция объекта на игровом поле.
         Цвет объекта в формате RGB.
        """
        self.position = position
        self.body_color = body_color

    def draw_cell(self, position: Tuple[int, int],
                  color: Tuple[int, int, int] = None):
        """
        Отрисовка ячейки.

        Параметр surface поверхность P  ygame для отрисовки.
        Параметр position позиция ячейки.
        Параметр color цвет ячейки. Если None, используется цвет объекта.
        """
        rect = pg.Rect(position, (GRID_SIZE, GRID_SIZE))
        if color is None:
            color = self.body_color
        pg.draw.rect(screen, color, rect)
        pg.draw.rect(screen, BORDER_COLOR, rect, 1)

    def draw(self):
        """
        Абстрактный метод для отрисовки объекта.
        Должен быть переопределён в дочерних классах.

        Параметр surface поверхность Pygame для отрисовки.
        """
        raise NotImplementedError("Метод переопределяется в дочерних классах.")


class Apple(GameObject):
    """Класс, представляющий яблоко в игре."""

    def __init__(self, occupied_positions: List[Tuple[int, int]] = None):
        """
        Инициализирует яблоко с красным цветом и случайной позицией.

        Параметр occupied_positions список занятых позиций
        (например, позиции змейки).
        """
        super().__init__(position=(0, 0), body_color=APPLE_COLOR)
        self.randomize_position(occupied_positions or [])

    def randomize_position(self, occupied_positions: List[Tuple[int, int]]):
        """
        Устанавливает случайную позицию яблока на игровом поле.

        Параметр occupied_positions cписок занятых позиций.
        """
        while True:
            self.position = (random.randint(0, GRID_WIDTH - 1) * GRID_SIZE,
                             random.randint(0, GRID_HEIGHT - 1) * GRID_SIZE)
            if self.position not in occupied_positions:
                break

    def draw(self):
        """
        Отрисовка яблока на игровой поверхности.

        Параметр surface поверхность Pygame для отрисовки.
        """
        self.draw_cell(self.position)


class Snake(GameObject):
    """Класс, представляющий змейку в игре."""

    def __init__(self):
        """
        Инициализирует змейку с начальной длиной,
        направлением и позицией.
        """
        super().__init__(position=CENTER_POSITION, body_color=SNAKE_COLOR)
        self.reset()

    def reset(self):
        """Сбрасывает змейку в начальное состояние."""
        self.length = 1
        self.positions = [self.position]
        self.direction = RIGHT
        self.next_direction = None

    def get_head_position(self) -> Tuple[int, int]:
        """
        Возвращает позицию головы змейки.

        Команда return возвращает кортеж с координатами головы.
        """
        return self.positions[0]

    def update_direction(self, new_direction: Tuple[int, int]):
        """
        Обновляет направление движения змейки.

        Параметр new_direction - новое направление движения.
        """
        # Предотвращаем разворот змейки
        opposite_direction = (-self.direction[0], -self.direction[1])
        if new_direction != opposite_direction:
            self.direction = new_direction

    def move(self):
        """
        Обновляет позицию змейки,
        добавляя новую голову и удаляя хвост,
        если длина не увеличилась.
        """
        x_dir, y_dir = self.direction
        x_head_pos, y_head_pos = self.get_head_position()
        new_head = (
            (x_head_pos + x_dir * GRID_SIZE) % SCREEN_WIDTH,
            (y_head_pos + y_dir * GRID_SIZE) % SCREEN_HEIGHT
        )
        self.positions.insert(0, new_head)
        if len(self.positions) > self.length:
            self.positions.pop()

    def draw(self):
        """
        Отрисовывает змейку на игровой поверхности.

        Параметр surface - поверхность Pygame для отрисовки.
        """
        for pos in self.positions:
            self.draw_cell(pos)


def handle_keys(snake: Snake):
    """
    Обрабатывает нажатия клавиш для изменения направления движения змейки.

    Параметр snake - объект змейки.
    """
    for event in pg.event.get():
        if event.type == pg.QUIT or
         (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
            pg.quit()
            raise SystemExit
        elif event.type == pg.KEYDOWN:
            if event.key in KEY_DIRECTION_MAPPING:
                new_direction = KEY_DIRECTION_MAPPING[event.key]
                snake.update_direction(new_direction)


def main():
    """Основной игровой цикл."""
    snake = Snake()
    apple = Apple(occupied_positions=snake.positions)

    running = True
    while running:
        clock.tick(SPEED)
        handle_keys(snake)
        snake.move()

        # Проверка столкновения с яблоком
        if snake.get_head_position() == apple.position:
            snake.length += 1
            apple.randomize_position(occupied_positions=snake.positions)

        # Проверка столкновения с собой
        elif snake.get_head_position() in snake.positions[1:]:
            snake.reset()
            apple.randomize_position(occupied_positions=snake.positions)

        # Отрисовка
        screen.fill(BOARD_BACKGROUND_COLOR)
        apple.draw()
        snake.draw()
        pg.display.update()


if __name__ == '__main__':
    main()
