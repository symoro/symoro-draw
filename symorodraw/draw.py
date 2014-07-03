5#!/usr/bin/env python
# -*- coding: utf-8

import wx
import wx.lib.agw.floatspin as FS
from wx.glcanvas import GLCanvas
from wx.glcanvas import GLContext

from pysymoro import robot
from symorodraw import objects

import canvas
import graphics
import data
from numpy import *
from numpy.linalg import inv, norm

import OpenGL.GL as gl
import OpenGL.GLU as glu
import OpenGL.GLUT as glut


class MainFrame(wx.Frame):
        '''Create Main Window of the program'''
        def __init__(self, *args, **kwargs):
                wx.Frame.__init__(self, *args, **kwargs)
                self.data = data.data()
                self.buttons = {}
                self.sizers = {}
                self.static_sizers = {}    
                self.canvas = {}
                self.panels = {}
                self.grids = {}
                self.check_boxes = {}
                self.texts = {}
                self.spins = {}
                
                self.menu_bars = {}
                self.menus = {}
                self.menu_items = {}
                
                self.mouse = wx.MouseEvent()
                
                self.create_menu()
                self.create_ui()

                self.Show()
                i = [key for key in self.data.GetList() if self.data.CheckKey(key, 'active')]
                for widget in i:
                        key = self.data.GetWidget(widget)
                        if not key['active']:
                                if self.data.GetValue(key['parent'],'w_type')=='sizer':
                                        self.sizers[key['parent']].Hide(key['position'])
                                elif self.data.GetValue(key['parent'],'w_type')=='static_sizer':
                                        self.static_sizers[key['parent']].Hide(key['position'])

                
        def create_menu(self):
                for key in self.data.GetTypedList('w_type','menu_bar'):
                        self.CreateMenuElements('MENU_BAR')      
                        self.AppendMenuElements('MENU_BAR')
                self.SetMenus()
                
        def CreateMenuElements(self, key):
                print key
                if self.data.GetValue(key,'w_type')=='menu_bar':
                        self.menu_bars[key] = wx.MenuBar()
                elif self.data.GetValue(key,'w_type')=='menu':
                        self.menus[key] = wx.Menu()
                elif self.data.GetValue(key,'w_type')=='menu_item':
                        menu_item = self.data.GetWidget(key)
                        if self.data.CheckKey(key,'id'):
                                menu_id = menu_item['id']
                        else:
                                menu_id = wx.ID_ANY
                                
                        self.menu_items[key]= wx.MenuItem(self.menus[menu_item['parent']], id=menu_id,  text=menu_item['label'])
                        if self.data.CheckKey(key,'callback'):
                                self.Bind(wx.EVT_MENU,  getattr(self, menu_item['callback']), self.menu_items[key])
                        else:
                                self.Bind(wx.EVT_MENU,  None, self.menu_items[key])
                        

                my_list = self.data.GetTypedList('parent',key)
                for name in my_list:    
                        self.CreateMenuElements(name)

        def AppendMenuElements(self, key):
                print key
                my_list = self.data.SortPosition(key)
                for name in my_list:
                        self.AppendMenuElements(name)
                        if self.data.GetValue(name,'w_type')=='menu':
                                menu = self.data.GetWidget(name)
                                if self.data.CheckKey(name,'w_type'):
                                        if menu['submenu']:
                                                self.menus[key].AppendSubMenu(self.menus[name], text=menu['label'])
                                        else:
                                                self.menu_bars[key].Append(self.menus[name], title=menu['label'])
                                        
                        elif self.data.GetValue(name,'w_type')=='menu_item':
                                menu_item = self.data.GetWidget(name)                              
                                self.menus[key].AppendItem(self.menu_items[name])

                        elif self.data.GetValue(name,'w_type') == 'menu_separator':
                                self.menus[key].AppendSeparator()

        def SetMenus(self):
                my_list = self.data.GetTypedList('w_type','menu_bar')
                for name in my_list:
                        self.SetMenuBar(self.menu_bars[name])
	
        def create_ui(self):
                self.CreateElements('MAIN')
                self.FillSizers('MAIN')
                self.SetSizerAndFit(self.sizers['MAIN'])

        def CreateElements(self, key):
                print key
                my_type = self.data.GetValue(key,'w_type')
                if my_type == 'static_text':
                        self.CreateText(key)
                elif my_type == 'canvas':
                        self.CreateCanvas(key)
                elif my_type == 'panel':
                        self.CreatePanel(key)
                elif my_type == 'sizer':
                        self.CreateSizer(key)
                elif my_type == 'button':
                        self.CreateButton(key)
                elif my_type == 'grid':
                        self.CreateGrid(key)
                elif my_type == 'static_sizer':
                        self.CreateStaticSizer(key)
                elif my_type == 'check_box':
                        self.CreateCheckBox(key)
                elif my_type == 'float_spin':
                        self.CreateFloatSpin(key)


                my_list = self.data.GetTypedList('parent',key)
                for name in my_list:    
                        self.CreateElements(name)

        def FillSizers(self, key):
                print key
                if not self.data.GetValue(key, 'w_type') == 'grid':
                        my_list = self.data.SortPosition(key)
                else:
                        my_list = self.data.GetTypedList('parent',key)
                        
                for name in my_list:
                        self.FillSizers(name)
                        
                        if self.data.GetValue(name,'w_type') == 'button':
                                self.FillButton(name)        
                                
                        if self.data.GetValue(name,'w_type') == 'static_sizer':
                                self.FillStaticSizer(name)
                                
                        if self.data.GetValue(name,'w_type') == 'sizer':
                                self.FillSizer(name)
                                
                        if self.data.GetValue(name,'w_type') == 'canvas':
                                self.FillCanvas(name)
                                
                        if self.data.GetValue(name,'w_type') == 'panel':
                                self.FillPanel(name)
                                
                        if self.data.GetValue(name,'w_type') == 'grid':
                                self.FillGrid(name)
                                
                        if self.data.GetValue(name,'w_type') == 'static_text':
                                self.FillStaticText(name)
                                
                        if self.data.GetValue(name,'w_type') == 'check_box':
                                self.FillCheckBox(name)
                                
                        if self.data.GetValue(name,'w_type') == 'float_spin':
                                self.FillFloatSpin(name)

        def CreateText(self, key):
                text = self.data.GetWidget(key)
                if not self.data.CheckKey(key, 'size'):
                        text['size']=(70, -1)
                self.texts[key] = wx.StaticText(parent=self.panels[text['panel']], size=text['size'], label=text['label'])
                        
        def CreateCanvas(self, key):
                self.canvas[key] = canvas.myGLCanvas(self)

        def CreatePanel(self, key):
                self.panels[key] = wx.Panel(self)
               
        def CreateGrid(self, key):
                grid = self.data.GetWidget(key)
                self.grids[key]=  wx.GridBagSizer(hgap=grid['horizontal'], vgap=grid['vertical'])

        def CreateButton(self, key):
                button = self.data.GetWidget(key)
                self.buttons[key] = wx.Button(parent=self.panels[button['panel']], label=button['label'])
                self.buttons[key].Bind(wx.EVT_BUTTON, getattr(self, button['callback']) )

        def CreateCheckBox(self, key):
                check_box = self.data.GetWidget(key)
                self.check_boxes[key] = wx.CheckBox(parent=self.panels[check_box['panel']], label=check_box['label'])
                self.check_boxes[key].Bind(wx.EVT_CHECKBOX,getattr(self, check_box['callback']))

        def CreateSizer(self, key):
                sizer = self.data.GetWidget(key)
                if not self.data.CheckKey(key, 'orientation'):
                        sizer['orientation'] = wx.HORIZONTAL
                        
                self.sizers[key] = wx.BoxSizer(sizer['orientation'])

        def CreateStaticSizer(self, key):
                sizer = self.data.GetWidget(key)
                if not self.data.CheckKey(key, 'id'):
                        sizer['id'] = wx.ID_ANY
                if not self.data.CheckKey(key, 'orientation'):
                        sizer['orientation'] = wx.HORIZONTAL
                if self.data.CheckKey(key, 'label'):
                        
                        self.static_sizers[key] = wx.StaticBoxSizer(wx.StaticBox(parent=self.panels[sizer['panel']], id=sizer['id'], label=self.data.GetValue(key,'label')
                                                                ), orient=sizer['orientation'])
                else:
                        self.static_sizers[key] = wx.StaticBoxSizer(wx.StaticBox(parent=self.panels[sizer['panel']], id=sizer['id'],), orient=sizer['orientation'])

        def CreateFloatSpin(self, key):
                spin = self.data.GetWidget(key)
                if not self.data.CheckKey(key, 'size'):
                        sizer['size'] = (70,-1)
                if not self.data.CheckKey(key, 'increment'):
                        sizer['increment'] = 0.5
                if not self.data.CheckKey(key, 'min_val'):
                        sizer['size'] = None
                if not self.data.CheckKey(key, 'max_val'):
                        sizer['increment'] = None
                        
                self.spins[key]=(FS.FloatSpin(self.panels[spin['panel']], size=spin['size'],
                             increment=spin['increment'], min_val=spin['min_val'], max_val=spin['max_val']))
                self.spins[key].Bind(FS.EVT_FLOATSPIN,  getattr(self, spin['callback']) )
                self.spins[key].SetDigits(2)
                        

        def FillButton(self, key):
                button = self.data.GetWidget(key)
                if self.data.GetValue(button['parent'],'w_type') =='grid':
                        self.grids[button['parent']].Add(self.buttons[key], pos=( button['vertical'],button['horizontal']))
                else:
                        if not self.data.CheckKey(key,'proportion'):
                                button['proportion'] = 0
                        if not self.data.CheckKey(key,'border'):
                                button['border'] = 1
                        if not self.data.CheckKey(key,'flag'):
                                button['flag'] = wx.EXPAND
                        if self.data.GetValue(button['parent'],'w_type') == 'static_sizer':
                                self.static_sizers[button['parent']].Add(self.buttons[key], proportion=button['proportion'], flag=button['flag'], border=button['border'])
                        elif self.data.GetValue(button['parent'],'w_type') == 'sizer':
                                self.sizers[button['parent']].Add(self.buttons[key], proportion=button['proportion'], flag=button['flag'], border=button['border'])        

                        

        def FillCheckBox(self, key):
                check_box = self.data.GetWidget(key)
                if self.data.GetValue(check_box['parent'],'w_type') =='grid':
                        self.grids[check_box['parent']].Add(self.check_boxes[key], pos=( check_box['vertical'],check_box['horizontal']))
                else:
                        if not self.data.CheckKey(key,'proportion'):
                                check_box['proportion'] = 0
                        if not self.data.CheckKey(key,'border'):
                                check_box['border'] = 1
                        if not self.data.CheckKey(key,'flag'):
                                check_box['flag'] = wx.EXPAND
                        if self.data.GetValue(check_box['parent'],'w_type') == 'static_sizer':
                                self.static_sizers[check_box['parent']].Add(self.check_boxes[key], proportion=check_box['proportion'], flag=check_box['flag'], border=check_box['border'])
                        elif self.data.GetValue(check_box['parent'],'w_type') == 'sizer':
                                self.sizers[check_box['parent']].Add(self.check_boxes[key], proportion=check_box['proportion'], flag=check_box['flag'], border=check_box['border'])

                        

        def FillStaticSizer(self, key):
                sizer = self.data.GetWidget(key)
                if self.data.GetValue(sizer['parent'],'w_type') =='panel':
                        self.panels[sizer['parent']].SetSizerAndFit(self.static_sizers[key])
                elif self.data.GetValue(sizer['parent'],'w_type') =='grid':
                        self.grids[sizer['parent']].Add(self.static_sizers[key], pos=( sizer['vertical'],sizer['horizontal']))
                elif self.data.GetValue(sizer['parent'],'w_type') =='sizer':
                        if not self.data.CheckKey(key,'proportion'):
                                sizer['proportion'] = 0
                        if not self.data.CheckKey(key,'border'):
                                sizer['border'] = 0
                        if not self.data.CheckKey(key,'flag'):
                                sizer['flag'] = wx.EXPAND
                        self.sizers[sizer['parent']].Add(self.static_sizers[key], proportion=sizer['proportion'], flag=sizer['flag'], border=sizer['border'])

        def FillSizer(self, key):
                sizer = self.data.GetWidget(key)
                if self.data.GetValue(sizer['parent'],'w_type') =='panel':
                        self.panels[sizer['parent']].SetSizerAndFit(self.sizers[key])
                elif self.data.GetValue(sizer['parent'],'w_type') =='grid':
                        self.grids[sizer['parent']].Add(self.sizers[key], pos=( sizer['vertical'],sizer['horizontal']))
                        
        def FillCanvas(self, key):
                canvas = self.data.GetWidget(key)
                if not self.data.CheckKey(key,'proportion'):
                        canvas['proportion'] = 0
                if not self.data.CheckKey(key,'border'):
                        canvas['border'] = 8
                if not self.data.CheckKey(key,'flag'):
                        canvas['flag'] =  wx.EXPAND| wx.ALL

                self.sizers[canvas['parent']].Add(self.canvas[key], proportion=canvas['proportion'], flag=canvas['flag'], border=canvas['border'])

        def FillPanel(self, key):
                panel = self.data.GetWidget(key)
                if not self.data.CheckKey(key,'proportion'):
                        panel['proportion'] = 0
                if not self.data.CheckKey(key,'border'):
                        panel['border'] = 1
                if not self.data.CheckKey(key,'flag'):
                        panel['flag'] =  wx.EXPAND
                 
                self.sizers[panel['parent']].Add(self.panels[key], proportion=panel['proportion'], flag=panel['flag'], border=panel['border'])
                 
        def FillGrid(self, key):
                grid = self.data.GetWidget(key)
                if not self.data.CheckKey(key,'proportion'):
                        grid['proportion'] = 0
                if not self.data.CheckKey(key,'border'):
                        grid['border'] = 0
                if not self.data.CheckKey(key,'flag'):
                        grid['flag'] =  wx.ALL
                if self.data.GetValue(grid['parent'],'w_type')=='sizer':
                        self.sizers[grid['parent']].Add(self.grids[key], proportion=grid['proportion'], flag=grid['flag'], border=grid['border'])
                elif self.data.GetValue(grid['parent'],'w_type')=='static_sizer':
                        self.static_sizers[grid['parent']].Add(self.grids[key], proportion=grid['proportion'], flag=grid['flag'], border=grid['border'])

        def FillStaticText(self, key):
                text = self.data.GetWidget(key)
                if self.data.GetValue(text['parent'],'w_type')=='grid':
                        self.grids[text['parent']].Add(self.texts[key],(self.data.GetValue(key,'horizontal'),self.data.GetValue(key,'vertical')))
                else:
                        if not self.data.CheckKey(key,'proportion'):
                                text['proportion'] = 0
                        if not self.data.CheckKey(key,'border'):
                                text['border'] = 0
                        if not self.data.CheckKey(key,'flag'):
                                text['flag'] =  wx.ALIGN_LEFT
                        if self.data.GetValue(text['parent'],'w_type')=='sizer':
                                self.sizers[text['parent']].Add(self.text[key], proportion=text['proportion'], flag=text['flag'], border=text['border'])
                        elif self.data.GetValue(text['parent'],'w_type')=='static_sizer':
                                self.static_sizers[text['parent']].Add(self.text[key], proportion=text['proportion'], flag=text['flag'], border=text['border'])

        def FillFloatSpin(self, key):
                spin = self.data.GetWidget(key)
                if self.data.GetValue(spin['parent'],'w_type')=='grid':
                        self.grids[spin['parent']].Add(self.spins[key],(self.data.GetValue(key,'horizontal'),self.data.GetValue(key,'vertical')))
                else:
                        if not self.data.CheckKey(key,'proportion'):
                                spin['proportion'] = 0
                        if not self.data.CheckKey(key,'border'):
                                spin['border'] = 0
                        if not self.data.CheckKey(key,'flag'):
                                spin['flag'] =  wx.ALIGN_LEFT
                        if self.data.GetValue(spin['parent'],'w_type')=='sizer':
                                self.sizers[spin['parent']].Add(self.spins[key], proportion=spin['proportion'], flag=spin['flag'], border=spin['border'])
                        elif self.data.GetValue(spin['parent'],'w_type')=='static_sizer':
                                self.static_sizers[spin['parent']].Add(self.spins[key], proportion=spin['proportion'], flag=spin['flag'], border=spin['border'])

        def OnPlane1(self, event):
                self.Init('PLANE1')
        
        def OnPlane2(self, event):
                self.Init('PLANE2')
        
        def OnPlane3(self, event):
                self.Init('PLANE3')
		
        def OnNew(self, event):
                pass
		
        def OnExport(self, event):
                self.Export()
                

        def Export(self):
                export = wx.TextEntryDialog(None, 'Give the name of the robot',  style=wx.SYSTEM_MENU|wx.OK|wx.CANCEL)
                if export.ShowModal()==wx.ID_OK:
                        name = export.GetValue()
                        if name:
                                self.canvas['CANVAS'].Export(export.GetValue())
                        else:
                                msg = wx.MessageDialog (None, 'Cannot export, please give the name of the robot.', style=wx.OK|wx.CENTRE)
                                if msg.ShowModal()==wx.ID_OK:
                                        self.Export()
                
		
        def OnClose(self, event):
                pass
        
        def OnShowDraw(self, event):
                pass
        
        def OnShowView(self, event):
                pass
        
        def OnRefPoint(self, event):
                self.Init('REF_POINT')
                self.data.FlagReset('PICK')

        def OnRefLine(self, event):
                self.Init('REF_POINT')
                self.data.FlagReset('PICK')

        def OnTop(self, event):
                self.SetCamera([0,1,0],[0,0,-1])

        def OnFront(self, event):
                self.SetCamera([0,0,1],[0,1,0])
                
        def OnRight(self, event):
                self.SetCamera([1,0,0],[0,1,0])

        def OnBottom(self, event):
                self.SetCamera([0,-1,0],[0,0,1])

        def OnBack(self, event):
                self.SetCamera([0,0,-1],[0,1,0])

        def OnLeft(self, event):
                self.SetCamera([-1,0,0],[0,1,0])
        
        def OnIsometric(self, event):
                self.canvas['CANVAS'].ChangeCameraParameters(hor_angle=pi/4, ver_angle=pi/4)         

        def SetCamera(self, up, eye):
                self.canvas['CANVAS'].up = up
                self.canvas['CANVAS'].cam = add(multiply(eye,norm(self.canvas['CANVAS'].u)),self.canvas['CANVAS'].cen)
                self.canvas['CANVAS'].CameraTransformation()
               
        def OnPan(self, event):
                pass

        def OnZoom(self, event):
                pass
        
        def OnRotate(self, event):
                pass

        def OnRevolute(self, event):
                self.Init('REVOLUTE')
                self.data.FlagReset('PICK')
                
        def OnPrismatic(self, event):
                self.Init('PRISMATIC')
                self.data.FlagReset('PICK')
                
        def OnFixed(self, event):
                self.Init('FIXED')
                self.data.FlagReset('PICK')

        def OnDelete(self, event):
                self.Init('DELETE')

        def OnAddAncestor(self, event):
                self.Init('ADD_ANC')

        def OnRemoveAncestor(self, event):
                self.Init('REM_ANC')

        def OnDefineD_H(self,event):
                self.canvas['CANVAS'].structure, self.canvas['CANVAS'].branches = self.canvas['CANVAS'].DefineStructure()
                if self.canvas['CANVAS'].structure and self.canvas['CANVAS'].branches:
                        joint = self.canvas['CANVAS'].structure[4][0]
                        if joint:
                                base = self.canvas['CANVAS'].elements[joint-1]
                        else:
                                base = self.canvas['CANVAS'].globFrame
                        base.gamma = 0
                        base.alpha = 0
                        base.theta = 0
                        base.d = 0
                        base.r = 0
                        base.b = 0
                        self.canvas['CANVAS'].GetParameters(self.canvas['CANVAS'].branches[self.canvas['CANVAS'].structure[0]][1:],
                                                            transpose(self.canvas['CANVAS'].elements[self.canvas['CANVAS'].structure[4][0]-1].T),
                                                            self.canvas['CANVAS'].structure[4][0])
                        self.canvas['CANVAS'].SetParameters()
                        self.data.FlagSet('MODE',1)

        def OnStructure(self,event):
                self.data.FlagReset('MODE')

        def OnAlpha(self, event):
                self.canvas['CANVAS'].elements[self.data.FlagGet('ACTIVE_JOINT')-1].alpha = event.EventObject.GetValue()
                self.canvas['CANVAS'].OnDraw()
                self.canvas['CANVAS'].Redraw()

        def OnTheta(self, event):
                self.canvas['CANVAS'].elements[self.data.FlagGet('ACTIVE_JOINT')-1].theta = event.EventObject.GetValue()
                self.canvas['CANVAS'].OnDraw()
                self.canvas['CANVAS'].Redraw()

        def OnGamma(self, event):
                self.canvas['CANVAS'].elements[self.data.FlagGet('ACTIVE_JOINT')-1].gamma = event.EventObject.GetValue()
                self.canvas['CANVAS'].OnDraw()
                self.canvas['CANVAS'].Redraw()

        def OnD(self, event):
                self.canvas['CANVAS'].elements[self.data.FlagGet('ACTIVE_JOINT')-1].d = event.EventObject.GetValue()
                self.canvas['CANVAS'].OnDraw()
                self.canvas['CANVAS'].Redraw()

        def OnB(self, event):
                self.canvas['CANVAS'].elements[self.data.FlagGet('ACTIVE_JOINT')-1].b = event.EventObject.GetValue()
                self.canvas['CANVAS'].OnDraw()
                self.canvas['CANVAS'].Redraw()

        def OnR(self, event):
                self.canvas['CANVAS'].elements[self.data.FlagGet('ACTIVE_JOINT')-1].r = event.EventObject.GetValue()
                self.canvas['CANVAS'].OnDraw()
                self.canvas['CANVAS'].Redraw()

        def OnParallel(self, event):
                self.Init('PARALLEL')

        def OnPerpendicular(self, event):
                 self.Init('PERPENDICULAR')

        def OnAtDistance(self, event):
                self.Init('AT_DISTANCE')

        def OnAtAngle(self,event):
                self.Init('AT_ANGLE')

        def OnCut(self, event):
                self.canvas['CANVAS'].elements[self.data.FlagGet('ACTIVE_JOINT')-1].cut_joint = event.EventObject.GetValue()

        def OnActive(self, event):
                self.canvas['CANVAS'].elements[self.data.FlagGet('ACTIVE_JOINT')-1].active = event.EventObject.GetValue()
                

        def OnChangeZAxis(self, event):
                self.canvas['CANVAS'].elements[self.data.FlagGet('ACTIVE_JOINT')-1].T[0:3,0:3] = self.canvas['CANVAS'].EulerTransformation(pi,[1,0,0]).dot(self.canvas['CANVAS'].elements[
                        self.data.FlagGet('ACTIVE_JOINT')-1].T[0:3,0:3])

        def Init(self, f_id):
                if not self.data.FlagGet(f_id):
                        self.data.FlagsChange('joint')
                        self.data.FlagsChange('ref')
                        self.data.FlagsChange('plane')
                        self.data.FlagsChange('button')
                        self.data.FlagsChange('constraints')
                        self.data.FlagIncrement(f_id)

        def ActiveJoint(self,joint_id):
                if not joint_id == -2:
                        joint = self.canvas['CANVAS'].elements[joint_id-1]
                else:
                        print 'id'
                        joint = self.canvas['CANVAS'].globFrame
                for key in self.data.GetTypedList('parent','PANEL_JOINT_SIZER'):
                        if not key=='ON_ANCESTORS':
                                self.sizers['PANEL_JOINT_SIZER'].Show(self.data.GetValue(key,'position'))
                self.check_boxes['ON_ACTIVE'].SetValue(joint.active)
                self.check_boxes['ON_CUT_JOINT'].SetValue(joint.cut_joint)
                self.data.FlagSet('ACTIVE_JOINT',joint_id)
                self.spins['ON_R'].SetValue(joint.r)
                self.spins['ON_THETA'].SetValue(joint.theta)
                self.spins['ON_D'].SetValue(joint.d)
                self.spins['ON_ALPHA'].SetValue(joint.alpha)
                self.spins['ON_B'].SetValue(joint.b)
                self.spins['ON_GAMMA'].SetValue(joint.gamma)

        def ActiveLink(self, link_id):
                self.sizers['PANEL_JOINT_SIZER'].Show(self.data.GetValue('ON_ANCESTORS','position'))
                self.data.FlagSet('ACTIVE_LINK',link_id)

        def Deactive(self):
                for key in self.data.GetTypedList('parent','PANEL_JOINT_SIZER'):
                        self.sizers['PANEL_JOINT_SIZER'].Hide(self.data.GetValue(key,'position'))
                self.data.FlagReset('ACTIVE_JOINT')
                self.data.FlagReset('ACTIVE_LINK')

if __name__ == '__main__':
        app = wx.App(redirect = False)
        style = wx.DEFAULT_FRAME_STYLE^wx.MAXIMIZE_BOX^wx.RESIZE_BORDER
        frame = MainFrame(
                parent = None,
                id = wx.ID_ANY,
                title = 'Draw_me',
                size = (-1, -1),
                style = style
        )
        app.MainLoop()
        app.Destroy()
