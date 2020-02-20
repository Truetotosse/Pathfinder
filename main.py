import random
import sys
import threading
import pygame
from  copy import deepcopy
import time
pygame.font.init()

finished=0
#defaults
size=50

searchx=size-1
searchy=size-1

startx=0
starty=0
#global arrays for rendering
cstate=[]
queue=[]
price=[]
visited=[]
#for deeper recursion
sys.setrecursionlimit(100000)
threading.stack_size(0x2000000)

#evaluating square
def scout(price,cost,x,y,xold,yold):
    global searchx
    global searchy
    return price[x][y]**1 + (cost[xold][yold]*abs(searchx-x)*abs(searchy-y))**0.1+(xold-x)*1.5+(yold-y)*1.5

#looking for the path
def walker(price,cost,memory,x,y):
    time.sleep(0.001)
    global visited
    global finished
    #marking visited for rendering purposes
    visited[x][y]=3
    global size
    global queue
    global cstate
    #exit if we found the path, saving costs for rendering purposes
    if x==searchx and y==searchy:
        cstate=deepcopy(cost)
        finished=1
        return
    else:
        for i in range(3):
                if x+i-1 in range(size) and x+i-1!=x:
                    ev=scout(price,cost,x+i-1,y,x,y)
                    count=0
                    #evaluate and post square into the queue, depending on its value
                    if cost[x+i-1][y]==1 or cost[x+i-1][y]>price[x+i-1][y]+cost[x][y]:
                        cost[x+i-1][y]=price[x+i-1][y]+cost[x][y]
                        memory[x+i-1][y]=[x,y]
                        while count<len(queue) and ev>queue[count][0] :
                            count+=1
                        else:

                            if len(queue)>count and (queue[count][1]==x+i-1 and queue[count][2]==y):
                                pass
                            else:

                                    queue.insert(count,[ev,x+i-1,y]) 
                        


        for i in range(3):
                if y+i-1 in range(size) and y+i-1!=y:
                    ev=scout(price,cost,x,y+i-1,x,y)
                    count=0
                    #evaluate and post square into the queue, depending on its value
                    if cost[x][y+i-1]==1 or cost[x][y+i-1]>price[x][y+i-1]+cost[x][y]:
                        cost[x][y+i-1]=price[x][y+i-1]+cost[x][y]
                        memory[x][y+i-1]=[x,y]
                        while count<len(queue) and ev>queue[count][0]:
                            count+=1
                        else:
                            if len(queue)>count and (queue[count][1]==x and queue[count][2]==y+i-1):
                                pass
                            else:
                                    queue.insert(count,[ev,x,y+i-1]) 
        #check the first item in the queue, deleting it from the queue
        next=queue[0]
        queue.pop(0)
        walker(price,cost,memory,next[1],next[2])


price=[[0 for col in range(size)] for row in range(size)]
memory=[[-1 for col in range(size)] for row in range(size)]
cost=[[1 for col in range(size)] for row in range(size)]
random.seed()
#generating random costs
for i in range(size):
    for j in range(size):
        random.seed()
        price[i][j]=random.randint(1, 85)
#10x10 test 
test=[[ 1, 4, 4, 5, 1, 1, 1, 1, 1, 1],
      [ 1,10,10,10,10,10,10,10,10, 1],
      [ 1,10,10,10,10,10,10,10,10, 1],
      [ 1,40, 1, 1, 1, 1, 1, 1, 1, 1],
      [ 1,40,40,40,40,40,40,40,40, 1],
      [ 1,40, 1, 1, 1, 1, 1, 1, 1, 1],
      [ 1,40, 1,10,10,10,10,10,10, 1],
      [ 1,40, 1, 1, 1, 1,10,10,10, 1],
      [ 1,40,40,40,40, 1,10,10,10, 1],
      [ 1, 1, 1, 1, 1, 1, 1,10,10, 1]]

'''
t = threading.Thread(target=walker,args=(price,cost,memory,0,0))
t.start()
#for i in range(10):
#    print(cost[i])
t.join()
'''

#visualisation

class table(pygame.sprite.Sprite):
    def __init__(self,win):
        global size
        global visited
        visited=deepcopy(cost)
        pygame.sprite.Sprite.__init__(self)
        fnt = pygame.font.SysFont("comicsans", 40)
        self.image = pygame.Surface((900, 900))
        self.image.fill((0, 255, 0))
        self.rect = self.image.get_rect()
        self.rect.center = (225, 225)
        self.max=0
        global cstate 


    def update(self,win):
        global visited
        global price
        global size
        fnt = pygame.font.SysFont("comicsans", 20)
        global cstate
        #background
        self.image = pygame.Surface((900, 1000))
        self.image.fill((210, 210, 210))
        self.rect = self.image.get_rect()
        self.rect.center = (450, 500)
        #85 shades of cost
        if finished==0:
            for i in range(size):
                for j in range(size):
                            pygame.draw.rect(self.image,(255-price[i][j]*2,255-price[i][j]*2,255-price[i][j]*2),((i*900/size,j*900/size),(900/size,900/size)))
                            if visited[i][j]==3:
                                pygame.draw.rect(self.image,(0,0,0),((i*900/size,j*900/size),(900/size,900/size)))
        #if finished create cost map and renderpath
        elif self.max==0:
            #search for max only once (in ui so that tick dependant, can be made parallel)
            for i1 in range(size):
                for j1 in range(size):
                    if cstate[i1][j1]>self.max:
                        self.max=cstate[i1][j1]
        else:
            #render costs map
            for i in range(size):
                for j in range(size):
                    #print(cstate[i][j]/self.max,cstate[i][j]*255)
                    pygame.draw.rect(self.image,(255-(cstate[i][j]/self.max*255),255-(cstate[i][j]/self.max*255),255-(cstate[i][j]/self.max*255)),((i*900/size,j*900/size),(900/size,900/size)))
            i=searchx
            j=searchy
            #render path
            while i!=startx or j!=starty:
                pygame.draw.rect(self.image,(0,0,255),((i*900/size,j*900/size),(900/size,900/size)))
                k=i
                i=memory[k][j][0]
                j=memory[k][j][1]
        #start and end squares
        pygame.draw.rect(self.image,(255,0,0),((searchx*900/size,searchy*900/size),(900/size,900/size)))
        pygame.draw.rect(self.image,(0,255,0),((startx*900/size,starty*900/size),(900/size,900/size)))
        #lines
        for i in range(size):
            #horizontal lines
            pygame.draw.line(self.image,(0,0,0),(0,900/size+i*900/size),(900,900/size+i*900/size),1)
            #vertical lines
            pygame.draw.line(self.image,(0,0,0),(900/size+i*900/size,0),(900/size+i*900/size,900),1)
        #tips for the user
        text = fnt.render(('space to find path'), 1, (0, 0, 0))
        self.image.blit(text, (20,920))
        text = fnt.render(('backspace to exit'), 1, (0, 0, 0))
        self.image.blit(text, (20,960))
        text = fnt.render(('left click to change finish square'), 1, (0, 0, 0))
        self.image.blit(text, (400,920))
        text = fnt.render(('right click to change starting square'), 1, (0, 0, 0))
        self.image.blit(text, (400,960))
        #saving previous render to compare

pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((900, 1000))
pygame.display.set_caption("Pathfinder")
clock = pygame.time.Clock()
all_sprites = pygame.sprite.Group()
all_sprites.add(table(screen))


running = True

#flag if started solving to prevent multiple threads
started=0

while running:
    # low fps so can see some steps
    clock.tick(90)

    for event in pygame.event.get():
        # check for closing window
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            if started==0:
                #if sudoku is not solved by chain reaction, start solving it by assumtions in a new thread
                started=1
                price[searchx][searchy]=0
                t = threading.Thread(target=walker,args=(price,cost,memory,startx,starty))
                t.start()
                #b=assumpt(b,i,j,0)
                break
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_BACKSPACE:
            #backspace for exit
            running = False
        elif event.type == pygame.MOUSEBUTTONUP:
            if started==0:
                pos = pygame.mouse.get_pos()
                if event.button==1:
                    searchx=int(pos[0]/900*size)
                    searchy=int(pos[1]/900*size)
                elif event.button==3:
                    startx=int(pos[0]/900*size)
                    starty=int(pos[1]/900*size)

       
    

    #pygame render update    
    all_sprites.update(screen)

    screen.fill((255, 255, 255))
    all_sprites.draw(screen)
    pygame.display.flip()

pygame.quit()
'''
for i in range(size):
    for j in range(size):
        print("{0:2.0f}".format(price[i][j]),end=' ')
    print('')


path=[['#' for col in range(size)] for row in range(size)]
i=searchx
j=searchy

while i+j+i*j!=0:
    path[i][j]=' '
    k=i
    i=memory[k][j][0]
    j=memory[k][j][1]

for i in range(size):
    for j in range(size):
        print("{0:5.0f}".format(cost[i][j]),end=' ')
    print('')
for i in range(size):
    print(path[i])
'''
import os
import psutil
process = psutil.Process(os.getpid())
print(process.memory_info().rss)