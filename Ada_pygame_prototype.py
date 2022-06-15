import pygame


class Runner:
    def __init__(self, duration_gap, duration_text, amount_text, task_type_gap,
                 num_attention_shifts, color_background, color_text, size_text, size_gap,
                 pos_text, pos_gap, title):
        # Initialize input parameters.
        self.duration_gap = duration_gap
        self.duration_text = duration_text
        self.amount_text = amount_text
        self.task_type_gap = task_type_gap
        self.num_attention_shifts = num_attention_shifts
        self.color_background = color_background
        self.color_text = color_text
        self.size_text = size_text
        self.size_gap = size_gap
        self.pos_text = pos_text
        self.pos_gap = pos_gap
        self.title = title

        # Constant values
        WIDTH_CANVAS = 800
        HEIGHT_CANVAS = 800
        FPS = 60
        ANCHOR = "topleft"

        # Create the canvas.
        # Setup pygame
        pygame.display.set_caption(self.title)
        self.surface = pygame.display.set_mode((WIDTH_CANVAS, HEIGHT_CANVAS))
        self.rect_canvas = self.surface.get_rect()
        self.clock = pygame.time.Clock()

        # Initialize global variables
        self.is_running = False
        self.fps = FPS
        self.is_text_showing = False
        self.timer = 0
        self.counter_attention_shifts = 0
        self.time_elapsed = 0

        self.content_text = "Wai bi ba bo? Wai bi ba ba."
        self.content_gap_temp = "Wubba lubba dub dub!"

        font_text = pygame.font.Font(None, self.size_text)
        self.image_text = font_text.render(self.content_text, True, self.color_text)
        self.rect_text = self.image_text.get_rect()
        setattr(self.rect_text, ANCHOR, self.pos_text)

        font_gap = pygame.font.Font(None, self.size_gap)
        self.image_gap = font_gap.render(self.content_gap_temp, True, self.color_text)
        self.rect_gap = self.image_gap.get_rect()
        setattr(self.rect_gap, ANCHOR, self.pos_gap)

    def mainloop(self):
        self.is_running = True
        while self.is_running:
            for event in pygame.event.get():
                # Normally close the game.
                if event.type == pygame.QUIT:
                    self.is_running = False
                # TODO: listen for keyboard press events.

            # Count the time elapsed.
            self.time_elapsed = self.clock.tick(self.fps)
            # Update the timer.
            self.timer += self.time_elapsed

            # Display text or gap content.
            if self.is_text_showing:
                # Draw content.
                self.surface.blit(self.image_text, self.rect_text)
                # Update the status.
                if self.timer > self.duration_text:
                    self.counter_attention_shifts += 1
                    self.is_text_showing = False
                    self.timer = 0
                    self.surface.fill(self.color_background)
            elif self.is_text_showing is False:
                self.surface.blit(self.image_gap, self.rect_gap)
                if self.timer > self.duration_gap:
                    self.is_text_showing = True
                    self.timer = 0
                    self.surface.fill(self.color_background)

            pygame.display.flip()

            # The experiment is over with exceeding the iteration times.
            if self.counter_attention_shifts > self.num_attention_shifts:
                self.is_running = False


def run_prototype():
    pygame.init()
    runner_trial = Runner(duration_gap=3000, duration_text=1500, amount_text=5, task_type_gap="default",
                          num_attention_shifts=5, color_background="black", color_text=(73, 232, 56),
                          size_text=48, size_gap=128, pos_text=(20, 0), pos_gap=(50, 250), title="trial_1")
    runner_trial.mainloop()
