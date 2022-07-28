import math
import zmq
import pygame
from nltk import tokenize
from socket import *

from Display_output import Config


def read_from_file(path_text):
    # Read materials from a text file. While the texts are all stacked up in one line.
    with open(path_text) as f:
        texts = f.read()
    return texts


def generate_latin_square(n: int, start_el: int = 1):  # Create the latin-square sequence.
    row = [i for i in range(1, n + 1)]
    row = row[start_el - 1:] + row[:start_el - 1]
    return [row[i:] + row[:i] for i in range(n)]


def create_waiting_canvas(content_texts, key_or_button, key_pressed):
    """
    Create a waiting canvas/widget to wait for experimenter's operations to proceed.
    :param key_or_button: Determine its key press event or mouse click event.
    :param content_texts: the instruction content.
    :return:
    """
    # Initiate the parameters
    pos_surface = (0, 0)
    font = "arial"
    size_font = 50
    color_text = (73, 232, 56)
    pos_y_text = 350

    # Create the canvas
    pygame.init()

    waiting_surface = pygame.display.set_mode(pos_surface, pygame.FULLSCREEN)
    waiting_font_text = pygame.font.SysFont(font, size_font)
    surface_instruction = waiting_font_text.render(content_texts, True, color_text)
    x_pos_centralization = (waiting_surface.get_size()[0] - surface_instruction.get_size()[0]) / 2
    waiting_surface.blit(surface_instruction, (x_pos_centralization, pos_y_text))

    pygame.display.flip()

    is_waiting = True
    while is_waiting:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and key_or_button is pygame.KEYDOWN:
                if event.key == key_pressed:
                    is_waiting = False
            elif event.type == pygame.MOUSEBUTTONDOWN and key_or_button is pygame.MOUSEBUTTONDOWN:
                if event.button == Config.RIGHT_CLICK_RING_MOUSE:
                    is_waiting = False

    pygame.quit()


def split_reading_texts(num_sentences, reading_material):  # Functions related to the text operations.
    """
    Split the reading texts into a certain amount of texts. Currently refers to the number of full sentences.
    :param num_sentences: The amount of texts. Indicating the number of information. Will add sentence processing later.
    :param reading_material: The text reading material.
    :return: The split reading text material.
    """
    # Split the reading material into full sentences.
    generated_full_sentences = tokenize.sent_tokenize(reading_material)
    num_sentences_total = len(generated_full_sentences)

    # Allocate assigned number of texts into chunks.
    len_chunks_designated = math.ceil(num_sentences_total / num_sentences)
    chunks = []
    counter_added_num_sentences = 0
    current_chunk = ""
    index_pointer_sentences = 0
    while True:
        current_chunk = current_chunk + generated_full_sentences[index_pointer_sentences] + " "
        # Update local variables.
        counter_added_num_sentences += 1
        index_pointer_sentences += 1

        # The legitimacy of the current chunk.
        if counter_added_num_sentences >= num_sentences:
            chunks.append(current_chunk)
            counter_added_num_sentences = 0
            current_chunk = ""

        # The legitimacy of the usage of the whole reading texts.
        if index_pointer_sentences >= num_sentences_total:
            if len(chunks) < len_chunks_designated:     # The chunk has not been extended yet.
                chunks.append(current_chunk)
            break

    # Texts info record.
    num_words_chunks = []   # Get the number of words per chunk
    for chunk in chunks:
        num_words_chunk = len(chunk.split())
        num_words_chunks.append(num_words_chunk)

    num_chunks = len(chunks)    # Get the number of chunks.
    return chunks, num_chunks, num_words_chunks


def create_IPA_computing_connection():
    """
    This function builds up the connection socket with local ipa calculation file.
    :return:
    """
    s = socket(AF_INET, SOCK_DGRAM)
    s.bind(('', Config.PORT_RANDOM))
    return s
