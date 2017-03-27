# coding=utf-8
# -------------------------------------------------------------------------------
# Name:        Object bounding box label tool
# Purpose:     Label object bboxes for Detection data
# Author:      HeRongWei modified from Qiushi
# Created:     2017/03/07

#
# -------------------------------------------------------------------------------
from __future__ import division
from Tkinter import *
import tkMessageBox
from PIL import Image, ImageTk
import os
import glob
import random
from xml.dom.minidom import Document
import numpy as np

# colors for the bboxes
COLORS = ['red', 'blue', 'yellow', 'pink', 'cyan', 'green', 'black']
# image sizes for the examples
SIZE = 256, 256

class LabelTool():
    def __init__(self, master):
        # set up the main frame
        self.parent = master
        self.parent.title("LabelTool")
        self.frame = Frame(self.parent)
        self.frame.pack(fill=BOTH, expand=1)
        self.parent.resizable(width=TRUE, height=TRUE)

        # initialize global state
        self.imageDir = ''
        self.imageList = []
        self.egDir = ''
        self.egList = []
        self.outDir = ''
        self.cur = 0
        self.total = 0
        self.category = 0
        self.count = 0
        self.color = ''
<<<<<<< 71de2d43a9d86cb9b06a13510a0dc35c05d7e254
        self.carMove1= []
        self.carMove2= []
        self.carLight= []
        self.manMove1= []
        self.manMove2= []
        self.bikeMove1= []
        self.bikeMove2= []
=======
        self.carMove1 = []
        self.carMove2 = []
        self.carLight = []
        self.manMove1 = []
        self.manMove2 = []
        self.bikeMove1 = []
        self.bikeMove2 = []
>>>>>>> second commit
        self.points = []
        self.imagename = ''
        self.labelfilename = ''
        self.boxcnt = 0
        self.cntCar = 0
        self.cntMan = 0
        self.cntBike = 0
        self.scale_value = 1
        # 2017-3-11 herongwei add the xmlfilename
        self.xmlfilename = ''
        self.tkimg = None


        # initialize mouse state
        self.STATE = {}
        self.STATE['click'] = 0
        self.STATE['x'], self.STATE['y'] = 0, 0

        # reference to bbox
        self.bboxIdList = []
        self.bboxId = None
        self.bboxList = []

        # 2017-3-9 herongwei reference to the lines of DrawCar
        self.lineIdList = []
        self.lineId = None

        self.hl = None
        self.vl = None

        # ----------------- GUI stuff ---------------------
        # dir entry & load
        self.label = Label(self.frame, text="Image Dir:")
        self.label.grid(row=0, column=0, sticky=E)
        self.entry = Entry(self.frame)
        self.entry.grid(row=0, column=1, sticky=W + E)
        self.ldBtn = Button(self.frame, text="Load", command=self.loadDir)
        self.ldBtn.grid(row=0, column=2, sticky=W + E)

        # main panel for labeling
        self.mainPanel = Canvas(self.frame, cursor='tcross')
        # 2017-3-10 herongwei modify
        self.mainPanel.bind("<Button-1>", self.drawCar)
        # 2017-3-9 herongwei add the process of Wheel
        self.mainPanel.bind("<Control-MouseWheel>", self.processWheel)
        # 2017-3-10 herongwei add the labeling of Other
        self.mainPanel.bind("<Control-Button-1>", self.drawMan)
        self.mainPanel.bind("<Shift-Button-1>", self.drawBicycle)
        self.mainPanel.bind("<Alt-Button-1>", self.drawTrafficTag)
        self.mainPanel.bind("<Control-Button-3>", self.drawGuideboard)
        self.mainPanel.bind("<Shift-Button-3>", self.drawSignalLight)
        self.mainPanel.bind("<Button-3>", self.drawGuardBar)
        self.mainPanel.bind("<Button-2>", self.drawReachArea)

        
        # 20117-3-25 heringwei add the keyBoard to callback
        # 2017-3-13 herongwei remove the motion of mouseMoving
        #self.mainPanel.bind("<Motion>", self.mouseMove)
        self.parent.bind("<Escape>", self.cancelBBox)  # press <Espace> to cancel current bbox
        self.parent.bind("q", self.carStraight)
        self.parent.bind("w", self.carLeft)
        self.parent.bind("e", self.carRight)
        self.parent.bind("a", self.carForward)
        self.parent.bind("s", self.carBackward)
        self.parent.bind("z", self.LIGHT_HIGHBEAM)
        self.parent.bind("x", self.LIGHT_LOWBEAM)
        self.parent.bind("c", self.BRAKELIGHT)
        self.parent.bind("r", self.manStraight)
        self.parent.bind("t", self.manLeft)
        self.parent.bind("y", self.manRight)
        self.parent.bind("f", self.manForward)
        self.parent.bind("g", self.manBackward)
        self.parent.bind("u", self.BicycleStraight)
        self.parent.bind("i", self.BicycleLeft)
        self.parent.bind("o", self.BicycleRight)
        self.parent.bind("j", self.BicycleForward)
        self.parent.bind("k", self.BicycleBackward)
        #self.parent.bind("s", self.cancelBBox)
        #self.parent.bind("a", self.prevImage)  # press 'a' to go backforward
        #self.parent.bind("d", self.nextImage)  # press 'd' to go forward
        self.mainPanel.grid(row=1, column=1, rowspan=4, sticky=W + N)
        
        self.mainPanel.focus_set()

        # showing bbox info & delete bbox
        self.listbox = Listbox(self.frame, width=10, height=12)
        self.listbox.grid(row=1, column=2, sticky=N)
        self.btnDel = Button(self.frame, text='Delete', command=self.delBBox)
        self.btnDel.grid(row=2, column=2, sticky=W + E + N)
        self.btnClear = Button(self.frame, text='ClearAll', command=self.clearBBox)
        self.btnClear.grid(row=3, column=2, sticky=W + E + N)
        # 2017-3-9 herongwei other buttons
        # self.btnDrawMan = Button(self.frame, text = 'DrawMan', command = self.drawMan)
        # self.btnDrawMan.grid(row = 5, column = 2, sticky = W+E+N)
        # 2017-3-14 herongwei add other buttons
        self.redBtn = Button(self.frame, text='Red', command=self.RedSelect)
        self.redBtn.grid(row=0, column=3, sticky=W+E+N)
        self.greenBtn = Button(self.frame, text='Green', command=self.GreenSelect)
        self.greenBtn.grid(row=1, column=3, sticky=W+E+N)
        self.yellowBtn = Button(self.frame,text='Yellow',command=self.YellowSelect)
        self.yellowBtn.grid(row=2, column=3, sticky=W+E+N)
        self.lbcnt = Label(self.frame, text="total:    ")
        self.lbcnt.grid(row=3, column=3, sticky=E)
        
        # 2017-3-15 herongwei add the button of car's Attributes (defalt=stop/straight)
<<<<<<< 71de2d43a9d86cb9b06a13510a0dc35c05d7e254
        self.carLeftBtn = Button(self.frame, text="carLeft", command=self.carLeft)
        self.carLeftBtn.grid(row=0, column=4, sticky=W+E+N)
        self.carRightBtn = Button(self.frame, text="carRight", command=self.carRight)
        self.carRightBtn.grid(row=1, column=4, sticky=W+E+N)
        self.carStraightBtn = Button(self.frame, text="carStraight", command=self.carStraight)
        self.carStraightBtn.grid(row=2, column=4, sticky=W+E+N )
        self.carForwardBtn = Button(self.frame, text="carForward", command=self.carForward)
        self.carForwardBtn.grid(row=3, column=4, sticky=W+E+N)
        self.carBackwardBtn = Button(self.frame, text="carBackward", command=self.carBackward)
        self.carBackwardBtn.grid(row=4, column=4, sticky=W+E+N)
        
        # 2017-3-15 herongwei add the button of CarLight's Attributes (defalt=None)
        self.LIGHT_HIGHBEAMBtn = Button(self.frame, text="LIGHT_HIGHBEAM", command=self.LIGHT_HIGHBEAM)
        self.LIGHT_HIGHBEAMBtn.grid(row=5, column=4, sticky=W+E+N)
        self.LIGHT_LOWBEAMBtn = Button(self.frame, text="LIGHT_LOWBEAM", command=self.LIGHT_LOWBEAM)
        self.LIGHT_LOWBEAMBtn.grid(row=6, column=4, sticky=W+E+N)
        self.BRAKELIGHTBtn = Button(self.frame, text="BRAKELIGHT", command=self.BRAKELIGHT)
        self.BRAKELIGHTBtn.grid(row=7, column=4, sticky=W+E+N)
        
        # 2017-3-15 herongwei add the button of Man's Attributes (defalt=stop)
        self.manLeftBtn = Button(self.frame, text="manLeft", command=self.manLeft)
        self.manLeftBtn.grid(row=0, column=5, sticky=W+E+N)
        self.manRightBtn = Button(self.frame, text="manRight", command=self.manRight)
        self.manRightBtn.grid(row=1, column=5, sticky=W+E+N)
        self.manStraightBtn = Button(self.frame, text="manStraight", command=self.manStraight)
        self.manStraightBtn.grid(row=2, column=5, sticky=W+E+N)
        self.manForwardBtn = Button(self.frame, text="manForward", command=self.manForward)
        self.manForwardBtn.grid(row=3, column=5, sticky=W+E+N)
        self.manBackwardBtn = Button(self.frame, text="manBackward", command=self.manBackward)
        self.manBackwardBtn.grid(row=4, column=5, sticky=W+E+N)

        # 2017-3-15 herongwei add the button of Bicycle's Attributes (defalt=None)
        self.BicycleForwardBtn = Button(self.frame, text="BicycleForward", command=self.BicycleForward)
        self.BicycleForwardBtn.grid(row=5, column=3, sticky=W+E+N)
        self.BicycleBackwardBtn = Button(self.frame, text="BicycleBackward", command=self.BicycleBackward)
        self.BicycleBackwardBtn.grid(row=6, column=3, sticky=W+E+N)

        self.BicycleLeftBtn = Button(self.frame, text="BicycleLeft", command=self.BicycleLeft)
        self.BicycleLeftBtn.grid(row=5, column=2, sticky=W+E+N)
        self.BicycleRightBtn = Button(self.frame, text="BicycleRight", command=self.BicycleRight)
        self.BicycleRightBtn.grid(row=6, column=2, sticky=W+E+N)
        self.BicycleStraightBtn = Button(self.frame, text="BicycleStrainght", command=self.BicycleStraight)
=======
        self.carLeftBtn = Button(self.frame, text="carLeft(w)", command=self.carLeft)
        self.carLeftBtn.grid(row=0, column=4, sticky=W+E+N)
        self.carRightBtn = Button(self.frame, text="carRight(e)", command=self.carRight)
        self.carRightBtn.grid(row=1, column=4, sticky=W+E+N)
        self.carStraightBtn = Button(self.frame, text="carStraight(q)", command=self.carStraight)
        self.carStraightBtn.grid(row=2, column=4, sticky=W+E+N )
        self.carForwardBtn = Button(self.frame, text="carForward(a)", command=self.carForward)
        self.carForwardBtn.grid(row=3, column=4, sticky=W+E+N)
        self.carBackwardBtn = Button(self.frame, text="carBackward(s)", command=self.carBackward)
        self.carBackwardBtn.grid(row=4, column=4, sticky=W+E+N)
        
        # 2017-3-15 herongwei add the button of CarLight's Attributes (defalt=None)
        self.LIGHT_HIGHBEAMBtn = Button(self.frame, text="LIGHT_HIGHBEAM(z)", command=self.LIGHT_HIGHBEAM)
        self.LIGHT_HIGHBEAMBtn.grid(row=5, column=4, sticky=W+E+N)
        self.LIGHT_LOWBEAMBtn = Button(self.frame, text="LIGHT_LOWBEAM(x)", command=self.LIGHT_LOWBEAM)
        self.LIGHT_LOWBEAMBtn.grid(row=6, column=4, sticky=W+E+N)
        self.BRAKELIGHTBtn = Button(self.frame, text="BRAKELIGHT(c)", command=self.BRAKELIGHT)
        self.BRAKELIGHTBtn.grid(row=7, column=4, sticky=W+E+N)
        
        # 2017-3-15 herongwei add the button of Man's Attributes (defalt=stop)
        self.manLeftBtn = Button(self.frame, text="manLeft(t)", command=self.manLeft)
        self.manLeftBtn.grid(row=0, column=5, sticky=W+E+N)
        self.manRightBtn = Button(self.frame, text="manRight(y)", command=self.manRight)
        self.manRightBtn.grid(row=1, column=5, sticky=W+E+N)
        self.manStraightBtn = Button(self.frame, text="manStraight(r)", command=self.manStraight)
        self.manStraightBtn.grid(row=2, column=5, sticky=W+E+N)
        self.manForwardBtn = Button(self.frame, text="manForward(f)", command=self.manForward)
        self.manForwardBtn.grid(row=3, column=5, sticky=W+E+N)
        self.manBackwardBtn = Button(self.frame, text="manBackward(g)", command=self.manBackward)
        self.manBackwardBtn.grid(row=4, column=5, sticky=W+E+N)

        # 2017-3-15 herongwei add the button of Bicycle's Attributes (defalt=None)
        self.BicycleForwardBtn = Button(self.frame, text="BicycleForward(j)", command=self.BicycleForward)
        self.BicycleForwardBtn.grid(row=5, column=3, sticky=W+E+N)
        self.BicycleBackwardBtn = Button(self.frame, text="BicycleBackward(k)", command=self.BicycleBackward)
        self.BicycleBackwardBtn.grid(row=6, column=3, sticky=W+E+N)

        self.BicycleLeftBtn = Button(self.frame, text="BicycleLeft(i)", command=self.BicycleLeft)
        self.BicycleLeftBtn.grid(row=5, column=2, sticky=W+E+N)
        self.BicycleRightBtn = Button(self.frame, text="BicycleRight(o)", command=self.BicycleRight)
        self.BicycleRightBtn.grid(row=6, column=2, sticky=W+E+N)
        self.BicycleStraightBtn = Button(self.frame, text="BicycleStrainght(u)", command=self.BicycleStraight)
>>>>>>> second commit
        self.BicycleStraightBtn.grid(row=7, column=2, sticky=W + E + N)
        
        # control panel for image navigation
        self.ctrPanel = Frame(self.frame)
        self.ctrPanel.grid(row=8, column=1, columnspan=2, sticky=W + E)
        #self.prevBtn = Button(self.ctrPanel, text='<< Prev', width=10, command=self.prevImage)
        #self.prevBtn.pack(side=LEFT, padx=5, pady=3)
        self.nextBtn = Button(self.ctrPanel, text='Next >>', width=10, command=self.nextImage)
        self.nextBtn.pack(side=LEFT, padx=5, pady=3)
        self.progLabel = Label(self.ctrPanel, text="Progress:     /    ")
        self.progLabel.pack(side=LEFT, padx=5)
        self.tmpLabel = Label(self.ctrPanel, text="Go to Image No.")
        self.tmpLabel.pack(side=LEFT, padx=5)
        self.idxEntry = Entry(self.ctrPanel, width=5)
        self.idxEntry.pack(side=LEFT)
        self.goBtn = Button(self.ctrPanel, text='Go', command=self.gotoImage)
        self.goBtn.pack(side=LEFT)

        # example pannel for illustration
        self.egPanel = Frame(self.frame, border=10)
        self.egPanel.grid(row=1, column=0, rowspan=5, sticky=N)
        self.tmpLabel2 = Label(self.egPanel, text="GUIDE:\n\
                               鼠标左键点击3次：车辆\n\
                               Control+鼠标左键：行人\n\
                               Shift+鼠标左键：自行/摩托车\n\
                               Alt+鼠标左键：交通标志\n\
                               Control+鼠标右键：路牌\n\
                               Shift+鼠标右键：信号灯\n\
                               鼠标右键：护栏\n\
                               滚轮按下：可行驶区域")
        self.tmpLabel2.pack(side=TOP, pady=5)
        self.egLabels = []
        for i in range(3):
            self.egLabels.append(Label(self.egPanel))
            self.egLabels[-1].pack(side=TOP)

        # display mouse position
        self.disp = Label(self.ctrPanel, text='')
        self.disp.pack(side=RIGHT)

        self.frame.columnconfigure(1, weight=1)
        self.frame.rowconfigure(4, weight=1)

    def loadDir(self, dbg=False):
        if not dbg:
            s = self.entry.get()
            self.parent.focus()
            self.category = int(s)
        else:
            s = r'D:\workspace\python\labelGUI'
        ##        if not os.path.isdir(s):
        ##            tkMessageBox.showerror("Error!", message = "The specified dir doesn't exist!")
        ##            return
        # get image list
        self.imageDir = os.path.join(r'./Images', '%03d' % (self.category))
        self.imageList = glob.glob(os.path.join(self.imageDir, '*.BMP'))
        if len(self.imageList) == 0:
            print 'No .JPEG images found in the specified dir!'
            return

        # default to the 1st image in the collection
        self.cur = 1
        self.total = len(self.imageList)

        # set up output dir
        self.outDir = os.path.join(r'./Labels', '%03d' % (self.category))
        if not os.path.exists(self.outDir):
            os.mkdir(self.outDir)

        # load example bboxes
        self.egDir = os.path.join(r'./Images', '%03d' % (self.category))
        if not os.path.exists(self.egDir):
            return
        filelist = glob.glob(os.path.join(self.egDir, '*.BMP'))
        self.tmp = []
        self.egList = []
        random.shuffle(filelist)
        for (i, f) in enumerate(filelist):
            if i == 3:
                break
            im = Image.open(f)
            r = min(SIZE[0] / im.size[0], SIZE[1] / im.size[1])
            new_size = int(r * im.size[0]), int(r * im.size[1])
            self.tmp.append(im.resize(new_size, Image.ANTIALIAS))
            self.egList.append(ImageTk.PhotoImage(self.tmp[-1]))
            self.egLabels[i].config(image=self.egList[-1], width=SIZE[0], height=SIZE[1])

        self.loadImage()
        print '%d images loaded from %s' % (self.total, s)
        

    def loadImage(self):
        # load image
        imagepath = self.imageList[self.cur - 1]
        self.img = Image.open(imagepath)
        
        self.tkimg = ImageTk.PhotoImage(self.img)
        tkimg_width = self.tkimg.width()*self.scale_value
        tkimg_height = self.tkimg.height()*self.scale_value
        # self.mainPanel.config(width = max(self.tkimg.width(), 400), height = max(self.tkimg.height(), 400))
        self.mainPanel.config(width=tkimg_width, height=tkimg_width)
        self.mainPanel.create_image(0, 0, image=self.tkimg, anchor=NW)
        self.progLabel.config(text="%04d/%04d" % (self.cur, self.total))

        # load labels
        # 2017-3-8 herongwei add another Point to be read from file
        # 2017-3-10 herongwei modified
        self.clearBBox()
        self.imagename = os.path.split(imagepath)[-1].split('.')[0]

        labelname = self.imagename + '.txt'
        self.labelfilename = os.path.join(self.outDir, labelname)
        xmlname = self.imagename + '.xml'
        self.xmlfilename = os.path.join(self.outDir, xmlname)

        bbox_cnt = 0
        if os.path.exists(self.labelfilename):
            with open(self.labelfilename) as f:
                
                for (i, line) in enumerate(f):
                    if i == 0:
                        bbox_cnt = int(line.strip())
                        continue
                    tmp = [int(t.strip()) for t in line.split()]
                    print tmp
                    if len(tmp) == 7:
                        if tmp[0] == 1:
                            self.bboxList.append(tuple(tmp))
                            tmpId = self.mainPanel.create_rectangle(tmp[1], tmp[2], \
                                                                    tmp[3], tmp[4], \
                                                                       width=2, \
                                                                       outline=COLORS[0], fill="orange")
                            self.drawLine(tmp[1], tmp[2], tmp[3], tmp[4], tmp[5], tmp[6])
                            self.bboxIdList.append(tmpId)
                            self.listbox.insert(END, '(%d, %d)(%d, %d)(%d, %d)' % (
                                                tmp[1], tmp[2], tmp[3], tmp[4], tmp[5], tmp[6]))
                            self.listbox.itemconfig(len(self.bboxIdList) - 1, fg=COLORS[0])
                        if tmp[0] == 7:
                            self.bboxList.append(tuple(tmp))
                            line = self.mainPanel.create_line(tmp[1], tmp[2], tmp[3], tmp[4],tmp[3], tmp[4], tmp[5], tmp[6], tmp[5], tmp[6],tmp[1], tmp[2],width=3)
                            
                            self.bboxIdList.append(tmpId)
                            self.listbox.insert(END, '(%d, %d)(%d, %d)(%d, %d)' % (
                                    tmp[1], tmp[2], tmp[3], tmp[4], tmp[5], tmp[6]))
                            self.listbox.itemconfig(len(self.bboxIdList) - 1, fg=COLORS[0])
                    if len(tmp) == 5:
                        self.bboxList.append(tuple(tmp))
                        tmpId = self.mainPanel.create_rectangle(tmp[1], tmp[2], \
                                                                tmp[3], tmp[4], \
                                                                width=2, \
                                                                outline=COLORS[0])
                        if tmp[0] == 6:
                            self.drawCircleOfTrafficLight(tmp[1], tmp[2], tmp[3], tmp[4])
                        self.bboxIdList.append(tmpId)
                        self.listbox.insert(END, '(%d, %d)(%d, %d)' % (tmp[1], tmp[2], tmp[3], tmp[4]))
                        self.listbox.itemconfig(len(self.bboxIdList) - 1, fg=COLORS[0])
               
    # 107-3-13 herongwei wirte infos into xml file
    def saveImage(self):
        doc = Document()
        detect = doc.createElement("detect")
        doc.appendChild(detect)

        with open(self.labelfilename, 'w') as f:
            f.write('%d\n' % len(self.bboxList))
            i_car = 0
            i_man = 0
            i_bike = 0
            for bbox in self.bboxList:
                f.write(' '.join(map(str, bbox)) + '\n')
                
                if len(bbox) == 7:
                    obj = doc.createElement("obj")
                    detect.appendChild(obj)
                    obj_type = doc.createElement("type")
                    obj.appendChild(obj_type)

                    if bbox[0] == 1 and i_car < self.cntCar:
                        type_str = "car"
                        obj_type_value = doc.createTextNode(type_str)
                        obj_type.appendChild(obj_type_value)
                        
                        car_move1 = doc.createElement("carMove1")
                        obj.appendChild(car_move1)
                        car_move1_value = doc.createTextNode(str(self.carMove1[i_car]))
                        car_move1.appendChild(car_move1_value)

                        car_move2 = doc.createElement("carMove2")
                        obj.appendChild(car_move2)
                        car_move2_value = doc.createTextNode(str(self.carMove2[i_car]))
                        car_move2.appendChild(car_move2_value)
                        
                        car_light = doc.createElement("carLight")
                        obj.appendChild(car_light)
                        car_Light_value = doc.createTextNode(str(self.carLight[i_car]))
                        car_light.appendChild(car_Light_value)
                        
                        axis = doc.createElement("axis")
                        obj.appendChild(axis)

                        x1_Tag = doc.createElement("x1")
                        axis.appendChild(x1_Tag)
                        x1_value = doc.createTextNode(str(bbox[1]))
                        x1_Tag.appendChild(x1_value)

                        y1_Tag = doc.createElement("y1")
                        axis.appendChild(y1_Tag)
                        y1_value = doc.createTextNode(str(bbox[2]))
                        y1_Tag.appendChild(y1_value)

                        x2_Tag = doc.createElement("x2")
                        axis.appendChild(x2_Tag)
                        x2_value = doc.createTextNode(str(bbox[3]))
                        x2_Tag.appendChild(x2_value)

                        y2_Tag = doc.createElement("y2")
                        axis.appendChild(y2_Tag)
                        y2_value = doc.createTextNode(str(bbox[4]))
                        y2_Tag.appendChild(y2_value)

                        x3_Tag = doc.createElement("x3")
                        axis.appendChild(x3_Tag)
                        x3_value = doc.createTextNode(str(bbox[5]))
                        x3_Tag.appendChild(x3_value)

                        y3_Tag = doc.createElement("y3")
                        axis.appendChild(y3_Tag)
                        y3_value = doc.createTextNode(str(bbox[6]))
                        y3_Tag.appendChild(y3_value)
                        
                        
                        i_car += 1
                            
                    elif bbox[0] == 7:
                        type_str = "GuardBar"
                        obj_type_value = doc.createTextNode(type_str)
                        obj_type.appendChild(obj_type_value)

                        axis = doc.createElement("axis")
                        obj.appendChild(axis)

                        x1_Tag = doc.createElement("x1")
                        axis.appendChild(x1_Tag)
                        x1_value = doc.createTextNode(str(bbox[1]))
                        x1_Tag.appendChild(x1_value)

                        y1_Tag = doc.createElement("y1")
                        axis.appendChild(y1_Tag)
                        y1_value = doc.createTextNode(str(bbox[2]))
                        y1_Tag.appendChild(y1_value)

                        x2_Tag = doc.createElement("x2")
                        axis.appendChild(x2_Tag)
                        x2_value = doc.createTextNode(str(bbox[3]))
                        x2_Tag.appendChild(x2_value)

                        y2_Tag = doc.createElement("y2")
                        axis.appendChild(y2_Tag)
                        y2_value = doc.createTextNode(str(bbox[4]))
                        y2_Tag.appendChild(y2_value)

                        x3_Tag = doc.createElement("x3")
                        axis.appendChild(x3_Tag)
                        x3_value = doc.createTextNode(str(bbox[5]))
                        x3_Tag.appendChild(x3_value)

                        y3_Tag = doc.createElement("y3")
                        axis.appendChild(y3_Tag)
                        y3_value = doc.createTextNode(str(bbox[6]))
                        y3_Tag.appendChild(y3_value)
                    
                if len(bbox) == 5 :
                    obj = doc.createElement("obj")
                    detect.appendChild(obj)
                    obj_type = doc.createElement("type")
                    obj.appendChild(obj_type)

                    if bbox[0] == 2 and i_man < self.cntMan:
                        print self.manMove1
                        print self.manMove2
                        print self.cntMan
                        type_str = "Man"
                        obj_type_value = doc.createTextNode(type_str)
                        obj_type.appendChild(obj_type_value)
                        
                        man_move1 = doc.createElement("manMove1")
                        obj.appendChild(man_move1)
                        man_move1_value = doc.createTextNode(str(self.manMove1[i_man]))
                        man_move1.appendChild(man_move1_value)

                        man_move2 = doc.createElement("manMove2")
                        obj.appendChild(man_move2)
                        man_move2_value = doc.createTextNode(str(self.manMove2[i_man]))
                        man_move2.appendChild(man_move2_value)

                        axis = doc.createElement("axis")
                        obj.appendChild(axis)
                        x1_Tag = doc.createElement("x1")
                        axis.appendChild(x1_Tag)
                        x1_value = doc.createTextNode(str(bbox[1]))
                        x1_Tag.appendChild(x1_value)

                        y1_Tag = doc.createElement("y1")
                        axis.appendChild(y1_Tag)
                        y1_value = doc.createTextNode(str(bbox[2]))
                        y1_Tag.appendChild(y1_value)

                        x2_Tag = doc.createElement("x2")
                        axis.appendChild(x2_Tag)
                        x2_value = doc.createTextNode(str(bbox[3]))
                        x2_Tag.appendChild(x2_value)

                        y2_Tag = doc.createElement("y2")
                        axis.appendChild(y2_Tag)
                        y2_value = doc.createTextNode(str(bbox[4]))
                        y2_Tag.appendChild(y2_value)
                        
                        i_man += 1
                    elif bbox[0] == 3 and i_man < self.cntBike:
                        type_str = "Bicycle"
                        obj_type_value = doc.createTextNode(type_str)
                        obj_type.appendChild(obj_type_value)
                        
                        bike_move1 = doc.createElement("bikeMove1")
                        obj.appendChild(bike_move1)
                        bike_move1_value = doc.createTextNode(str(self.bikeMove1[i_bike]))
                        bike_move1.appendChild(bike_move1_value)

                        bike_move2 = doc.createElement("bikeMove2")
                        obj.appendChild(bike_move2)
                        bike_move2_value = doc.createTextNode(str(self.bikeMove2[i_bike]))
                        bike_move2.appendChild(bike_move2_value)

                        axis = doc.createElement("axis")
                        obj.appendChild(axis)
                        x1_Tag = doc.createElement("x1")
                        axis.appendChild(x1_Tag)
                        x1_value = doc.createTextNode(str(bbox[1]))
                        x1_Tag.appendChild(x1_value)

                        y1_Tag = doc.createElement("y1")
                        axis.appendChild(y1_Tag)
                        y1_value = doc.createTextNode(str(bbox[2]))
                        y1_Tag.appendChild(y1_value)

                        x2_Tag = doc.createElement("x2")
                        axis.appendChild(x2_Tag)
                        x2_value = doc.createTextNode(str(bbox[3]))
                        x2_Tag.appendChild(x2_value)

                        y2_Tag = doc.createElement("y2")
                        axis.appendChild(y2_Tag)
                        y2_value = doc.createTextNode(str(bbox[4]))
                        y2_Tag.appendChild(y2_value)
                        
                        i_bike += 1
                    elif bbox[0] == 4:
                        type_str = "TrafficTag"
                        obj_type_value = doc.createTextNode(type_str)
                        obj_type.appendChild(obj_type_value)

                        axis = doc.createElement("axis")
                        obj.appendChild(axis)
                        x1_Tag = doc.createElement("x1")
                        axis.appendChild(x1_Tag)
                        x1_value = doc.createTextNode(str(bbox[1]))
                        x1_Tag.appendChild(x1_value)

                        y1_Tag = doc.createElement("y1")
                        axis.appendChild(y1_Tag)
                        y1_value = doc.createTextNode(str(bbox[2]))
                        y1_Tag.appendChild(y1_value)

                        x2_Tag = doc.createElement("x2")
                        axis.appendChild(x2_Tag)
                        x2_value = doc.createTextNode(str(bbox[3]))
                        x2_Tag.appendChild(x2_value)

                        y2_Tag = doc.createElement("y2")
                        axis.appendChild(y2_Tag)
                        y2_value = doc.createTextNode(str(bbox[4]))
                        y2_Tag.appendChild(y2_value)
                    elif bbox[0] == 5:
                        type_str = "Guideboard"
                        obj_type_value = doc.createTextNode(type_str)
                        obj_type.appendChild(obj_type_value)

                        axis = doc.createElement("axis")
                        obj.appendChild(axis)
                        x1_Tag = doc.createElement("x1")
                        axis.appendChild(x1_Tag)
                        x1_value = doc.createTextNode(str(bbox[1]))
                        x1_Tag.appendChild(x1_value)

                        y1_Tag = doc.createElement("y1")
                        axis.appendChild(y1_Tag)
                        y1_value = doc.createTextNode(str(bbox[2]))
                        y1_Tag.appendChild(y1_value)

                        x2_Tag = doc.createElement("x2")
                        axis.appendChild(x2_Tag)
                        x2_value = doc.createTextNode(str(bbox[3]))
                        x2_Tag.appendChild(x2_value)

                        y2_Tag = doc.createElement("y2")
                        axis.appendChild(y2_Tag)
                        y2_value = doc.createTextNode(str(bbox[4]))
                        y2_Tag.appendChild(y2_value)
                    elif bbox[0] == 6:
                        type_str = "SingalLight"
                        obj_type_value = doc.createTextNode(type_str)
                        obj_type.appendChild(obj_type_value)

                        color_type = doc.createElement("color")
                        obj.appendChild(color_type)
                        color_value = doc.createTextNode(str(self.color))
                        color_type.appendChild(color_value)
                        
                        axis = doc.createElement("axis")
                        obj.appendChild(axis)
                        x1_Tag = doc.createElement("x1")
                        axis.appendChild(x1_Tag)
                        x1_value = doc.createTextNode(str(bbox[1]))
                        x1_Tag.appendChild(x1_value)

                        y1_Tag = doc.createElement("y1")
                        axis.appendChild(y1_Tag)
                        y1_value = doc.createTextNode(str(bbox[2]))
                        y1_Tag.appendChild(y1_value)

                        x2_Tag = doc.createElement("x2")
                        axis.appendChild(x2_Tag)
                        x2_value = doc.createTextNode(str(bbox[3]))
                        x2_Tag.appendChild(x2_value)

                        y2_Tag = doc.createElement("y2")
                        axis.appendChild(y2_Tag)
                        y2_value = doc.createTextNode(str(bbox[4]))
                        y2_Tag.appendChild(y2_value)
        obj = doc.createElement("obj")
        detect.appendChild(obj)

        obj_type = doc.createElement("type")
        obj.appendChild(obj_type)
        obj_type_value = doc.createTextNode("ReachArea")
        obj_type.appendChild(obj_type_value)

        axis = doc.createElement("axis")
        obj.appendChild(axis)
        for i in range(len(self.points)):
            x_value, y_value = self.points[i]

            x_Tag = doc.createElement("x"+str(i+1))
            axis.appendChild(x_Tag)
            x_value = doc.createTextNode(str(x_value))
            x_Tag.appendChild(x_value)

            y_Tag = doc.createElement("y"+str(i+1))
            axis.appendChild(y_Tag)
            y_value = doc.createTextNode(str(y_value))
            y_Tag.appendChild(y_value)

        ff = open(self.xmlfilename, "w")
        ff.write(doc.toprettyxml(indent="  "))
        ff.close()
        print 'Image No. %d saved' % (self.cur)

    # 2017-3-8 herongwei add the third Points to DrawCar
    # 2017-3-10 herongwei modified
    # 2017-3-11 herongwei wirte into xml file
    # 2017-3-13 herongwei add one more param to recognize the type of obj
    def drawCar(self, event):
        
        if self.STATE['click'] == 0:
            self.dots = []
            self.STATE['x'], self.STATE['y'] = event.x, event.y
            self.dots.append((event.x, event.y))
        else:
            x1, x2 = min(self.STATE['x'], event.x), max(self.STATE['x'], event.x)
            y1, y2 = min(self.STATE['y'], event.y), max(self.STATE['y'], event.y)
            self.mouseMove_for_car(event)
            self.dots.append((event.x, event.y))
            if self.STATE['click'] == 2:
                x1, y1 = self.dots[0]
                x2, y2 = self.dots[1]
                x3, y3 = self.dots[2]

                self.drawLine(x1, y1, x2, y2, x3, y3) 
                
                tkMessageBox.showinfo("alert!", "please choose the left or right")
                self.bboxList.append((1, x1, y1, x2, y2, x3, y3))
<<<<<<< 71de2d43a9d86cb9b06a13510a0dc35c05d7e254
                print self.bboxList
=======
                self.boxcnt += 1
>>>>>>> second commit
                self.bboxIdList.append(self.bboxId)
                self.bboxId = None
                self.listbox.insert(END, '车(%d, %d)(%d, %d)(%d, %d)' % (x1, y1, x2, y2, x3, y3))
                self.listbox.itemconfig(len(self.bboxIdList) - 1, fg=COLORS[0])
                #self.cntCar += 1
                
        self.STATE['click'] = self.STATE['click'] + 1
        self.STATE['click'] = self.STATE['click'] % 3
        self.cntCar += 1
<<<<<<< 71de2d43a9d86cb9b06a13510a0dc35c05d7e254
        
=======


>>>>>>> second commit
        self.lbcnt.config(text="%d" % self.boxcnt)

    # 2017-3-8 herongwei add the function of drawing other lines
    def drawLine(self, x1, y1, x2, y2, x3, y3):
        line1 = None
        y_key = 360
        if x2 < x3:
            k1 = (y3 - y2) / (x3 - x2)
            x_key = x3 + (y_key - y3) / k1
            k2 = (y_key - y1) / (x_key - x2)
            yy = k2 * (x3 - x2) + y1
            # 2017-3-9 herongwei
            #line1 = self.mainPanel.create_line(x2, y2, x3, y3, x3, y3, x3, yy, x2, y1, x3, yy, width=5)
            line1 = self.mainPanel.create_polygon(x2, y2, x3, y3,x3, yy, x2, y1, width=2, outline=COLORS[0], fill="orange")
        if x2 > x3:
            k1 = (y3 - y2) / (x3 - x1)
            x_key = x3 + (y_key - y3) / k1
            k2 = (y_key - y1) / (x_key - x1)
            yy = k2 * (x3 - x1) + y1
            # 2017-3-9 herongwei
            line1 = self.mainPanel.create_polygon(x1, y2, x3, y3, x3, yy, x1, y1, width=2, outline=COLORS[0], fill="orange")

        self.lineIdList.append(line1)

<<<<<<< 71de2d43a9d86cb9b06a13510a0dc35c05d7e254
=======

>>>>>>> second commit
    # 2017-3-13 herongwei add the function of drawing GuarbBar
    def drawGuardBar(self, event):
        if self.STATE['click'] == 0:
            self.dots = []
            self.dots.append((event.x, event.y))
        else:
            self.dots.append((event.x, event.y))
            if self.STATE['click'] == 2:
                x1, y1 = self.dots[0]
                x2, y2 = self.dots[1]
                x3, y3 = self.dots[2]

                line = self.mainPanel.create_line(x1, y1, x2, y2, x2, y2, x3, y3, x1, y1, x3, y3, width=3)
               
                self.bboxList.append((7, x1, y1, x2, y2, x3, y3))
                self.bboxIdList.append(self.bboxId)
                self.bboxId = None
<<<<<<< 71de2d43a9d86cb9b06a13510a0dc35c05d7e254
=======
                self.boxcnt += 1
>>>>>>> second commit
                self.listbox.insert(END, '护栏(%d, %d)(%d, %d)(%d, %d)' % (x1, y1, x2, y2, x3, y3))
                self.listbox.itemconfig(len(self.bboxIdList) - 1, fg=COLORS[0])
        self.STATE['click'] = self.STATE['click'] + 1
        self.STATE['click'] = self.STATE['click'] % 3
        
        self.lbcnt.config(text="%d" % self.boxcnt)

    # 2017-3-13 herongwei add the function of drawReachArea
    def drawReachArea(self, event):
        self.points.append((event.x, event.y))
        tmp1 = self.count - 1
        tmpX, tmpY = self.points[tmp1]
        tmpXX, tmpYY = self.points[self.count]
        self.mainPanel.create_line(tmpX, tmpY, tmpXX, tmpYY, width=5)
        self.count += 1
        self.lbcnt.config(text="%d" % self.boxcnt)

    # 2017-3-9 herongwei add the function of drawMan
    # 2017-3-13 herongwei add one more param to recognize the type of obj
    def drawMan(self, event):
        if self.STATE['click'] == 0:
            self.STATE['x'], self.STATE['y'] = event.x, event.y
        else:
            x1, x2 = min(self.STATE['x'], event.x), max(self.STATE['x'], event.x)
            y1, y2 = min(self.STATE['y'], event.y), max(self.STATE['y'], event.y)
            self.mouseMove(event)
            
            tkMessageBox.showinfo("alert!", "please choose left or right")
            
            self.bboxList.append((2, x1, y1, x2, y2))
            self.bboxIdList.append(self.bboxId)
            self.bboxId = None
            self.listbox.insert(END, '行人(%d, %d) -> (%d, %d)' % (x1, y1, x2, y2))
            self.listbox.itemconfig(len(self.bboxIdList) - 1, fg=COLORS[5])
            
        self.STATE['click'] = 1 - self.STATE['click']
        self.cntMan += 1
        
        self.lbcnt.config(text="%d" % self.boxcnt)

    # 2017-3-10 herongwei add the fuction of drawBicycle
    # 2017-3-13 herongwei add one more param to recognize the type of obj
    def drawBicycle(self, event):
        if self.STATE['click'] == 0:
            self.STATE['x'], self.STATE['y'] = event.x, event.y
        else:
            x1, x2 = min(self.STATE['x'], event.x), max(self.STATE['x'], event.x)
            y1, y2 = min(self.STATE['y'], event.y), max(self.STATE['y'], event.y)
            self.mouseMove(event)
            
            tkMessageBox.showinfo("alert!", "please choose left or right")
            
            self.bboxList.append((3, x1, y1, x2, y2))
            self.bboxIdList.append(self.bboxId)
            self.bboxId = None
            self.listbox.insert(END, '自行/摩托车(%d, %d) -> (%d, %d)' % (x1, y1, x2, y2))
            self.listbox.itemconfig(len(self.bboxIdList) - 1, fg=COLORS[0])
            
        self.STATE['click'] = 1 - self.STATE['click']
        self.cntBike += 1
        
        self.lbcnt.config(text="%d" % self.boxcnt)

    # 2017-3-10 herongwei add the function of drawTrafficTag
    # 2017-3-13 herongwei add one more param to recognize the type of obj
    def drawTrafficTag(self, event):
        if self.STATE['click'] == 0:
            self.STATE['x'], self.STATE['y'] = event.x, event.y
        else:
            x1, x2 = min(self.STATE['x'], event.x), max(self.STATE['x'], event.x)
            y1, y2 = min(self.STATE['y'], event.y), max(self.STATE['y'], event.y)
            self.mouseMove(event)
            self.bboxList.append((4, x1, y1, x2, y2))
            self.bboxIdList.append(self.bboxId)
            self.bboxId = None
            self.listbox.insert(END, '交通标志(%d, %d) -> (%d, %d)' % (x1, y1, x2, y2))
            self.listbox.itemconfig(len(self.bboxIdList) - 1, fg=COLORS[5])
            
        self.STATE['click'] = 1 - self.STATE['click']
        
        self.lbcnt.config(text="%d" % self.boxcnt)

    # 2017-3-10 herongwei add the function of drawGuideboard
    # 2017-3-13 herongwei add one more param to recognize the type of obj
    def drawGuideboard(self, event):
        if self.STATE['click'] == 0:
            self.STATE['x'], self.STATE['y'] = event.x, event.y
        else:
            x1, x2 = min(self.STATE['x'], event.x), max(self.STATE['x'], event.x)
            y1, y2 = min(self.STATE['y'], event.y), max(self.STATE['y'], event.y)
            self.mouseMove(event)
            self.bboxList.append((5, x1, y1, x2, y2))
            self.bboxIdList.append(self.bboxId)
            self.bboxId = None
            self.listbox.insert(END, '路牌(%d, %d) -> (%d, %d)' % (x1, y1, x2, y2))
            self.listbox.itemconfig(len(self.bboxIdList) - 1, fg=COLORS[0])
            
        self.STATE['click'] = 1 - self.STATE['click']
        
        self.lbcnt.config(text="%d" % self.boxcnt)

    # 2017-3-10 herongwei add the function of drawSignalLight
    # 2017-3-13 herongwei add one more param to recognize the type of obj
    def drawSignalLight(self, event):
        if self.STATE['click'] == 0:
            self.STATE['x'], self.STATE['y'] = event.x, event.y
        else:
            x1, x2 = min(self.STATE['x'], event.x), max(self.STATE['x'], event.x)
            y1, y2 = min(self.STATE['y'], event.y), max(self.STATE['y'], event.y)
            self.mouseMove(event)
            
            self.drawCircleOfTrafficLight(x1, y1, x2, y2)
            
            tkMessageBox.showinfo("alert!", "please choose the color of TrafficLight")
            
            self.bboxList.append((6, x1, y1, x2, y2))
            self.bboxIdList.append(self.bboxId)
            self.bboxId = None
            self.listbox.insert(END, '信号灯(%d, %d) -> (%d, %d)' % (x1, y1, x2, y2))
            self.listbox.itemconfig(len(self.bboxIdList) - 1, fg=COLORS[0])
            
        self.STATE['click'] = 1 - self.STATE['click']
        
        self.lbcnt.config(text="%d" % self.boxcnt)
    
    # 2017-3-14 herongwei add the function of drawing Circle in the SignalLight
    def drawCircleOfTrafficLight(self, x1, y1, x2, y2):
        x_range = abs(x1-x2)
        y_range = abs(y1-y2)
        if x_range > y_range:
            d = (x_range / 3)
            self.mainPanel.create_oval(x1, y1, x1+d, y2, width=2)
            self.mainPanel.create_oval(x1+d, y1, x1+2*d, y2, width=2)
            self.mainPanel.create_oval(x1+2*d, y1, x2, y2, width=2)
        if x_range < y_range:
            d = (y_range / 3)
            self.mainPanel.create_oval(x1, y1, x2, y1+d, width=2)
            self.mainPanel.create_oval(x1, y1+d, x2, y1+2*d, width=2)
            self.mainPanel.create_oval(x1, y1+2*d, x2, y2, width=2)
    
    # 2017-3-9 herongwei add the function of enlarge or zoom image
    # 2017-3-13 herongwei need to be debugging
    def processWheel(self, event):
        d = event.delta
        if d < 0:
            amt= 0.9
        else:
            amt= 1.1
        print "ok"
        imagepath = self.imageList[self.cur - 1]
        self.img = Image.open(imagepath)
        self.tkimg = ImageTk.PhotoImage(self.img)
        tkimg_width = self.tkimg.width()*self.scale_value
        tkimg_height = self.tkimg.height()*self.scale_value
        # self.mainPanel.config(width = max(self.tkimg.width(), 400), height = max(self.tkimg.height(), 400))
        self.mainPanel.config(width=tkimg_width, height=tkimg_width)
        self.mainPanel.create_image(0, 0, image=self.tkimg, anchor=NW)
        #self.mainPanel.scale(ALL, 200, 200, amt, amt)      
        #self.loadImage()
        #print str(self.mainPanel.size)

    def mouseMove(self, event):
        self.disp.config(text='x: %d, y: %d' % (event.x, event.y))
        if self.tkimg:
            if self.hl:
                self.mainPanel.delete(self.hl)
            self.hl = self.mainPanel.create_line(0, event.y, self.tkimg.width(), event.y, width=2)
            if self.vl:
                self.mainPanel.delete(self.vl)
            self.vl = self.mainPanel.create_line(event.x, 0, event.x, self.tkimg.height(), width=2)
        if 1 == self.STATE['click']:
            if self.bboxId:
                self.mainPanel.delete(self.bboxId)
            self.bboxId = self.mainPanel.create_rectangle(self.STATE['x'], self.STATE['y'], \
                                                          event.x, event.y, \
                                                          width=2, \
                                                          outline=COLORS[0])
    
    def mouseMove_for_car(self, event):
        self.disp.config(text='x: %d, y: %d' % (event.x, event.y))
        if self.tkimg:
            if self.hl:
                self.mainPanel.delete(self.hl)
            self.hl = self.mainPanel.create_line(0, event.y, self.tkimg.width(), event.y, width=2)
            if self.vl:
                self.mainPanel.delete(self.vl)
            self.vl = self.mainPanel.create_line(event.x, 0, event.x, self.tkimg.height(), width=2)
        if 1 == self.STATE['click']:
            if self.bboxId:
                self.mainPanel.delete(self.bboxId)
            self.bboxId = self.mainPanel.create_rectangle(self.STATE['x'], self.STATE['y'], \
                                                          event.x, event.y, \
                                                          width=2, \
                                                          outline=COLORS[0], fill="orange")
    
    def cancelBBox(self, event):
        if 1 == self.STATE['click']:
            if self.bboxId:
                self.mainPanel.delete(self.bboxId)
                # self.mainPanel.delete(self.lineId)
                self.bboxId = None
                self.STATE['click'] = 0

    # 2017-3-9 herongwei add the function of deleting the other lines of car
    def delBBox(self):
        sel = self.listbox.curselection()
        if len(sel) != 1:
            return
        idx = int(sel[0])
        self.mainPanel.delete(self.bboxIdList[idx])
        # 2017-3-9 herongwei
        self.mainPanel.delete(self.lineIdList[idx])
        self.lineIdList.remove(self.lineIdList[idx])
        
        self.carMove1.pop(idx)
        self.carMove2.pop(idx)
        
        self.lineIdList.pop(idx)
        self.bboxIdList.pop(idx)
        self.bboxList.pop(idx)
        self.listbox.delete(idx)
        self.cntCar -= 1

    # 2017-3-9 herongwei add the function of deleting all other lines of car
    def clearBBox(self):
        for idx in range(len(self.bboxIdList)):
            self.mainPanel.delete(self.bboxIdList[idx])

        # 2017-3-9 herongwei
        for idx2 in range(len(self.lineIdList)):
            self.mainPanel.delete(self.lineIdList[idx2])

        self.listbox.delete(0, len(self.bboxList))
        self.bboxIdList = []
        self.bboxList = []
        self.cntCar = 0

    # 2017-3-14 herongwei add the function of selecting color of SignalLight
    def RedSelect(self):
        self.color = "red"
        tkMessageBox.showinfo("info", "Select Red")
        
    
    # 2017-3-14 herongwei add the function of selecting color of SignalLight
    def GreenSelect(self):
        self.color = "green"
        tkMessageBox.showinfo("info", "Select green")
        
    
    def YellowSelect(self):
        self.color = "yellow"
        tkMessageBox.showinfo("info", "Select yellow")
       
    # 2017-3-24 herongwei add selection of other attributes of objections
    def carStraight(self, event=None):
        self.carMove1.append("go_straight")
        tkMessageBox.showinfo("carDiversion", "car Go Straight and please choose the direction of car")
        
    def carLeft(self, event=None):
        self.carMove1.append("turn_left")
        tkMessageBox.showinfo("carDiversion", "car Turn Left and please choose the direction of car")
        
    
    def carRight(self, event=None):
        self.carMove1.append("turn_right")
        tkMessageBox.showinfo("carDiversion", "car Turn Right and please choose the direction of car")
        
    
    def carForward(self, event=None):
        self.carMove2.append("go_foward")
        tkMessageBox.showinfo("carDirection", "car Go Forward and please choose the state of car_Light")
        
    def carBackward(self, event=None):
        self.carMove2.append("go_backward")
        tkMessageBox.showinfo("carDirection", "car Go Backward and please choose the state of car_Light")

        
    def LIGHT_HIGHBEAM(self, event=None):
        self.carLight.append("LIGHT_HIGHBEAM")
        tkMessageBox.showinfo("car_Light_state", "LIGHT_HIGHBEAM and please choose another car")
    
    def LIGHT_LOWBEAM(self, event=None):
        self.carLight.append("LIGHT_LOWBEAM")
        tkMessageBox.showinfo("car_Light_state", "LIGHT_LOWBEAM and please choose another car")
    
    def BRAKELIGHT(self, event=None):
        self.carLight.append("BRAKELIGHT")
        tkMessageBox.showinfo("car_Light_state", "BRAKELIGHT and please choose another car")
    
    def manForward(self, event=None):
        self.manMove2.append("go_forward")
        tkMessageBox.showinfo("manDirection", "man Go Forward and please choose another man")
        
    def manBackward(self, event=None):
        self.manMove2.append("go_backward")
        tkMessageBox.showinfo("manDirection", "man Go Backward and please choose another man")
        
    def manStraight(self, event=None):
        self.manMove1.append("go_straight")
        tkMessageBox.showinfo("manDirection", "man Go Straight and please choose the direction of man")
    
    def manLeft(self, event=None):
        self.manMove1.append("turn_left")
        tkMessageBox.showinfo("manDirection", "man Turn Left and please choose the direction of man")
    
    def manRight(self, event=None):
        self.manMove1.append("turn_right")
        tkMessageBox.showinfo("manDirection", "man Turn Right and please choose the direction of man")
    
    def BicycleForward(self, event=None):
        self.bikeMove2.append("go_forward")
        tkMessageBox.showinfo("bikeDirection", "bike Go Straight and please choose another bike")
    
    def BicycleBackward(self, event=None):
        self.bikeMove2.append("go_backword")
        tkMessageBox.showinfo("bikeDirection", "bike Go Backward and please choose another bike")
        
    def BicycleStraight(self, event=None):
        self.bikeMove1.append("go_straight")
        tkMessageBox.showinfo("bikeDirection", "bike Go Straight and please choose direction of bike")
    
    def BicycleLeft(self, event=None):
        self.bikeMove1.append("turn_left")
        tkMessageBox.showinfo("bikeDirection", "bike Turn Left and please choose the direction of bike")
    
    def BicycleRight(self, event=None):
        self.bikeMove1.append("turn_right")
        tkMessageBox.showinfo("bikeDirection", "bike Turn Right and please choose the direction of bike")
    
    


	if self.cur > 1:
            self.cur -= 1
            self.loadImage()

    def nextImage(self, event=None):
        tkMessageBox.showinfo("info", "Make Sure you have labeled all the objects and their attributes!")
        self.saveImage()
        if self.cur < self.total:
            self.cur += 1
            self.loadImage()
            self.lbcnt.config(text="%d" % self.boxcnt)
        self.cntMan += 1

    def gotoImage(self):
        idx = int(self.idxEntry.get())
        if 1 <= idx and idx <= self.total:
            self.saveImage()
            self.cur = idx
            self.loadImage()
        


##    def setImage(self, imagepath = r'test2.png'):
##        self.img = Image.open(imagepath)
##        self.tkimg = ImageTk.PhotoImage(self.img)
##        self.mainPanel.config(width = self.tkimg.width())
##        self.mainPanel.config(height = self.tkimg.height())
##        self.mainPanel.create_image(0, 0, image = self.tkimg, anchor=NW)

if __name__ == '__main__':
    root = Tk()

    tool = LabelTool(root)
    root.resizable(width=True, height=True)

    root.mainloop()

