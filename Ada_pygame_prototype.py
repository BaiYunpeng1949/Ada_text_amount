import pygame
import math

TEXTS_1 = "US banks JPMorgan Chase, Citigroup and Wells Fargo said on Wednesday (Jun 15) they had raised their prime lending rates by 75 basis points to 4.75 per cent, effective Thursday, " \
          "matching the Federal Reserve's rate hike earlier in the day." \
          "The Fed raised its target interest rate by three-quarters of a percentage point, the most by the US central bank since 1994, " \
          "as it seeks to tame red-hot inflation. The central bank faces the task of charting a course for the economy to weather rate increases without a repeat of the 1970s-style predicament when the central bank's interest hikes aimed at fighting inflation resulted in a steep recession." \
          "Inflation, which has become a hot-button political issue, has worsened with the Ukraine war, hitting market sentiment and piling pressure on to an already battered supply chain." \
          "However, since banks make money on the difference between what they earn from lending and payouts on deposits and other funds, they typically thrive in a high interest rate environment."


class Runner:
    def __init__(self, duration_gap, duration_text, amount_text, source_text, task_type_gap,
                 num_attention_shifts, color_background, color_text, size_text, size_gap,
                 pos_text, pos_gap, title):
        # Initialize input parameters.
        self.duration_gap = duration_gap
        self.duration_text = duration_text
        self.amount_text = amount_text
        self.texts = source_text
        self.texts_chunks = []
        self.task_type_gap = task_type_gap
        self.num_attention_shifts = num_attention_shifts
        self.color_background = color_background
        self.color_text = color_text
        self.size_text = size_text
        self.size_gap = size_gap
        self.pos_text = pos_text    # Coordinators whose origins are from the top left corner.
        self.pos_gap = pos_gap
        self.title = title

        # Constant values
        WIDTH_SURFACE = 800
        HEIGHT_SURFACE = 800
        FPS = 60
        ANCHOR = "topleft"
        self.MARGIN_RIGHT = 50
        self.MARGIN_LEFT = self.pos_text[0]
        self.MARGIN_BOTTOM = 50
        self.MARGIN_TOP = self.pos_text[1]

        # Create the canvas.
        # Setup pygame
        pygame.display.set_caption(self.title)
        self.surface = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.rect_canvas = self.surface.get_rect()
        self.clock = pygame.time.Clock()

        # Initialize global variables
        self.is_running = False
        self.fps = FPS
        self.is_text_showing = False
        self.timer = 0
        self.counter_attention_shifts = 0
        self.time_elapsed = 0

        self.content_text_temp = ""
        self.content_gap_temp = "GAGAGA"

        self.font_text = pygame.font.Font(None, self.size_text)
        self.image_text = self.font_text.render(self.content_text_temp, True, self.color_text)
        self.rect_text = self.image_text.get_rect()
        setattr(self.rect_text, ANCHOR, self.pos_text)

        self.font_gap = pygame.font.Font(None, self.size_gap)
        self.image_gap = self.font_gap.render(self.content_gap_temp, True, self.color_text)
        self.rect_gap = self.image_gap.get_rect()
        setattr(self.rect_gap, ANCHOR, self.pos_gap)

        # Split the text according to the given chunk size.
        self.split_amount_texts()

    def mainloop(self):
        self.is_running = True
        while self.is_running:
            for event in pygame.event.get():
                # Normally close the game.
                if event.type == pygame.QUIT:
                    self.is_running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.is_running = False
                # TODO: listen for keyboard press events.

            # Count the time elapsed.
            self.time_elapsed = self.clock.tick(self.fps)
            # Update the timer.
            self.timer += self.time_elapsed

            # Display text or gap content.
            if self.is_text_showing:
                # Draw content.
                # Get the current texts.
                self.content_text_temp = self.texts_chunks[self.counter_attention_shifts]
                self.image_text = self.font_text.render(self.content_text_temp, True, self.color_text)
                # self.surface.blit(self.image_text, self.rect_text)
                self.render_texts_multiple_lines()

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
                    # self.surface.fill(self.color_background)

            pygame.display.flip()

            # The experiment is over with exceeding the iteration times.
            if self.counter_attention_shifts > self.num_attention_shifts:
                self.is_running = False

        pygame.quit()

    def split_amount_texts(self):
        word_list = self.texts.split()
        num_words = len(word_list)
        num_texts_chunks = int(math.ceil(num_words / self.amount_text))

        for i in range(num_texts_chunks):
            text_chunk = ""
            index_pick_texts = i * self.amount_text
            if i < (num_texts_chunks - 1):
                num_left_words = self.amount_text
            elif i == (num_texts_chunks - 1):   # The last chunk, maybe not enough words.
                num_left_words = num_words - (num_texts_chunks - 1) * self.amount_text

            for k in range(num_left_words):
                text_chunk = text_chunk + " " + word_list[index_pick_texts + k]

            self.texts_chunks.append(text_chunk)

    def render_texts_multiple_lines(self):
        words = self.content_text_temp.split(' ')
        space = self.font_text.size(' ')[0]
        surface_width, surface_height = self.surface.get_size()
        max_width = surface_width - self.MARGIN_RIGHT - self.MARGIN_LEFT
        max_height = surface_height - self.MARGIN_BOTTOM - self.MARGIN_TOP
        x_text, y_text = self.pos_text

        # Render word by word.
        for word in words:
            word_surface = self.font_text.render(word, 0, self.color_text)
            word_width, word_height = word_surface.get_size()
            if x_text + word_width >= max_width:
                x_text = self.pos_text[0]   # Reset the x_text.
                y_text += word_height

            if word != '':  # TODO: the first element is a null, might because of the split.
                self.surface.blit(word_surface, (x_text, y_text))
                x_text += word_width + space



def run_prototype():
    pygame.init()
    runner_trial = Runner(duration_gap=3000, duration_text=1500, amount_text=25, source_text=TEXTS_1,
                          task_type_gap="default",
                          num_attention_shifts=5, color_background="black", color_text=(73, 232, 56),
                          size_text=70, size_gap=64, pos_text=(50, 250), pos_gap=(50, 200), title="trial_1")
    runner_trial.mainloop()
