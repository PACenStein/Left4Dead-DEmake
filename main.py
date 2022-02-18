import pygame 
import numpy 
from numba import njit

def main():
    pygame.init()
    window = pygame.display.set_mode((800,600))
    running = True
    clock = pygame.time.Clock()
    pygame.mouse.set_visible(False)

    hres = 250 #horizontal resolution
    halfvres = int(hres*0.375) #vertical resolution/2
    mod = hres/60 #used as a scaling factor for 60 degree fov

    size = 25
    noenemies = size*2 #number of enemies
    posx, posy, rot, maph, exitx, exity = gen_map(size) #set player/ cameras x, y rotation value, map height, exit location
    
    
    frame = numpy.random.uniform(0,1, (hres, halfvres*2, 3))
    sky = pygame.image.load('textures/enviroment/sky.jpg') #300*100 --> each 
    sky = pygame.surfarray.array3d(pygame.transform.smoothscale(sky, (720, halfvres*2)))/255
    floor = pygame.surfarray.array3d(pygame.image.load('textures/enviroment/floor.jpg'))/255
    wall = pygame.surfarray.array3d(pygame.image.load('textures/enviroment/wall.jpg'))/255
    sprites, spsize, axe, axesp = get_sprites(hres)
    
    enemies = spawn_enemies(noenemies, maph, size)

    while running:
        ticks = pygame.time.get_ticks()/200
        er = min(clock.tick()/500, 0.3)
        if int(posx) == exitx and int(posy) == exity: #if player reachs the end
            if noenemies < size:
                print("You got out of the maze!")
                pygame.time.wait(1000)
                running = False
            elif int(ticks%10+0.9) == 0:
                print("There is still work to do...")
        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            if axesp < 1 and event.type == pygame.MOUSEBUTTONDOWN:
                axesp = 1
                
        frame = new_frame(posx, posy, rot, frame, sky, floor, hres, halfvres, mod, maph, size,
                          wall, exitx, exity)
        surf = pygame.surfarray.make_surface(frame*255) #copies array of pixels from frame to window
        
        enemies = sort_sprites(posx, posy, rot, enemies, maph, size, er/5)
        surf, en = draw_sprites(surf, sprites, enemies, spsize, hres, halfvres, ticks, axe, axesp)

        surf = pygame.transform.scale(surf, (800, 600)) #scale frame
        
        if int(axesp) > 0:
            if axesp == 1 and enemies[en][3] > 1 and enemies[en][3] < 10:
                enemies[en][0] = 0
                noenemies = noenemies - 1
            axesp = (axesp + er*5)%4

        window.blit(surf, (0,0)) #draw to window at 0,0
        pygame.display.update()
        fps = int(clock.get_fps())
        pygame.display.set_caption("Enemies remaining: " + str(noenemies) + " - FPS: " + str(fps))
        posx, posy, rot = movement(pygame.key.get_pressed(), posx, posy, rot, maph, er)
        pygame.mouse.set_pos(400,300)

def movement(pressed_keys, posx, posy, rot, maph, et): #et makes player speed and fps independent 
    x, y, rot0, diag = posx, posy, rot, 0
    if pygame.mouse.get_focused():
        p_mouse = pygame.mouse.get_pos()
        rot = rot + numpy.clip((p_mouse[0]-400)/200, -0.2, .2)

    if pressed_keys[pygame.K_PAGEUP] or pressed_keys[ord('q')]:
        rot = rot - 0.75*et

    elif pressed_keys[pygame.K_PAGEDOWN] or pressed_keys[ord('e')]:
        rot = rot + 0.75*et

    if pressed_keys[pygame.K_UP] or pressed_keys[ord('w')]:
        x, y, diag = x + et*numpy.cos(rot), y + et*numpy.sin(rot), 1

    elif pressed_keys[pygame.K_DOWN] or pressed_keys[ord('s')]:
        x, y, diag = x - et*numpy.cos(rot), y - et*numpy.sin(rot), 1
        
    if pressed_keys[pygame.K_LEFT] or pressed_keys[ord('a')]:
        et = et/(diag+1)
        x, y = x + et*numpy.sin(rot), y - et*numpy.cos(rot)
        
    elif pressed_keys[pygame.K_RIGHT] or pressed_keys[ord('d')]:
        et = et/(diag+1)
        x, y = x - et*numpy.sin(rot), y + et*numpy.cos(rot)


    if not(maph[int(x-0.2)][int(y)] or maph[int(x+0.2)][int(y)] or
           maph[int(x)][int(y-0.2)] or maph[int(x)][int(y+0.2)]):
        posx, posy = x, y
        
    elif not(maph[int(posx-0.2)][int(y)] or maph[int(posx+0.2)][int(y)] or
             maph[int(posx)][int(y-0.2)] or maph[int(posx)][int(y+0.2)]):
        posy = y
        
    elif not(maph[int(x-0.2)][int(posy)] or maph[int(x+0.2)][int(posy)] or
             maph[int(x)][int(posy-0.2)] or maph[int(x)][int(posy+0.2)]):
        posx = x
        
    return posx, posy, rot

def gen_map(size):
    #randomly generated map using walker algorithim. Moves from one side of a map to another, mapping out walls
    
    maph = numpy.random.choice([0, 0, 0, 0, 1, 1], (size,size))
    maph[0,:], maph[size-1,:], maph[:,0], maph[:,size-1] = (1,1,1,1)

    posx, posy, rot = 1.5, numpy.random.randint(1, size -1)+.5, numpy.pi/4
    x, y = int(posx), int(posy)
    maph[x][y] = 0
    count = 0
    while True:
        testx, testy = (x, y)
        if numpy.random.uniform() > 0.5:
            testx = testx + numpy.random.choice([-1, 1])
        else:
            testy = testy + numpy.random.choice([-1, 1])
        if testx > 0 and testx < size -1 and testy > 0 and testy < size -1:
            if maph[testx][testy] == 0 or count > 5:
                count = 0
                x, y = (testx, testy)
                maph[x][y] = 0
                if x == size-2:
                    exitx, exity = (x, y)
                    break
            else:
                count = count+1
    return posx, posy, rot, maph, exitx, exity

@njit() #optimise, 14 fps to 160
def new_frame(posx, posy, rot, frame, sky, floor, hres, halfvres, mod, maph, size, wall, exitx, exity):
    for i in range(hres): #pass through  the collumns that make up the image 
        rot_i = rot + numpy.deg2rad(i/mod - 30) #angle that represents each angle in frame, calculates cosine of angle 
        sin, cos, cos2 = numpy.sin(rot_i), numpy.cos(rot_i), numpy.cos(numpy.deg2rad(i/mod - 30)) #cos2 reduces distortion (fish eye effect), n = halfvres/(halfvres-j)/cos2
        frame[i][:] = sky[int(numpy.rad2deg(rot_i)*2%718)][:] #convert sky image to array (359 keeps it within index)

        x, y = posx, posy
        while maph[int(x)%(size-1)][int(y)%(size-1)] == 0: #convert sky image to array (359 keeps it within indexs)
            x, y = x +0.01*cos, y +0.01*sin #calculate distance to wall

        n = numpy.sqrt((x-posx)**2+(y-posy)**2)#abs((x - posx)/cos) distance always an absoulte value      
        h = int(halfvres/(n*cos2 + 0.001)) #calculate height of wall, cos2 corrects fisheye effect, 0.001 ensure no dividing by 0

        xx = int(x*3%1*99)        
        if x%1 < 0.02 or x%1 > 0.98: #calculate position of wall
            xx = int(y*3%1*99)
        yy = numpy.linspace(0, 3, h*2)*99%99 #repeating texture

        shade = 0.3 + 0.7*(h/halfvres) #DOF effect
        #height value will get too big, blowing out shading. This fixes that by limiting the shading values to 1
        if shade > 1:
            shade = 1
        #shadows      
        cornershadow = 0  #corners where walls overlap
        if maph[int(x-0.33)%(size-1)][int(y-0.33)%(size-1)]:#if blocked from light
            cornershadow = 1
            
        if maph[int(x-0.01)%(size-1)][int(y-0.01)%(size-1)]:
            shade, cornershadow = shade*0.5, 0 #increase shade factor
            
        c = shade
        for k in range(h*2):
            if halfvres - h +k >= 0 and halfvres - h +k < 2*halfvres:
                if cornershadow and 1-k/(2*h) < 1-xx/99:
                    c, cornershadow = 0.5*c, 0
                frame[i][halfvres - h +k] = c*wall[xx][int(yy[k])] #fill pixels in with colour from texture
                #wall reflections
                if halfvres+3*h-k < halfvres*2:
                    frame[i][halfvres+3*h-k] = c*wall[xx][int(yy[k])]
                
        for j in range(halfvres -h): #iterate through lines calculating distance to player. distnace is inversly proportional to the increment of the lines on the screen
            n = (halfvres/(halfvres-j))/cos2
            x, y = posx + cos*n, posy + sin*n
            xx, yy = int(x*3%1*99), int(y*3%1*99)

            shade = 0.2 + 0.8*(1-j/halfvres) #DOF effect
            if maph[int(x-0.33)%(size-1)][int(y-0.33)%(size-1)]: #if blocked from light
                shade = shade*0.5 #increase shade factor
            elif ((maph[int(x-0.33)%(size-1)][int(y)%(size-1)] and y%1>x%1)  or
                  (maph[int(x)%(size-1)][int(y-0.33)%(size-1)] and x%1>y%1)):
                shade = shade*0.5 #increase shade factor

            frame[i][halfvres*2-j-1] = shade*(floor[xx][yy]*2+frame[i][halfvres*2-j-1])/3 #scale floor
            
            if int(x) == exitx and int(y) == exity and (x%1-0.5)**2 + (y%1-0.5)**2 < 0.2: #checks if player is in the exit circle
                ee = j/(10*halfvres)
                frame[i][j:2*halfvres-j] = (ee*numpy.ones(3)+frame[i][j:2*halfvres-j])/(1+ee)

    return frame

@njit() #orders sprites based on distance to player
def sort_sprites(posx, posy, rot, enemies, maph, size, er):
    for en in range(len(enemies)):
        cos, sin = er*numpy.cos(enemies[en][6]), er*numpy.sin(enemies[en][6])
        enx, eny = enemies[en][0]+cos, enemies[en][1]+sin
        if (maph[int(enx-0.1)%(size-1)][int(eny-0.1)%(size-1)] or
            maph[int(enx-0.1)%(size-1)][int(eny+0.1)%(size-1)] or
            maph[int(enx+0.1)%(size-1)][int(eny-0.1)%(size-1)] or
            maph[int(enx+0.1)%(size-1)][int(eny+0.1)%(size-1)]):
            enx, eny = enemies[en][0], enemies[en][1]
            enemies[en][6] = enemies[en][6] + numpy.random.uniform(-0.5, 0.5)
        else:
            enemies[en][0], enemies[en][1] = enx, eny
        angle = numpy.arctan((eny-posy)/(enx-posx))
        if abs(posx+numpy.cos(angle)-enx) > abs(posx-enx):
            angle = (angle - numpy.pi)%(2*numpy.pi)
        angle2= (rot-angle)%(2*numpy.pi)
        if angle2 > 10.5*numpy.pi/6 or angle2 < 1.5*numpy.pi/6:
            dir2p = ((enemies[en][6] - angle -3*numpy.pi/4)%(2*numpy.pi))/(numpy.pi/2)
            enemies[en][2] = angle2
            enemies[en][7] = dir2p
            enemies[en][3] = 1/numpy.sqrt((enx-posx)**2+(eny-posy)**2+1e-16)
            cos, sin = (posx-enx)*enemies[en][3], (posy-eny)*enemies[en][3]
            x, y = enx, eny
            for i in range(int((1/enemies[en][3])/0.05)):
                x, y = x +0.05*cos, y +0.05*sin
                if (maph[int(x-0.02*cos)%(size-1)][int(y)%(size-1)] or
                    maph[int(x)%(size-1)][int(y-0.02*sin)%(size-1)]):
                    enemies[en][3] = 9999
                    break
        else:
           enemies[en][3] = 9999

    enemies = enemies[enemies[:, 3].argsort()]
    return enemies

def spawn_enemies(number, maph, msize):
    enemies = []
    for i in range(number):
        x, y = numpy.random.uniform(1, msize-2), numpy.random.uniform(1, msize-2)
        while (maph[int(x-0.1)%(msize-1)][int(y-0.1)%(msize-1)] or
               maph[int(x-0.1)%(msize-1)][int(y+0.1)%(msize-1)] or
               maph[int(x+0.1)%(msize-1)][int(y-0.1)%(msize-1)] or
               maph[int(x+0.1)%(msize-1)][int(y+0.1)%(msize-1)]):
            x, y = numpy.random.uniform(1, msize-1), numpy.random.uniform(1, msize-1)
        angle2p, invdist2p, dir2p = 0, 0, 0 # angle, inv dist, dir2p relative to player
        entype = numpy.random.choice([0,1]) # 0 zombie, 1 skeleton
        direction = numpy.random.uniform(0, 2*numpy.pi) # facing direction
        size = numpy.random.uniform(7, 10)
        enemies.append([x, y, angle2p, invdist2p, entype, size, direction, dir2p])

    return numpy.asarray(enemies)

def get_sprites(hres):
    sheet = pygame.image.load('textures/enemies/zombie_n_skeleton4.png').convert_alpha()
    sprites = [[], []]
    axesheet = pygame.image.load('textures/weapons/fireaxe1.png').convert_alpha() 
    axe = []
    for i in range(3):
        subaxe = pygame.Surface.subsurface(axesheet,(i*800,0,800,600))
        axe.append(pygame.transform.smoothscale(subaxe, (hres, int(hres*0.75))))
        xx = i*32
        sprites[0].append([])
        sprites[1].append([])
        for j in range(4):
            yy = j*100
            sprites[0][i].append(pygame.Surface.subsurface(sheet,(xx,yy,32,100)))
            sprites[1][i].append(pygame.Surface.subsurface(sheet,(xx+96,yy,32,100)))

    spsize = numpy.asarray(sprites[0][1][0].get_size())*hres/800

    axe.append(axe[1]) # extra middle frame
    axesp = 0 #current sprite for the axe
    
    return sprites, spsize, axe, axesp

def draw_sprites(surf, sprites, enemies, spsize, hres, halfvres, ticks, axe, axesp):
    #enemies : x, y, angle, distance, type, size, direction, direction in relation to player
    cycle = int(ticks)%3 # animation cycle for enemies
    for en in range(len(enemies)):
        if enemies[en][3] >  10:
            break
        types, dir2p = int(enemies[en][4]), int(enemies[en][7])
        cos2 = numpy.cos(enemies[en][2])
        scale = min(enemies[en][3], 2)*spsize*enemies[en][5]/cos2
        vert = halfvres + halfvres*min(enemies[en][3], 2)/cos2
        hor = hres/2 - hres*numpy.sin(enemies[en][2])
        spsurf = pygame.transform.scale(sprites[types][cycle][dir2p], scale)
        surf.blit(spsurf, (hor,vert)-scale/2)

    axepos = (numpy.sin(ticks)*10*hres/800,(numpy.cos(ticks)*10+15)*hres/800) # axe shake
    surf.blit(axe[int(axesp)], axepos)

    return surf, en-1

if __name__ == '__main__':
    main()
    pygame.quit()