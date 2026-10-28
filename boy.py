from pico2d import SDL_KEYDOWN, SDL_KEYUP, SDLK_a, SDLK_LEFT, SDLK_RIGHT, load_image
import time
from transitions import Machine

class Boy:
    def __init__(self):
        self.x, self.y = 400, 90
        self.frame = 0
        self.face_dir = 1
        self.pressed_directions = []
        self.auto_run_key_down = False
        self.idle_start_time = time.monotonic()
        self.image = load_image('animation_sheet.png')
        self.machine = Machine(
            model=self,
            states=['AUTO_RUN', 'IDLE', 'SLEEP', 'RUN'],
            initial='IDLE',
            auto_transitions=False,
            transitions=[
                {'trigger': 'sleep', 'source': 'IDLE', 'dest': 'SLEEP'},
                {'trigger': 'start_running', 'source': ['IDLE', 'SLEEP'], 'dest': 'RUN'},
                {
                    'trigger': 'start_auto_run',
                    'source': ['IDLE', 'SLEEP', 'RUN'],
                    'dest': 'AUTO_RUN',
                    'after': 'reset_auto_run_timer',
                },
                {
                    'trigger': 'stop_auto_run',
                    'source': 'AUTO_RUN',
                    'dest': 'IDLE',
                    'after': 'reset_idle_timer',
                },
                {
                    'trigger': 'stop_running',
                    'source': 'RUN',
                    'dest': 'IDLE',
                    'after': 'reset_idle_timer',
                },
            ],
        )

    def reset_idle_timer(self):
        self.idle_start_time = time.monotonic()

    def reset_auto_run_timer(self):
        self.auto_run_start_time = time.monotonic()

    def handle_event(self, event):
        if event.type == SDL_KEYDOWN and event.key == SDLK_a:
            if not self.auto_run_key_down:
                self.auto_run_key_down = True
                if self.state == 'AUTO_RUN':
                    self.stop_auto_run()
                    if self.pressed_directions:
                        self.start_running()
                else:
                    self.start_auto_run()
            return
        if event.type == SDL_KEYUP and event.key == SDLK_a:
            self.auto_run_key_down = False
            return

        if event.type == SDL_KEYDOWN and event.key in (SDLK_LEFT, SDLK_RIGHT):
            if event.key not in self.pressed_directions:
                self.pressed_directions.append(event.key)
            self.face_dir = 1 if event.key == SDLK_RIGHT else -1
            if self.state not in ('RUN', 'AUTO_RUN'):
                self.start_running()
        elif event.type == SDL_KEYUP and event.key in self.pressed_directions:
            self.pressed_directions.remove(event.key)
            if self.pressed_directions:
                direction = self.pressed_directions[-1]
                self.face_dir = 1 if direction == SDLK_RIGHT else -1
            else:
                if self.state == 'RUN':
                    self.stop_running()

    def update(self):
        if self.state == 'AUTO_RUN':
            if time.monotonic() - self.auto_run_start_time >= 5:
                self.stop_auto_run()
                return
            self.x = max(50, min(750, self.x + self.face_dir * 5))
            self.frame = (self.frame + 1) % 8
        elif self.state == 'RUN':
            self.x = max(50, min(750, self.x + self.face_dir * 5))
            self.frame = (self.frame + 1) % 8
        elif self.state == 'IDLE':
            self.frame = (self.frame + 1) % 8
            if time.monotonic() - self.idle_start_time >= 5:
                self.sleep()
        elif self.state == 'SLEEP':
            self.frame = 1

    def draw(self):
        if self.state in ('AUTO_RUN', 'RUN'):
            row = 100 if self.face_dir == 1 else 0
        else:
            row = 300 if self.face_dir == 1 else 200
        self.image.clip_draw(self.frame * 100, row, 100, 100, self.x, self.y)