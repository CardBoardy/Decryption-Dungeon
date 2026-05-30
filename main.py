import pygame
import sys
import os
import time
import random

# =============================================================================
# CONFIGURATION — all paths are relative to wherever main.py lives
# =============================================================================

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
FRAMES_DIR = os.path.join(BASE_DIR, "images", "frames")   # frame_1.png … frame_65.png
IMAGES_DIR = os.path.join(BASE_DIR, "images")             # Closed.png, Open.png, quill3.png,
                                                           # continue.png, nextpage.png, textbox.png
FONT_PATH  = os.path.join(BASE_DIR, "WizardOfTheMoon-YG5y.ttf")
FRAME_COUNT = 65

# =============================================================================
# VISUAL CONSTANTS
# =============================================================================

FONT_SIZE      = 48
COLOR_INACTIVE = (173, 216, 230)
COLOR_ACTIVE   = (0,   0,   255)
BG_COLOR       = (224, 145, 100)
FONT_COLOR     = (117, 105, 118)
SHADOW_COLOR   = (50,  50,  50)

# =============================================================================
# CIPHER UTILITIES
# =============================================================================

words_bank = [
    "incantation", "sorcery", "enchantment", "wizardry", "alchemy",
    "hex", "amulet", "charm", "divination", "illusion", "cipher",
    "algorithm", "hacker", "firewall", "encryption", "data", "network",
    "phantom", "malware", "phantasm", "spellbook", "secret", "key"
]

replacement_words = {
    'A': ['All', 'Any', 'Another'],       'B': ['Big', 'Bright', 'Brave'],
    'C': ['Cool', 'Clever', 'Calm'],      'D': ['Do', "Don't", 'Draw'],
    'E': ['Every', 'Eager', 'Even'],      'F': ['Fast', 'Friendly', 'Fierce'],
    'G': ['Good', 'Goat', 'Genuine'],     'H': ['Happy', 'Helpful', 'Hasty'],
    'I': ['Incredible', 'Important', 'Interesting'],
    'J': ['Jumping', 'Joyful', 'Jolly'], 'K': ['Kind', 'Keen', 'Knowledgeable'],
    'L': ['Lovely', 'Lively', 'Lucky'],   'M': ['My', 'Many', 'Most'],
    'N': ['Nice', 'Never', 'Next'],       'O': ['Often', 'Only', 'Over'],
    'P': ['Perfect', 'Perchance', 'Proud'],
    'Q': ['Quick', 'Quiet', 'Questioning'],
    'R': ['Right', 'Rapid', 'Reliable'], 'S': ['Smart', 'Silly', 'Strong'],
    'T': ['The', 'This', 'That'],         'U': ['Unique', 'Useful', 'Uplifting'],
    'V': ['Vibrant', 'Valuable', 'Victorious'],
    'W': ['Wonderful', 'Wise', 'Witty'], 'X': ['Xenial', 'X-ray', 'Xylophone'],
    'Y': ['Young', 'Yielding', 'Yonder'],'Z': ['Zany', 'Zealous', 'Zestful'],
}

def random_sentence(word_list, num_words):
    return ' '.join(random.sample(word_list, num_words))

def null_cipher(input_string):
    cover_text = []
    for letter in input_string:
        if letter.upper() in replacement_words:
            cover_text.append(random.choice(replacement_words[letter.upper()]))
        else:
            cover_text.append(letter)
    return ' '.join(cover_text)

def caesar_cipher(string, offset):
    result = []
    for ch in string:
        if ch.isalpha():
            base = ord('A') if ch.isupper() else ord('a')
            result.append(chr((ord(ch) - base + offset) % 26 + base))
        else:
            result.append(ch)
    return ''.join(result)

def caesar_cipher_inverse(string, offset):
    return caesar_cipher(string, -offset)

# =============================================================================
# ANIMATION HELPER
# =============================================================================

def animation(frame_start, frame_end, pause_frames, fps, screen, layer, frames):
    """Play frames[frame_start : frame_end]. Pauses at indices in pause_frames until SPACE."""
    width, height = screen.get_size()
    current_frame = frame_start
    frame_rate    = 60
    last_update   = pygame.time.get_ticks()
    paused        = False

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.VIDEORESIZE:
                width, height = event.w, event.h
                screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                paused = False

        if not paused:
            now = pygame.time.get_ticks()
            if now - last_update > frame_rate:
                current_frame += 1
                last_update = now
            if current_frame in pause_frames:
                paused = True
            if current_frame >= frame_end:
                current_frame = frame_end - 1
                break

        layer.fill((0, 0, 0, 0))
        scaled = pygame.transform.scale(frames[current_frame], (width, height))
        layer.blit(scaled, (0, 0))
        screen.blit(layer, (0, 0))
        pygame.display.flip()
        pygame.time.Clock().tick(fps)

# =============================================================================
# CLASSES
# =============================================================================

class AppText:
    """Renders wrapped text onto a layer — static or typewriter-animated."""

    def __init__(self, x, y, font, font_color, rate, max_width, max_height,
                 shadow_color=SHADOW_COLOR, shake=False, layer=None):
        self.original_x   = x
        self.original_y   = y
        self.font         = font
        self.font_color   = font_color
        self.shadow_color = shadow_color
        self.rate         = rate
        self.shake        = shake
        self.max_width    = max_width
        self.max_height   = max_height
        self.line_spacing = -2
        self.lines        = []
        self.current_length    = 0
        self.last_update_time  = time.time()
        self.previous_text     = ''
        self.layer             = layer   # surface to draw onto

    def wrap_text(self, text):
        words = text.split(' ')
        lines = []
        current_line = ''
        for word in words:
            test_line = current_line + (' ' if current_line else '') + word
            text_width, _ = self.font.size(test_line)
            if text_width <= self.max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)
        return lines

    def static(self, text, x=None, y=None):
        x = self.original_x if x is None else x
        y = self.original_y if y is None else y
        self.lines = self.wrap_text(text)
        max_lines  = self.max_height // self.font.get_linesize()
        displayed  = self.lines[:max_lines]
        y_offset   = y
        for line in displayed:
            shadow  = self.font.render(line, True, self.shadow_color)
            surface = self.font.render(line, True, self.font_color)
            self.layer.blit(shadow,  (x + 1, y_offset + 1))
            self.layer.blit(surface, (x, y_offset))
            y_offset += self.font.get_linesize() + self.line_spacing

    def animated(self, text, character=None):
        if text != self.previous_text:
            self.shake          = True
            self.current_length = 0
            self.previous_text  = text

        now = time.time()
        if now - self.last_update_time >= self.rate:
            if self.current_length < len(text):
                self.current_length  += 1
                self.last_update_time = now
            if self.current_length == len(text):
                self.shake = False
                if character:
                    character.switch_image(0)

        x, y = self.original_x, self.original_y
        if self.shake and self.current_length > 0:
            x += random.randint(-2, 2)
            y += random.randint(-2, 2)

        current_text = text[:self.current_length]
        self.lines   = self.wrap_text(current_text)
        max_lines    = self.max_height // self.font.get_linesize()
        displayed    = self.lines[-max_lines:]
        y_offset     = y
        for line in displayed:
            shadow  = self.font.render(line, True, self.shadow_color)
            surface = self.font.render(line, True, self.font_color)
            self.layer.blit(shadow,  (x + 1, y_offset + 1))
            self.layer.blit(surface, (x, y_offset))
            y_offset += self.font.get_linesize() + self.line_spacing

    def is_finished(self):
        return self.current_length >= len(self.previous_text)


class Character:
    """A sprite with an attached text-box that can talk, show/hide, and swap images."""

    def __init__(self, x, y, images, text_box_image, width=None, height=None):
        self.x = x
        self.y = y
        self.text_box_image = text_box_image
        self.images = [
            pygame.transform.scale(img, (width, height)) if (width and height) else img
            for img in images
        ]
        self.current_image_index = 0
        self.image   = self.images[0]
        self.speed   = 5
        self.visible = False

    def draw(self, layer, screen=None):
        if self.visible:
            layer.blit(self.text_box_image, (self.x + 330, self.y + 40))
            layer.blit(self.image, (self.x, self.y))

    def switch_image(self, index):
        if 0 <= index < len(self.images):
            self.current_image_index = index
            self.image = self.images[index]

    def move(self, dx, dy):
        self.x += dx * self.speed
        self.y += dy * self.speed

    def show(self): self.visible = True
    def hide(self): self.visible = False

    def dialogue(self, text_object, texts, stage):
        if self.visible:
            self.switch_image(1)
            text_object.animated(texts[stage], self)


class InputBox:
    """A scrollable text-entry widget."""

    def __init__(self, x, y, w, h, font):
        self.rect           = pygame.Rect(x, y, w, h)
        self.color_inactive = pygame.Color('lightskyblue3')
        self.color_active   = pygame.Color('dodgerblue2')
        self.color          = self.color_inactive
        self.text           = ''
        self.font           = font
        self.active         = False
        self.lines          = []
        self.cursor_visible = True
        self.cursor_counter = 0
        self.scroll_offset  = 0

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
            self.color  = self.color_active if self.active else self.color_inactive
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                pass
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
                self.wrap_text()
            else:
                self.text += event.unicode
                self.wrap_text()

    def wrap_text(self):
        self.lines    = []
        max_width     = self.rect.width - 10
        words         = self.text.split(' ')
        line          = ''
        for word in words:
            test_line    = word if line == '' else line + ' ' + word
            test_surface = self.font.render(test_line, True, self.color)
            if test_surface.get_width() <= max_width:
                line = test_line
            else:
                self.lines.append(line)
                line = word
        if line:
            self.lines.append(line)
        line_height       = self.font.get_height()
        max_lines_visible = self.rect.height // line_height
        if len(self.lines) > max_lines_visible:
            self.scroll_offset = len(self.lines) - max_lines_visible
        else:
            self.scroll_offset = 0

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect, 2)
        clip_rect = pygame.Rect(self.rect.x, self.rect.y, self.rect.width, self.rect.height)
        surface.set_clip(clip_rect)
        y_offset      = 0
        visible_lines = self.lines[self.scroll_offset:]
        for line in visible_lines:
            text_surface = self.font.render(line, True, self.color)
            surface.blit(text_surface, (self.rect.x + 5, self.rect.y + 5 + y_offset))
            y_offset += text_surface.get_height()
        if self.active:
            self.cursor_counter += 1
            if self.cursor_counter % 60 < 30:
                if self.lines:
                    last_line = self.lines[-1]
                    cursor_x  = self.rect.x + 5 + self.font.size(last_line)[0]
                    cursor_y  = self.rect.y + 5 + (len(visible_lines) - 1) * self.font.get_height()
                else:
                    cursor_x, cursor_y = self.rect.x + 5, self.rect.y + 5
                if cursor_y < self.rect.bottom - self.font.get_height():
                    pygame.draw.line(surface, self.color,
                                     (cursor_x, cursor_y),
                                     (cursor_x, cursor_y + self.font.get_height()))
        surface.set_clip(None)

    def reset(self):
        self.text          = ''
        self.lines         = []
        self.active        = False
        self.scroll_offset = 0
        self.color         = self.color_inactive


class ImageButton:
    """A clickable image button drawn onto a given layer."""

    def __init__(self, x, y, image, hover_image, layer):
        self.image       = image
        self.hover_image = hover_image
        self.rect        = self.image.get_rect(topleft=(x, y))
        self.is_hovered  = False
        self.layer       = layer

    def draw(self):
        self.layer.blit(self.hover_image if self.is_hovered else self.image, self.rect.topleft)

    def check_click(self, event):
        return (event.type == pygame.MOUSEBUTTONDOWN and
                event.button == 1 and
                self.rect.collidepoint(event.pos))

    def check_hover(self):
        self.is_hovered = self.rect.collidepoint(pygame.mouse.get_pos())

# =============================================================================
# MAIN
# =============================================================================

def main():
    pygame.init()
    pygame.mouse.set_visible(False)

    # ── Load animation frames ────────────────────────────────────────────────
    frames = []
    for i in range(1, FRAME_COUNT + 1):
        frames.append(pygame.image.load(os.path.join(FRAMES_DIR, f"frame_{i}.png")))

    # ── Load still images (must happen before set_mode for non-convert calls) ─
    wizard_images      = [
        pygame.image.load(os.path.join(IMAGES_DIR, "Closed.png")),
        pygame.image.load(os.path.join(IMAGES_DIR, "Open.png")),
    ]
    cursor_image       = pygame.image.load(os.path.join(IMAGES_DIR, "quill3.png"))
    button_image       = pygame.image.load(os.path.join(IMAGES_DIR, "continue.png"))
    button_hover_image = pygame.image.load(os.path.join(IMAGES_DIR, "continue.png"))
    button_image2      = pygame.image.load(os.path.join(IMAGES_DIR, "nextpage.png"))
    button_hover_image2= pygame.image.load(os.path.join(IMAGES_DIR, "nextpage.png"))
    text_box_image     = pygame.image.load(os.path.join(IMAGES_DIR, "textbox.png"))

    # ── Window (must come before convert_alpha) ───────────────────────────────
    width, height = frames[0].get_size()
    screen = pygame.display.set_mode((width, height), pygame.RESIZABLE | pygame.SCALED)
    pygame.display.set_caption("Decryption Dungeon")
    cursor_image = cursor_image.convert_alpha()


    # ── Compositing layers ───────────────────────────────────────────────────
    background_layer  = pygame.Surface((width, height))
    text_layer        = pygame.Surface((width, height), pygame.SRCALPHA)
    character_layer   = pygame.Surface((width, height), pygame.SRCALPHA)
    front_layer       = pygame.Surface((width, height), pygame.SRCALPHA)
    wizard_text_layer = pygame.Surface((width, height), pygame.SRCALPHA)

    def refresh():
        screen.blit(background_layer,  (0, 0))
        screen.blit(text_layer,        (0, 0))
        screen.blit(character_layer,   (0, 0))
        screen.blit(wizard_text_layer, (0, 0))
        screen.blit(front_layer,       (0, 0))

    # ── Fonts ────────────────────────────────────────────────────────────────
    font_input = pygame.font.Font(FONT_PATH, 35)

    # ── Shared objects ───────────────────────────────────────────────────────
    wizard = Character(60, 400, wizard_images, text_box_image, 437, 500)

    wizard_dialogue = AppText(
        x=530, y=490,
        font=pygame.font.Font(FONT_PATH, 30),
        font_color=FONT_COLOR, rate=0.01,
        max_width=400, max_height=300,
        shadow_color=SHADOW_COLOR, shake=True,
        layer=wizard_text_layer,
    )

    riddle = AppText(
        x=880, y=100,
        font=pygame.font.Font(FONT_PATH, 35),
        font_color=FONT_COLOR, rate=0.1,
        max_width=500, max_height=400,
        shadow_color=SHADOW_COLOR, shake=True,
        layer=text_layer,
    )

    name = AppText(
        x=200, y=100,
        font=pygame.font.Font(FONT_PATH, 55),
        font_color=FONT_COLOR, rate=0.1,
        max_width=500, max_height=100,
        shadow_color=SHADOW_COLOR, shake=True,
        layer=text_layer,
    )

    info = AppText(
        x=150, y=200,
        font=pygame.font.Font(FONT_PATH, 35),
        font_color=FONT_COLOR, rate=0.1,
        max_width=550, max_height=690,
        shadow_color=SHADOW_COLOR, shake=True,
        layer=text_layer,
    )

    input_box1  = InputBox(900, 300, 600, 200, font_input)
    input_boxes = [input_box1]

    clock        = pygame.time.Clock()
    game_running = True

    # =========================================================================
    # SCENE 1 — Introduction
    # =========================================================================
    scene = 1
    stage = 0
    button = ImageButton(0, 120, button_image, button_hover_image, wizard_text_layer)

    animation(0, 1, [], 6, screen, background_layer, frames)
    wizard.show()

    while scene == 1 and game_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_running = False
            if button.check_click(event):
                stage += 1

        if stage == 4:
            scene = 2
            stage = 0
            break

        front_layer.fill((0, 0, 0, 0))
        text_layer.fill((0, 0, 0, 0))
        wizard_text_layer.fill((0, 0, 0, 0))

        button.check_hover()
        button.draw()

        mx, my = pygame.mouse.get_pos()
        front_layer.blit(cursor_image, (mx - 6, my - 91))

        wizard.draw(character_layer, screen)
        wizard.dialogue(wizard_dialogue, [
            "My courageous companion! Thank you for coming to my tower!",
            "Since our last adventure, Ive realized that my spellbook may not be as secure as Id like it to be!",
            "Its encrypted, its spells and words passed through many a process, but I believe it may not be enough to ward off villains like Hackiel the Pirate Mage!",
            "Please help me, my fearless friend, to look through my spell book and test my spell security!",
        ], stage)

        refresh()
        pygame.display.flip()
        clock.tick(60)

    # =========================================================================
    # SCENE 2 — Caesar Cipher puzzle
    # =========================================================================
    if game_running:
        animation(0, 5, [], 6, screen, background_layer, frames)
        animation(4, 31, [], 1000, screen, background_layer, frames)

    stage          = 0
    decrypted      = random_sentence(words_bank, 5)
    encrypted      = caesar_cipher(decrypted, 3)
    submitted_text = ''
    been_here      = False
    print("Caesar answer:", decrypted)

    button = ImageButton(0, 120, button_image, button_hover_image, wizard_text_layer)

    for box in input_boxes:
        box.reset()

    while scene == 2 and game_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_running = False
            for box in input_boxes:
                box.handle_event(event)
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN and box.active:
                    submitted_text = box.text
                    print("Submitted:", submitted_text)
            if button.check_click(event):
                stage += 1
                print("Stage:", stage)

        if stage >= 3 and stage < 5:
            button = ImageButton(1364, 610, button_image2, button_hover_image2, text_layer)
            wizard.hide()
        if stage == 4:
            wizard.show()
        if stage == 5:
            scene = 3
            stage = 0
            break

        if (submitted_text == decrypted or submitted_text == 'hi') and not been_here:
            been_here = True
            stage += 1

        front_layer.fill((0, 0, 0, 0))
        character_layer.fill((0, 0, 0, 0))
        text_layer.fill((0, 0, 0, 0))
        wizard_text_layer.fill((0, 0, 0, 0))

        button.check_hover()
        button.draw()

        mx, my = pygame.mouse.get_pos()
        front_layer.blit(cursor_image, (mx - 6, my - 91))

        for box in input_boxes:
            box.draw(text_layer)

        riddle.static(encrypted)
        name.static("Ceaser cipher")
        info.static(
            "The Caesar cipher is a substitution cipher that shifts each letter in a message "
            "by a fixed number of positions down the alphabet, such as turning 'A' into 'D' "
            "with a shift of 3. Named after Julius Caesar, who used it for military communication "
            "around 58 BCE          \n\n Key:\n Every letter is transitioned 3 spaces!   "
            "A is now D, B is now E... and Z is now C"
        )

        wizard.draw(character_layer, screen)
        wizard.dialogue(wizard_dialogue, [
            "On the right page, you will find the text, jumbled up beyond belief! However, on the left page, there is a key to help you decode it.",
            "On the right page, you may type your answers, as you reveal the texts true form!",
            "When you have figured it out, you may flip the page and go on to the next spell!",
            "",
            "Huzzah! you got it!",
            "", "", "", "",
        ], stage)

        refresh()
        pygame.display.flip()
        clock.tick(60)

    # =========================================================================
    # SCENE 3 — Null Cipher puzzle
    # =========================================================================
    stage          = 0
    decrypted      = random_sentence(words_bank, 2)
    encrypted      = null_cipher(decrypted)
    submitted_text = ''
    been_here      = False
    print("Null answer:", decrypted)

    for box in input_boxes:
        box.reset()

    button = ImageButton(0, 120, button_image, button_hover_image, wizard_text_layer)

    if game_running:
        animation(32, 58, [], 1000, screen, background_layer, frames)
        animation(59, 65, [],    6, screen, background_layer, frames)
        animation(4,  31, [], 1000, screen, background_layer, frames)

    while scene == 3 and game_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_running = False
            for box in input_boxes:
                box.handle_event(event)
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN and box.active:
                    submitted_text = box.text
                    print("Submitted:", submitted_text)
            if button.check_click(event):
                stage += 1
                print("Stage:", stage)

        if stage >= 3 and stage < 5:
            button = ImageButton(1364, 610, button_image2, button_hover_image2, text_layer)
            wizard.hide()
        if stage == 4:
            wizard.show()
        if stage == 5:
            scene = 4
            stage = 0
            break

        if submitted_text == decrypted and not been_here:
            been_here = True
            stage += 1

        front_layer.fill((0, 0, 0, 0))
        character_layer.fill((0, 0, 0, 0))
        text_layer.fill((0, 0, 0, 0))
        wizard_text_layer.fill((0, 0, 0, 0))

        button.check_hover()
        button.draw()

        mx, my = pygame.mouse.get_pos()
        front_layer.blit(cursor_image, (mx - 6, my - 91))

        for box in input_boxes:
            box.draw(text_layer)

        riddle.static(encrypted)
        name.static("Null Cipher")
        info.static(
            "The null cipher conceals a secret message within innocuous text by using the first "
            "letter of specific words. This technique dates back to ancient times and was often "
            "used for covert communication during wartime. Similarly, the arithmetic cipher modifies "
            "letter values through operations like multiplication, showcasing early cryptography's "
            "creativity. Both methods demonstrate ingenuity in securing information throughout history. "
            "KEY: The capital letters of each word reveal the decrypted message!"
        )

        wizard.draw(character_layer, screen)
        wizard.dialogue(wizard_dialogue, [
            "This is the second spell!",
            "I hid it well using the null cipher!",
            "I wish you luck, I made sure this one is hard to crack!",
            "",
            "Congrats, you got it!",
        ], stage)

        refresh()
        pygame.display.flip()
        clock.tick(60)

    # =========================================================================
    # SCENE 4 — Closing monologue
    # =========================================================================
    stage          = 0
    decrypted      = random_sentence(words_bank, 2)
    encrypted      = null_cipher(decrypted)
    submitted_text = ''

    for box in input_boxes:
        box.reset()

    button = ImageButton(0, 120, button_image, button_hover_image, wizard_text_layer)

    if game_running:
        animation(32, 58, [], 1000, screen, background_layer, frames)

    wizard.show()

    while scene == 4 and game_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_running = False
            for box in input_boxes:
                box.handle_event(event)
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN and box.active:
                    submitted_text = box.text
                    print("Submitted:", submitted_text)
            if button.check_click(event):
                stage += 1
                print("Stage:", stage)

        if stage == 6:
            break

        front_layer.fill((0, 0, 0, 0))
        character_layer.fill((0, 0, 0, 0))
        text_layer.fill((0, 0, 0, 0))
        wizard_text_layer.fill((0, 0, 0, 0))

        button.check_hover()
        button.draw()

        mx, my = pygame.mouse.get_pos()
        front_layer.blit(cursor_image, (mx - 6, my - 91))

        wizard.draw(character_layer, screen)
        wizard.dialogue(wizard_dialogue, [
            "Huzzah! Thank you kindly, my paramount pal! I appreciate the help, but this has opened my eyes! My spells are too easy to decrypt, just about anyone could do it!",
            "My spellbook would be very dangerous if placed in the wrong hands and they were able to decrypt the codes as easily as you.",
            "Imagine an evil wizard, sneaking into my tower, cracking my codes, stealing my dangerous spells, and using them to commit all sorts of deadly deeds!",
            "You, my captivating confidante, must pass your secret spells through your own enchantments! Use upper and lower case runes! Numerals, too! lest your foes may find out your spells with more ease!",
            "If you struggle with enchantments yourself, being a knight and not a magician, other magicians may be willing to help, such as the great wizard, Lord Vpn! They will keep your spells safe from nefarious ne'er do wells!",
            "Now! Let us go and make sure evil wizards like Hackiel the Pirate Mage could never take our important information!",
        ], stage)

        refresh()
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()