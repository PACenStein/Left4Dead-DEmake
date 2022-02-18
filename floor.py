import pygame 
import numpy 
from numba import njit #used for optimising

def main():

    pygame.init()
    window = pygame.display.set_mode((800, 600))
    running = True
    clock = pygame.time.Clock() #ties player movement to fps

    hres = 120 #horizontal resolution
    halfvres = 100 #vertical resolution/2

    mod = hres/60 #used as a scaling factor for 60 degree fov
    posx, posy, rot = 0, 0, 0 #set player/ cameras x, y and rotation value
    frame = numpy.random.uniform(0, 1, (hres, halfvres*2, 3))

    #textures
    sky = pygame.image.load('textures/enviroment/sky.jpg')
    sky = pygame.surfarray.array3d(pygame.transform.scale(sky, (360, halfvres*2))) #300*100 --> each collumn = a degree of the players fov
    floor = pygame.surfarray.array3d(pygame.image.load('textures/enviroment/floor.jpg'))


    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        frame = new_frame(posx, posy, rot, frame, sky, floor, hres, halfvres, mod)


        surf = pygame.surfarray.make_surface(frame * 255) #copies array of pixels from frame to screen
        surf = pygame.transform.scale(surf, (800, 600)) #scale frame
        
        fps = int(clock.get_fps())
        pygame.display.set_caption("LEFT 4 DEMAKE - FPS: " + str(fps))

        window.blit(surf, (0, 0)) #draw to window at 0,0
        pygame.display.update()

        posx, posy, rot = movement(posx, posy, rot, pygame.key.get_pressed(), clock.tick()) #update movement

def movement(posx, posy, rot, keys, et): #et makes player speed and fps independent 
    #left turn
    if keys[pygame.K_LEFT] or keys[ord('a')]:
        rot = rot - 0.005*et #rotate, changing angle
    #right turn
    if keys[pygame.K_RIGHT] or keys[ord('d')]:
        rot = rot + 0.005*et #rotate, changing angle
    #foward
    if keys[pygame.K_UP] or keys[ord('w')]:
        posx, posy = posx + numpy.cos(rot)*0.005*et, posy + numpy.sin(rot)*0.005*et #increase pos

    if keys[pygame.K_DOWN] or keys[ord('s')]:
        posx, posy = posx - numpy.cos(rot)*0.005*et, posy - numpy.sin(rot)*0.005*et #decrease pos
    
    return posx, posy, rot

@njit() #optimise, 14 fps to 160
def new_frame(posx, posy, rot, frame, sky, floor, hres, halfvres, mod):
    for i in range(hres): #pass through  the collumns that make up the image 
            
            rot_i = rot + numpy.deg2rad(i/mod - 30) #angle that represents each angle in frame, calculates cosine of angle 
            sin, cos, cos2 = numpy.sin(rot_i), numpy.cos(rot_i), numpy.cos(numpy.deg2rad(i/mod - 30)) #cos2 reduces distortion (fish eye effect), n = halfvres/(halfvres-j)/cos2
            frame[i][:] = sky[int(numpy.rad2deg(rot_i)%359)][:]/255 #convert sky image to array (359 keeps it within indexs)
        
            for j in range(halfvres): #iterate through lines calculating distance to player. distnace is inversly proportional to the increment of the lines on the screen
                n = halfvres/(halfvres-j)/cos2
                x, y = posx + cos*n, posy + sin*n
                xx, yy = int(x*2%1*100), int(y*2%1*100)

                shade = 0.2 + 0.8*(1-j/halfvres) #DOF effect

                frame[i][halfvres*2-j-1] = shade*floor[xx][yy]/255 #scale floor
    
    return frame


if __name__ == '__main__':
    main()
    pygame.quit()