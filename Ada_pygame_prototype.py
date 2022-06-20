import math
import random

import pygame

# TODO: the input texts' formats need to contain a space bar after every sentence. Change the code to recognize captal font in the future.
TEXTS_1 = "US banks JPMorgan Chase, Citigroup and Wells Fargo said on Wednesday (Jun 15) they had raised their prime lending rates by 75 basis points to 4.75 per cent, effective Thursday, " \
          "matching the Federal Reserve's rate hike earlier in the day. " \
          "The Fed raised its target interest rate by three-quarters of a percentage point, the most by the US central bank since 1994, " \
          "as it seeks to tame red-hot inflation. The central bank faces the task of charting a course for the economy to weather rate increases without a repeat of the 1970s-style predicament when the central bank's interest hikes aimed at fighting inflation resulted in a steep recession. " \
          "Inflation, which has become a hot-button political issue, has worsened with the Ukraine war, hitting market sentiment and piling pressure on to an already battered supply chain. " \
          "However, since banks make money on the difference between what they earn from lending and payouts on deposits and other funds, they typically thrive in a high interest rate environment."
TEXTS_2 = "If you've missed George Calombaris' friendly onscreen persona on MasterChef Australia, " \
          "you'll want to catch the show's former judge in Singapore at the ongoing GastroBeats. " \
          "The chef is part of an eight-hands collaboration featuring the MasterChef franchise alums Derek Cheong, " \
          "Genevieve Lee and Sarah Todd. As part of his event from Jun 20 to 26, " \
          "Calombaris will introduce several dishes including an interesting " \
          "'surf and turf' one comprising taramasalata (cured cod roe) with poached prawns and lup cheong (Chinese sausage) bolognaise. " \
          "Calombaris laid low following the collapse of his business empire in 2020 after admitting to underpaying AU$7.83m (S$7.56m) in wages to employees. " \
          "During the same period, Calombaris and his fellow MasterChef judges Matt Preston and Gary Mehigan were replaced after season 11, " \
          "when negotiations for a pay rise with broadcaster Network Ten broke down. Cue the pandemic, " \
          "which gave the 43-year-old a real chance to re-examine and redefine his life. " \
          "'I've learnt to pause, take a breath and ask if I want to do something and if that something is going to make me feel good,' " \
          "said the affable chef who is now the culinary director at the historic Hotel Sorrento in Melbourne. " \
          "Working on television is still something he enjoys, " \
          "so it is no surprise when Calombaris tells us that he will soon be back on our screens. " \
          "'We will be making some very exciting announcements in the next couple of weeks about a prime time show that we are first going to air in Australia,' " \
          "he told CNA Lifestyle. 'This show is special. I've seen the first couple of episodes, " \
          "and I'm blown away. I hate seeing myself on television, I really do, but making this felt good. " \
          "It felt authentic. There's nothing like it in that food space, so stay tuned. I'll be back on that TV of yours.' " \
          "Also in the works in an online platform called Culinary Wonderland, which he's co-founded and is scheduled for launch later this year. " \
          "'Imagine it as the Google for food but underpinned by some of the best foodies and chefs all over the world.' " \
          "But first things first: His maiden post-pandemic trip out of Australia to Singapore. 'I have a big soft spot for Singapore. " \
          "A lot of my best chef mates are there cooking at the highest level,' " \
          "he said excitedly. Besides his crazy-sounding surf and turf dish at GastroBeats " \
          "('it's going to be great,' he promised), he will also be serving a modern take on that Melbournian classic: Avocado toast. " \
          "And he'll be doing all three of the things that he loves best: 'Cooking for people, feeding people and meeting people.' " \
          "Once that's done, Calombaris said he plans to catch up with his friends and discover the depths of smaller hawker stalls and Singapore's heritage fare on his 10-day trip. " \
          "When asked what he's most looking forward to, Calombaris said, 'I'm just looking forward to eating chilli crab and chicken rice again.'"

# Avoid using string magic words. Declare global variables.
GAP_COUNT_TASK = "count task"
GAP_MATH_TASK = "math task"
# Modes
MODE_RSVP = "rsvp"
MODE_MANUAL = "manual"


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
        self.time_elapsed = 0
        self.counter_attention_shifts = 0

        # Parameters for text reading.
        self.index_content_texts = 0
        self.texts_chunks = []
        self.marks = [",", ".", "!", "?", ";", ":", "'"]
        self.threshold_bottom_num_text_reserve_sentence = 3     # If the words are less than 3, then reserve this sentence.
        self.threshold_top_num_text_abandon_sentence = 5        # If the words are more than 5, then abandon this sentence.
        self.log_actual_amounts_texts = []

        # Parameters for subtask type 2: count task.
        self.timer_count_gap_task = 0
        self.FPS_GAP_COUNT_TASK = 3  # Set the fps for flashing shapes in gap task type 2.
        self.counter_count_gap_task_shapes_change = 0
        self.duration_count_gap_task_shapes_change = self.duration_gap / self.FPS_GAP_COUNT_TASK  # Unit is ms.
        self.color_gap_count_task_shape = self.color_text
        self.size_gap_count_task_shape = 35

        # Declare the drawing space.
        surface_width, surface_height = self.surface.get_size()
        self.max_width = surface_width - self.MARGIN_RIGHT - self.MARGIN_LEFT
        self.max_height = surface_height - self.MARGIN_BOTTOM - self.MARGIN_TOP

        self.MARGIN_COO_LEFT_GAP_COUNT_TASK = 30
        self.MARGIN_COO_RIGHT_GAP_COUNT_TASK = surface_width - self.MARGIN_COO_LEFT_GAP_COUNT_TASK
        self.MARGIN_COO_TOP_GAP_COUNT_TASK = 45
        self.MARGIN_COO_BOT_GAP_COUNT_TASK = surface_height - self.MARGIN_COO_TOP_GAP_COUNT_TASK

        self.gap_math_task_chunks = []
        self.gap_math_task_chunks_results = []

        self.types_shapes_gap_count_task = ['circle', 'triangle', 'rectangle']
        self.shapes_gap_count_task_chunks = []  # Store all (across different attention shifts) the indices of shapes
        # to be displayed in a 2-d array.
        self.pos_gap_count_task_chunks = []  # Store all the positions of shapes. 2-d list,
        # index of items in a shift, and index of shifts.
        self.num_gap_count_task_shapes = int(math.floor((self.duration_gap / 1000) * self.FPS_GAP_COUNT_TASK))

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

        # Initialize variables by inner functions.
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
            self.timer_count_gap_task += self.time_elapsed

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
                if self.task_type_gap == GAP_MATH_TASK:
                    self.content_gap_temp = self.gap_math_task_chunks[self.counter_attention_shifts]
                    self.image_gap = self.font_gap.render(self.content_gap_temp, True, self.color_text)

                self.render_gap_tasks()  # Render content according to task type.

                if self.timer > self.duration_gap:
                    self.is_text_showing = True
                    self.timer = 0
                    self.surface.fill(self.color_background)
                    # Flush the counter for gap task type 2: count task.
                    self.counter_count_gap_task_shapes_change = 0

            pygame.display.flip()

            # The experiment is over with exceeding the iteration times.
            if self.counter_attention_shifts >= self.num_attention_shifts:
                self.is_running = False

        # Log here
        print(self.gap_math_task_chunks_results)  # TODO: log out the results here.
        print("The actual number of texts displayed are: " + str(self.log_actual_amounts_texts))

        pygame.quit()

    def split_amount_texts(self):
        word_list = self.texts.split()
        num_words = len(word_list)
        num_texts_chunks = int(math.ceil(num_words / self.amount_text))
        indices_words_contain_marks = []

        # TODO: split according to the sentences, this is also useful in the future schemes: like the context mode.
        for i in range(num_words):
            for mark in self.marks:
                if (list(word_list[i]))[-1] == mark:
                    indices_words_contain_marks.append(i)
                    break

        # Find the closest index (higher value) in the list.
        def find_closest_index(input_indices_list, input_index):
            input_indices_list.sort(reverse=True)
            difference = lambda input_indices_list: abs(input_indices_list - input_index)
            res = min(input_indices_list, key=difference)
            return res

        # Dynamically split texts with a boolean flag.
        is_over = False
        index_start = 0
        amount_left_texts = self.amount_text
        record_index_stop = 0
        while is_over is False:
            # Initialize the stop index.
            if amount_left_texts >= self.amount_text:
                index_stop = index_start + self.amount_text - 1
            else:
                index_stop = index_start + amount_left_texts - 1

            # If I don't use the copy(), but simply list a = list b, when b is sorted, so as a.
            copy_indices_words_contain_marks = indices_words_contain_marks.copy()
            index_closest_stop_mark = find_closest_index(copy_indices_words_contain_marks, index_stop)

            # Handle the exception that will cause a infinite loop (the closest index stuck in one position).
            if index_closest_stop_mark == record_index_stop:
                index_index_closest_stop_mark = indices_words_contain_marks.index(index_closest_stop_mark)
                index_closest_stop_mark = indices_words_contain_marks[index_index_closest_stop_mark + 1]

            index_stop = index_closest_stop_mark

            # Populate the content of texts.
            texts_chunk = ""
            for word in word_list[index_start:(index_stop + 1)]:
                texts_chunk = texts_chunk + word + " "
            self.texts_chunks.append(texts_chunk)
            self.log_actual_amounts_texts.append((index_stop + 1) - index_start)

            # When the loop is over, refresh the starting index.
            record_index_stop = index_stop
            index_start = index_stop + 1
            amount_left_texts = (num_words - 1) - index_stop

            if amount_left_texts == 0:
                is_over = True

    def render_texts_multiple_lines(self):
        words = self.content_text_temp.split(' ')
        space = self.font_text.size(' ')[0]
        x_text, y_text = self.pos_text

        # Render word by word.
        for word in words:
            word_surface = self.font_text.render(word, 0, self.color_text)
            word_width, word_height = word_surface.get_size()
            if x_text + word_width >= self.max_width:
                x_text = self.pos_text[0]  # Reset the x_text.
                y_text += word_height

            self.surface.blit(word_surface, (x_text, y_text))
            x_text += word_width + space

    def generate_subtask(self):
        """
        Generate different types of subtasks.
        Please specify tasks' parameters here.
        :return: subtasks' answers.
        """
        if self.task_type_gap == GAP_MATH_TASK:
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
                self.gap_math_task_chunks.append(gap_task)
                self.gap_math_task_chunks_results.append(results)

        elif self.task_type_gap == GAP_COUNT_TASK:
            # Task type 2: count task - count the number of a certain shape, e.g., circle, triangle, and rectangle.
            for j in range(self.num_attention_shifts):
                types_shapes_current_shift = []
                pos_shapes_current_shift = []
                results = []
                for i in range(self.num_gap_count_task_shapes):
                    types_shapes_current_shift.append(random.choice(self.types_shapes_gap_count_task))
                    pos_x = random.randint(self.MARGIN_COO_LEFT_GAP_COUNT_TASK, self.MARGIN_COO_RIGHT_GAP_COUNT_TASK)
                    pos_y = random.randint(self.MARGIN_COO_TOP_GAP_COUNT_TASK, self.MARGIN_COO_BOT_GAP_COUNT_TASK)
                    pos_shapes_current_shift.append((pos_x, pos_y))
                self.shapes_gap_count_task_chunks.append(types_shapes_current_shift)
                self.pos_gap_count_task_chunks.append(pos_shapes_current_shift)

                # Collect the appearances of different shapes.
                count_shape_circle = types_shapes_current_shift.count("circle")
                count_shape_triangle = types_shapes_current_shift.count("triangle")
                count_shape_rectangle = types_shapes_current_shift.count("rectangle")
                results.append("circle: " + str(count_shape_circle) + " ")
                results.append("triangle: " + str(count_shape_triangle) + " ")
                results.append("rectangle: " + str(count_shape_rectangle) + " ")
                self.gap_math_task_chunks_results.append(results)

    def render_gap_tasks(self):
        if self.task_type_gap == GAP_MATH_TASK:
            line_list = self.gap_math_task_chunks[self.counter_attention_shifts].splitlines()
            x_line, y_line = self.pos_gap
            for line in line_list:
                line_surface = self.font_gap.render(line, 0, self.color_text)
                line_width, line_height = line_surface.get_size()
                self.surface.blit(line_surface, (x_line, y_line))
                y_line += line_height

        elif self.task_type_gap == GAP_COUNT_TASK:
            # Update the timer
            if self.timer_count_gap_task >= self.duration_count_gap_task_shapes_change:
                self.timer_count_gap_task = 0
                self.counter_count_gap_task_shapes_change += 1
                self.surface.fill(self.color_background)
            else:
                type_shape = self.shapes_gap_count_task_chunks[self.counter_attention_shifts][
                    self.counter_count_gap_task_shapes_change]
                pos_shape = self.pos_gap_count_task_chunks[self.counter_attention_shifts][
                    self.counter_count_gap_task_shapes_change]

                if type_shape == "circle":
                    pygame.draw.circle(self.surface, self.color_gap_count_task_shape,
                                       pos_shape, self.size_gap_count_task_shape)
                elif type_shape == "triangle":
                    height = 2 * self.size_gap_count_task_shape
                    point_1 = (pos_shape[0], pos_shape[1])
                    point_2 = (pos_shape[0] - height / math.sqrt(3), pos_shape[1] - height)
                    point_3 = (pos_shape[0] + height / math.sqrt(3), pos_shape[1] - height)
                    pygame.draw.polygon(self.surface, color=self.color_gap_count_task_shape,
                                        points=[point_1, point_2, point_3])
                elif type_shape == "rectangle":
                    width = 2 * self.size_gap_count_task_shape
                    height = width
                    pygame.draw.rect(self.surface, self.color_gap_count_task_shape,
                                     [pos_shape[0], pos_shape[1], width, height], 0)


# TODO: add a configuration file to be read here.
# TODO: fix the sentences problem by endding them with marks.


def run_prototype():
    pygame.init()
    runner_trial = Runner(duration_gap=1500,
                          duration_text=30000,
                          amount_text=15,
                          source_text=TEXTS_1,
                          task_type_gap=GAP_COUNT_TASK,
                          num_attention_shifts=5,
                          color_background="black", color_text=(73, 232, 56),
                          size_text=70, size_gap=64, pos_text=(50, 250), pos_gap=(0, 0), title="trial_1")
    runner_trial.mainloop()
