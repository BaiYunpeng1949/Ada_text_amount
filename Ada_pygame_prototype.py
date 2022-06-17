import math
import random

import pygame

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
        self.index_content_texts = 0
        self.texts_chunks = []
        self.gap_task_chunks = []
        self.gap_task_chunks_results = []  # TODO: could be printed out or saved in log.

        self.content_text_temp = ""
        self.content_gap_temp = "Ga Ga Ga Ga Ga"

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

        # Generate the subtasks.
        self.generate_subtask()

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
                    elif event.key == pygame.K_SPACE:
                        if self.is_text_showing:
                            self.surface.fill(self.color_background)  # Clear up.
                            self.index_content_texts += 1
                            # If the index of content is out of the range, loop back to 0.
                            if self.index_content_texts == len(self.texts_chunks):
                                self.index_content_texts = 0

                # TODO: listen for keyboard press events.

            # Count the time elapsed.
            self.time_elapsed = self.clock.tick(self.fps)
            # Update the timer.
            self.timer += self.time_elapsed

            # Display text content.
            if self.is_text_showing:
                # Draw content.
                # Get the current texts.
                self.content_text_temp = self.texts_chunks[self.index_content_texts]
                self.image_text = self.font_text.render(self.content_text_temp, True, self.color_text)
                self.render_texts_multiple_lines()  # Render text content word by word, line by line.
                # Update the status.
                if self.timer > self.duration_text:
                    self.counter_attention_shifts += 1
                    self.is_text_showing = False
                    self.timer = 0
                    self.surface.fill(self.color_background)

            # Display the gap content.
            elif self.is_text_showing is False:
                self.content_gap_temp = self.gap_task_chunks[self.counter_attention_shifts]
                self.image_gap = self.font_gap.render(self.content_gap_temp, True, self.color_text)
                self.render_gap_tasks()  # Render content according to task type.
                if self.timer > self.duration_gap:
                    self.is_text_showing = True
                    self.timer = 0
                    self.surface.fill(self.color_background)

            pygame.display.flip()

            # The experiment is over with exceeding the iteration times.
            if self.counter_attention_shifts >= self.num_attention_shifts:
                self.is_running = False
        print(self.gap_task_chunks_results)
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
                x_text = self.pos_text[0]  # Reset the x_text.
                y_text += word_height

            if word != '':  # TODO: the first element is a null, might because of the split.
                self.surface.blit(word_surface, (x_text, y_text))
                x_text += word_width + space

    def generate_subtask(self):
        """
        Generate different types of subtasks.
        Please specify tasks' parameters here.
        :return: subtasks' answers.
        """
        if self.task_type_gap == "math task":
            # Task type 1: mathematical tasks - several double-digit multiplication tasks.
            ROW_EQUATIONS = 5
            for i in range(self.num_attention_shifts):
                # Generate ROW_EQUATIONS * 2 numbers between 10 and 99.
                numbers_random = random.sample(range(10, 99), 2 * ROW_EQUATIONS)
                # Statically allocate equations, without considering the line excess issue.
                gap_task = ""
                results = ""
                for j in range(ROW_EQUATIONS):
                    gap_task = gap_task + str(numbers_random[2 * j]) + " * " + str(numbers_random[2 * j + 1]) + " = \n"
                    results = results + str(numbers_random[2 * j]) + " * " + str(numbers_random[2 * j + 1]) + " = " + \
                              str(numbers_random[2 * j] * numbers_random[2 * j + 1]) + " "
                self.gap_task_chunks.append(gap_task)
                self.gap_task_chunks_results.append(results)

    def render_gap_tasks(self):
        if self.task_type_gap == "math task":
            line_list = self.gap_task_chunks[self.counter_attention_shifts].splitlines()
            x_line, y_line = self.pos_gap
            for line in line_list:
                line_surface = self.font_gap.render(line, 0, self.color_text)
                line_width, line_height = line_surface.get_size()
                self.surface.blit(line_surface, (x_line, y_line))
                y_line += line_height


def run_prototype():
    pygame.init()
    runner_trial = Runner(duration_gap=1500, duration_text=3000, amount_text=30, source_text=TEXTS_1,
                          task_type_gap="math task",
                          num_attention_shifts=5, color_background="black", color_text=(73, 232, 56),
                          size_text=70, size_gap=64, pos_text=(50, 250), pos_gap=(0, 0), title="trial_1")
    runner_trial.mainloop()
