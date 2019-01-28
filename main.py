from tkinter import *
from PIL import Image
from PIL import ImageTk
from tkinter import filedialog
import cv2
import numpy as np
import atexit 

class ImageEditor:
    def __init__(self, root):
        self.root=root
        self.panelA = None
        self.panelB = None
        self.editSettings = None
        self.image=None
        self.canvas_image=None
        self.start_x=None
        self.start_y=None
        self.curX=None
        self.curY=None
        self.toCrop=False
        self.history=[]
        self.openedRow=-1
        self.openedWidget=None
        self.imageMod=None
        self.post_init()

    def post_init(self):
        self.menubar = Menu(self.root)
        self.filemenu = Menu(self.menubar, tearoff=0)
        self.filemenu.add_command(label="Open file", command=self.select_image)
        self.filemenu.add_command(label="Save file", command=self.save_image)
        self.filemenu.add_command(label="Edit settings", command=self.edit_initialize)
        self.filemenu.add_command(label="Exit", command=self.quit)
        self.menubar.add_cascade(label="File", menu=self.filemenu)
        self.root.config(menu=self.menubar)
        self.root.bind('<Control-s>', self.save_image)
        self.root.bind('<Control-o>', self.select_image)
        self.root.bind('<Control-e>', self.edit_initialize)
        self.root.bind('<Control-q>', self.quit)

    def quit(self, event=None):
        self.root.destroy()

    def on_closing(self):
        self.editSettings.destroy()
        self.editSettings = None

    def change_panelB(self,image=None):
        imageOnB = None
        try:
            if(image == None):
                imageOnB = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
        except:
            imageOnB = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        imageOnB = Image.fromarray(imageOnB)
        imageOnB=ImageTk.PhotoImage(imageOnB)
        self.root.imageOnB = imageOnB
        if self.panelB is None:
            self.panelB = Canvas(self.root, bg='white', height = self.image.shape[0], width = self.image.shape[1])
            self.canvas_image = self.panelB.create_image(0,0,anchor="nw",image=imageOnB)
            self.panelB.pack(side="right", padx=10, pady=10)  
            self.panelB.bind("<ButtonPress-1>", self.on_button_press)
            self.panelB.bind("<B1-Motion>", self.on_move_press)
            self.panelB.bind("<ButtonRelease-1>", self.on_button_release)
        else:
            self.panelB.itemconfig(self.canvas_image, image = imageOnB)

    def on_button_press(self,event):
        if(self.toCrop):
            self.start_x = self.panelB.canvasx(event.x)
            self.start_y = self.panelB.canvasy(event.y)
            self.rect = self.panelB.create_rectangle(0,0, 1, 1, fill="", outline='green', width=3)

    def on_move_press(self,event):
        if(self.toCrop):
            self.curX = self.panelB.canvasx(event.x)
            self.curY = self.panelB.canvasy(event.y)
            self.panelB.coords(self.rect, self.start_x, self.start_y, self.curX, self.curY) 

    def on_button_release(self,event):
        if(self.toCrop):
            self.panelB.delete(self.rect)
            self.cropImage()
    
    def change_panelA(self):
        imageOnA = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
        imageOnA = Image.fromarray(imageOnA)
        imageOnA=ImageTk.PhotoImage(imageOnA)
        self.root.imageOnA = imageOnA
        if self.panelA is None:
            self.panelA = Label(image = imageOnA, height = self.height, width = self.width)
            self.panelA.pack(side="left", padx=10, pady=10)  
        else:
            self.panelA.configure(image=imageOnA)           

    def select_image(self,event=None):
        path = filedialog.askopenfilename()
        if len(path) > 0:
            self.image = cv2.imread(path)
            self.height = self.image.shape[0]
            self.width = self.image.shape[1]
            if (self.width > 640):
                r = 640.0 / self.image.shape[1]
                dim = (640, int(self.image.shape[0] * r))
                self.image = cv2.resize(self.image, dim, interpolation=cv2.INTER_AREA)
                self.height = self.image.shape[0]
                self.width = self.image.shape[1]
            if (self.height > 480):
                r = 480.0 / self.image.shape[0]
                dim = (int(self.image.shape[1] * r), 480)
                self.image = cv2.resize(self.image, dim, interpolation=cv2.INTER_AREA)
                self.height = self.image.shape[0]
                self.width = self.image.shape[1]
            self.imageMod=self.image.copy()
            self.change_panelA()
            self.change_panelB()
            if self.editSettings is None:
                self.edit_initialize()
            
    def save_image(self,event=None):
        if self.panelB is None:
            return
        f = filedialog.asksaveasfile(mode='w',filetypes = (("jpeg files","*.jpg"),("all files","*.*")))
        if f is None:
            return
        if f:
            try:
                cv2.imwrite(f.name,self.changed)
            except:
                cv2.imwrite(f.name,self.image)

    def setDefault(self):
        self.rotateVar.set(0)
        self.translateXVar.set(1)
        self.translateYVar.set(1)
        self.resizeXVar.set(1)
        self.resizeYVar.set(1)
        self.flipVEntry.config(text="False")
        self.flipHEntry.config(text="False")
        self.cropEntry.config(text="False")
        self.toCrop = False


    def Confirm(self, LabelWidget, ScaleWidget, EntryWidget, ConfirmWidget, CloseWidget, OpenWidget, OpenRow):
        self.image=self.imageMod
        self.Close(LabelWidget, ScaleWidget, EntryWidget, ConfirmWidget, CloseWidget, OpenWidget, OpenRow)

    def Close(self, LabelWidget, ScaleWidget, EntryWidget, ConfirmWidget, CloseWidget, OpenWidget, OpenRow):
        LabelWidget.grid_forget()
        ScaleWidget.grid_forget()
        EntryWidget.grid_forget()
        ConfirmWidget.grid_forget()
        CloseWidget.grid_forget()
        self.imageMod = self.image
        OpenWidget.grid(row=OpenRow,column=0,columnspan=3, padx=5,pady=5)
        self.openedRow = -1
        self.openedWidget = None
        self.setDefault()
        self.change_panelB(self.image)

    def Open(self, LabelWidget, ScaleWidget, EntryWidget, ConfirmWidget, CloseWidget, OpenWidget, OpenRow):
        OpenWidget.grid_forget()
        LabelWidget.grid(row=OpenRow,column=0, padx=5,pady=5)
        ScaleWidget.grid(row=OpenRow,column=1, padx=5,pady=5)
        EntryWidget.grid(row=OpenRow,column=2, padx=5,pady=5)
        ConfirmWidget.grid(row=OpenRow,column=3, padx=5,pady=5)
        CloseWidget.grid(row=OpenRow,column=4, padx=5,pady=5)
        if (self.openedRow == -1):
            pass
        else:
            for children in self.editSettings.grid_slaves(row = self.openedRow):
                children.grid_forget()
            self.openedWidget.grid(row=self.openedRow,column=0,columnspan=3, padx=5,pady=5)
            self.imageMod = self.image
            self.setDefault()
            self.change_panelB(self.image)
        self.openedRow = OpenRow
        self.openedWidget = OpenWidget

    def rotateImage(self, name=None, index=None, mode=None):
        (h, w) = self.image.shape[:2]
        (cX, cY) = (w / 2, h / 2)
        M = cv2.getRotationMatrix2D((cX, cY), self.rotateVar.get(), 1.0)
        image = cv2.warpAffine(self.image, M, (w, h), borderMode=cv2.BORDER_CONSTANT, borderValue=(255,255,255))
        self.imageMod=image
        self.change_panelB(image)

    def translateXImage(self, name=None, index=None, mode=None):
        M = np.float32([[1, 0, float(self.translateXVar.get())], [0, 1, 0]])
        image = cv2.warpAffine(self.image, M, (self.image.shape[1], self.image.shape[0]), borderMode=cv2.BORDER_CONSTANT, borderValue=(255,255,255))
        self.imageMod=image
        self.change_panelB(image)

    def translateYImage(self, name=None, index=None, mode=None):
        M = np.float32([[1, 0, 0], [0, 1, float(self.translateYVar.get())]])
        image = cv2.warpAffine(self.image, M, (self.image.shape[1], self.image.shape[0]), borderMode=cv2.BORDER_CONSTANT, borderValue=(255,255,255))
        self.imageMod=image
        self.change_panelB(image)

    def resizeXImage(self, name=None, index=None, mode=None):
        dim=(int(self.resizeXVar.get()*self.image.shape[1]),int(self.image.shape[0]))
        image = cv2.resize(self.image, dim, interpolation=cv2.INTER_AREA)
        self.imageMod=image
        self.change_panelB(image)

    def resizeYImage(self, name=None, index=None, mode=None):
        dim=(int(self.image.shape[1]),int(self.resizeYVar.get()*self.image.shape[0]))
        image = cv2.resize(self.image, dim, interpolation=cv2.INTER_AREA)
        self.imageMod=image
        self.change_panelB(image)

    def flipVImage(self, name=None, index=None, mode=None):
        image = cv2.flip(self.imageMod,1)
        if (self.flipVEntry.cget("text")=="False"):
            self.flipVEntry.config(text="True")
        else:
            self.flipVEntry.config(text="False")
        self.imageMod=image
        self.change_panelB(image)

    def flipHImage(self, name=None, index=None, mode=None):
        image = cv2.flip(self.imageMod,0)
        if (self.flipHEntry.cget("text")=="False"):
            self.flipHEntry.config(text="True")
        else:
            self.flipHEntry.config(text="False")
        self.imageMod=image
        self.change_panelB(image)

    def precropImage(self, name=None, index=None, mode=None):
        if (self.cropEntry.cget("text")=="False"):
            self.cropEntry.config(text="True")
            self.toCrop = True
        else:
            self.cropEntry.config(text="False")
            self.toCrop = False

    def cropImage(self, name=None, index=None, mode=None):
        if(self.toCrop == True):
            image = self.imageMod[int(self.start_y):int(self.curY),int(self.start_x):int(self.curX)]
            self.imageMod = image
            self.change_panelB(image)
            self.cropEntry.config(text="False")
            self.toCrop=False

    def CreateEntry(self, VarDefault, TraceFunc, OpenText, ScaleMin, ScaleMax, OpenRow, resolution = 1):
        Var = DoubleVar()
        Var.set(VarDefault)
        Var.trace("w", TraceFunc)
        OpenWidget = Button(self.editSettings, text=OpenText, command=lambda: self.Open(LabelWidget, ScaleWidget, EntryWidget, ConfirmWidget, CloseWidget, OpenWidget, OpenRow), width=90)
        LabelWidget=Label(self.editSettings,text=OpenText)
        ScaleWidget = Scale(self.editSettings, from_=ScaleMin, to=ScaleMax, orient=HORIZONTAL, length=360, variable=Var, showvalue=0, resolution = resolution)
        EntryWidget = Entry(self.editSettings, textvariable=Var)
        ConfirmWidget = Button(self.editSettings, text="Confirm", command=lambda: self.Confirm(LabelWidget, ScaleWidget, EntryWidget, ConfirmWidget, CloseWidget, OpenWidget, OpenRow))
        CloseWidget = Button(self.editSettings, text="Close", command=lambda: self.Close(LabelWidget, ScaleWidget, EntryWidget, ConfirmWidget, CloseWidget, OpenWidget, OpenRow))
        OpenWidget.grid(row=OpenRow,column=0,columnspan=3, padx=5,pady=5)
        return Var, OpenWidget, LabelWidget, ScaleWidget, EntryWidget, ConfirmWidget, CloseWidget

    def CreateButtonEntry(self, TraceFunc, OpenText, OpenRow):
        OpenWidget = Button(self.editSettings, text=OpenText, command=lambda: self.Open(LabelWidget, ButtonWidget, EntryWidget, ConfirmWidget, CloseWidget, OpenWidget, OpenRow), width=90)
        LabelWidget=Label(self.editSettings,text=OpenText)
        ButtonWidget = Button(self.editSettings, text=OpenText, command=TraceFunc)
        EntryWidget = Label(self.editSettings, text="False")
        ConfirmWidget = Button(self.editSettings, text="Confirm", command=lambda: self.Confirm(LabelWidget, ButtonWidget, EntryWidget, ConfirmWidget, CloseWidget, OpenWidget, OpenRow))
        CloseWidget = Button(self.editSettings, text="Close", command=lambda: self.Close(LabelWidget, ButtonWidget, EntryWidget, ConfirmWidget, CloseWidget, OpenWidget, OpenRow))
        OpenWidget.grid(row=OpenRow,column=0,columnspan=3, padx=5,pady=5)
        return OpenWidget, LabelWidget, ButtonWidget, EntryWidget, ConfirmWidget, CloseWidget

    def edit_initialize(self, event=None):
        if (self.panelB != None):
            self.editSettings = Toplevel()
            self.editSettings.wm_title("Edit Settings")
            self.editSettings.protocol("WM_DELETE_WINDOW", self.on_closing)
            self.rotateVar, self.rotateOpen, self.rotateLabel, self.rotateScale, self.rotateEntry, self.rotateConfirm, self.rotateClose = self.CreateEntry(VarDefault = 0, TraceFunc = self.rotateImage, OpenText = "Rotate", ScaleMin = -180, ScaleMax = 180, OpenRow = 0)
            self.translateXVar, self.translateXOpen, self.translateXLabel, self.translateXScale, self.translateXEntry, self.translateXConfirm, self.translateXClose = self.CreateEntry(VarDefault = 1, TraceFunc = self.translateXImage, OpenText = "Translate X", ScaleMin = -self.image.shape[1], ScaleMax = self.image.shape[1], OpenRow = 1)
            self.translateYVar, self.translateYOpen, self.translateYLabel, self.translateYScale, self.translateYEntry, self.translateYConfirm, self.translateYClose = self.CreateEntry(VarDefault = 1, TraceFunc = self.translateYImage, OpenText = "Translate Y", ScaleMin = -self.image.shape[0], ScaleMax = self.image.shape[0], OpenRow = 2)
            self.resizeXVar, self.resizeXOpen, self.resizeXLabel, self.resizeXScale, self.resizeXEntry, self.resizeXConfirm, self.resizeXClose = self.CreateEntry(VarDefault = 1, TraceFunc = self.resizeXImage, OpenText = "Resize X", ScaleMin = 0.1, ScaleMax = 5, resolution=0.1, OpenRow = 3)
            self.resizeYVar, self.resizeYOpen, self.resizeYLabel, self.resizeYScale, self.resizeYEntry, self.resizeYConfirm, self.resizeYClose = self.CreateEntry(VarDefault = 1, TraceFunc = self.resizeYImage, OpenText = "Resize Y", ScaleMin = 0.1, ScaleMax = 5, resolution=0.1, OpenRow = 4)
            self.flipVOpen, self.flipVLabel, self.flipVButton, self.flipVEntry, self.flipVConfirm, self.flipVClose = self.CreateButtonEntry(TraceFunc = self.flipVImage, OpenText = "Flip vertically", OpenRow = 5)
            self.flipHOpen, self.flipHLabel, self.flipHButton, self.flipHEntry, self.flipHConfirm, self.flipHClose = self.CreateButtonEntry(TraceFunc = self.flipHImage, OpenText = "Flip horizontally", OpenRow = 6)
            self.cropOpen, self.cropLabel, self.cropButton, self.cropEntry, self.cropConfirm, self.cropClose = self.CreateButtonEntry(TraceFunc = self.precropImage, OpenText = "Crop image", OpenRow = 7)

if __name__ == '__main__':
    root = Tk()
    root.title("OpenCV Editor")
    Editor = ImageEditor(root)
    root.mainloop()