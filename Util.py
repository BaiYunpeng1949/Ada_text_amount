import pygame


def read_from_file(path_text):
    # Read materials from a text file. While the texts are all stacked up in one line.
    with open(path_text) as f:
        texts = f.read()
    return texts


def create_waiting_canvas(content_texts):
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
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    is_waiting = False

    pygame.quit()