from pygame_functions import *
import numpy as np
import pygame
import random
import copy

pygame.init()

# Générer l'écran et la musique
scale = 30
screen = pygame.display.set_mode((18 * scale, 20 * scale))
music_loader()

# Graphique : police d'écriture, couleur des blocs
font=pygame.font.SysFont('lucidaconsole', int(0.9 * scale))
colors = [(23, 126, 137), (82, 72, 156), (64, 98, 157), (246, 86, 79), (244, 211, 91), (137, 210, 220), (228, 183, 229)]

# Vitesse
frame_threshold = 9
clock = pygame.time.Clock()

# Paramétrage initial
tetris_field, score, level, lines, current_block, next_block, frame_count, line_breaking = initialisation()
pause = False

done = False

#move_queue = random_player()
#print(move_queue)

while not done:

    frame_count += 1

	# Représentation graphique du tableau
    screen.fill((0, 0, 0))
    pygame.draw.rect(screen, (20, 20, 20), pygame.Rect(0, 0, 10 * scale, 20 * scale))
    next_block_drawer(next_block, screen, colors, scale)
    text_writer(score, level, lines, screen, font, scale)
    
        
    movement_block = copy.copy(current_block) # Bloc temporaire, qui prend la place du "vrai"
    # bloc si on est en mode de jeu normal (ni pause, ni ligne qui clignote) et si ses coordonnées
    # sont bonnes

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
            
        if event.type == pygame.KEYDOWN: # Actions utilisateur
            if event.key == pygame.K_q: movement_block.x -= 1
            if event.key == pygame.K_d: movement_block.x += 1
            if event.key == pygame.K_s: movement_block.y += 1
            if event.key == pygame.K_m: movement_block.rotate()
            if event.key == pygame.K_l: movement_block.antirotate()
            if event.key == pygame.K_v: pause = not pause
    
        coord_correct(movement_block)
        
    
    if pause == True:
        
        pause_writer(screen, font, scale)
    
    elif line_breaking == False:
        
        #queue_reader(move_queue)
        #print(move_queue)
        
        draw_field(tetris_field + full_size_block(current_block), screen, colors, scale = scale)
    
        if block_collision(tetris_field, movement_block, type = None) == False:
            current_block = movement_block
          
        if frame_count % frame_threshold == 0: # Vérifier collisions et faire tomber bloc si possible
        
            if bottom_collision(current_block) or block_collision(tetris_field, current_block, "y"):
                tetris_field = tetris_field + full_size_block(current_block)
                
                if line_completed(tetris_field) is not None:
                
                    starting_frame = frame_count
                    line_breaking = True
                    line_indices = line_completed(tetris_field)
                
                else:
                    current_block, next_block = next_block, random_block()
                    #move_queue = random_player()
                    #print(move_queue)
    	    
                if np.any(tetris_field[0,:] > 0): # Fin du jeu
                    
                    pygame.draw.rect(screen, (20, 20, 20), pygame.Rect(0, 0, 10 * scale, 20 * scale))
                    defeat_writer(screen, font, scale)
                    pygame.display.flip()
                
                    new_event = pygame.event.wait()
                
                    while new_event.type != pygame.KEYDOWN and new_event.type != pygame.QUIT:
                        new_event = pygame.event.wait()
                
                    else:
                        if new_event.type == pygame.QUIT:
                            done = True
                            continue
                        else:
                            tetris_field, score, level, lines, current_block, next_block, frame_count, line_breaking = initialisation()

    	    
            else: current_block.y += 1 
                
    else: # Si au moins une ligne est complétée, ça doit clignoter
        
        current_animation = frame_count - starting_frame
        total_duration = 105
        flash_duration = total_duration * 2 // 6
        
        draw_field(tetris_field, screen, colors, scale = scale)
                
        if current_animation < total_duration and current_animation % flash_duration < flash_duration // 2 :
            
            for line in line_indices:
                line_rect = pygame.Rect(0, line * scale, 10 * scale, scale)
                pygame.draw.rect(screen, (255,255,255), line_rect)
                
        elif current_animation < total_duration and current_animation > 5 * flash_duration // 2:
        
            for line in line_indices:
                line_rect = pygame.Rect(0, line * scale, 10 * scale, scale)
                pygame.draw.rect(screen, (20,20,20), line_rect)
                
        elif current_animation > total_duration:
            line_breaking = False
            lines += len(line_indices)
            score += score_calculator(tetris_field, level)   
            tetris_field = remove_lines_completed(tetris_field)
            current_block, next_block = next_block, random_block()
            #move_queue = random_player()
            #print(move_queue)     


    pygame.display.flip()

    
    clock.tick(100)