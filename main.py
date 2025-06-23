import pygame
import json

pygame.init()
width=880
height=600
fps=60

game_over=0
level=1
max_level=4

def reset_level():
    player.rect.x=40
    player.rect.y=490
    player.key=False
    lava_group.empty()
    exit_group.empty()
    with open(f'levels/level{level}.json','r') as file:
        world_data=json.load(file)
    world= World(world_data)
    return world

screen=pygame.display.set_mode((width,height))
pygame.display.set_caption('Babuin')
clock=pygame.time.Clock()

with open('levels/level1.json', 'r') as file:
    world_data=json.load(file)
tile_size=40
fon=pygame.image.load('images/bg8.png')
fon=pygame.transform.scale(fon,(width,height))


class Player():
    def __init__(self):
        self.images_right=[]
        self.images_left=[]
        self.index=0
        self.counter=0
        self.direction=0
        for num in range(1,3):
            img_right=pygame.image.load(f'images/player{num}.png')
            img_right=pygame.transform.scale(img_right,(60,70))
            img_left=pygame.transform.flip(img_right,True,False)
            self.images_right.append(img_right)
            self.images_left.append(img_left)
        self.image = self.images_right[self.index]
        self.rect = self.image.get_rect(x=40, y=490)
        self.speed=10
        self.gravity=0
        self.jumped=False
        self.width=self.image.get_width()
        self.height = self.image.get_height()
        self.death_image=pygame.image.load('images/death.jpg')
        self.death_image = pygame.transform.scale(self.death_image,(60,70))
        self.key=False

    def update(self):
        global game_over
        x = 0
        y = 0
        walk_speed = 10  # раз в 10 повторений будет анимация

        if game_over==0:

            key = pygame.key.get_pressed()
            if key[pygame.K_SPACE] and self.jumped == False:
                self.gravity = -15
                self.jumped = True

            if key[pygame.K_a]:
                x -= 5
                self.direction = -1
                self.counter += 1
            if key[pygame.K_d]:
                x += 5
                self.direction = 1
                self.counter += 1

            if self.counter > walk_speed:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images_right):
                    self.index = 0
                if self.direction == 1:
                    self.image = self.images_right[self.index]
                else:
                    self.image = self.images_left[self.index]

            # add gravity
            self.gravity += 1.3
            if self.gravity > 10:
                self.gravity = 10
            y += self.gravity

            for tile in world.tile_list:
                if tile[1].colliderect(self.rect.x + x, self.rect.y, self.width, self.height):
                    x = 0
                if tile[1].colliderect(self.rect.x, self.rect.y + y, self.width, self.height):
                    if self.gravity < 0:
                        y = tile[1].bottom - self.rect.top
                        self.gravity = 0
                    elif self.gravity >= 0:
                        y = tile[1].top - self.rect.bottom
                        self.gravity = 0
                        self.jumped = False

            # update player coordinates
            self.rect.x += x
            self.rect.y += y

            if self.rect.bottom > height:
                 self.rect.bottom = height
            if pygame.sprite.spritecollide(self, key_group, True):
                self.key=True
            if pygame.sprite.spritecollide(self, lava_group, False):
                game_over = -1
            if pygame.sprite.spritecollide(self, exit_group, False) and self.key:
                game_over = 1
        elif game_over==-1:
            self.image=self.death_image
            if self.rect.y>0:
                self.rect.y-=5
        screen.blit(self.image, self.rect)




class World():
    def __init__(self,data):
        img_rock=pygame.image.load('images/map/tile10.png')
        img_rock_grass = pygame.image.load('images/map/tile7.png')
        self.tile_list=[]
        row_count=0
        for row in data:
            col_count=0
            for tile in row:
                if tile==1 or tile==2:
                    images={1:img_rock,2:img_rock_grass}
                    img=pygame.transform.scale(images[tile],(tile_size,tile_size))
                    img_rect=img.get_rect()
                    img_rect.x=col_count*tile_size
                    img_rect.y=row_count*tile_size
                    tile=(img,img_rect)
                    self.tile_list.append(tile)
                elif tile==3:
                    lava=Lava(col_count*tile_size,row_count*tile_size+(tile_size//2))
                    lava_group.add(lava)
                elif tile==5:
                    exit=Exit(col_count*tile_size,row_count*tile_size-(tile_size//2))
                    exit_group.add(exit)
                elif tile==6:
                    key=Key(col_count*tile_size+(tile_size//2),row_count*tile_size+(tile_size//2))
                    key_group.add(key)
                col_count+=1
            row_count+=1

    def draw(self):
        for tile in self.tile_list:
            screen.blit(tile[0],tile[1])

class Lava(pygame.sprite.Sprite):
    def __init__(self,x,y):
        super().__init__()
        img=pygame.image.load('images/map/tile6.png')
        self.image=pygame.transform.scale(img,(tile_size,(tile_size//2)))
        self.rect=self.image.get_rect()
        self.rect.x=x
        self.rect.y = y

lava_group=pygame.sprite.Group()

class Button():
    def __init__(self,x,y,image):
        self.image=pygame.image.load(image)
        self.rect=self.image.get_rect(center=(x,y))

    def draw(self):
        action=False
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            if pygame.mouse.get_pressed()[0]==1:
                action=True

        screen.blit(self.image,self.rect)
        return action

class Exit(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        img = pygame.image.load('images/exit.png')
        self.image = pygame.transform.scale(img, (tile_size, int(tile_size * 1.5)))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

exit_group=pygame.sprite.Group()


class Key(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        img = pygame.image.load('images/map/key1.png')
        self.image = pygame.transform.scale(img, (tile_size // 2,(tile_size // 2)))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

key_group=pygame.sprite.Group()


player=Player()
world=World(world_data)

restart_button=Button(width//2,height//2,'images/restart.png')
start_button = Button(width//2 - 150, height //2, "images/start_btn.png")
exit_button = Button(width//2 + 150, height //2, "images/exit_btn.png")
run=True
main_menu=True
while run:
    screen.blit(fon,(0,0))
    for i in pygame.event.get():
        if i.type==pygame.QUIT:
            run=False




    player.update()
    world.draw()
    lava_group.draw(screen)
    exit_group.draw(screen)
    key_group.draw(screen)
    lava_group.update()

    if game_over==-1:
        if restart_button.draw():
            player=Player()
            # world=World(world_data)
            world=reset_level()
            game_over=0
    if game_over==1:
        # player.key=False
        game_over=0
        if level<max_level:
            level+=1
            world=reset_level()
        else:
            print('win')
            main_menu=True


    if main_menu:
        if exit_button.draw():
            run=False
        if start_button.draw():
            main_menu=False
            level=1
            world=reset_level()

    pygame.display.update()
    clock.tick(fps)
pygame.quit()
































