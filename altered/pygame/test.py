import pygame, sys
from pgu import gui

screen = None
WIDTH = 640
HEIGHT = 480
def init_pygame():
    global screen
    pygame.display.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.DOUBLEBUF)
    pygame.display.set_caption('Testing PGU')

class SimpleDialog(gui.Dialog):
    def __init__(self):
        title = gui.Label("Spam")
        main = gui.Container(width=20, height=20)
        # I patched PGU to use new style classes.
        super(SimpleDialog, self).__init__(title, main, width=40, height=40)

    def close(self, *args, **kwargs):
        print ("closing")
        return super(SimpleDialog, self).close(*args, **kwargs)

def run():
    init_pygame()
    app = gui.App()

    dialog = SimpleDialog()
    app.init(dialog)

    empty = gui.Container(width=WIDTH, height=HEIGHT)
    app.init(empty)

    app.paint(screen)
    pygame.display.flip()
    while True:
        app.paint(screen)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 3: # right mouse button
                    print ("opening")
                    dialog.open()
                else:
                    app.event(event)
            elif event.type == pygame.QUIT:
                sys.exit()
            else:
                app.event(event)

if __name__=='__main__':
    run()