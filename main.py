import random
import sys
import threading
import pygame
from  copy import deepcopy
import time
import math
pygame.font.init()

finished=0
#defaults
size=240

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
def scout(price,cost,x,y,xold,yold,speed):
    global searchx
    global searchy
    #if speed=='furious':
    #   return price[x][y]**1 + (cost[xold][yold]*(abs(searchx-x)+1)*(abs(searchy-y)+1))**0.1+(xold-x)*1.5+(yold-y)*1.5
    if speed=='furious' or 'feeling lucky':
        return price[x][y]**1 + (cost[xold][yold]*((abs(searchx-x)+abs(searchy-y))**2))**0.2+(xold-x)*math.log(size)+(yold-y)*math.log(size)
    if speed=='fast':
        return price[x][y]**1 + (abs(searchx-x)**2+abs(searchy-y)**2)/(abs(searchx-x)+abs(searchy-y)+1)+(xold-x)*1.5+(yold-y)*1.5

#looking for the path
def walker(price,cost,memory,x,y,deep,speed):
    #time.sleep(0.001)
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
                    if speed=='fast&furious':
                        if deep>size*math.log(size)*2:
                            ev=scout(price,cost,x+i-1,y,x,y,'fast')
                        else:
                            ev=scout(price,cost,x+i-1,y,x,y,'furious')
                    else:
                        ev=scout(price,cost,x+i-1,y,x,y,speed)
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
                                    count+=1 
                                    while count<len(queue):
                                        if queue[count][1]==x+i-1 and queue[count][2]==y:
                                            queue.pop(count)
                                        count+=1
                        


        for i in range(3):
                if y+i-1 in range(size) and y+i-1!=y:
                    if speed=='fast&furious':
                        if deep>size*math.log(size)*2:
                            ev=scout(price,cost,x,y+i-1,x,y,'fast')
                        else:
                            ev=scout(price,cost,x,y+i-1,x,y,'furious')
                    else:
                        ev=scout(price,cost,x,y+i-1,x,y,speed)
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
                                    count+=1
                                    while count<len(queue):
                                        if queue[count][1]==x and queue[count][2]==y+i-1:
                                            queue.pop(count) 
                                        count+=1
        #check the first item in the queue, deleting it from the queue
        '''
        next=queue[0]
        queue.pop(0)
        walker(price,cost,memory,next[1],next[2],deep+1,speed)
        '''
        if speed=='feeling lucky':
            try:
                nicetry=random.randint(0,5)
                next=queue[nicetry]
                queue.pop(nicetry)
                walker(price,cost,memory,next[1],next[2],deep+1,speed)
            except IndexError:
                next=queue[0]
                queue.pop(0)
                walker(price,cost,memory,next[1],next[2],deep+1,speed)
        else:
            next=queue[0]
            queue.pop(0)
            walker(price,cost,memory,next[1],next[2],deep+1,speed)

price=[[0 for col in range(size)] for row in range(size)]
memory=[[-1 for col in range(size)] for row in range(size)]
cost=[[1 for col in range(size)] for row in range(size)]
random.seed()
#generating random costs
for i in range(size):
    for j in range(size):
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
        self.image = pygame.Surface((720, 720))
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
        self.image = pygame.Surface((720, 820))
        self.image.fill((210, 210, 210))
        self.rect = self.image.get_rect()
        self.rect.center = (360, 410)
        #85 shades of cost
        if finished==0:
            for i in range(size):
                for j in range(size):
                            pygame.draw.rect(self.image,(255-price[i][j]*2,255-price[i][j]*2,255-price[i][j]*2),((i*720/size,j*720/size),(720/size,720/size)))
                            if visited[i][j]==3:
                                pygame.draw.rect(self.image,(0,0,0),((i*720/size,j*720/size),(720/size,720/size)))
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
                    pygame.draw.rect(self.image,(255-(cstate[i][j]/self.max*255),255-(cstate[i][j]/self.max*255),255-(cstate[i][j]/self.max*255)),((i*720/size,j*720/size),(720/size,720/size)))
            i=searchx
            j=searchy
            #render path
            while i!=startx or j!=starty:
                pygame.draw.rect(self.image,(0,0,255),((i*720/size,j*720/size),(720/size,720/size)))
                k=i
                i=memory[k][j][0]
                j=memory[k][j][1]
        #start and end squares
        pygame.draw.rect(self.image,(255,0,0),((searchx*720/size,searchy*720/size),(720/size,720/size)))
        pygame.draw.rect(self.image,(0,255,0),((startx*720/size,starty*720/size),(720/size,720/size)))
        #lines
        for i in range(size):
            #horizontal lines
            pygame.draw.line(self.image,(0,0,0),(0,720/size+i*720/size),(720,720/size+i*720/size),1)
            #vertical lines
            pygame.draw.line(self.image,(0,0,0),(720/size+i*720/size,0),(720/size+i*720/size,720),1)
        #tips for the user
        text = fnt.render(('space to find path furiously(size<=80), numpad enter for fast, return(enter) for fast&furious'), 1, (0, 0, 0))
        self.image.blit(text, (20,740))
        text = fnt.render(('feeling lucky press Lshift, backspace to exit'), 1, (0, 0, 0))
        self.image.blit(text, (20,760))
        text = fnt.render(('left click to change finish square'), 1, (0, 0, 0))
        self.image.blit(text, (360,760))
        text = fnt.render(('right click to change starting square'), 1, (0, 0, 0))
        self.image.blit(text, (360,780))


pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((720, 820))
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
                
                started=1
                price[searchx][searchy]=0
                t = threading.Thread(target=walker,args=(price,cost,memory,startx,starty,0,'furious'))
                t.start()
                #b=assumpt(b,i,j,0)
                break
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            if started==0:
                
                started=1
                price[searchx][searchy]=0
                t = threading.Thread(target=walker,args=(price,cost,memory,startx,starty,0,'fast&furious'))
                t.start()
               
                break
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_KP_ENTER:
            if started==0:
                
                started=1
                price[searchx][searchy]=0
                t = threading.Thread(target=walker,args=(price,cost,memory,startx,starty,0,'fast'))
                t.start()
                
                break
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_LSHIFT:
            if started==0:
               
                started=1
                price[searchx][searchy]=0
                t = threading.Thread(target=walker,args=(price,cost,memory,startx,starty,0,'feeling lucky'))
                t.start()
                
                break
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_BACKSPACE:
            #backspace for exit
            running = False
        elif event.type == pygame.MOUSEBUTTONUP:
            if started==0:
                pos = pygame.mouse.get_pos()
                if event.button==1:
                    searchx=int(pos[0]/720*size)
                    searchy=int(pos[1]/720*size)
                elif event.button==3:
                    startx=int(pos[0]/720*size)
                    starty=int(pos[1]/720*size)

       
    

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