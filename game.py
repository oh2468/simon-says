import pygame
import random
import time
import json



class Game:
    _DEFAULT_NUM_TILES = 4
    _GAME_DELAY = 1
    _BLINK_SPEED = 5
    _GAME_SPEED = 10
    _CLICK_SPEED = 20
    _BLINK_VALUE = 100

    _GAME_MODE_TILES = {
        1: _DEFAULT_NUM_TILES,
        2: 6,
        3: 9,
    }
    
    _TILE_COLORS = [
        (200, 0, 0),
        (0, 200, 0),
        (0, 0, 200),
        (200, 200, 0),
        (200, 0, 200),
        (0, 200, 200),
        (155, 155, 155),
        (255, 127, 0),
        #(0, 0, 0),
        (128, 0, 0),
    ]


    def __init__(self, game_window, mode):
        self._game_window = game_window
        self._game_window.fill((0, 0, 0))
        self._game_mode = mode
        self._num_tiles = self._GAME_MODE_TILES.get(self._game_mode, self._DEFAULT_NUM_TILES)
        self._simon_says = []
        self._rects = self._init_rects()
        self._rects_with_colors = list(zip(self._rects, self._TILE_COLORS))
        self._sound_on = True


    def _init_rects(self):
        match self._num_tiles:
            case 6:
                x_r, y_r = 3, 2
            case 9:
                x_r = y_r = 3
            case _:
                x_r = y_r = 2

        x_part, y_part = self._game_window.get_width() / x_r, self._game_window.get_height() / y_r

        size = min(x_part, y_part)
        diff = max(x_part, y_part) - size
        pad = 10

        if x_part <= y_part:
            pad_x = pad
            pad_y = int(diff / 2) + pad_x
        else:
            pad_y = pad
            pad_x = int(diff / 2) + pad_y

        rects =  [pygame.Rect(x_part * x, y_part * y, x_part, y_part) for y in range(y_r) for x in range(x_r)]
        for rect in rects:
            rect.w = rect.h = size
            rect.x += pad_x
            rect.y += pad_y
            rect.w -= (2 * pad)
            rect.h -= (2 * pad)

        return rects


    def _draw_tiles(self, blink_index=None):
        for i, (rect, color) in enumerate(self._rects_with_colors):
            if i == blink_index:
                color = tuple(min(c + self._BLINK_VALUE, 255) for c in color)
            pygame.draw.rect(self._game_window, color, rect)
        pygame.display.update()


    def _blink_tile(self, tile_index, fps, speed):
        fps.tick(speed)
        self._draw_tiles(tile_index)
        fps.tick(speed)
        self._draw_tiles()
        fps.tick(speed)


    def _blink_and_beep_tiles(self):
        pass

    
    def _blink_pattern(self, fps):
        time.sleep(1)
        
        self._simon_says.append(random.randrange(0, self._num_tiles))
        #print(f"PATTERN: {self._simon_says}")

        for tile_index in self._simon_says:
            self._blink_tile(tile_index, fps, self._BLINK_SPEED)
        
        pygame.event.clear()
        return self._simon_says[:]


    def _draw_text(self, text, size, y_pos, color=(255, 255, 255)):
        text_font = pygame.font.SysFont("times new roman", size, True)
        text_label = text_font.render(text, True, color)
        text_rect = text_label.get_rect()
        text_rect.center = self._game_window.get_width() / 2, y_pos
        self._game_window.blit(text_label, text_rect)


    def _draw_game_over(self, score):
        title_y = self._game_window.get_height() / 4
        score_y = title_y * 2
        text_size = int(title_y  / 2)

        self._game_window.fill((0, 0, 0))

        self._draw_text("!! GAME OVER !!", text_size, title_y)
        self._draw_text(f"Score: {score}", text_size, score_y)

        pygame.display.update()
        time.sleep(3)


    def run_game(self):
        fps = pygame.time.Clock()
        clicked = -1
        blinks = []
        correct_clicks = 0
        current_score = -1

        self._draw_tiles()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    print("Quitting the game!")
                    pygame.quit()
                    quit()

                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    print("SPACE - (coming soon: (un)mute)")

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == pygame.BUTTON_LEFT:
                    x, y = pygame.mouse.get_pos()
                    for i, rect in enumerate(self._rects):
                        if rect.collidepoint(x, y):
                            clicked = i
                            self._blink_tile(clicked, fps, self._CLICK_SPEED)

            if clicked >= 0:
                if clicked != blinks.pop(0):
                    ScoreHandler.update_high_score(self._game_mode, current_score, time.time())
                    self._draw_game_over(current_score)
                    return current_score
                else:
                    correct_clicks += 1
                    clicked = -1

            if not blinks:
                current_score += 1
                blinks = self._blink_pattern(fps)

            fps.tick(self._GAME_SPEED)



class ScoreHandler:
    HIGH_SCORE_FILE_NAME = "high_scores.txt"
    HIGH_SCORE_MODE_MODEL = {"high_scores": [
        {
        "mode": 1,
        "description": "4 tile mode",
        "score": 0,
        "score_moment": 0,
        }, {
        "mode": 2,
        "description": "6 tile mode",
        "score": 0,
        "score_moment": 0,
        }, {
        "mode": 3,
        "description": "9 tile mode",
        "score": 0,
        "score_moment": 0,
        },
    ]}


    def put_high_scores(scores):
        with open(ScoreHandler.HIGH_SCORE_FILE_NAME, "w", encoding="UTF-8") as file:
            json.dump(scores, file)


    def update_high_score(mode, score, time_stamp):
        scores = ScoreHandler.get_high_scores()
        updated = False
        for score_mode in scores["high_scores"]:
            if score_mode["mode"] == mode and score > score_mode["score"]:
                score_mode["score"] = score
                score_mode["score_moment"] = time_stamp
                updated = True
        
        if updated:
            ScoreHandler.put_high_scores(scores)


    def get_high_scores():
        try:
            with open(ScoreHandler.HIGH_SCORE_FILE_NAME, "r", encoding="UTF-8") as file:
                return json.load(file)
        except FileNotFoundError:
            ScoreHandler.put_high_scores(ScoreHandler.HIGH_SCORE_MODE_MODEL)
            return ScoreHandler.get_high_scores()



class Home:
    _GAME_TITLE = "Simon Says (WHAT?!)"
    #_WINDOW_SIZE = (720, 540)
    _WINDOW_SIZE = (480, 480)
    _TEXT_COLOR = (0, 0, 0)

    _HOME_SCREEN_CONTENT = {
        "All Time High Scores": 0,
        "(Mode 1)  Play With 4 Tiles": 1,
        "(Mode 2)  Play With 6 Tiles": 2,
        "(Mode 3)  Play With 9 Tiles": 3,
    }


    def __init__(self):
        pygame.init()
        pygame.display.set_caption(self._GAME_TITLE)
        self._game_window = pygame.display.set_mode(self._WINDOW_SIZE)
        self._game_window.fill((0, 0, 0))
        self._menu_titles = list(self._HOME_SCREEN_CONTENT.keys())
        self._menu_modes = list(self._HOME_SCREEN_CONTENT.values())
        self._menu_surfaces = self._init_menu_items()
    

    def _draw_text_on_surface(self, surface, text, bold, centered, size=None, color=None):
            font = pygame.font.SysFont("times new roman", size or int(surface.get_height() / 4), bold)
            label = font.render(text, True, color or self._TEXT_COLOR)
            label_rect = label.get_rect()
            if centered:
                label_rect.center = surface.get_width() / 2, surface.get_height() / 2
            else:
                label_rect.centery = surface.get_height() / 2
            surface.blit(label, label_rect)


    def _draw_item_menu_score_row(self):
        scores = ScoreHandler.get_high_scores()

        surface = self._menu_surfaces[0]
        row_color = surface.get_at((0, 0))
        triad_color = (row_color[1], row_color[2], row_color[0])
        surface.fill(triad_color)
        
        x, y = surface.get_size()
        sub_x, sub_y = x / 3,  y / 2
        text_size = int(sub_y / 2)

        title_surface = surface.subsurface(0, 0, x, sub_y)
        title_surface.fill(triad_color)
        score_surface = surface.subsurface(0, sub_y, x, sub_y)

        self._draw_text_on_surface(title_surface, self._menu_titles[0], True, True, size=text_size)

        for i, score in enumerate(scores["high_scores"]):
            mode_surface = score_surface.subsurface(i * sub_x, 0, sub_x, sub_y)
            text = f" Mode {score['mode']}: {score['score']}"
            self._draw_text_on_surface(mode_surface, text, False, False, size=text_size)


    def _init_menu_items(self):
        item_count = len(self._HOME_SCREEN_CONTENT)
        x, y = self._game_window.get_width(), self._game_window.get_height() / item_count
        return [self._game_window.subsurface(0, i * y, x, y) for i in range(item_count)]

    
    def _draw_menu_items(self):
        for surf, title in zip(self._menu_surfaces, self._menu_titles):
            surf.fill((100, random.randint(150, 255), 100))
            self._draw_text_on_surface(surf, title, True, True)

        self._draw_item_menu_score_row()

        pygame.display.update()
        pygame.event.clear()


    def run_main(self):
        fps = pygame.time.Clock()
        update_menu = True
        item_clicked = None
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    print("Quitting the game!")
                    return

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == pygame.BUTTON_LEFT:
                    x, y = pygame.mouse.get_pos()

                    for i, surf in enumerate(self._menu_surfaces):
                        if y < (i + 1) * surf.get_height():
                            item_clicked = i
                            break
                
                # if event.type == pygame.MOUSEBUTTONDOWN and event.button == pygame.BUTTON_RIGHT:
                #     print(f"COLOR: {self._game_window.get_at(pygame.mouse.get_pos())}")
           
            if item_clicked:
                mode = self._menu_modes[item_clicked]
                game = Game(self._game_window, mode)
                game.run_game()
                update_menu = True 
                item_clicked = None

            if update_menu:
                self._draw_menu_items()
                update_menu = False

            fps.tick(10)


if __name__ == "__main__":
    print("Now starting my AMAZING game!")
    
    home = Home()
    home.run_main()

    print("You seem to be done for now. Good Bye!")



