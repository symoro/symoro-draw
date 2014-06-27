#!/usr/bin/env python
# -*- coding: utf-8 -*-


from math import atan2

import wx
import wx.lib.agw.floatspin as FS
from wx.glcanvas import GLCanvas
from wx.glcanvas import GLContext

import OpenGL.GL as gl
import OpenGL.GLU as glu

from numpy import *
from numpy.linalg import norm, inv 
from sympy import Expr
import draw

from pysymoro.invgeom import loop_solve
from pysymoro.geometry import dgm
from symoroutils import samplerobots
from symoroutils import symbolmgr
from symoroutils import tools
import itertools

from objects import Frame, SuperRevoluteJoint, FixedJoint, SuperPrismaticJoint, JointObject, Point, Line


class myGLCanvas(GLCanvas):
    def __init__(self, parent, size=(700, 700)):
        super(myGLCanvas, self).__init__(parent, size=size)
        self.context = GLContext(self)
        self.Bind(wx.EVT_PAINT, self.OnPaintAll)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnMouseDown)
        self.Bind(wx.EVT_LEFT_UP, self.OnMouseUp)
        self.Bind(wx.EVT_RIGHT_DOWN, self.OnMouseDown)
        self.Bind(wx.EVT_RIGHT_UP, self.OnMouseUp)
        self.Bind(wx.EVT_MOTION, self.OnMouseMotion)
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
        self.size = self.GetClientSize()
        self.mode = 'RENDER'

        #Camera General Data
        self.init = 0
        self.fov = 40
        self.aspect = 1

        #Camera Actual Configuration Data
        self.cen = [0,0,0]
        self.up = [0, 0, 1]
        self.cam = [0,-10,0]
        self.u = [0,0,10]
        self.buffer_size = 32

        #window data
        self.length = 5
        self.parent = parent

        #elements
        self.elements = []
        self.bufer = []
        self.plane = []
        self.planes = []
        self.structure = []


    def assign_mono_scale(self):
        """Sets the coefficients used to draw objects

        This function calculates coefficients which are used
        to draw the objects (Joints, links, end-effectors)
        It computes the minimum and maximum r or d different from 0.
        Then uses those sizes to determine the reference
        numbers which are used all over the class.
        """
        minv = inf
        for jnt in self.jnt_objs[1:]:
            dist = max(abs(jnt.r), abs(jnt.d))
            if dist < minv and dist != 0:
                minv = dist
        if minv == inf:
            minv = 1.
        self.length = 0.4 * minv
        #print self.length
        for jnt in self.jnt_objs:
            if isinstance(jnt, PrismaticJoint):
                jnt.r = 3.5 * self.length
            jnt.set_length(self.length)

    def OnEraseBackground(self, event):
        # Do nothing, to avoid flashing on MSW.
        # This is needed
        pass
    
    def OnSize(self, event):
        size = self.size = self.GetClientSize()
        if self.GetContext():
            self.SetCurrent(self.context)
            gl.glViewport(0, 0, size.width, size.height)
        event.Skip()

    ## Mouse handling
    def OnMouseDown(self, evt):
        self.CaptureMouse()
        self.lastx, self.lasty = evt.GetPosition()
        
        if not self.parent.data.FlagGet('CHANGE_ANC'):
            self.DeactivateJoint()
        
        for key in self.parent.data.FlagList('joint'):
            if self.parent.data.FlagGet(key) == 1:
                self.parent.data.FlagIncrement(key)
                self.origin = self.lastx, self.lasty
                
            elif self.parent.data.FlagGet(key) == 2:
               self.CreateJoint(key)

        if self.parent.data.FlagGet('PICK'):
            print 'pick'
            my_buffer = self.Pick()
            self.DefinePlane(my_buffer)
            if self.parent.data.FlagGet('DELETE'):
                self.OnDelete(my_buffer)
            elif self.parent.data.FlagGet('CHANGE_ANC'):
                self.ChangeAncestor(my_buffer)
            else:
                self.ActivateJoint(my_buffer)
                
                    

        if self.parent.data.FlagGet('REF_POINT'):
                self.DrawElements(my_type='POINT', pos = self.GetCoordinates(self.lastx, self.lasty))
                self.OnDraw()
                self.Redraw()
                self.parent.data.FlagReset('REF_POINT')
                self.parent.data.FlagIncrement('PICK')

    def ActivateJoint(self, my_buffer):
        for min_d, max_d, name in my_buffer:
            if len(name)==1:
                self.DeactivateJoint()
                self.parent.ActiveJoint(self.elements[name[0]-1].active,self.elements[name[0]-1].cut_joint,name[0])
                self.elements[name[0]-1].color_j=[1,0,0]
                self.elements[name[0]-1].color_l=[1,0,0]
            break            

    def DeactivateJoint(self):
        if self.parent.data.FlagGet('ACTIVE_JOINT'):
            if isinstance(self.elements[self.parent.data.FlagGet('ACTIVE_JOINT')-1],SuperRevoluteJoint):
                self.elements[self.parent.data.FlagGet('ACTIVE_JOINT')-1].color_j=[1,1,0]
            else:
                self.elements[self.parent.data.FlagGet('ACTIVE_JOINT')-1].color_j=[1,0.6,0]
            self.elements[self.parent.data.FlagGet('ACTIVE_JOINT')-1].color_l=[1,1,1]
            self.elements[self.parent.data.FlagGet('ACTIVE_JOINT')-1].active=self.parent.check_boxes['ON_ACTIVE'].GetValue()
            self.elements[self.parent.data.FlagGet('ACTIVE_JOINT')-1].cut_joint=self.parent.check_boxes['ON_CUT_JOINT'].GetValue()
            self.parent.DeactiveJoint()

    def ChangeAncestor(self, my_buffer):
        for a, b, name in my_buffer:
            if not isinstance(self.elements[name[0]-1],Point):
                if not name[0]:
                    self.elements[self.parent.data.FlagGet('ACTIVE_JOINT')-1].anc_pos = [0,0,0]
                else:
                    self.elements[self.parent.data.FlagGet('ACTIVE_JOINT')-1].anc_pos = self.elements[name[0]-1].T[3,0:3]
                for remove in self.structure:
                    remove[1] = [i for i in remove[1] if not i==self.parent.data.FlagGet('ACTIVE_JOINT')]
                        
                self.structure[name[0]][1].append(self.parent.data.FlagGet('ACTIVE_JOINT'))
                self.parent.data.FlagReset('CHANGE_ANC')
                break

    def OnDelete(self, my_buffer):
        for a, b, name in my_buffer:
            if not name[0]==0:
                for i in range(len(self.structure)):
                    if self.structure[i][0]==name[0]:
                        self.structure[i-1][1] += self.structure[i][1]
                        for j in self.structure[i][1]:
                            self.elements[j-1].anc_pos = self.elements[self.structure[i][0]-1].T[3,0:3]
                                
                self.structure = [i for i in self.structure if not i[0]==name[0]]
                for element in self.structure:
                    element[1] = [i for i in element[1] if not i==name[0]]
                    element[1] = [i-1 if i>name[0] else i for i in element[1]]
                self.structure = [[i[0]-1,i[1]] if i[0]>name[0] else i for i in self.structure]
                        
                for element in self.elements[name[0]-1:]:
                    element.my_id -= 1
                del self.elements[name[0]-1]
                self.my_id -= 1
                self.parent.data.FlagReset('DELETE')
                break
                
        
                
                
    def DefinePlane(self, my_buffer):
        for key in self.parent.data.FlagList('plane'):
            if self.parent.data.FlagGet(key)==1:
                del self.plane[:]
            for min_depth, max_depth, name in my_buffer:
                if not name in self.plane:
                    if (len(name)==1 and
                        (((key == 'PLANE3' and self.parent.data.FlagGet(key)) or (self.parent.data.FlagGet(key)==1  and  key == 'PLANE1'))) and
                        isinstance(self.elements[name[0]-1], Point)):
                        self.plane.append(name)  
                        if self.parent.data.FlagGet(key) == 3:
                            self.InitPlane3()
                            break
                        else:
                            self.parent.data.FlagIncrement(key)              
                    elif (self.parent.data.FlagGet(key) and key == 'PLANE2') or (self.parent.data.FlagGet(key)>1 and key == 'PLANE1'):
                        self.plane.append(name)
                        if self.parent.data.FlagGet(key)==1 and key=='PLANE2':
                            self.parent.data.FlagIncrement(key)
                            break   
                        elif key=='PLANE1':
                            self.InitPlane1()
                            break   
                        elif key=='PLANE2':
                            self.InitPlane2()
                            break

    def InitPlane3(self):
        vect1 = subtract(self.elements[self.plane[0][0]-1].pos,self.elements[self.plane[1][0]-1].pos)
        vect2 = subtract(self.elements[self.plane[2][0]-1].pos,self.elements[self.plane[1][0]-1].pos)
        vect1 /= norm(vect1)
        vect2 /= norm(vect2)
        if norm(cross(vect1,vect2))<0.01:
            print 'Cannot create the plane, points are colinear'
        else:
            normal = cross(vect1,vect2)
            normal /= norm(normal)
            point = self.elements[self.plane[1][0]-1].pos
            self.CreatePlane(normal,point, vect1)
        self.parent.data.FlagReset('PLANE3')
        del self.plane[:]

    def InitPlane1(self):
        if len(name)==1:
            axis = self.elements[self.plane[1][0]-1]
            vect1 = inv(self.elements[self.plane[1][0]-1].T[0:3,0:3]).dot([1,0,0])
        else:
            if name[0]==0:
                axis = self.globFrame
            else:
                axis = self.elements[self.plane[1][0]-1]
            if name[1]==1:
                vect1 = inv(axis.T[0:3,0:3]).dot([1,0,0])
            elif name[1]==2:
                vect1 = inv(axis.T[0:3,0:3]).dot([0,1,0])
            else:
                vect1 = inv(axis.T[0:3,0:3]).dot([0,0,1])
        vect1 /= norm(vect1)

        vect2 = axis.T[3,0:3]-self.elements[self.plane[0][0]-1].pos
        vect2 /= norm(vect2)                       
        if norm(cross(vect1,vect2))<0.01:
            print 'Cannot create the plane, points on the line'
        else:
            normal = cross(vect1,vect2)
            normal /= norm(normal)
            point = axis.T[3,0:3]
            self.CreatePlane(normal,point, vect1)
        self.parent.data.FlagReset('PLANE1')
        del self.plane[:]

    def InitPlane2(self):
        vect = []
        point = []
        for i in range(0,2):
            print self.plane[i]
            if len(self.plane[i])==1:
                vect.append(inv(self.elements[self.plane[i][0]-1].T[0:3,0:3]).dot([1,0,0]))
                point.append(self.elements[self.plane[i][0]-1].T[3,0:3])
            else:
                if self.plane[i][0]==0:
                    axis = self.globFrame
                else:
                    axis = self.elements[self.plane[i][0]-1]

                if self.plane[i][1]==1:
                    vect.append(inv(axis.T[0:3,0:3]).dot([1,0,0]))
                    print 'x-axis'
                elif self.plane[i][1]==2:
                    vect.append(inv(axis.T[0:3,0:3]).dot([0,1,0]))
                    print 'y-axis'
                else:
                    vect.append(inv(axis.T[0:3,0:3]).dot([0,0,1]))
                    print 'z-axis'
                point.append(axis.T[3,0:3])
            vect[i] /= norm(vect[i])
                                    
        check = point[1]-point[0]
        if norm(check) > 0.01 and (vect[1][0]*vect[0][1]-vect[1][1]*vect[0][0])>0.01:
            t = (vect[1][0]*check[1]-vect[1][1]*check[0])/(vect[1][0]*vect[0][1]-vect[1][1]*vect[0][0])
            r = (vect[0][0]*t-check[0])/vect[1][0]
            s = check[2]-vect[0][2]*t-vect[1][2]*r      
        else:
            s = 0
        print norm(cross(vect[0],vect[1]))
                            
        if norm(cross(vect[0],vect[1]))<0.01 or s > 2:
            print 'Cannot create the plane, line to not intersect'
        else:
            normal = cross(vect[0],vect[1])
            normal /= norm(normal)
            print vect[0], vect[1]
            self.CreatePlane(normal,point[0], vect[0])
        self.parent.data.FlagReset('PLANE2')
        del self.plane[:]
                            
        

    def CreatePlane(self, normal, point, line):
        print 'Creating plane'
            
        self.cen = point
        self.cam = add(self.cen,multiply(normal,5))
        up = cross(line,normal)
        self.up = up/norm(up)
        
        self.cen = self.cen + multiply(up,0.01)
        self.plane[:] = []
        self.CameraTransformation()
        self.OnDraw()
        self.Redraw()



    def OnMouseUp(self, _):
        if self.HasCapture():
            self.ReleaseMouse()

    def OnMouseMotion(self, evt):
        if evt.Dragging():
            x, y = evt.GetPosition()
            
            if evt.LeftIsDown():
                dx, dy = x - self.lastx, y - self.lasty
                self.lastx, self.lasty = x, y

                if evt.RightIsDown():
                    self.Pan(dx,dy)
                else:
                    self.Rotate(dx,dy)
                    
            elif evt.RightIsDown():
                self.Zoom(y)


            self.CameraTransformation()
            self.Refresh(False)

   
    ## Create elemnts
    def CreateJoint(self, my_type):
        coefY = norm(self.u)*tan(radians(self.fov/2))/self.size.height*2
        coefX = norm(self.u)*tan(radians(self.fov/2))/self.size.width*2*self.aspect
                
        lastX = (self.lastx-self.size.width/2)*coefX
        lastY = (-self.lasty+self.size.height/2)*coefY
        originX = (self.origin[0]-self.size.width/2)*coefX
        originY = (-self.origin[1]+self.size.height/2)*coefY
        
        angle = arctan2(lastY-originY, lastX-originX)

        G = gl.glGetFloatv(gl.GL_MODELVIEW_MATRIX)
        R = self.EulerTransformation(angle, self.u/norm(self.u))
        T = vstack((hstack((R,vstack(([0,0,0])))),[0,0,0,1]))
        
##        Ry = self.EulerTransformation(pi/2, [1,0,0])
##        T2 = vstack((hstack((Ry,vstack(([0,0,0])))),[0,0,0,1]))
        T = inv(G).dot(T)
        T[3,0:3]=self.GetCoordinates(self.origin[0], self.origin[1])

        self.DrawElements(T=T,my_type=my_type)
        self.OnDraw()
        self.Redraw()
        self.parent.data.FlagReset(my_type)
        self.parent.data.FlagIncrement('PICK')
    
    
    ## Functions conected with camera
    def GetCoordinates(self, x, y):
        coefY = norm(self.u)*tan(radians(self.fov/2))/self.size.height*2
        coefX = norm(self.u)*tan(radians(self.fov/2))/self.size.width*2*self.aspect
                
        screenX = (x-self.size.width/2)*coefX
        screenY = (-y+self.size.height/2)*coefY
        z = 0

        u = self.u/norm(self.u)
        up = self.up/norm(self.up)
        r = cross(u,up)
        r /= norm(r)
        up = cross(r,u)
        up = up/norm(up)
        d = norm([screenX,screenY])
        a = atan2(screenY, screenX)
        dy = multiply(up,sin(a)*d)
        dx = multiply(r,cos(a)*d)

        trans = dy+dx+self.cen
##        print trans
##      print glu.gluUnProject(x,y, self.cen[2]) 
                
        return trans

    def EulerTransformation(self, angle, vector):
        e0 = cos(angle/2)
        e = multiply(sin(angle/2),vector)

        R = 2*vstack((hstack((e0*e0+e[0]*e[0]-0.5,e[0]*e[1]-e0*e[2],e[0]*e[2]+e0*e[1])),
             hstack((e[0]*e[1]+e0*e[2],e0*e0+e[1]*e[1]-0.5,e[2]*e[1]-e0*e[0])),
             hstack((e[0]*e[2]-e0*e[1],e[2]*e[1]+e0*e[0],e0*e0+e[2]*e[2]-0.5))))
        return R     

    def CameraTransformation(self):

        gl.glLoadIdentity()
        glu.gluLookAt(self.cam[0],self.cam[1],self.cam[2],
            self.cen[0], self.cen[1], self.cen[2],
            self.up[0], self.up[1], self.up[2])
        self.u = subtract(self.cen,self.cam)
##        self.Refresh(False)

    def SetCamera(self, ver, hor):

        u = cross(self.up, self.u/norm(self.u))

        R1 = self.EulerTransformation(ver, u/norm(u))
        R2 = self.EulerTransformation(hor, self.up)
        u = R2.dot(R1)
        u = hstack(u.dot(vstack(self.u)))
        u = u/norm(u)

        if not norm(cross(u,self.up))<0.05:
            self.cam  = subtract(self.cen,multiply(u,norm(self.u)))

    def Pan(self,dx,dy):
        coefY = norm(self.u)*tan(radians(self.fov/2))/self.size.height*2
        coefX = norm(self.u)*tan(radians(self.fov/2))/self.size.width*2*self.aspect
        d= norm(dx+dy)
        a = atan2(dy,dx)
        u = self.u/norm(self.u)
        r = cross(self.up,self.u)
        r /= norm(r)
        up = cross(self.u,r)
        up /= norm(up)
        dx = multiply(d*cos(a)*coefX*0.25,r)
        dy = multiply(coefY*d*sin(a)*0.5,up)
        self.cen += add(dx,dy)

    def Rotate(self,dx,dy):
        coef = norm(self.u)/self.length*sin(radians(self.fov/2.))
        d_hor = dx*coef/self.size.width
        d_ver = dy*coef/self.size.height
        self.SetCamera(d_ver,d_hor) 

    
    def Zoom(self,y):
        dy = y - self.lasty
        self.lasty = y
        du = 2 * float(dy) / self.size.height
        self.cam += multiply(self.u,du)

    ## Drawing Functions        
    def OnPaintAll(self, event):
        
        self.SetCurrent(self.context)
        if not self.init:
            self.InitGL()
            self.init = 1
            self.globFrame = Frame(0, T = identity(4), my_id=0)
            self.globFrame.set_length(.5)
            self.structure.append([0,[]])
            self.my_id = 1
    
        self.OnDraw()
        self.Redraw()
        event.Skip()

    def OnDraw(self):
        if not self.init:
            return
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        gl.glEnableClientState(gl.GL_VERTEX_ARRAY)
        gl.glEnableClientState(gl.GL_NORMAL_ARRAY)
        
##        globFrame.T = self.getCoordinates(self.size.width*0.1, self.size.height*0.9)
##        globFrame.set_lenght(0.25)


        self.globFrame.draw_frames()
        

        for element in self.elements:
##            print element

            if isinstance(element, JointObject):
##                print 'joint'
                element.draw_joint()

            elif isinstance(element, Frame):
##                print 'frame'
                element.draw_frames()
                
        
        gl.glDisableClientState(gl.GL_VERTEX_ARRAY)
        gl.glDisableClientState(gl.GL_NORMAL_ARRAY)


    def Redraw(self):
        gl.glFlush()
        self.SwapBuffers()
        self.Refresh(False)

    def DrawElements(self, my_type, T=identity(4), pos=[0,0,0]):
        if my_type=='POINT':
            self.elements.append(Point(pos, self.my_id,0))
            self.elements[-1].set_length(0.2)
        else:   
            if my_type=='FIXED':
                self.elements.append(Frame(T=T, my_id=self.my_id))
            elif my_type=='PRISMATIC':
                self.elements.append(SuperPrismaticJoint(self.my_id,T,0))
            elif my_type=='REVOLUTE':
                self.elements.append(SuperRevoluteJoint(self.my_id,T,0))
            self.elements[-1].set_length(0.5)
            if not len(self.elements)==1:    
                self.elements[-1].anc_pos = self.elements[self.structure[-1][0]-1].T[3,0:3]
                print self.elements[self.structure[-1][0]-1].T[3,0:3]
            self.structure[-1][1].append(self.my_id)
            self.structure.append([self.my_id,[]])
            
        
        self.my_id += 1
        if self.my_id > self.buffer_size:
            if self.buffer_size*2 <  self.max_stack:
                self.buffer_size *= 2
            elif self.my_id <= self.max_stack:
                self.buffer_size = self.max_stack
            else:
                print 'maximum value of elements has been achived, cannot add more independent elements, element will be crated but they would not be choosable from window view'

    ##OpenGL handling
    def Pick(self):
        self.globFrame.named = False
        
        for element in self.elements:
            element.named = False
            
        gl.glSelectBuffer(512)
        gl.glRenderMode(gl.GL_SELECT)
        gl.glInitNames()
        gl.glPushMatrix()
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        glu.gluPickMatrix(self.lastx, self.size.height-self.lasty ,0.25, 0.25, [0, 0, self.size.width, self.size.height])
        glu.gluPerspective(self.fov, self.aspect, 0.2, 200.0)
        gl.glMatrixMode(gl.GL_MODELVIEW)
        self.CameraTransformation()
        self.OnDraw()
        my_buffer = gl.glRenderMode(gl.GL_RENDER)
        gl.glPopMatrix()
        gl.glPushMatrix()
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        glu.gluPerspective(self.fov, self.aspect, 0.2, 200.0)
        gl.glMatrixMode(gl.GL_MODELVIEW)
        self.CameraTransformation()
        self.OnDraw()
        self.Redraw()
        gl.glPopMatrix()
##        for a, b, c in my_buffer:
##            print c

        return my_buffer
        
    def InitGL(self):
        # set viewing projection
        mat_specular = (1.0, 1.0, 1.0, 1.0)
        light_position = (.3, .3, 0.5, 0.0)
        light_position1 = (-0.3, 0.3, 0.5, 0.0)
        diffuseMaterial = (1., 1., 1., 1.0)
        ambientMaterial = (0.5, .5, .5, 1.0)

        gl.glClearColor(1.0, 1.0, 1.0, 1.0)
        gl.glShadeModel(gl.GL_SMOOTH)
        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glMaterialfv(gl.GL_FRONT, gl.GL_AMBIENT, ambientMaterial)
        gl.glMaterialfv(gl.GL_FRONT, gl.GL_DIFFUSE, diffuseMaterial)
        gl.glMaterialfv(gl.GL_FRONT, gl.GL_SPECULAR, mat_specular)
        gl.glMaterialf(gl.GL_FRONT, gl.GL_SHININESS, 25.0)
        gl.glLightfv(gl.GL_LIGHT0, gl.GL_POSITION, light_position)
        gl.glLightfv(gl.GL_LIGHT1, gl.GL_POSITION, light_position1)
        gl.glEnable(gl.GL_LIGHTING)
        gl.glEnable(gl.GL_LIGHT0)
        gl.glEnable(gl.GL_LIGHT1)

        gl.glColorMaterial(gl.GL_FRONT, gl.GL_DIFFUSE)
        gl.glEnable(gl.GL_COLOR_MATERIAL)

        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        glu.gluPerspective(self.fov, self.aspect, 0.2, 200.0)

        gl.glMatrixMode(gl.GL_MODELVIEW)
        
        self.CameraTransformation()
        self.globTrans = gl.glGetFloatv(gl.GL_MODELVIEW_MATRIX)
        gl.glRenderMode(gl.GL_RENDER)
        self.max_stack = gl.glGetFloatv(gl.GL_MAX_NAME_STACK_DEPTH)
  
        
        
        

    
