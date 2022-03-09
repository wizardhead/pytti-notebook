"""
Run the following in the notebook prior to using objects in this module:

    !pip install -q ipycanvas
    from google.colab import output
    output.enable_custom_widget_manager()
"""

#https://github.com/martinRenou/ipycanvas/issues/170#issuecomment-1062071346
#https://github.com/martinRenou/ipycanvas/blob/master/examples/hand_drawing.ipynb

from IPython.display import display
from ipywidgets import Image
from ipywidgets import ColorPicker, IntSlider, link, AppLayout, HBox

from ipycanvas import (
  Canvas,
  RoughCanvas, 
  MultiRoughCanvas,
  MultiCanvas,
  hold_canvas,
)

from functools import partial

class Sketcher:
    def __init__(
        self,
        starting_color="#749cb8",
    ):
        self.starting_color=starting_color
        self.init_canvas()
        self.init_picker()
        self.link()

    def link(self):
        picker, canvas = self.picker, self.mask_canvas
        #picker, canvas = self.picker, self.container[1]
        link((picker, "value"), (canvas, "stroke_style"))
        link((picker, "value"), (canvas, "fill_style"))
        return picker, canvas 

    def init_picker(self):
        self.picker = ColorPicker(
            description="Color:", 
            value=self.starting_color,
        )

    @property
    def mask_canvas(self): 
        return self.container[1]

    @property
    def bgnd_canvas(self): 
        return self.container[0]

    def init_canvas(
        self,
        width = 400,
        height = 400,
    ):
        self.width = width
        self.height = height 
        self.container = MultiCanvas(2, width=width, height=height, sync_image_data=True)

        self.mask_canvas.sync_image_data=True
        self.mask_canvas.on_mouse_down(self.on_mouse_down)
        self.mask_canvas.on_mouse_move(self.on_mouse_move)
        self.mask_canvas.on_mouse_up(self.on_mouse_up)
        self.mask_canvas.stroke_style = self.starting_color # can I just link the picker here?
        self.mask_canvas.fill_style = self.starting_color # can I just link the picker here?

        self.drawing = False
        self.position = None
        self.shape = []
        return self.container

    def set_background(self, im):
        self.bgnd_canvas.draw_image(im, 0,0)

    def on_mouse_down(self, x, y):
        self.drawing = True
        self.position = (x, y)
        self.shape = [self.position]

    def on_mouse_move(self, x1, y1):
        if not self.drawing:
            return
        with hold_canvas(self.container):
            x0, y0 = self.position
            self.mask_canvas.stroke_line(x0, y0, x1, y1)
            self.position = (x1, y1)
        self.shape.append(self.position)

    def on_mouse_up(self, x1, y1):
        self.drawing = False
        with hold_canvas(self.container):
            x_previous, y_previous = self.position
            x0, y0 = self.shape[0]
            self.mask_canvas.stroke_line(x_previous, y_previous, x1, y1)
            self.mask_canvas.stroke_line(x1, y1, x0, y0)
            self.shape.append((x0, y0))             
            self.mask_canvas.fill_polygon(self.shape)
        self.shape = []
        self.mask_canvas.save()

    def undo(self):
        # yeah.... this doesn't work.
        self.mask_canvas.restore()

    def show(self):
        display(HBox((self.container, self.picker)))
        #display(self.container)