import pygame
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
INITIAL_POSITION = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

# Цвета
BOARD_BACKGROUND_COLOR = (0, 0, 0)
BORDER_COLOR = (93, 216, 228)
APPLE_COLOR = (255, 0, 0)
SNAKE_COLOR = (0, 255, 0)

# Скорость движения змейки (FPS)
SPEED = 10

# Инициализация Pygame
pygame.init()

# Настройка игрового окна
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Змейка')

# Настройка времени
clock = pygame.time.Clock()

# Сопоставление клавиш с направлениями
KEY_DIRECTION_MAPPING = {
    pygame.K_UP: UP,
    pygame.K_DOWN: DOWN,
    pygame.K_LEFT: LEFT,
    pygame.K_RIGHT: RIGHT
}


class GameObject:
    """Родительский класс для игровых объектов."""

    def __init__(self, position: Tuple[int, int], body_color: Tuple[int, int, int]):
        """
        Инициализирует основные атрибуты игрового объекта.

         Позиция объекта на игровом поле.
         Цвет объекта в формате RGB.
        """
        self.position = position
        self.body_color = body_color

    def draw_cell(self, surface: pygame.Surface, position: Tuple[int, int], color: Tuple[int, int, int] = None):
        """
        Отрисовка ячейки.

        Параметр surface поверхность Pygame для отрисовки.
        Параметр position позиция ячейки.
        Параметр color цвет ячейки. Если None, используется цвет объекта.
        """
        rect = pygame.Rect(position, (GRID_SIZE, GRID_SIZE))
        if color is None:
            color = self.body_color
        pygame.draw.rect(surface, color, rect)
        pygame.draw.rect(surface, BORDER_COLOR, rect, 1)

    def draw(self, surface: pygame.Surface):
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

        Параметр occupied_positions список занятых позиций (например, позиции змейки).
        """
        super().__init__(position=(0, 0), body_color=APPLE_COLOR)
        self.randomize_position(occupied_positions or [])

    def randomize_position(self, occupied_positions: List[Tuple[int, int]]):
        """
        Устанавливает случайную позицию яблока на игровом поле.

        Параметр occupied_positions cписок занятых позиций.
        """
        while True:
            x = random.randint(0, GRID_WIDTH - 1) * GRID_SIZE
            y = random.randint(0, GRID_HEIGHT - 1) * GRID_SIZE
            new_position = (x, y)
            if new_position not in occupied_positions:
                self.position = new_position
                break

    def draw(self, surface: pygame.Surface):
        """
        Отрисовка яблока на игровой поверхности.

        Параметр surface поверхность Pygame для отрисовки.
        """
        self.draw_cell(surface, self.position)


class Snake(GameObject):
    """Класс, представляющий змейку в игре."""

    def __init__(self):
        """
        Инициализирует змейку с начальной длиной, направлением и позицией.
        """
        super().__init__(position=INITIAL_POSITION, body_color=SNAKE_COLOR)
        self.reset()

    def reset(self):
        """
        Сбрасывает змейку в начальное состояние.
        """
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
        Обновляет позицию змейки, добавляя новую голову и удаляя хвост, если длина не увеличилась.
        """
        current_head = self.get_head_position()
        new_head = (
            (current_head[0] + self.direction[0] * GRID_SIZE) % SCREEN_WIDTH,
            (current_head[1] + self.direction[1] * GRID_SIZE) % SCREEN_HEIGHT
        )
        self.positions.insert(0, new_head)
        if len(self.positions) > self.length:
            self.positions.pop()

    def draw(self, surface: pygame.Surface):
        """
        Отрисовывает змейку на игровой поверхности.

        Параметр surface - поверхность Pygame для отрисовки.
        """
        for pos in self.positions:
            self.draw_cell(surface, pos)


def handle_keys(snake: Snake):
    """
    Обрабатывает нажатия клавиш для изменения направления движения змейки.

    Параметр snake - объект змейки.
    """
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
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
        if snake.get_head_position() in snake.positions[1:]:
            snake.reset()
            apple.randomize_position(occupied_positions=snake.positions)

        # Отрисовка
        screen.fill(BOARD_BACKGROUND_COLOR)
        apple.draw(screen)
        snake.draw(screen)
        pygame.display.update()


if __name__ == '__main__':
    main()