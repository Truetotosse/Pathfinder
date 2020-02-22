import random
import sys
import threading
import pygame
from  copy import deepcopy
import time
import math
pygame.font.init()



#defaults
sizes=[30,60,75,90,100,150,180,225,300]
currentsize=1
size=60
diff=60
windowsize=900
searchx=size-1
searchy=size-1
speeds=['deep','stochastic','forward','combined']
modes=['commute','random']
currentmode=0
currentspeed=0
startx=0
starty=0
mode='commute'
#global arrays for rendering
cstate=[]
queue=[]
price=[]
visited=[]
#for deeper recursion
sys.setrecursionlimit(100000)
threading.stack_size(0x2000000)
finished=0
started=0
#evaluating square
def scout(price,cost,x,y,xold,yold,speed):
    global searchx
    global searchy
    global startx
    global starty
    #if speed=='furious':
    #   return price[x][y]**1 + (cost[xold][yold]*(abs(searchx-x)+1)*(abs(searchy-y)+1))**0.1+(xold-x)*1.5+(yold-y)*1.5
    
    if speed=='deep' or speed=='stochastic':
        '''
        return price[x][y]**1 + (cost[xold][yold]*((abs(searchx-x)+abs(searchy-y))**2))**0.2+(xold-x)*math.log(size)+(yold-y)*math.log(size)
        '''
        #after series of experimentations this is function i'm satisfied with
        return (price[x][y])*math.log(size)/(math.log(size*1.5-( ( abs(searchx-x)**2 + abs(searchy-y) **2) **0.5)+1)+1) + \
          math.log( cost[xold][yold]  /  (size*1.5-( ( abs(searchx-x)**2 + abs(searchy-y) **2) **0.5)))+  \
         (((abs(searchx-x)+abs(searchy-y))**2)*math.log(size)+1)**0.2+( -abs(searchx-xold)  +abs(searchx-x))*math.log(size)*2+(  -abs(searchy-yold)  +abs(searchy-y) )*math.log(size)*2
      

    if speed=='forward':
        return (price[x][y]*math.log(size) + ((abs(searchx-x)+abs(searchy-y))**2)+(xold-x)*math.log(size)+(yold-y)*math.log(size))/(math.log((abs(startx-x)+abs(starty-y)+1)**2)+1)

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
                    if speed=='combined':
                        if deep>size*math.log(size)*2:
                            ev=scout(price,cost,x+i-1,y,x,y,'forward')
                        else:
                            ev=scout(price,cost,x+i-1,y,x,y,'deep')
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
                    if speed=='combined':
                        if deep>size*math.log(size)*2:
                            ev=scout(price,cost,x,y+i-1,x,y,'forward')
                        else:
                            ev=scout(price,cost,x,y+i-1,x,y,'deep')
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
        if speed=='stochastic':
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


memory=[[-1 for col in range(size)] for row in range(size)]
cost=[[1 for col in range(size)] for row in range(size)]
random.seed()
#generating random costs

def generate(size,mode,diff):
    price=[[3 for col in range(size)] for row in range(size)]
    if mode=='random':
        for i in range(size):
            for j in range(size):
                price[i][j]=random.randint(1, diff)
    elif mode=='commute':
        building=[2,3,5,6,8,12]
        longivity=1
        while longivity<size-1:
            build=random.randint(0,5)
            cost=build+random.randint(1,5)
            for i in range(longivity,longivity+building[build]):
                if i>=size-1:
                    break
                
                for j in range(0,size):
                    if j%(building[build]+1)<building[build]:
                        price[i][j]=125
                    else:
                        price[i][j]=cost
            longivity+=building[build]+1
    return price


    

def tableudpdate(size,mode,diff):
    global price
    global searchx
    global searchy
    global startx
    global starty
    global cost
    global memory
    global visited
    global cstate
    global queue
    global started
    global finished
    started=0
    finished=0
    cstate=[]
    queue=[]
    memory=[[-1 for col in range(size)] for row in range(size)]
    cost=[[1 for col in range(size)] for row in range(size)]
    visited=deepcopy(cost)
    random.seed()
    #generating random costs
    price=generate(size,mode,diff)
    searchx=size-1
    searchy=size-1
    startx=0
    starty=0

def buttonpress(**kwargs):
    global currentsize
    global currentspeed
    global currentmode
    global running
    global mode
    global size
    mode=modes[currentmode]
    size=sizes[currentsize]
    speed=speeds[currentspeed]

    if kwargs['object']=='size': 
        currentsize+=kwargs['change']
        if currentsize<0:
            currentsize=len(sizes)-1       
        if currentsize>=len(sizes):
            currentsize=0
        size=sizes[currentsize]
        tableudpdate(size,mode,diff)

    if kwargs['object']=='mode': 
        currentmode+=kwargs['change']
        if currentmode<0:
            currentmode=len(modes)-1
        if currentmode>=len(modes):
            currentmode=0
        mode=modes[currentmode]
        tableudpdate(size,mode,diff)

    if kwargs['object']=='speed': 
        currentspeed+=kwargs['change']
        if currentspeed<0:
            currentspeed=len(speeds)-1
        if currentspeed>=len(speeds):
            currentspeed=0
    if kwargs['object']=='exit':
        running=False

    if kwargs['object']=='solve':
        pass

    if kwargs['object']=='stop':
        global searchx
        global searchy
        searchx=queue[0][1]
        searchy=queue[0][2]


    if kwargs['object']=='newtry':
        pass

    if kwargs['object']=='refresh':
        tableudpdate(size,mode,diff)
    

#visualisation


class table(pygame.sprite.Sprite):
    def __init__(self,win):
        global size
        global visited
        visited=deepcopy(cost)
        pygame.sprite.Sprite.__init__(self)
        fnt = pygame.font.SysFont("comicsans", 40)
        self.image = pygame.Surface((windowsize+200, windowsize))
        self.image.fill((0, 255, 0))
        self.rect = self.image.get_rect()
        self.rect.center = (windowsize//2+100, windowsize//2)
        self.max=0
        global cstate 


    def update(self,win):
        global mode
        global visited
        global price
        global size
        fnt = pygame.font.SysFont("comicsans", 20)
        global cstate
        #background
        self.image = pygame.Surface((windowsize+200, windowsize))
        self.image.fill((210, 210, 210))
        self.rect = self.image.get_rect()
        self.rect.center = (windowsize//2+100, windowsize//2)
        #85 shades of cost
        if finished==0:
            for i in range(size):
                for j in range(size):
                            if mode=='random':
                                pygame.draw.rect(self.image,(255-price[i][j]*2,255-price[i][j]*2,255-price[i][j]*2),((i*windowsize/size,j*windowsize/size),(windowsize/size,windowsize/size)))
                            else:
                                if price[i][j]==125:
                                    pygame.draw.rect(self.image,(40,40,40),((i*windowsize/size,j*windowsize/size),(windowsize/size,windowsize/size)))
                                else:
                                    pygame.draw.rect(self.image,(25*price[i][j],255-25*price[i][j],10*price[i][j]),((i*windowsize/size,j*windowsize/size),(windowsize/size,windowsize/size)))
                            if visited[i][j]==3:
                                pygame.draw.rect(self.image,(0,0,0),((i*windowsize/size,j*windowsize/size),(windowsize/size,windowsize/size)))
            if self.max>0:
                self.max=0
        #if finished create cost map and renderpath
        elif self.max==0:
            #search for max only once (in ui so that tick dependant, can be made parallel)
            for i1 in range(size):
                for j1 in range(size):
                    if cstate[i1][j1]>self.max:
                        self.max=cstate[i1][j1]
            print(self.max)
            print(cost[searchx][searchy])
        else:
            #render costs map
            for i in range(size):
                for j in range(size):
                    #print(cstate[i][j]/self.max,cstate[i][j]*255)
                    pygame.draw.rect(self.image,(255-(cstate[i][j]/self.max*250),255-(cstate[i][j]/self.max*250),255-(cstate[i][j]/self.max*250)),((i*windowsize/size,j*windowsize/size),(windowsize/size,windowsize/size)))
            i=searchx
            j=searchy
            #render path
            while i!=startx or j!=starty:
                pygame.draw.rect(self.image,(0,0,255),((i*windowsize/size,j*windowsize/size),(windowsize/size,windowsize/size)))
                k=i
                i=memory[k][j][0]
                j=memory[k][j][1]
        #start and end squares
        pygame.draw.rect(self.image,(255,0,0),((searchx*windowsize/size,searchy*windowsize/size),(windowsize/size,windowsize/size)))
        pygame.draw.rect(self.image,(0,255,0),((startx*windowsize/size,starty*windowsize/size),(windowsize/size,windowsize/size)))
        #lines
       

class controls(pygame.sprite.Sprite):
    def __init__(self,win):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((200, windowsize))
        self.image.fill((180, 180, 180))
        self.rect = self.image.get_rect()
        self.rect.center = (windowsize+100, windowsize//2)

    def update(self,win):
        self.image = pygame.Surface((200, windowsize))
        self.image.fill((180, 180, 180))
        self.rect = self.image.get_rect()
        self.rect.center = (windowsize+100, windowsize//2)
        fnt = pygame.font.SysFont("comicsans", 30)
        #tips for the user
        if finished==0 and started==1:
            color=(10,10,10)
        else:
            color=(240,240,250)

        text = fnt.render(('Change size'), 1, (0, 0, 0))
        self.image.blit(text, (35,20))
        pygame.draw.rect(self.image,color,((0,60),(60,60)))
        pygame.draw.rect(self.image,color,((140,60),(60,60)))
        pygame.draw.polygon(self.image,(10,10,10),((10,90),(50,70),(50,110)))
        pygame.draw.polygon(self.image,(10,10,10),((190,90),(150,70),(150,110)))
        text = fnt.render(str(size), 1, (0, 0, 0))
        self.image.blit(text, (100-text.get_rect().width//2,85))

        text = fnt.render(('Change mode'), 1, (0, 0, 0))
        self.image.blit(text, (30,140))
        pygame.draw.rect(self.image,color,((0,180),(60,60)))
        pygame.draw.rect(self.image,color,((140,180),(60,60)))
        pygame.draw.polygon(self.image,(10,10,10),((10,120+90),(50,120+70),(50,120+110)))
        pygame.draw.polygon(self.image,(10,10,10),((190,120+90),(150,120+70),(150,120+110)))
        fnt = pygame.font.SysFont("comicsans", 25)
        text = fnt.render(mode, 1, (0, 0, 0))
        self.image.blit(text, (100-text.get_rect().width//2,205))
        fnt = pygame.font.SysFont("comicsans", 30)

        text = fnt.render(('Change method'), 1, (0, 0, 0))
        self.image.blit(text, (25,260))
        pygame.draw.rect(self.image,color,((0,120+120+60),(60,60)))
        pygame.draw.rect(self.image,color,((140,120+120+60),(60,60)))
        pygame.draw.polygon(self.image,(10,10,10),((10,120+120+90),(50,120+120+70),(50,120+120+110)))
        pygame.draw.polygon(self.image,(10,10,10),((190,120+120+90),(150,120+120+70),(150,120+120+110)))
        fnt = pygame.font.SysFont("comicsans", 25)
        text = fnt.render(speeds[currentspeed], 1, (0, 0, 0))
        self.image.blit(text, (100-text.get_rect().width//2,325))
        fnt = pygame.font.SysFont("comicsans", 40)

        pygame.draw.rect(self.image,(240,240,250),((0,120+120+120+60),(200,60)))
        if started==1 and finished==0:
            text = fnt.render('Stop(space)', 1, (0, 0, 0))
        elif started==1 and finished==1:
            text = fnt.render('Refresh(space)', 1, (0, 0, 0))
        else:
            text = fnt.render('Solve(space)', 1, (0, 0, 0))
        self.image.blit(text, (100-text.get_rect().width//2,120+315))

        fnt = pygame.font.SysFont("comicsans", 30)
        text = fnt.render('Use left click', 1, (0, 0, 0))
        self.image.blit(text, (100-text.get_rect().width//2,120+415))
        text = fnt.render('to set destination', 1, (0, 0, 0))
        self.image.blit(text, (100-text.get_rect().width//2,120+445))
        text = fnt.render('Use right click', 1, (0, 0, 0))
        self.image.blit(text, (100-text.get_rect().width//2,120+515))
        text = fnt.render('to set start', 1, (0, 0, 0))
        self.image.blit(text, (100-text.get_rect().width//2,120+545))

        fnt = pygame.font.SysFont("comicsans", 30)
        pygame.draw.rect(self.image,color,((0,windowsize-180),(200,60)))
        text = fnt.render('New set(tab)', 1, (0, 0, 0))
        self.image.blit(text, (100-text.get_rect().width//2,windowsize-160))


        fnt = pygame.font.SysFont("comicsans", 30)
        pygame.draw.rect(self.image,color,((0,windowsize-60),(200,60)))
        text = fnt.render('Exit(backspace)', 1, (0, 0, 0))
        self.image.blit(text, (100-text.get_rect().width//2,windowsize-40))


pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((windowsize+200, windowsize))
pygame.display.set_caption("Pathfinder")
clock = pygame.time.Clock()
all_sprites = pygame.sprite.Group()
all_sprites.add(table(screen))
all_sprites.add(controls(screen))


running = True

#flag if started solving to prevent multiple threads
started=0

price=generate(size,mode,diff)



while running:
    # low fps so can see some steps
    clock.tick(90)

    for event in pygame.event.get():
        # check for closing window
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            if started==1 and finished==0:
                buttonpress(object='stop')
            elif started==1 and finished==1:
                searchx=size-1
                searchy=size-1
                started=0
                finished=0
                cstate=[]
                queue=[]
                memory=[[-1 for col in range(size)] for row in range(size)]
                cost=[[1 for col in range(size)] for row in range(size)]
                visited=deepcopy(cost)
                random.seed()
                #generating random costs
                price=generate(size,mode,diff)
                table.__init__(table,screen)
            else:        
                started=1
                price[searchx][searchy]=0
                t = threading.Thread(target=walker,args=(price,cost,memory,startx,starty,0,speeds[currentspeed]))
                t.start()
                #b=assumpt(b,i,j,0)
                break
        
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_BACKSPACE:
            #backspace for exit
            running = False
        elif event.type == pygame.MOUSEBUTTONUP:
            pos = pygame.mouse.get_pos()
            if pos[0]<windowsize and pos[0]<windowsize:
                if started==0:
                    pos = pygame.mouse.get_pos()
                    if event.button==1:
                        searchx=int(pos[0]/windowsize*size)
                        searchy=int(pos[1]/windowsize*size)
                    elif event.button==3:
                        startx=int(pos[0]/windowsize*size)
                        starty=int(pos[1]/windowsize*size)
            else:
                pos=[pos[0]-windowsize,pos[1]]
                if started==0 or finished==1:    
                    if 0<=pos[0]<=60 and 60<=pos[1]<=120:
                        buttonpress(object='size',change=-1)
                    elif 140<=pos[0]<=200 and 60<=pos[1]<=120:
                        buttonpress(object='size',change=1)

                    elif 0<=pos[0]<=60 and 180<=pos[1]<=240:
                        buttonpress(object='mode',change=-1)
                    elif 140<=pos[0]<=200 and 180<=pos[1]<=240:
                        buttonpress(object='mode',change=1)

                    elif 0<=pos[0]<=60 and 300<=pos[1]<=360:
                        buttonpress(object='speed',change=-1)
                    elif 140<=pos[0]<=200 and 300<=pos[1]<=360:
                        buttonpress(object='speed',change=1)

                    elif 0<=pos[0]<=200 and windowsize-60<=pos[1]<=windowsize:
                        buttonpress(object='exit')

                    elif 0<=pos[0]<=200 and windowsize-180<=pos[1]<=windowsize-120:
                        buttonpress(object='refresh')

                    elif 0<=pos[0]<=200 and 420<=pos[1]<=480:
                        if started==1 and finished==0:
                            buttonpress(object='stop')
                        elif started==1 and finished==1:
                            searchx=size-1
                            searchy=size-1
                            started=0
                            finished=0
                            cstate=[]
                            queue=[]
                            memory=[[-1 for col in range(size)] for row in range(size)]
                            cost=[[1 for col in range(size)] for row in range(size)]
                            visited=deepcopy(cost)
                            random.seed()
                            #generating random costs
                            price=generate(size,mode,diff)
                            table.__init__(table,screen)
                        else:        
                            started=1
                            price[searchx][searchy]=0
                            t = threading.Thread(target=walker,args=(price,cost,memory,startx,starty,0,speeds[currentspeed]))
                            t.start()
                else:
                    if 0<=pos[0]<=200 and 420<=pos[1]<=480:
                        if started==1 and finished==0:
                            buttonpress(object='stop')

                        elif started==1 and finished==1:
                            searchx=size-1
                            searchy=size-1
                            started=0
                            finished=0
                            cstate=[]
                            queue=[]
                            memory=[[-1 for col in range(size)] for row in range(size)]
                            cost=[[1 for col in range(size)] for row in range(size)]
                            visited=deepcopy(cost)
                            random.seed()
                            #generating random costs
                            price=generate(size,mode,diff)
                            table.__init__(table,screen)
                        else:        
                            started=1
                            price[searchx][searchy]=0
                            t = threading.Thread(target=walker,args=(price,cost,memory,startx,starty,0,speeds[currentspeed]))
                            t.start()
                            #b=assumpt(b,i,j,0)



        elif event.type == pygame.KEYDOWN and event.key == pygame.K_TAB:
            if started==0 or finished==1:
                buttonpress(object='refresh')


    #pygame render update    
    all_sprites.update(screen)

    screen.fill((255, 255, 255))
    all_sprites.draw(screen)
    pygame.display.flip()

pygame.quit()


