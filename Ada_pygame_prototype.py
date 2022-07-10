import math
import nltk
import numpy as np
import os
import pygame
import random
import sys
from nltk import tokenize

import CONFIG


class Runner:
    def __init__(self, participant_name, experiment_time, trial_information,
                 duration_gap, duration_text, amount_text, source_text_path, task_type_gap,
                 mode_update, condition_exp,
                 color_background, color_text, size_text, size_gap,
                 pos_text, pos_gap, title="AdaPrototype"):
        # Package setup for splitting sentences.
        nltk.download('punkt')

        # Set experiment parameters.
        self.participant_name = participant_name
        self.experiment_time = experiment_time
        self.trial_information = trial_information

        # Initialize input parameters.
        self.duration_gap = duration_gap
        self.duration_text = duration_text
        self.amount_text = amount_text
        self.texts_path = source_text_path
        self.task_type_gap = task_type_gap
        self.num_attention_shifts = 9   # Initialize this parameter.    # TODO: need to be a input instead of an output in real settings.
        self.mode_text_update = mode_update
        self.condition_experiment = condition_exp
        self.color_background = color_background
        self.color_stop_reminder_background = "white"
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
        self.MARGIN_BOTTOM = 0
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
        self.timer_elapsed_read_text_mode_manual = 0
        self.counter_attention_shifts = 0

        # Parameters for text reading.
        self.texts = self.read_from_file()
        self.index_content_texts = 0
        self.texts_chunks = []

        self.marks = [",", ".", "!", "?", ";", ":", "'", '"']   # Take care of "'" and '"'. Kind of tricky here.
        self.threshold_bottom_num_text_reserve_sentence = 3     # If the words are less than 3, then reserve this sentence.
        self.threshold_top_num_text_abandon_sentence = 5        # If the words are more than 5, then abandon this sentence.

        self.wps_dynamical_duration_text = 80  # Words per second for dynamically changing duration of text reading at different text chunks.
        self.offset_seconds_dynamical_duration_text = 2  # The unit is second.

        # Intialize logs.
        self.log_actual_amounts_texts = []
        self.log_time_elapsed_read_text_mode_manual = []  # Store participants' reading speed: how many time for a certain amount of words.
        self.log_time_elapsed_read_text_mode_rsvp = []      # Self update time chunk allocation.
        self.log_time_elapsed_waiting_next_trial = []

        # Parameters for subtask type 2: count task.
        self.timer_count_gap_task = 0
        self.FPS_GAP_COUNT_TASK = 2  # Set the fps for flashing shapes in gap task type 2.
        self.counter_count_gap_task_shapes_change = 0   # The shape changes in a single attention shift.
        self.duration_count_gap_task_shapes_change = 1000 / self.FPS_GAP_COUNT_TASK  # Unit is ms.
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
        self.num_gap_count_task_shapes = int(math.floor(self.duration_gap / self.duration_count_gap_task_shapes_change))

        self.content_text_temp = CONFIG.BLANK_LINE
        self.content_gap_temp = "Ga Ga Ga Ga Ga"

        self.font_type_selected = pygame.font.get_fonts()[0]  # We select the system's first font, "arial" font.

        self.font_text = pygame.font.SysFont(self.font_type_selected, self.size_text)
        self.image_text = self.font_text.render(self.content_text_temp, True, self.color_text)
        self.rect_text = self.image_text.get_rect()
        setattr(self.rect_text, ANCHOR, self.pos_text)

        # Settings for the "present all" mode.
        self.opacity_texts_present_all = 255
        self.num_scrolling_press_keys_present_all = 0  # This variable will record the current number of scrolling operations, positive numbers negative numbers mean scrolling up and down.

        self.y_range_texts_display_present_all_mode = self.max_height
        self.surface_words = self.font_text.render(" ", 0, self.color_text)
        self.height_line = self.surface_words.get_size()[1]
        self.num_lines_tolerated_present_all_mode = int(
            math.floor(self.y_range_texts_display_present_all_mode / self.height_line))
        self.offset_y_texts_static_present_all_mode = self.y_range_texts_display_present_all_mode - self.num_lines_tolerated_present_all_mode * self.height_line + self.MARGIN_TOP

        self.boundary_num_pages = self.get_num_pages()

        # Settings for the "contextual adaptive" mode.
        self.opacity_texts_contextual_adaptive_context = 135
        self.opacity_texts_contextual_adaptive = 255

        # Settings for the "adaptive" mode.
        self.opacity_texts_adaptive = 255

        # Settings for gap tasks.
        self.font_gap = pygame.font.SysFont(self.font_type_selected, self.size_gap)
        self.image_gap = self.font_gap.render(self.content_gap_temp, True, self.color_text)
        self.rect_gap = self.image_gap.get_rect()
        setattr(self.rect_gap, ANCHOR, self.pos_gap)

        # Initialize variables by inner functions.
        self.prepare_materials_dynamically()

    def prepare_materials_dynamically(self):
        # Run the whole material prepare procedure here.
        # Split texts.
        self.split_full_sentences_chunks()
        # Allocate time.
        self.allocate_time_adaptively()
        # Split the text according to the given chunk size.
        # self.split_short_sentences_texts() # Deprecated text split method. But it will be reserved here.
        # Generate the subtasks.
        self.generate_subtask()

    def centralize_instructions_postition(self, text_instruction, y_pos_instruction):
        """
        The function dynamically put the text instruction on the center position.
        :param text_instruction:
        :return:
        """
        # Get the current canvas size.
        canvas_width = self.surface.get_size()[0]
        # Calculate the shown text instruction size (Assume one line).
        surface_instruction = self.font_text.render(text_instruction, 0, self.color_text)
        width_instruction = surface_instruction.get_size()[0]
        # Calculate the text instruction position to make it is placed on the central horizontally.
        half_width_instruction = width_instruction / 2
        central_width_canvas = canvas_width / 2
        x_pos_instruction = central_width_canvas - half_width_instruction

        # Update on the canvas.
        self.surface.blit(surface_instruction,
                          (x_pos_instruction, y_pos_instruction))

    def mainloop(self):
        self.is_running = True
        while self.is_running:
            for event in pygame.event.get():
                # Normally close the game.
                if event.type == pygame.QUIT:
                    self.is_running = False
                # Key press detection.
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.is_running = False
                    elif event.key == pygame.K_SPACE:
                        # Only on the manual mode, can update the reading content by pressing the button.
                        if self.is_text_showing and self.mode_text_update is CONFIG.MODE_MANUAL:
                            # Clear up and update.
                            self.surface.fill(self.color_background)
                            self.is_text_showing = False
                            self.timer = 0
                            # Index for the text display, could be added.
                            if self.index_content_texts < len(self.texts_chunks) - 1:
                                self.index_content_texts += 1
                            # Index of the gap task, could not be added with the last one.
                            if self.counter_attention_shifts < self.num_attention_shifts:
                                self.counter_attention_shifts += 1

                            # Collect the time spent on the certain amount of text.
                            self.log_time_elapsed_read_text_mode_manual.append(self.timer_elapsed_read_text_mode_manual)
                            self.timer_elapsed_read_text_mode_manual = 0
                    # On the present-all mode, use up and down keys to scroll the texts.
                    elif event.key == pygame.K_PAGEUP or event.key == pygame.K_PAGEDOWN:
                        if self.is_text_showing and self.mode_text_update is CONFIG.MODE_PRESENT_ALL:
                            # Clear up to avoid occlusions.
                            self.surface.fill(self.color_background)
                            # Update the scrolling parameters, including how many lines are operated, scroll up or down.
                            if event.key == pygame.K_PAGEUP:
                                # Scrolling up. But not exceed the upper boundary.
                                if self.num_scrolling_press_keys_present_all < 0:
                                    self.num_scrolling_press_keys_present_all += 1
                            elif event.key == pygame.K_PAGEDOWN:
                                # Scrolling down. Not exceed the lower boundary.
                                if self.num_scrolling_press_keys_present_all > (-(self.boundary_num_pages - 1)):
                                    # Minus 1 because initially participants are in the 1st page, and parameter self.num_scrolling_press_keys_present_all starts from 0.
                                    self.num_scrolling_press_keys_present_all -= 1

            # Count the time elapsed.
            self.time_elapsed = self.clock.tick(self.fps)
            # Update the timer.
            self.timer += self.time_elapsed

            # Display text content. Check the legimacy of indicies, in case of index out of range.
            if self.counter_attention_shifts < self.num_attention_shifts:
                # Display the texts and gap task.
                if self.is_text_showing:
                    # Draw content.
                    # In the RSVP mode. Get the current texts. display different chunks of texts.
                    if (self.mode_text_update is CONFIG.MODE_ADAPTIVE) or (
                            self.mode_text_update is CONFIG.MODE_MANUAL) or (
                            self.mode_text_update is CONFIG.MODE_CONTEXTUAL):
                        self.content_text_temp = self.texts_chunks[self.index_content_texts]
                    # In the Present-all mode, display all texts once.
                    elif self.mode_text_update is CONFIG.MODE_PRESENT_ALL:
                        self.content_text_temp = self.texts

                    # Adaptively arrange the duration of the text reading. The global variable duration_text is updated.
                    self.duration_text = self.log_time_elapsed_read_text_mode_rsvp[self.index_content_texts]

                    # Display texts. No matter which mode.
                    self.render_texts_multiple_lines()  # Render text content word by word, line by line.

                    # Update the status automatically if in the rsvp mode or in the present-all mode.
                    if self.timer > self.duration_text:
                        if (self.mode_text_update is CONFIG.MODE_ADAPTIVE) or (
                                self.mode_text_update is CONFIG.MODE_PRESENT_ALL) or (
                                self.mode_text_update is CONFIG.MODE_CONTEXTUAL):
                            self.counter_attention_shifts += 1
                            self.is_text_showing = False
                            self.timer = 0
                            self.surface.fill(self.color_background)

                            # RSVP update mode for text display.
                            self.index_content_texts += 1

                            # Update log file for the RSVP mode and present all mode.
                            self.log_time_elapsed_read_text_mode_rsvp.append(self.duration_text)
                        # Record the time spent on a certain amount of words in the manual mode.
                        elif self.mode_text_update is CONFIG.MODE_MANUAL:
                            self.timer_elapsed_read_text_mode_manual += self.time_elapsed

                # Display the gap content.
                elif self.is_text_showing is False:
                    if self.task_type_gap == CONFIG.GAP_MATH_TASK:
                        self.content_gap_temp = self.gap_math_task_chunks[self.counter_attention_shifts]
                        self.image_gap = self.font_gap.render(self.content_gap_temp, True, self.color_text)

                    self.render_gap_tasks()  # Render content according to task type.

                    if self.timer > self.duration_gap:
                        self.is_text_showing = True
                        self.timer = 0
                        self.surface.fill(self.color_background)
                        # Flush the counter for gap task type 2: count task.
                        self.counter_count_gap_task_shapes_change = 0

                        # Pause after the gap task is over, wait for the participant to start next reading session.
                        # Display information.
                        self.surface.fill(self.color_background)
                        self.centralize_instructions_postition(
                            text_instruction="To start reading, click [R] on the ring",
                            y_pos_instruction=350)
                        pygame.display.flip()
                        # Pause here.
                        is_waiting_participant_next_trial = True
                        # Timer settings
                        timer_waiting = 0
                        while is_waiting_participant_next_trial:
                            # Timer update.
                            time_elapsed_waiting = self.clock.tick(self.fps)
                            timer_waiting = timer_waiting + time_elapsed_waiting
                            for event in pygame.event.get():
                                if event.type == pygame.MOUSEBUTTONDOWN:
                                    if event.button == 3:  # 3 stands for the right click.
                                        is_waiting_participant_next_trial = False  # Jump out of the loop.
                                        # Clear the scene.
                                        self.surface.fill(self.color_background)
                                        # Update the time elapsed while waiting
                                        self.log_time_elapsed_waiting_next_trial.append(timer_waiting)

            pygame.display.flip()

            # The experiment is over with exceeding the iteration times. It only works in rsvp mode.
            if self.counter_attention_shifts >= self.num_attention_shifts:
                self.is_running = False

        # Log here, once the tial is over. In case data lost due to following wrong operations.
        self.generate_log_file()

        # Show the last scene to help with record where the reader stopped.
        # Display the white background to indicate participants to stop.
        self.render_texts_multiple_lines()
        pygame.display.flip()

        # Waiting for the experimenter to press the Space key to show the instruction to the participant.
        # Consider the natural operation: Esc for stop and Space for proceeding. Noted in the experimenter specification.
        is_waiting_experimenter_questions = True
        is_questions_finished = False
        while is_waiting_experimenter_questions:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        # If the questions are not finished, then show the instructions.
                        if is_questions_finished is False:
                            # Add feedback to the key press for the experimenter. The feedback is the screen black out.
                            self.surface.fill(self.color_background)
                            self.centralize_instructions_postition(
                                text_instruction="Now please remove the glasses and answer questions",
                                y_pos_instruction=350)
                            # Update the flag.
                            is_questions_finished = True
                        elif is_questions_finished:
                            self.surface.fill(self.color_background)
                            self.centralize_instructions_postition(
                                text_instruction="To start the next trial, click [R] on the ring",
                                y_pos_instruction=350)
                            # Update the flag.
                            is_waiting_experimenter_questions = False
                        # Update the scene.
                        pygame.display.flip()

        # Waiting for the participant to click the R button on the ringmouse to start the next trial (quit the current one, the new one will be started automatically).
        is_waiting_participant_next_study = True
        while is_waiting_participant_next_study:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 3:    # 3 stands for the right click.
                        is_waiting_participant_next_study = False  # Jump out of the loop.

        # Quit the game at the main method.
        pygame.quit()

    def read_from_file(self):
        # Read materials from a text file. While the texts are all stacked up in one line.
        with open(self.texts_path) as f:
            texts = f.read()
        return texts

    def allocate_time_adaptively(self):
        """
        The basic time allocation algorithm, our adaptive mode's heart.
        :return: time allocation - log_time_elapsed_read_text_mode_rsvp
        """
        for i in range(len(self.texts_chunks)):
            num_words = self.log_actual_amounts_texts[i]
            duration_text = int(math.ceil(num_words / self.wps_dynamical_duration_text) + \
                            self.offset_seconds_dynamical_duration_text) * 1000
            self.log_time_elapsed_read_text_mode_rsvp.append(duration_text)

    def split_full_sentences_chunks(self):
        """
        This function split texts with full stops, i.e., stop with ".".
        And allocate different text chunks with our proposed idea of adaptive and contextual adaptive methods.
        :return: text chunks, time allocated, and some log files.
        """
        # Get the word range reference.
        amount_words_reference = self.amount_text

        # Split the sentences.
        # Store all number of words and texts in each sentence. Initialize the dictionary.
        dic_texts_sentences = {
            "number of words per sentence": [0],
            "texts in each sentence": [""]
        }

        split_full_sentences = tokenize.sent_tokenize(self.texts)
        for i in range(len(split_full_sentences)):
            if i == 0:
                dic_texts_sentences["number of words per sentence"][i] = len(split_full_sentences[i].split())
                dic_texts_sentences["texts in each sentence"][i] = split_full_sentences[i]
            else:
                dic_texts_sentences["number of words per sentence"].append(len(split_full_sentences[i].split()))
                dic_texts_sentences["texts in each sentence"].append(split_full_sentences[i])

        # Allocate sentences into chunks.
        # Current logic: every chunk composes 3 parts: earlier context (1 sentence, low opacity),
        # current texts (multiple sentences, number of words > reference, full opacity), later context (1 sentence, low opacity).
        # Initialize parameters.
        index_earlier_context = 0
        index_texts_start = 0
        index_texts_ending = 0
        index_later_context = 0
        counter_num_chunks = 0
        index_pointer = 0   # A sliding pointer.

        while True:
            # Refresh the buffers.
            buffer_num_words_chunk = 0
            buffer_texts_chunk = []

            # Allocate for the texts first.
            # Initialize buffer for counting number of words.
            buffer_num_words_chunk += dic_texts_sentences["number of words per sentence"][index_pointer]

            if buffer_num_words_chunk >= amount_words_reference:
                # Just one sentence in this text chunk.
                index_texts_start = index_pointer
                index_texts_ending = index_pointer
            else:
                # Feed texts in a loop.
                index_texts_start = index_pointer
                while True:
                    # Normal situations.
                    if index_pointer + 1 < len(split_full_sentences):
                        index_pointer += 1
                        buffer_num_words_chunk += dic_texts_sentences["number of words per sentence"][index_pointer]    # Check the eligibility of the index_pointer.
                    # Special situations: not enough data. Has already reached the bottom boundary.
                    else:
                        # Stop here.
                        index_texts_ending = index_pointer
                        # Break because the index is out of range.
                        break

                    # Jump out of the loop because number of words is enough.
                    if buffer_num_words_chunk >= amount_words_reference:
                        # Update indices.
                        index_texts_ending = index_pointer
                        break

            # Allocate the corresponding earlier and later chunks.
            if index_texts_start - 1 < 0:
                # There is no earlier chunk since it is the first chunk.
                index_earlier_context = index_texts_start   # 0.
            else:
                index_earlier_context = index_texts_start - 1
            if index_texts_ending + 1 >= len(split_full_sentences):
                # There is no later chunk since it is the last chunk.
                index_later_context = index_texts_ending    # The last index.
            else:
                index_later_context = index_texts_ending + 1

            # Add sentences into buffer.
            for sentence in split_full_sentences[index_earlier_context:(index_later_context + 1)]:
                buffer_texts_chunk.append(sentence + " ")
            self.texts_chunks.append(buffer_texts_chunk)
            self.log_actual_amounts_texts.append(buffer_num_words_chunk)

            # Update counters.
            counter_num_chunks += 1
            # "index_pointer" stopped at the last chunk, now move to the new chunk.
            index_pointer += 1

            # Jump out of the chunk.
            if index_pointer >= len(split_full_sentences):
                break

        # Update the parameters.
        self.num_attention_shifts = len(self.texts_chunks)

    def split_short_sentences_texts(self):
        # Split texts into short sentences. Not have to be full stops that end with ".".
        word_list = self.texts.split()
        num_words = len(word_list)
        num_texts_chunks = int(math.ceil(num_words / self.amount_text))
        # Store the indices of words contain marks. Simple stops, maybe not full stop.
        indices_words_contain_marks = []

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
                # Redefine the number of attention shifts.
                self.num_attention_shifts = len(self.texts_chunks)

        # Adaptively allocate reading duration according to the number of words
        for i in range(len(self.texts_chunks)):
            num_words = self.log_actual_amounts_texts[i]
            duration_text = int(math.ceil(num_words / self.wps_dynamical_duration_text) + \
                            self.offset_seconds_dynamical_duration_text) * 1000
            self.log_time_elapsed_read_text_mode_rsvp.append(duration_text)

    def render_texts_multiple_lines(self):
        # Refresh the canvas/scene/window. Or the opacity will just be aggregated.
        if self.is_running:
            # While the trial is still on the run.
            self.surface.fill(self.color_background)
        elif self.is_running is False:
            # If the trial is stopped by Esc key. Or terminates normally. Display the white background to indicate participants to stop.
            self.surface.fill(self.color_stop_reminder_background)

        # Add some texts into the buffer to counter errors when pressing the esc key in the first gap task.
        if self.content_text_temp is CONFIG.BLANK_LINE:
            # Display texts only when they were displayed.
            self.content_text_temp = ["The experimenter stopped the trial in advance.", ""]

        # To be reminded that the displayed texts are stored in self.content_text_temp.
        # Determine the current texts to be displayed.
        texts_earlier_context_display = ""
        texts_middle = ""
        texts_later_context_display = ""

        # Only under the adaptive or contextual adaptive modes, sentences are stored in lists.
        if self.mode_text_update is CONFIG.MODE_ADAPTIVE or self.mode_text_update is CONFIG.MODE_CONTEXTUAL:
            # The 1st chunk.
            if self.index_content_texts == 0:
                for i in range(len(self.content_text_temp) - 1):
                    texts_middle += self.content_text_temp[i]
                texts_later_context_display = self.content_text_temp[
                    -1]
            # The last chunk.
            elif self.index_content_texts == (len(self.texts_chunks) - 1):
                texts_earlier_context_display = self.content_text_temp[0]
                for i in range(1, len(self.content_text_temp)):  # Change this
                    texts_middle += self.content_text_temp[i]
            # Middle chunks.
            else:
                texts_earlier_context_display = self.content_text_temp[0]
                for i in range(1, (len(self.content_text_temp) - 1)):  # Change this
                    texts_middle += self.content_text_temp[i]
                texts_later_context_display = self.content_text_temp[-1]
        elif self.mode_text_update is CONFIG.MODE_PRESENT_ALL:
            texts_middle = self.texts

        # Auxiliary tool for rendering texts.
        def render_words(texts_display, x_text, y_text, opacity):
            words = texts_display.split(' ')
            space = self.font_text.size(' ')[0]

            # Some position related parameters update.
            offset_y_texts_dynamical = (self.y_range_texts_display_present_all_mode + self.MARGIN_TOP) * self.num_scrolling_press_keys_present_all  # The page update. Page by page.
            offset_y_texts_static = self.offset_y_texts_static_present_all_mode

            # Render the texts word by word.
            count_num_lines = 1  # Have to start from 1! - reserved especially for the "present all" mode.
            for word in words:
                word_surface = self.font_text.render(word, 0, self.color_text)
                word_surface.set_alpha(opacity)

                word_width, word_height = word_surface.get_size()
                if x_text + word_width >= self.max_width:
                    # Update the counter. Already starts from the second line.
                    count_num_lines += 1
                    # Update the position.
                    x_text = self.pos_text[0]  # Reset the x_text.
                    y_text += word_height
                    # Check if need to create a new page.
                    if (count_num_lines % self.num_lines_tolerated_present_all_mode == 1) and (count_num_lines > 1):
                        y_text += offset_y_texts_static

                # Horizontally lay up the words.
                self.surface.blit(word_surface, (x_text, y_text + offset_y_texts_dynamical))
                x_text += word_width + space
            return x_text, y_text

        # Distinguish between different modes: adaptive and contextual adaptive.
        if self.mode_text_update is CONFIG.MODE_ADAPTIVE:
            render_words(texts_display=texts_middle,
                         x_text=self.pos_text[0],
                         y_text=self.pos_text[1],
                         opacity=self.opacity_texts_adaptive)
        elif self.mode_text_update is CONFIG.MODE_CONTEXTUAL:
            # texts_display = texts_earlier_context_display + texts_middle + texts_later_context_display
            if self.index_content_texts > 0:
                x_middle_start_text, y_middle_start_text = render_words(texts_display=texts_earlier_context_display,
                                                                        x_text=self.pos_text[0],
                                                                        y_text=self.pos_text[1],
                                                                        opacity=self.opacity_texts_contextual_adaptive_context)
            elif self.index_content_texts == 0:
                x_middle_start_text, y_middle_start_text = self.pos_text
            x_later_start_text, y_later_start_text = render_words(texts_display=texts_middle,
                                                                  x_text=x_middle_start_text,
                                                                  y_text=y_middle_start_text,
                                                                  opacity=self.opacity_texts_contextual_adaptive)
            render_words(texts_display=texts_later_context_display,
                         x_text=x_later_start_text,
                         y_text=y_later_start_text,
                         opacity=self.opacity_texts_contextual_adaptive_context)
        elif self.mode_text_update is CONFIG.MODE_PRESENT_ALL:
            render_words(texts_display=texts_middle,
                         x_text=self.pos_text[0],
                         y_text=self.pos_text[1],
                         opacity=self.opacity_texts_present_all)

    def get_num_pages(self):
        """
        Get the number of lines and number of pages when displaying all texts at once. Especially in the "present all" mode.
        :return: count_num_lines
        """
        words = self.texts.split(' ')
        space = self.font_text.size(' ')[0]
        x_text, y_text = self.pos_text

        # Render word by word.
        count_num_lines = 1  # Have to start from 1!
        for word in words:
            word_surface = self.font_text.render(word, 0, self.color_text)
            word_width, word_height = word_surface.get_size()
            if x_text + word_width >= self.max_width:
                # Update the counter. Already starts from the second line.
                count_num_lines += 1
                x_text = self.pos_text[0]
            x_text += word_width + space

        num_pages = int(math.ceil(count_num_lines / self.num_lines_tolerated_present_all_mode))
        return num_pages

    def generate_subtask(self):
        """
        Generate different types of subtasks.
        Please specify tasks' parameters here.
        :return: subtasks' answers.
        """
        if self.task_type_gap == CONFIG.GAP_MATH_TASK:
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

        elif self.task_type_gap == CONFIG.GAP_COUNT_TASK:
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
        if self.task_type_gap == CONFIG.GAP_MATH_TASK:
            line_list = self.gap_math_task_chunks[self.counter_attention_shifts].splitlines()
            x_line, y_line = self.pos_gap
            for line in line_list:
                line_surface = self.font_gap.render(line, 0, self.color_text)
                line_width, line_height = line_surface.get_size()
                self.surface.blit(line_surface, (x_line, y_line))
                y_line += line_height

        elif self.task_type_gap == CONFIG.GAP_COUNT_TASK:
            # Update the timer
            self.timer_count_gap_task += self.time_elapsed
            if self.timer_count_gap_task >= self.duration_count_gap_task_shapes_change:
                # Move to the next shape if the current shape exceeds time.
                self.timer_count_gap_task = 0
                if self.counter_count_gap_task_shapes_change < self.num_gap_count_task_shapes - 1:
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

    def generate_log_file(self):
        """
        This function records experiment results into text files.
        And also store some of the configuration and calculated parameters to the global variables, to enable the initialization of the function "last scene".
        :return: text files, and global variables.
        """
        folder_path = "Results/" + self.experiment_time + "/" + self.participant_name + "/"

        # Check the existence of the folder. If not, create one.
        if os.path.exists(folder_path) is False:
            os.makedirs(folder_path)

        if self.condition_experiment == CONFIG.CONDITION_POS_HOR:
            # file_path = folder_path + self.trial_information + "_pos" + str(self.pos_text[0]) + ".txt"
            file_path = folder_path + self.trial_information + ".txt"
        if not os.path.exists(file_path):
            with open(file_path, 'w') as f:
                f.write("Participant Information: " + "\n")
                f.write("Participant Name: " + self.participant_name + "\n")
                f.write("Experiment Time: " + self.experiment_time + "\n")
                f.write("Trial Number / Condition: " + self.trial_information + "\n")
                f.write("Text source path: " + self.texts_path + "\n")

                f.write("\n")
                f.write("Configuration: " + "\n")
                f.write("Duration of gap task: " + str(self.duration_gap) + " ms" + "\n")
                f.write("Duration of text reading: " + str(self.duration_text) + " ms" + "\n")
                f.write("Amount of text in a chunk: " + str(self.amount_text) + " words" + "\n")
                f.write("Text read: " + self.texts_path + "\n")
                f.write("The type of task type: " + self.task_type_gap + "\n")
                f.write("The number of attention shifts: " + str(self.num_attention_shifts) + "\n")
                f.write("The mode of text content update: " + self.mode_text_update + "\n")
                f.write("The color of OHMD background: " + str(self.color_background) + "\n")
                f.write("The color of OHMD texts: " + str(self.color_text) + "\n")
                f.write("The size of texts: " + str(self.size_text) + " pixels" + "\n")
                f.write("The size of gap tasks: " + str(self.size_gap) + " pixels" + "\n")
                f.write("The position of texts: " + str(self.pos_text) + "\n")
                f.write("The position of gap tasks: " + str(self.pos_gap) + "\n")

                f.write("\n")
                f.write("Logs: " + "\n")
                for i in range(self.num_attention_shifts):
                    f.write("The " + str(i + 1) + " text chunk: " + "\n")
                    f.write("Gap task results: " + str(self.gap_math_task_chunks_results[i]) + "\n")
                    if i < len(self.log_time_elapsed_waiting_next_trial):   # Cater to the excession error.
                        f.write("Time elapsed while waiting before the new reading tiral: " + str(self.log_time_elapsed_waiting_next_trial[i]) + " ms." + "\n")
                        f.write("The total time spent on the non-reading trial: " + str(self.log_time_elapsed_waiting_next_trial[i] + self.duration_gap) + " ms." + "\n")

                f.write("\n")
                for i in range(len(self.texts_chunks)):
                    f.write("The " + str(i + 1) + " attention shift: " + "\n")
                    if (self.mode_text_update is CONFIG.MODE_ADAPTIVE) or (
                            self.mode_text_update is CONFIG.MODE_CONTEXTUAL):
                        f.write("Amount of texts in this chunk: " + str(self.log_actual_amounts_texts[i]) +
                                "    Time spent: " + str(self.log_time_elapsed_read_text_mode_rsvp[i]) + " ms" + "\n")
                        # Log the text chunks if the current mode is Adaptive.
                        texts_display_log = ""
                        for j in range(len(self.texts_chunks[i])):
                            texts_display_log += self.texts_chunks[i][j]
                        f.write(texts_display_log + "\n")
                    elif self.mode_text_update is CONFIG.MODE_MANUAL:
                        if i < len(self.log_time_elapsed_read_text_mode_manual):
                            f.write("Amount of texts in this chunk: " + str(self.log_actual_amounts_texts[i]) +
                                    "    Time spent: " + str(
                                self.log_time_elapsed_read_text_mode_manual[i]) + " ms" + "\n")
                        else:
                            f.write("Amount of texts in this chunk: " + str(self.log_actual_amounts_texts[i]) + "\n")

                        f.write("The average elapsed time is: " +
                                str(np.mean(self.log_time_elapsed_read_text_mode_manual)) + " ms")
                    elif self.mode_text_update is CONFIG.MODE_PRESENT_ALL:
                        f.write("    Time spent: " + str(self.log_time_elapsed_read_text_mode_rsvp[i]) + " ms" + "\n")


def run_prototype():
    # Run the prototype.
    pygame.init()
    runner_trial = Runner(participant_name="Bai Yunpeng",
                          experiment_time="28 June 2022",
                          trial_information="trial1",
                          duration_gap=500,
                          duration_text=5000,
                          amount_text=35,
                          source_text_path="Reading Materials/Pilot version 1 July/Education_403.txt",
                          task_type_gap=CONFIG.GAP_COUNT_TASK,
                          mode_update=CONFIG.MODE_PRESENT_ALL,
                          condition_exp=CONFIG.CONDITION_POS_HOR,
                          color_background="black", color_text=(73, 232, 56),
                          size_text=60, size_gap=64,
                          pos_text=(50, 50), pos_gap=(0, 0))
    runner_trial.mainloop()


def run_pilots(name, time, id_participant):
    # Auxiliary functions.
    # Create the latin-square sequence.
    def generate_latin_square(n: int, start_el: int = 1):
        row = [i for i in range(1, n + 1)]
        row = row[start_el - 1:] + row[:start_el - 1]
        return [row[i:] + row[:i] for i in range(n)]

    # Start the training session.
    num_conditions_trainings = len(CONFIG.CONDITIOMS_TRAININGS)
    for i in range(num_conditions_trainings):
        duration_gap_current_condition_training = CONFIG.CONDITIOMS_TRAININGS[(i + 1)]["duration_gap"]
        mode_update_current_condition_training = CONFIG.CONDITIOMS_TRAININGS[(i + 1)]["mode_update"]
        # The training session starts
        print("The training session starts.")

        # Initiate.
        pygame.init()

        # Initiate the pilot study actuator.
        runner_training_current = Runner(participant_name=name + "_" + str(id_participant),
                                         experiment_time=time,
                                         trial_information="training_" + str(i + 1),
                                         duration_gap=duration_gap_current_condition_training,
                                         duration_text=5000,
                                         amount_text=35,
                                         source_text_path=CONFIG.SOURCE_TEXTS_PATH_LIST[0],
                                         # The first text is for training session.
                                         task_type_gap=CONFIG.GAP_COUNT_TASK,
                                         mode_update=mode_update_current_condition_training,
                                         condition_exp=CONFIG.CONDITION_POS_HOR,
                                         color_background="black", color_text=(73, 232, 56),
                                         size_text=60, size_gap=64,
                                         pos_text=(50, 50), pos_gap=(0, 0))

        print("During the trainging session.......Now is the training: " + str(
            i + 1) + " .........")

        # Run the pilot.
        runner_training_current.mainloop()

    print("The training session is finished, the formal study will begin.")
    # Wait for the formal studies to be started.
    pygame.init()

    waiting_surface = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    waiting_font_text = pygame.font.SysFont("arial", 50)
    surface_instruction = waiting_font_text.render(
        "This is the end of the training session. Can we proceed to the formal study?", True, (73, 232, 56))
    x_pos_centralization = (waiting_surface.get_size()[0] - surface_instruction.get_size()[0]) / 2
    waiting_surface.blit(surface_instruction, (x_pos_centralization, 350))

    pygame.display.flip()

    is_waiting = True
    while is_waiting:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    is_waiting = False

    pygame.quit()

    # Start the studies.
    # Get the number of conditions.
    num_conditions_studies = len(CONFIG.CONDITIONS_STUDIES)

    # Get the latin square sequence.
    sequences_latin_square = generate_latin_square(n=num_conditions_studies)

    # Get the seqeunce of pilot study for this particular parcitipant according to latin square.
    index_current_participant_in_sequences = int(id_participant % num_conditions_studies) - 1
    sequence_current_participant = sequences_latin_square[index_current_participant_in_sequences]

    # Went through all condition for participants.
    for i in range(num_conditions_studies):
        # Determine the pilot study condition according to the participant's id.
        index_current_participant_in_conditions = sequence_current_participant[i]
        duration_gap_current_condition_studies = CONFIG.CONDITIONS_STUDIES[index_current_participant_in_conditions][
            "duration_gap"]
        mode_update_current_condition_studies = CONFIG.CONDITIONS_STUDIES[index_current_participant_in_conditions][
            "mode_update"]

        # Initiate.
        pygame.init()

        # Initiate the pilot study actuator.
        runner_pilot_current = Runner(participant_name=name + "_" + str(id_participant),
                                      experiment_time=time,
                                      trial_information="sequence_" + str(i + 1) + "_" +
                                                        str(mode_update_current_condition_studies) + "_" +
                                                        str(duration_gap_current_condition_studies),
                                      duration_gap=duration_gap_current_condition_studies,
                                      duration_text=5000,
                                      amount_text=35,
                                      source_text_path=CONFIG.SOURCE_TEXTS_PATH_LIST[i + 1],
                                      # The first text is for training session.
                                      task_type_gap=CONFIG.GAP_COUNT_TASK,
                                      mode_update=mode_update_current_condition_studies,
                                      condition_exp=CONFIG.CONDITION_POS_HOR,
                                      color_background="black", color_text=(73, 232, 56),
                                      size_text=60, size_gap=64,
                                      pos_text=(50, 50), pos_gap=(0, 0))

        print("During the study.......Now is the condition: " + str(
            index_current_participant_in_conditions) + " .........")

        # Run the pilot.
        runner_pilot_current.mainloop()

    print("All the studies are over, thank you for participating.")
    sys.exit()
