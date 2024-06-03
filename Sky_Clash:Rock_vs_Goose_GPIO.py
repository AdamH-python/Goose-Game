# Import modules used in functions and inputs from the game
import pygame
import random
from sys import exit
import RPi.GPIO as gpio
import math

# Warnings can disrupt the game, so I set them to be off to not interfere
gpio.setwarnings(False)


#######
### FUNCTION DEFINITIONS
#######

# This function tells python to recognize the joystick and buttons as inputs
def gpio_init():
    gpio.setmode(gpio.BOARD)
    gpio.setup(16, gpio.IN, pull_up_down=gpio.PUD_DOWN)
    gpio.setup(18, gpio.IN, pull_up_down=gpio.PUD_DOWN)
    gpio.setup(38, gpio.IN, pull_up_down=gpio.PUD_DOWN)
    gpio.setup(40, gpio.IN, pull_up_down=gpio.PUD_DOWN)


# This function is used to animate the goose so that its sprite changes with time
def player_animation():
    global player_surf, goose_index, player_rect
    
    goose_index += 0.1
    if int(goose_index) >= len(goose_fly): 
        goose_index = 0.0
    player_surf = goose_fly[int(goose_index)]


#######
### CLASS DEFENITION
#######
        
# I use this class for all the temporary rocks that are getting thrown at the goose
class a_rock():
    def __init__(self, start):
        
        # These create the rock texture, give it a rectangle to move, and a mask for more accurate collision
        self.rock = pygame.transform.scale(pygame.image.load('Goose_graphics/Rock.png'), (300, 300))
        self.rect = self.rock.get_rect(midright = start)
        self.mask = pygame.mask.from_surface(self.rock)
        
        # These check to see if the rock collided with anything, and if it hit the goose respectively
        self.collide = False
        self.point = False


    def CHUCKIT(self, opponent, opponent_mask):
        global p2_score, p1_score_clock, barrier_mask, barrier_rect
        
        # This checks to see if it is currently hitting the protective barrier. If it is, it changes so it stops displaying, but it doesn't score a point
        if self.mask.overlap(barrier_mask, (barrier_rect.x - self.rect.x, barrier_rect.y - self.rect.y)):
            self.collide = True
        # This checks for overlap with the goose specifically and if it did it tells it to stop and that it scored a point
        elif self.mask.overlap(opponent_mask, (opponent.x - self.rect.x, opponent.y - self.rect.y)) and self.collide == False:
            self.point = True
            self.collide = True
        
        # These check if the rock has collided with something. If not, it keeps moving
        else:
            if self.collide:
                pass
            else:
                screen.blit(self.rock, (self.rect))
                self.rect.x -= 20
        

########
### Main
########


################
### GRAPHICS, ALL MADE BY ME
################


# This sets some of the miscelaneus things that need to happen, like setting the screen size, starting pygame, grabbing the font used for the game, and starting the clock
gpio_init()
pygame.init()
screen = pygame.display.set_mode((1440, 800))
pygame.display.set_caption('Sky Clash: Rock vs. Goose')
clock = pygame.time.Clock()
test_font = pygame.font.Font('Goose_font/Pixeltype.ttf', 50)
pygame.mouse.set_visible(False)


#######
### BACKGROUND & MISC.
#######

# This brings in the static pages that will be called multiple times, but can never change
Background_surface = pygame.transform.scale(pygame.image.load('Goose_graphics/Flight_Background.png').convert(), (800, 800))
Background_surface2 = pygame.transform.scale(pygame.image.load('Goose_graphics/Flight_Background2.png').convert(), (800, 800))
power_up = pygame.transform.scale(pygame.image.load('Goose_graphics/power_up.png'), (200, 200))
p1_win = pygame.transform.scale(pygame.image.load('Goose_graphics/P1win.png').convert(), (1440, 800))
p2_win = pygame.transform.scale(pygame.image.load('Goose_graphics/P2win.png').convert(), (1440, 800))


#######
### PLAYER 1
#######

# This brings in the various states of the gooses surface, and adds some of the logical components to help it switch between surfaces easier
goose_fly_1 = pygame.transform.scale(pygame.image.load('Goose_graphics/Goose/Goose_Fly_1.png').convert_alpha(), (100, 100))
goose_fly_2 = pygame.transform.scale(pygame.image.load('Goose_graphics/Goose/Goose_Fly_2.png').convert_alpha(), (100, 100))
goose_fly_3 = pygame.transform.scale(pygame.image.load('Goose_graphics/Goose/Goose_Fly_3.png').convert_alpha(), (100, 100))
goose_fly = [goose_fly_1, goose_fly_1, goose_fly_2, goose_fly_2, goose_fly_3, goose_fly_3, goose_fly_3, goose_fly_2, goose_fly_2]
goose_index = 0.0
player_surf = goose_fly[int(goose_index)]
player_rect = player_surf.get_rect(midleft = (30, 200))

# This sets the default speed of the goose, which is altered later
speed = 10



#######
### PLAYER 2 
#######

# This sets up some collision with the main rock that is being controlled by the second player, aswell as some logic to get the moving rocks organized
player_2_surf = pygame.transform.scale(pygame.image.load('Goose_graphics/Rock.png'), (300, 300))
player_2_rect = player_2_surf.get_rect(midright = (1420, 200)) 
player_2_mask = pygame.mask.from_surface(player_2_surf)
thrown_rocks = -1
dropping = False
drop_clock = 0
rocks = []


#######
### BARRIER 
#######

# This sets up the collision for the barrier
barrier = pygame.transform.scale(pygame.image.load('Goose_graphics/Barrier.png'), (300, 300))
barrier_rect = barrier.get_rect(midright = (player_2_rect.x + 200, player_rect.y + 50))
barrier_mask = pygame.mask.from_surface(barrier)
barrier_rect.midright = (-100, 200)


#######
### VARIABLES
#######


cooldown = 0
cooldown_clock = 0
p1_score = 0
p2_score = 0
power_up_clock = 0
p1_score_clock = 0
other_clock = 0
display_powerup = False
resets = 0
bari = False
playing = False
win = False


#######
### TEXT DISPLAYS
#######

# Sets the title in the middle
title = test_font.render("Sky Clash: Rock vs. Goose", False, "Black")
title_rect = title.get_rect(center = (770, 50))


#######
### PLAY LOOP
#######


while True:
    
    #######
    ### JUST SOME MATH SO YOU CAN LEAVE
    #######
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
    
    
    #######
    ### LOAD SURFACES
    #######

    # Displays the up to date score for both players
    P1_score_display = pygame.transform.scale(test_font.render(str(p1_score), False, 'Black'), (50, 100))
    P2_score_display = pygame.transform.scale(test_font.render(str(p2_score), False, 'Black'), (50, 100))

    # Player 1 is always moving, so it's mask needs to update with its movement
    player_mask = pygame.mask.from_surface(player_surf)
    
    # Displays the static pages
    screen.blit(Background_surface, (0, 0))
    screen.blit(Background_surface2, (800, 0))
    screen.blit(P1_score_display, (340, 50))
    screen.blit(P2_score_display, (1100, 50))
    screen.blit(title, (title_rect))
    
    # Checks to see if the game is playing, and if not it either displays the start, or the end
    if playing:
        # Animates and displays the players
        player_animation()
        screen.blit(player_surf,(player_rect))
        screen.blit(player_2_surf, (player_2_rect))
        
        # Displays the power up
        if display_powerup == True:
            screen.blit(power_up, (power_up_rect))
        # Displays the barrier and updates its mask and location
        if bari:
            barrier_mask = pygame.mask.from_surface(barrier)
            barrier_rect.midright = player_rect.midright
            barrier_rect.y += 50
            barrier_rect.x += 200
            screen.blit(barrier, barrier_rect)
        
            

        #######
        ### PLAYER 1 INPUTS
        #######
        
        # Moves the player up if it can
        if gpio.input(40) == gpio.HIGH and gpio.input(38) == gpio.LOW and player_rect.y > 20:
            player_rect.y -= speed
        
        # Moves the player down if it can
        if gpio.input(40) == gpio.LOW and gpio.input(38) == gpio.HIGH and player_rect.y < 680:
            player_rect.y += speed
            
        # Moves the player left if it can
        if gpio.input(40) == gpio.HIGH and gpio.input(38) == gpio.HIGH and player_rect.x > 15:
            player_rect.x -= speed
        
        # Moves the player right if it can
        if gpio.input(40) == gpio.LOW and gpio.input(38) == gpio.LOW and player_rect.x < 1000:
            player_rect.x += speed

        # Moves the second player up if it can
        if gpio.input(16) == gpio.HIGH and player_2_rect.y > 20:
            player_2_rect.y -= 10
            
        # Moves the second player up if it can
        if gpio.input(18) == gpio.HIGH and player_2_rect.y < 600:
            player_2_rect.y += 10

            
        #######
        ### CHUCK DAT ROCK
        #######
            
        # Checks if cooldown is up, if it is it throws a rock
        if cooldown < 1:
            dropping = True
            throwing = a_rock(player_2_rect.center)
            rocks.append(throwing)
            thrown_rocks += 1
            cooldown += 1
           
        # Drops the rock and updates the score
        if dropping:
            amount_hit = 0
            check_reset = 0
            for i in range(len(rocks)):
                rocks[i].CHUCKIT(player_rect, player_mask)
                if rocks[i].point:
                    amount_hit += 1
                    p2_score = amount_hit
                    check_reset += 1
                    if check_reset > resets:
                        p1_score_clock = 0
                        resets = check_reset
                    


        #######
        ### POWERUPS
        #######
        
        # Adds the powerup, checks for collision, and if it collides it gives the player a random power with different probabilities
        if display_powerup:
            if power_up_mask.overlap(player_mask, (player_rect.x - power_up_rect.x, player_rect.y - power_up_rect.y)):
                power = random.randint(1, 5)
                screen.blit (power_up, (100, 100))
                if power == 1 or power == 2:
                    speed += 3
                elif power == 3 or power == 4:
                    speed -= 3
                elif power == 5:
                    bari = True
                display_powerup = False
                power_up_clock = 0

            
        #######
        ### COOLDOWNS
        #######
            
        # Adds the cooldown for throwing the rock
        cooldown_clock += 0.1
        if int(cooldown_clock) == 3:
            cooldown -= 1
            cooldown_clock = 0
            
        # Player 1 scores with time, so this counts and gives score over time
        p1_score_clock += 1
        if p1_score_clock == 360:
            p1_score_clock = 0
            p1_score += 1
            
        # Displays the powerup at a random point after some time
        power_up_clock += random.random()
        if power_up_clock >= 300 and not display_powerup:
            display_powerup = True
            power_up_rect = power_up.get_rect(center = (random.randint(15, 1000), random.randint(20, 680)))
            power_up_mask = pygame.mask.from_surface(power_up)
            speed = 10
            bari = False

        #######
        ### WIN CHECK
        #######
        if p1_score >= to_score:
            win = True
            playing = False
            winner = 1
        if p2_score >= to_score:
            win = True
            winner = 2
            playing = False

    else:
        # If your not playing and it hasn't ended, it asks what score you want to play until
        if not win:
            to_score = int(input('What score do you need to win? '))
            playing = True
        else:
            # If someone has won, it displays their win screen
            if winner == 1:
                screen.blit(p1_win, (0, 0))
            if winner == 2:
                screen.blit(p2_win, (0, 0))
            
        
    #######
    ### Boring stuff
    #######
    
    # Tells pygame to load frames
    pygame.display.update()
    clock.tick(60)

    