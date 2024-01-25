from random import randint


class BoardException(Exception):
    pass


class BoardOutException(BoardException):
    def __str__(self):
        return "Вы стреляете за пределы доски"


class BoardUsedException(BoardException):
    def __str__(self):
        return "В это место вы уже стреляли"


class BoardWrongShipException(BoardException):
    pass


class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f'Dot({self.x}, {self.y})'


class Ship:
    def __init__(self, bow, size, orient):
        self.size = size
        self.bow = bow
        self.orient = orient
        self.lives = size

    @property
    def dots(self):
        ship_dots = []
        for i in range(self.size):
            cur_x = self.bow.x
            cur_y = self.bow.y

            if self.orient == 0:
                cur_x += i

            if self.orient == 1:
                cur_y += i

            ship_dots.append(Dot(cur_x, cur_y))

        return ship_dots

    def shoot(self, shot):
        return shot in self.dots


class Board:
    def __init__(self, hid=False, size=6):
        self.hid = hid
        self.size = size

        self.count = 0

        self.field = [['0']*size for _ in range(size)]

        self.busy = []
        self.ships = []

    def __str__(self):
        res = ''
        res += "   | 1 | 2 | 3 | 4 | 5 | 6 |"

        for i, row in enumerate(self.field):
            res += f"\n {i+1} | " + " | ".join(row) + " | "

        if self.hid:
            res = res.replace("■", "0")

        return res

    def out(self, d):
        return not (0 <= d.x < self.size and 0 <= d.y < self.size)

    def contour(self, ship, verb=False):
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for d in ship.dots:
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                if not (self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.field[cur.x][cur.y] = "."
                    self.busy.append(cur)

    def add_ship(self, ship):
        for d in ship.dots:
            if self.out(d) or d in self.busy:
                raise BoardWrongShipException()
        for d in ship.dots:
            self.field[d.x][d.y] = '■'
            self.busy.append(d)

            self.ships.append(ship)
            self.contour(ship)

    def shot(self, d):
        if self.out(d):
            raise BoardOutException
        if d in self.busy:
            raise BoardUsedException

        self.busy.append(d)

        for ship in self.ships:
            if ship.shoot(d):
                ship.lives -= 1
                self.field[d.x][d.y] = "X"

                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, verb=True)
                    print("Корабля больше нет")
                    return True
                else:
                    print("Корабль подбит")
                    return True

        self.field[d.x][d.y] = "."
        print("Промах")
        return False

    def begin(self):
        self.busy = []


class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)


class AI(Player):
    def ask(self):
        d = Dot(randint(0, 5), randint(0, 5))
        print(f"Ход компьютера: {d.x + 1}{d.y + 1}")
        return d


class User(Player):
    def ask(self):
        while True:
            cords = input("Ваш ход: ").split()
            if len(cords) != 2:
                print("Введите 2 координаты.")
                continue

            x, y = cords
            if not (x.isdigit()) or not (y.isdigit()):
                print("Введите числа!")
                continue

            x, y = int(x), int(y)

            return Dot(x-1, y-1)


class Game:
    def __init__(self, size=6):
        self.size = size
        player_b = self.random_board()
        comp_b = self.random_board()
        comp_b.hid = True

        self.ai = AI(comp_b, player_b)
        self.user = User(player_b, comp_b)

    def try_board(self):
        lens = [3, 2, 2, 1, 1, 1, 1]
        board = Board(size=self.size)
        attempts = 0
        for size in lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), size, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    def random_board(self):
        board = None
        while board is None:
            board = self.try_board()
        return board

    def greet(self):
        print("*****************************")
        print("    Доброго времени суток    ")
        print("       Рад вас видеть        ")
        print("      в игре морской...      ")
        print("           боооой            ")
        print("*****************************")
        print(" Для того чтобы сделать ход  ")
        print("необходимо ввести координаты ")
        print("             х у             ")
        print("       х  - это строка       ")
        print("       у - это столбец       ")

    def loop(self):
        num = 0
        while True:
            print("-"*29)
            print("Доска пользователя: ")
            print(self.user.board)
            print("-" * 29)
            print("Доска компьютера: ")
            print(self.ai.board)
            print("-" * 29)
            if num % 2 == 0:
                print("Ход пользователя: ")
                repeat = self.user.move()
            else:
                print("Ход компьютера: ")
                repeat = self.ai.move()

            if repeat:
                num -= 1

            if self.ai.board.count == 7:
                print("*" * 29)
                print("Пользователь выиграл!")
                break
            elif self.user.board.count == 7:
                print("*" * 29)
                print("Компьютер выиграл!")
                break

            num += 1

    def start(self):
        self.greet()
        self.loop()


g = Game()
g.start()
