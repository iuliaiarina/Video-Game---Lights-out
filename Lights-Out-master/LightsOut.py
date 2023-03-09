# -*- coding: utf-8 -*-
import os
import shutil

import pygame
from subprocess import Popen, PIPE
import numpy as np



# path to mace 4:
PATH_TO_MACE4 = "LADR-2009-11A/bin/mace4"

 
class PygView(object):

    def __init__(self, width=1000, height=600, fps=60):
        pygame.init()
        pygame.display.set_caption("Press ESC to quit")
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.DOUBLEBUF)
        self.background = pygame.Surface(self.screen.get_size()).convert()  
        self.background.fill((255,255,255)) # fill background white
        self.clock = pygame.time.Clock()
        self.fps = fps
        self.playtime = 0.0
        self.font = pygame.font.SysFont('mono', 24, bold=True)
        self.initialMat = np.zeros((3,3)).astype(int)
        # ------------- drawing the initial buttons ----------
        button = self.font.render('Solve', True, (0,255,0), (0,0,128))
        buttonRect = button.get_rect()
        buttonRect.center = (500,500)
        self.background.blit(button,buttonRect)
        randButton = self.font.render('Random', True, (0,255,0),(0,0,128))
        randRect = randButton.get_rect()
        randRect.center = (340,500)
        self.background.blit(randButton,randRect)
        setupButton = self.font.render('Begin', True, (0,255,0), (0,0,128))
        setupRect = setupButton.get_rect()
        setupRect.center = (425,500)
        self.background.blit(setupButton,setupRect)

        
        
    def ChooseInitBoard(self,sz = 3):
        randMat = np.random.randint(2,size=sz*sz)
        randMat = randMat.reshape((sz,sz))
        return randMat
    
    def checkWin(self, flag, Mat = np.ones((5,5))):
        size = len(Mat)
        if flag == True:
            for i in range(size):
                if flag == True:
                    for j in range(size):
                        if Mat[i,j]==1:
                            flag = False
                            break
        return flag
    
    def paintInit(self, Mat = np.ones((5,5)), sM = np.zeros((5,5))):
        '''paint the initial boards'''
        size = len(Mat)
        shift = size + 2
        for row in range(size):
            for col in range(size):
                mycell = Cell(col=col, row=row, color=(0,255*Mat[row,col],255),
                              background=self.background)
                mycell.blit(self.background)
                solcell = Cell(col=col+shift, row=row, color=(255*sM[row,col],0,255),
                               background=self.background)
                solcell.blit(self.background)
                
    def paintPuz(self,Mat = np.ones((5,5))):
        '''paint the original puzzle'''
        size = len(Mat)
        for row in range(size):
            for col in range(size):
                mycell = Cell(col=col, row=row, 
                              color=(255*Mat[row,col],255*Mat[row,col],255*(1-Mat[row,col])),
                              background=self.background)
                mycell.blit(self.background)
        

    def paint(self,col=0, row=0, color=(0,0,255)):
        """update a single cell"""
        mycell = Cell(col=col,row=row,color=color,background=self.background)
        mycell.blit(self.background)


    def prove(self, sir):
        # aici scriem start-ul in fisierul aux.p9 :
        shutil.copy("allLights.in","aux.p9")
        file = open('aux.p9', 'r+')
        file.seek(176, os.SEEK_SET)
        file.write(sir)
        file.close()

        # rulam mace4 si cautam G-ul:
        output = self.run_mace4()
        file = open('output.out', 'wb')
        file.write(output)
        file.close()
        file = open('output.out', 'r')
        word = 'relation(g(_)'
        findg = ""
        lines = file.readlines()
        for line in lines:
            if line.find(word)!=-1:
                findg= line

        start = findg.find('[') + 2
        g = {}
        for i in range(9):
            g[i] = (int(findg[start + i*3]))
        print("Rezultat:")
        print(g)
        return g

    def run_mace4(self):
        cmd = [PATH_TO_MACE4, '-f', "aux.p9"]
        p = Popen(cmd, stdout=PIPE, stderr=PIPE)
        return p.stdout.read()
        
    def click(self, row, col, M = np.ones((3,3)),sM = np.zeros((3,3))):
        size = len(M)
        shift = size + 2
        if row>=size or col >=size:
            pass
        else:
            for i in range(size):
                for j in range(size):
                    if (np.abs(row-i) < 2 and col == j) or (row == i and np.abs(col-j) < 2):
                        M[i,j] = (M[i,j]+1) % 2 ##toggle light and adjacent lights
                        self.paint(row=i ,col=j ,color=(0,255*M[i,j] ,255))
            sM[row,col] = sM[row,col]+1
            ##paint the cell clicked on in the solution
            self.paint(col=col+shift,row=row,color=(255*(sM[row,col]%2),0,255)) 
        return M, sM
    
    def toggle(self, row, col, M = np.ones((3,3))):
        size = len(M)
        if row>=size or col >=size:
            pass
        else:
            M[row,col] = (M[row,col]+1)%2 ##toggle the light
            # print(row,col)
            self.paint(row=row,col=col,color=(0,255*M[row,col],255)) 
        return M




##Edit this to run one step of the solving algorithm each frame##
    def run(self):
        """The mainloop"""
        initMat = np.zeros((3,3))
        matrix = np.zeros((3,3))
        size = 3
        solMatrix = np.zeros((size,size))  ## keep track of the buttons pressed in working to solve
        self.paintInit(Mat=matrix, sM=solMatrix)
        running = True
        setup = True ##this flag is False when the user has finished setup
        stop = False  ##this flag is True when the clock updates should stop
        solving = False  ##this flag is True when the solving process is running
        while running:
            row = -1
            col = -1
            pos = []
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False 
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                elif event.type == pygame.MOUSEBUTTONUP:
                    pos = pygame.mouse.get_pos()
                    if 5<=pos[0]%55 and 5<=pos[1]%55:  ##make sure the click isn't on a boundary 
                        row = pos[1]//55
                        col = pos[0]//55
            # aici  alege actiunile:
            if setup == True and len(pos)>0:
                if pos[1]<450:  ##it could be on a cell
                    matrix = self.toggle(row,col,matrix)
                elif 485<=pos[1]<=515:  ##it could be on a button
                    if 300<=pos[0]<=385:  ##it's the 'random' button
                        matrix = self.ChooseInitBoard()
                        self.paintInit(Mat = matrix, sM = solMatrix)
                    elif 390<=pos[0]<=460:  ##it's the 'begin' button
                        # comment de aici i-au orice matrice este introdusa:
                            print("Matricea initiala:")
                            print(matrix)
                            setup = False
                            print('Out of Setup Mode')
                            initMat = matrix.astype(int)
                            matrix = matrix.astype(int)
                            self.clock = pygame.time.Clock()
                            stop = False  ##begin the clock
            elif solving == False and len(pos)>0:
                ##don't allow clicking while it's solving##
                if 460<=pos[0]<=540 and 485<=pos[1]<=515:  ##then we clicked on the 'solve' button
                    solving = True
                    #initializare pentru rezolvare:
                    start = [matrix.item(0), matrix.item(1), matrix.item(2),matrix.item(3),matrix.item(4),matrix.item(5),matrix.item(6),matrix.item(7),matrix.item(8)]
                    i = 0
                    sir = ""
                    for x in start:
                        if x == 0:
                            sir = sir + "-start(" + str(i) +").\n"
                        if x == 1:
                            sir = sir + "start(" + str(i) + ").\n"
                        i = i + 1
                    # am calculat start-ul si extragem rezultatul "g":
                    g = self.prove(sir)
                    # index pt g:
                    indx = 0
                elif row>=0 and col>=0:
                    print("Input de la User cand rezolva:",row,col)
                    matrix, solMatrix = self.click(row, col, matrix, solMatrix)
            
            if solving == True:

                if g.get(indx)==1:
                    j = indx % 3
                    i = (int) ((indx - j) / 3)

                    matrix, solMatrix = self.click(row=i, col=j, M=matrix, sM=solMatrix)
                indx = indx + 1
                if indx==9:  ## final:
                        solving = False

            if stop == False:
                if self.checkWin(True, Mat = matrix): #checkflag == True:
                    print('You Win!!')
                    stop = True
                    if self.playtime != 0: ##if the game was actually played
                        setup = True
                        self.paintPuz(Mat = initMat)
                else:
                    milliseconds = self.clock.tick(self.fps)
                    self.playtime += milliseconds / 1000.0
            self.draw_text("Clicks: {:6.4}{}PLAYTIME: {:6.4} SECONDS".format(
                    np.sum(solMatrix), " "*5, self.playtime))
            self.draw_text("Min Clicks: {:6.3}".format(np.sum(solMatrix%2)), loc=(50,570))
            self.draw_text("Minimal Solution", loc=((3*size/2)*55,(size+0.5)*55))
            pygame.display.flip()
            self.screen.blit(self.background, (0, 0))
            
        pygame.quit()


    def draw_text(self, text,loc=(50,550), color=(0,0,0)):
        """Center text in window
        """
        fw, fh = self.font.size(text)
        surface = self.font.render(text, True, color)
        self.screen.blit(surface, loc)
        
class Cell(object):
    """This is meant to be a method to draw a single cell"""
    def __init__(self, length = 50, col = 0, row = 0, color=(0,0,255), 
                 background = pygame.Surface((400,400))):
        self.length = length
        self.x = col*55
        self.y = row*55
        self.color = color
        self.surface = background
        ##draw background for the cell##
        pygame.draw.rect(self.surface, (0,0,1), (self.x,self.y,self.length+10, self.length+10))
        ##draw the cell##
        pygame.draw.rect(self.surface, self.color, (self.x+5, self.y+5, self.length, self.length))
        self.surface = self.surface.convert() # for faster blitting.
                
    def blit(self,background):
        background.blit(self.surface, (0,0))
            

    
####

if __name__ == '__main__':

    # call with width of window and fps
    PygView().run()