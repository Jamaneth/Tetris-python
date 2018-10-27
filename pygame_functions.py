import pygame
import numpy as np
import random
import copy
import pyautogui


#################################
#
# Définition des tétrominos
#
#################################

class Tetromino:
    
    def __init__(self):
        self.shape = np.zeros((2, 4))
        self.x = 4
        self.y = 0
        self.height = 2
        self.width = 3
        
    def rotate(self):
        self.shape = np.rot90(self.shape, k = 3)
        self.height, self.width = self.width, self.height
        return(self)
    
    def antirotate(self):
        self.shape = np.rot90(self.shape)
        self.height, self.width = self.width, self.height
        return(self)
    
    def empty(self, orientation):
        
        non_empty_x = np.apply_along_axis(sum, 0, self.shape)
        non_empty_y = np.apply_along_axis(sum, 1, self.shape)
        
        if orientation == "left":
            return np.amin(np.where(non_empty_x > 0))
        
        elif orientation == "right":
            return self.width - np.amax(np.where(non_empty_x > 0)) - 1
        
        elif orientation == "top":
            return np.amin(np.where(non_empty_y > 0))
        
        elif orientation == "bottom":
            return self.height - np.amax(np.where(non_empty_y > 0)) - 1
        
    def simple_shape(self):
        new_shape = self.shape[~np.all(self.shape == 0, axis=1)]
        return new_shape[:,~np.all(new_shape == 0, axis=0)]
    
    def simple_height(self):
        return np.ma.size(self.simple_shape(), 0)
    
    def simple_width(self):
        return np.ma.size(self.simple_shape(), 1)

    
class Line(Tetromino):
    
    def __init__(self):
        Tetromino.__init__(self)
        self.shape = np.zeros((3, 4))
        self.shape[1,:] = 1
        self.height = 3
        self.width = 4
    
class JBlock(Tetromino):
    
    def __init__(self):
        Tetromino.__init__(self)
        self.shape = np.array(([0,0,0], [1,1,1], [0,0,1]))
        self.height = 3
        
class LBlock(Tetromino):
    
    def __init__(self):
        Tetromino.__init__(self)
        self.shape = np.array(([0,0,0], [1,1,1], [1,0,0]))
        self.height = 3
        
class Square(Tetromino):
    
    def __init__(self):
        Tetromino.__init__(self)
        self.shape = np.array(([1,1], [1,1]))
        self.width = 2
        
class SBlock(Tetromino):
    
    def __init__(self):
        Tetromino.__init__(self)
        self.shape = np.array(([0,1,1], [1,1,0]))
        
class ZBlock(Tetromino):
    
    def __init__(self):
        Tetromino.__init__(self)
        self.shape = np.array(([1,1,0], [0,1,1]))
        
class TBlock(Tetromino):
    
    def __init__(self):
        Tetromino.__init__(self)
        self.shape = np.array(([0,0,0], [1,1,1], [0,1,0]))
        self.height = 3


#################################
#
# Fonctions d'interaction
#
#################################


def random_block(difficulty = "normal"):

    # Génère un bloc aléatoirement
    #   - Le mode "easy" est surtout là pour débugguer si besoin
    #   - Le mode "hard" est pour vérifier que la combinaison de blocks S et Z est impossible
    
    colors = [(23, 126, 137), (82, 72, 156), (64, 98, 157), (246, 86, 79), (244, 211, 91), (137, 210, 220), (228, 183, 229)]
    
    if difficulty == "easy":
        block_list = [Line(), Square()]
        return block_list[random.randrange(0,2)]
        
    elif difficulty == "normal":
        block_list = [Line(), Square(), LBlock(), JBlock(), ZBlock(), SBlock(), TBlock()]
        random_number = random.randrange(0,7)
        block = block_list[random_number]
        block.shape = block.shape * (1 + random_number / 10)
        return block
        
    elif difficulty == "hard":
        block_list = [ZBlock(), SBlock()]
        return block_list[random.randrange(0,2)]
    

def full_size_block(block, x_max = 9, y_max = 19):

    # block: Tetromino type
    # Scale un petit tetromino à l'échelle du plateau, ce qui permet de le superposer
    # à la grille

    full_line = np.c_[np.zeros((block.simple_height(), block.x + block.empty("left") - 1)),
                      block.simple_shape(),
                      np.zeros((block.simple_height(), 10 - block.x - block.width + block.empty("right") + 1))]
    
    full_table = np.r_[np.zeros((block.y + block.empty("top"), 10)),
                       full_line,
                       np.zeros((20 - block.y - block.height + block.empty("bottom"), 10))]
    
    return(full_table)
    
    
def coord_correct(block):

    # Si le block a une valeur qui dépasse au niveau de l'axe des x, on corrige ça pour
    # éviter de sortir des limites du cadre !
    
    
    # Si ça dépasse au niveau des côtés
    if block.x + block.empty("left") - 1 < 0:
        block.x = 1 - block.empty("left")
    elif 10 - block.x - block.width + block.empty("right") + 1 < 0:
        block.x = 10 - block.width + block.empty("right") + 1
        
    # Si ça tombe trop bas
    if block.y + block.simple_height() > 20:
        block.y = 20 - block.height



def block_collision(tetris_field, block, type):

    # Détermine si un futur mouvement provoquera une collision
    
    function_block = copy.copy(block) # Eviter d'écraser une valeur quelconque dans le bloc initial
    
    if type == "y":
        function_block.y += 1
        
    elif type == "+x":
        function_block.x += 1
        
    elif type == "-x":
        function_block.x -= 1
        
    elif type == "rot":
        function_block.rotate()
        
    elif type == "antirot":
        function_block.antirotate()
        
    coord_correct(function_block)
    
    return np.any(tetris_field + full_size_block(function_block) >= 2)
    
    
def bottom_collision(block, max_y = 20):

	# Eviter que les blocs tombent à l'infini

    return block.y + block.simple_height() + block.empty("top") >= 20


def line_completed(tetris_field):

    full_lines = np.argwhere(np.all(tetris_field >= 1, axis = 1))
    
    if(len(full_lines) > 0):
        return(full_lines)
        
    else:
        return(None)

def remove_lines_completed(tetris_field):

    full_lines = line_completed(tetris_field)
    number_lines = len(full_lines)
    
    tetris_field = np.concatenate((np.zeros((number_lines ,10)), np.delete(tetris_field, full_lines, axis = 0)))
    
    return tetris_field
    
    
def score_calculator(tetris_field, level):

    lines_gotten = len(line_completed(tetris_field))
    score_scale = [0, 40, 100, 300, 1200]
    
    return score_scale[lines_gotten] * (level + 1)
    
    
#################################
#
# Dessin
#
#################################

def line_completed_draw(tetris_field, screen, colors, clock, x_max = 10, scale = 20):
    
    line_indices = line_completed(tetris_field)
    
    line_colors = [(255, 255, 255), (255, 255, 102)]
    
    draw_field(tetris_field, screen, colors)
    
    for frame in range(0,120):
    
        color_choice = int(frame // 20 > 10)
        
        for line in line_indices:
            line_rect = pygame.Rect(0, line * scale, 10 * scale, scale)
            pygame.draw.rect(screen, line_colors[color_choice], line_rect)
            pygame.display.update(line_rect)
	
    #clock.tick(120)
    
    for line in line_indices:
        pygame.draw.rect(screen, (60, 60, 60), pygame.Rect(0, line * scale, 10 * scale, scale))
        
    pygame.display.flip()    
    pygame.time.wait(500)


def draw_field(field_array, screen, colors, x_max = 10, y_max = 20, scale = 20):
    for x in range(0, x_max):
        for y in range(0, y_max):
            if field_array[y,x] > 0:
                color_digit = int(str(field_array[y,x])[-1])
                try:
                    pygame.draw.rect(screen, colors[color_digit], pygame.Rect(x * scale, y * scale, scale, scale))
                except IndexError:
                    pass
                
                
def next_block_drawer(block, screen, colors, scale = 20):
    for x in range(0, block.width):
        for y in range(0, block.height):
            if block.shape[y,x] > 0:
                color_digit = int(str(block.shape[y,x])[-1])
                pygame.draw.rect(screen, colors[color_digit], pygame.Rect((x + 12) * scale, (y + 15) * scale, scale, scale))                



#################################
#
# Text writers
#
#################################


                
def text_writer(score, level, lines, screen, font, scale = 20):
    
    score_title = font.render("Score", 1,(255,255,255))
    score_text = font.render(str(score), 1, (255, 255, 255))

    screen.blit(score_title, (12 * scale, 2 * scale))
    screen.blit(score_text, (12 * scale, 3 * scale))

    level_title = font.render("Level", 1, (255,255,255))
    level_text = font.render(str(level), 1, (255, 255, 255))
    
    screen.blit(level_title, (12 * scale, 6 * scale))
    screen.blit(level_text, (12 * scale, 7 * scale))    
    
    line_title = font.render("Lines", 1, (255, 255, 255))
    line_text = font.render(str(lines), 1, (255,255,255))

    screen.blit(line_title, (12 * scale, 10 * scale))
    screen.blit(line_text, (12 * scale, 11 * scale))    
    
    block_title = font.render("Next:", 1, (255, 255, 255))
    
    screen.blit(block_title, (12 * scale, 14 * scale))
    
    
def defeat_writer(screen, font, scale = 20):

    defeat_title = font.render("You lost! :-(", 1, (232, 133, 39))
    defeat_text1 = font.render("Press any key", 1, (232, 133, 39))
    defeat_text2 = font.render("to try again.", 1, (232, 133, 39))
    
    screen.blit(defeat_title, (1.5 * scale, 3 * scale))
    screen.blit(defeat_text1, (1.5 * scale, 6 * scale))
    screen.blit(defeat_text2, (1.5 * scale, 8 * scale))


def pause_writer(screen, font, scale = 20):

    pause_title = font.render("PAUSE", 1, (232, 133, 39))
    pause_text1 = font.render("Press 'V' to", 1, (232, 133, 39))
    pause_text2 = font.render("resume game", 1, (232, 133, 39))
    
    screen.blit(pause_title, (1.5 * scale, 3 * scale))
    screen.blit(pause_text1, (1.5 * scale, 6 * scale))
    screen.blit(pause_text2, (1.5 * scale, 8 * scale))


#################################
#
# Initialisation
#
#################################
    
    
def initialisation():
    score = 0
    level = 9
    lines = 0
    current_block, next_block = random_block(), random_block()
    frame_count = 0
    line_breaking = False
    tetris_field = np.zeros((20, 10))
    
    return tetris_field, score, level, lines, current_block, next_block, frame_count, line_breaking
    

def music_loader(music_type = "A"):

    pygame.mixer.music.load('./music/Music-' + music_type + '.ogg')
    pygame.mixer.music.play(loops = -1)
    
    
    
#################################
#
# Amusement random
#
#################################

def random_player():
    
    move_queue = []
    
    lateral_moves = random.randint(0,5)
    lateral_direction = ["left", "right"][random.randint(0,1)]
    lateral_queue = [lateral_direction] * lateral_moves
    move_queue += lateral_queue
    
    rotations = random.randint(0,3)
    rotation_direction = ["clock", "anticlock"][random.randint(0,1)]
    rotation_queue = [rotation_direction] * rotations
    move_queue += rotation_queue
    
    return(move_queue)


def move_reader(move):

    if move == "left":
        pyautogui.press("a")
            
    elif move == "right":
        pyautogui.press("d")

    elif move == "clock":
        pyautogui.press(";")
    
    elif move == "anticlock":
        pyautogui.press("l")
         

def queue_reader(move_queue):
         
    if move_queue is not None and len(move_queue) >= 1:
        next_move = move_queue.pop()
        move_reader(next_move)
        
        
        
        
        