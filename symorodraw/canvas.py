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
from sympy import Expr, var, Symbol, Matrix
import draw

from pysymoro.invgeom import loop_solve
from pysymoro.geometry import dgm
from pysymoro.robot import Robot
from symoroutils import samplerobots
from symoroutils import symbolmgr
from symoroutils import tools
from symoroutils import parfile
from symoroutils.tools import CLOSED_LOOP, SIMPLE, TREE, TYPES, INT_KEYS

import itertools

from objects import Frame, SuperRevoluteJoint, FixedJoint, SuperPrismaticJoint, JointObject, Point, Line, SuperFixedJoint


class myGLCanvas(GLCanvas):
    def __init__(self, parent, size=(900, 900)):
        super(myGLCanvas, self).__init__(parent, size=size)
        self.context = GLContext(self)
        self.Bind(wx.EVT_PAINT, self.OnPaintAll)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnMouseDown)
        self.Bind(wx.EVT_LEFT_UP, self.OnMouseUp)
        self.Bind(wx.EVT_RIGHT_DOWN, self.OnMouseDown)
        self.Bind(wx.EVT_RIGHT_UP, self.OnMouseUp)
        self.Bind(wx.EVT_MOTION, self.OnMouseMotion)
        self.Bind(wx.EVT_LEFT_DCLICK, self.OnMouseDoubleLeft)
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
        self.size = self.GetClientSize()

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
        self.structure = []
        self.links = []
        self.branches = []
        self.d_init = False
        self.old_T = []


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
        
        if not (self.parent.data.FlagGet('ADD_ANC') or self.parent.data.FlagGet('REM_ANC')):
            self.Deactivate()
        
        for key in self.parent.data.FlagList('joint'):
            if self.parent.data.FlagGet(key) == 1:
                self.parent.data.FlagIncrement(key)
                self.origin = self.lastx, self.lasty
                
            elif self.parent.data.FlagGet(key) == 2:
               self.CreateJoint(key)

        if self.parent.data.FlagGet('PICK'):
            my_buffer = self.Pick()
            if self.parent.data.FlagGet('PLANE1') or  self.parent.data.FlagGet('PLANE2') or  self.parent.data.FlagGet('PLANE3'):
                self.DefinePlane(my_buffer)
            elif self.parent.data.FlagGet('DELETE'):
                self.OnDelete(my_buffer)
            elif self.parent.data.FlagGet('ADD_ANC'):
                self.AddAncestor(my_buffer)
            elif self.parent.data.FlagGet('REM_ANC'):
                self.RemAncestor(my_buffer)
            elif self.parent.data.FlagGet('PARALLEL'):
                self.MakeConstrain(my_buffer, 'PARALLEL')
            elif self.parent.data.FlagGet('PERPENDICULAR'):
                self.MakeConstrain(my_buffer, 'PERPENDICULAR')
            elif self.parent.data.FlagGet('AT_ANGLE'):
                self.MakeConstrain(my_buffer, 'AT_ANGLE')
            elif self.parent.data.FlagGet('AT_DISTANCE'):
                self.MakeConstrain(my_buffer, 'AT_DISTANCE')
            else:
                self.Activate(my_buffer)
            
        if self.parent.data.FlagGet('REF_POINT'):
                self.DrawElements(my_type='POINT', pos = self.GetCoordinates(self.lastx, self.lasty))
                self.OnDraw()
                self.Redraw()
                self.parent.data.FlagReset('REF_POINT')
                self.parent.data.FlagIncrement('PICK')

        

    def OnMouseDoubleLeft(self, evt):
        self.parent.data.FlagsChange('joint')
        self.parent.data.FlagsChange('ref')
        self.parent.data.FlagsChange('plane')
        self.parent.data.FlagsChange('button')
        self.parent.data.FlagsChange('constraints')
        del self.plane[:]

    def Export(self, name):
        NJ = len([i for i in self.elements if isinstance(i, SuperRevoluteJoint) or isinstance(i, SuperPrismaticJoint)])
        NL = len([i for i in self.elements if isinstance(i, Point)])-1
        NF = NL+2*(NJ-NL)
        
        if not self.structure:
            return
        if not self.structure[0]-self.structure[1]:
            structure = SIMPLE
        elif not NJ-NL:
            structure = TREE
        else:
            structure = CLOSED_LOOP

        robot = Robot(name, NJ=NJ, NL=NL, NF=NF, is_mobile=False,
                 structure=structure)
        
        robot.G = Matrix([var('G1'), var('G2'), var('G3')])
        if self.structure[4][0]:
            robot.Z = transpose(self.elements[self.structure[4][0]-1].T)

        frames = []
        end = []
        cut = []
        
        for branch in self.branches[self.structure[0]:self.structure[1]+1]:
            fr = [i for i in branch[2:-2] if not isinstance(self.elements[i-1], Point)]
           
            if not self.elements[branch[-2]-1].virtual_joint:
                end.append(branch[-2])
            else:
                cut.append(branch[-2])

        frames = fr + end + cut

        sigma, mu, theta, alpha, gamma, d, r, b, ant = [],[],[],[],[],[],[],[],[]

        for frame in frames:
##            
            if isinstance(self.elements[frame-1], SuperPrismaticJoint):
                sigma.append(1)
            elif isinstance(self.elements[frame-1], SuperRevoluteJoint):
                sigma.append(0)
            else:
                sigma.append(2)
                
            i = [i for i in range(len(frames)) if frames[i] == self.elements[frame-1].ant]
            if len(i)==0 and self.elements[frame-1].ant==self.structure[4][0]:
                ant.append(0)
            elif len(i)>0:
                rant.append(i[0])
            else:
                msg = wx.MessageDialog (None, 'Export error, cannot deifne the parameters.', style=wx.OK|wx.CENTRE)
                msg.ShowModal()
                return 

            if self.elements[frame-1].active and not self.elements[frame-1].cut_joint:
                mu.append(1)
            else:
                mu.append(0)
        
            if isinstance(self.elements[frame-1], SuperRevoluteJoint) and not self.elements[frame-1].virtual_joint:
                theta.append(var('th%s' % (len(theta+1))))
            else:
                theta.append(self.elements[frame-1].theta)
                
            if isinstance(self.elements[frame-1], SuperRevoluteJoint) and not self.elements[frame-1].virtual_joint:
                theta.append(var('r%s' % (len(theta+1))))
            else:
                r.append(self.elements[frame-1].r)
                
            alpha.append(self.elements[frame-1].alpha)
            d.append(self.elements[frame-1].d)
            gamma.append(self.elements[frame-1].gamma)
            b.append(self.elements[frame-1].b)

        robot.sigma[1:] = sigma
        robot.theta[1:] = theta
        robot.alpha[1:] = alpha
        robot.gamma[1:] = gamma
        robot.d[1:] = d
        robot.r[1:] = r
        robot.b[1:] = b
        robot.ant[1:] = ant
        
                    
        parfile.writepar(robot)
        
                    

    def DefineStructure(self):
        self.branches = []
        self.structure = []
        self.elements = [i for i in self.elements if not i.virtual_joint]
        self.my_id = len(self.elements)+1
        branches = []
        links = self.links
        start = 0
        cut_joints = []
        struct = []
        start = self.FindStart(links, branches)
        branches.append([])
        used = []
        joints = []
        fixed = [start]
        my_links = []
        
        for element in self.elements:
            if isinstance(element, SuperRevoluteJoint) or isinstance(element, SuperPrismaticJoint):
                i = [i for i in self.links if i[1]==element.my_id] 
                if len(i)<2:
                    msg = wx.MessageDialog (None, 'Cannot define the structure, at least one joint missing conection.', style=wx.OK|wx.CENTRE)
                    msg.ShowModal()
                    return struct, branches
                elif element.cut_joint:
                    cut_joints.append([i[0][0],i[0][1],i[1][0]])

        NJ = len([i for i in self.elements if isinstance(i, SuperRevoluteJoint) or isinstance(i, SuperPrismaticJoint)])
        NL = len([i for i in self.elements if isinstance(i, Point)])-1

        if len(cut_joints) < NJ-NL:
            msg = wx.MessageDialog (None, 'Cannot define the structure, please define more cut joints.', style=wx.OK|wx.CENTRE)
            msg.ShowModal()
            return struct, branches

        branches[-1], links, used, joints, fixed, my_links = self.GetBranch(start, links, used, joints, fixed, cut_joints, my_links)
        struct.append(len(branches)-1)
        

        while len(branches[-1])>1:
            key = self.FindKey(links, branches)
            branches.append([])
            branches[-1], links, used, joints, fixed, my_links= self.GetBranch(key, links, used, joints, fixed, cut_joints, my_links)

        for branch in branches:
            if  [i for i in cut_joints if i[1]==branch[-1] and [2]==branch[-2]]:
                print 'cut', branch[-1], branch[-2]

##                    if isinstance(self.elements[joint-1], SuperRevoluteJoint):
##                        self.DrawElements(my_type='REVOLUTE', T=self.elements[joint-1].T)
##                    else:
##                        self.DrawElements(my_type='PRISMATIC', T=self.elements[joint-1].T)
##                    self.elements[-1].show_frame = False
##                    self.elements[-1].show_joint = False
##                    joint = self.elements[-1].my_id
##                    self.elements[-1].virtual_joint = True

        struct.append(len(branches)-2)
        struct.append(used)
        struct.append(joints)
        struct.append(fixed)
        struct.append(cut_joints)
        struct.append(my_links)
        return struct, branches

    def FindKey(self, links, branches):
        key = -1
        for branch in branches:
            for link in links:
                if link[0] in branch[:-1] :
                    return link[0]
        return key        

    def FindStart(self, links, branches):
        i = [i[1] for i in links if not i[1]]
        if len(i):
            return i[0]
        else:
            i = [i[1] for i in links if isinstance(i[1], SuperFixedJoint)]
            if len(i):
                return i[0]
        
        return -1

    def GetBranch(self, key, links, used, joints, fixed, cut_joints, my_links):
        branch = []
        check = True
        branch.append(key)
        
        
        while check:
            check = False
            if_break = False
            for link in links:
                if link[0]==key:
                    key = link[0-1]
                    branch.append(key)
                    check = True
                    if_break = True
                    remove = link
                    used.append(link)
                    if not key in joints and not isinstance(self.elements[key-1], SuperFixedJoint) and not key==0:
                        joints.append(key)
                    elif not key in fixed and (isinstance(self.elements[key-1], SuperFixedJoint) or key==0):
                        fixed.append(key)
                elif link[1]==key and (len(branch)<2 or (not ([branch[-2],branch[-1],link[0]] in cut_joints) and (not ([link[0],branch[-1],branch[-2]] in cut_joints)))):

                    branch.append(link[1-1])
                    key = link[1-1]
                    check = True
                    if_break = True
                    remove = link
                    used.append(remove)
                    if not key in link and isinstance(self.elements[key-1], Point):
                        my_links.append(key)
                if if_break:
                    links = [i for i in links if not i==remove]
                    break
                
        return  branch, links, used, joints, fixed, my_links

    def Activate(self, my_buffer):
        for min_d, max_d, name in my_buffer:
    
            self.Deactivate()
            if len(name)>1:
                if name[0]:
                    self.elements[name[0]-1].color_j=[1,0,0]
                    self.parent.ActiveJoint(name[0], self.elements[name[0]-1].param)
                elif name[0]==0:
                    self.parent.ActiveJoint(-2, 0)
            else:
                self.elements[name[0]-1].color_j=[1,0,0]
                self.elements[name[0]-1].color_l=[1,0,0]
                self.parent.ActiveLink(name[0])
            break
        

    def Deactivate(self):
        if self.parent.data.FlagGet('ACTIVE_JOINT')==-2:
            self.globFrame.color_j=[0,0.6,0.5]
        elif self.parent.data.FlagGet('ACTIVE_JOINT'):
            if isinstance(self.elements[self.parent.data.FlagGet('ACTIVE_JOINT')-1],SuperRevoluteJoint):
                self.elements[self.parent.data.FlagGet('ACTIVE_JOINT')-1].color_j=[1,1,0]
            elif isinstance(self.elements[self.parent.data.FlagGet('ACTIVE_JOINT')-1],SuperPrismaticJoint):
                self.elements[self.parent.data.FlagGet('ACTIVE_JOINT')-1].color_j=[1,0.6,0]
            else:
                self.elements[self.parent.data.FlagGet('ACTIVE_JOINT')-1].color_j=[0,0.6,0.5]
            
        elif self.parent.data.FlagGet('ACTIVE_LINK'):
            self.elements[self.parent.data.FlagGet('ACTIVE_LINK')-1].color_j=[0,0.6,0.5]
            self.elements[self.parent.data.FlagGet('ACTIVE_LINK')-1].color_l=[1,1,1]
        self.parent.Deactive()

    def AddAncestor(self, my_buffer):
        for a, b, name in my_buffer:
            if not name[0] or not isinstance(self.elements[name[0]-1],Point):
                if not [self.parent.data.FlagGet('ACTIVE_LINK'),name[0]] in self.links:
                    if len([i for i in self.links if i[1]==name[0]])<2:
                        self.links.append([self.parent.data.FlagGet('ACTIVE_LINK'),name[0]])
                        if not name[0] and not [i for i in self.elements[self.parent.data.FlagGet('ACTIVE_LINK')-1].anc_pos if all(i==[0,0,0])]:
                            self.elements[self.parent.data.FlagGet('ACTIVE_LINK')-1].anc_pos.append([0,0,0])
                        elif name[0]  and not [i for i in self.elements[self.parent.data.FlagGet('ACTIVE_LINK')-1].anc_pos if all(i== self.elements[name[0]-1].T[3,0:3])]:
                            self.elements[self.parent.data.FlagGet('ACTIVE_LINK')-1].anc_pos.append(self.elements[name[0]-1].T[3,0:3])
                
        
                self.parent.data.FlagReset('ADD_ANC')
                break

    def RemAncestor(self, my_buffer):
        for a, b, name in my_buffer:
            if not isinstance(self.elements[name[0]-1],Point) or not name[0]:
                self.links=[i for i in self.links if not i==[self.parent.data.FlagGet('ACTIVE_LINK'),name[0]]]

                if name[0]:
                    self.elements[self.parent.data.FlagGet('ACTIVE_LINK')-1].anc_pos = [
                        i for i in self.elements[self.parent.data.FlagGet('ACTIVE_LINK')-1].anc_pos if not all(i==self.elements[name[0]-1].T[3,0:3])]
                else:
                    self.elements[self.parent.data.FlagGet('ACTIVE_JOINT')-1].anc_pos = [
                        i for i in self.elements[self.parent.data.FlagGet('ACTIVE_LINK')-1].anc_pos if not all(i==[0,0,0])]
                    
                self.parent.data.FlagReset('REM_ANC')
                break

    def MakeConstrain(self, my_buffer, flag):
            for min_d, max_d, name in my_buffer:
                if  not name[0] or not isinstance(self.elements[name[0]-1],Point):
                    if self.parent.data.FlagGet(flag)==1:
                        self.plane.append(name[0])
                        self.parent.data.FlagIncrement(flag)
                    elif not (name[0] in self.plane) and name[0]:
                        if not self.plane[0]:
                            axis = self.globFrame
                        else:
                            axis = self.elements[self.plane[-1]-1]
                        if flag=='PARALLEL':
                            self.elements[name[0]-1].T[0:3,0:3]=axis.T[0:3,0:3]
                        elif flag=='PERPENDICULAR':
                            self.elements[name[0]-1].T[0:3,0:3]=self.EulerTransformation(pi/2,[1,0,0]).dot(axis.T[0:3,0:3])
                        elif flag=='AT_ANGLE':
                            export = wx.TextEntryDialog(None, 'Give the angle(degrees)',  style=wx.SYSTEM_MENU|wx.OK|wx.CANCEL)
                            if export.ShowModal()==wx.ID_OK:
                                self.elements[name[0]-1].T[0:3,0:3]=self.EulerTransformation(radians(int(export.GetValue())),[1,0,0]).dot(axis.T[0:3,0:3])
                        elif flag=='AT_DISTANCE':
                            export = wx.TextEntryDialog(None, 'Give the distance',  style=wx.SYSTEM_MENU|wx.OK|wx.CANCEL)
                            if export.ShowModal()==wx.ID_OK:
                                val = float(export.GetValue())
                                u = subtract(self.elements[name[0]-1].T[3,0:3],axis.T[3,0:3])
                                u /= norm(u)
                                self.elements[name[0]-1].T[3,0:3]=add(axis.T[3,0:3],multiply(u,val))

                        del self.plane[:]
                        self.parent.data.FlagReset(flag)
                    elif not name[0]:
                        del self.plane[:]
                        self.parent.data.FlagReset(flag)
                    break
                        

    def OnDelete(self, my_buffer):
        for a, b, name in my_buffer:
            if name and name[0]:
                if len(name)>1:
                    for l in [i for i in self.links if i[1]==name[0]]:
                        self.elements[l[0]-1].anc_pos = [i for i in self.elements[l[0]-1].anc_pos if not all(i==self.elements[name[0]-1].T[3,0:3])]   
                    self.links = [i for i in self.links if not i[1]==name[0]]
                else:
                    self.links = [i for i in self.links if not i[0]==name[0]]                

                for i in self.links:
                    if i[0]>name[0]:
                        i[0] -= 1
                    if i[1]>name[0]:
                        i[1] -= 1
                                         
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
                    if ((name[0] and (isinstance(self.elements[name[0]-1], Point) or name[1]==0)) and
                        (((key == 'PLANE3' and self.parent.data.FlagGet(key)) or (self.parent.data.FlagGet(key)==1  and  key == 'PLANE1')))):
                        self.plane.append(name)  
                        if self.parent.data.FlagGet(key) == 3:
                            self.InitPlane3()
                            break
                        else:
                            self.parent.data.FlagIncrement(key)              
                    elif (not(name[0] and (isinstance(self.elements[name[0]-1], Point) or name[1]==0)) and
                              ((self.parent.data.FlagGet(key) and key == 'PLANE2') or (self.parent.data.FlagGet(key)>1 and key == 'PLANE1'))):
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
        points = []
        for i in range(0,3):
            print self.plane[i][0]-1
            if isinstance(self.elements[self.plane[i][0]-1], Point):
                points.append(self.elements[self.plane[i][0]-1].pos)
            else:
                points.append(self.elements[self.plane[i][0]-1].T[3,0:3])
                
        vect1 = subtract(points[0],points[1])
        vect2 = subtract(points[0],points[2])
        vect1 /= norm(vect1)
        vect2 /= norm(vect2)
        if norm(cross(vect1,vect2))<0.01:
            print 'Cannot create the plane, points are colinear'
        else:
            normal = cross(vect1,vect2)
            normal /= norm(normal)  
            self.CreatePlane(normal,points[0], vect1)
        self.parent.data.FlagReset('PLANE3')
        del self.plane[:]

    def InitPlane1(self):
        if isinstance(self.elements[self.plane[0][0]-1], Point):
            point = self.elements[self.plane[0][0]-1].pos
        else:
            point = self.elements[self.plane[0][0]-1].T[3,0:3]
        
        if self.plane[1][1]==4:
            axis = self.elements[self.plane[1][0]-1]
            vect1 = inv(self.elements[self.plane[1][0]-1].T[0:3,0:3]).dot([0,0,1])
        else:
            if not self.plane[1][0]:
                axis = self.globFrame
            else:
                axis = self.elements[self.plane[1][0]-1]
            if self.plane[1][1]==1:
                vect1 = inv(axis.T[0:3,0:3]).dot([1,0,0])
            elif self.plane[1][2]==1:
                vect1 = inv(axis.T[0:3,0:3]).dot([0,1,0])
            else:
                vect1 = inv(axis.T[0:3,0:3]).dot([0,0,1])
                
        vect1 /= norm(vect1)
        vect2 = axis.T[3,0:3]-point
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
            if self.plane[i][1]==4:
                vect.append(inv(self.elements[self.plane[i][0]-1].T[0:3,0:3]).dot([0,0,1]))
                point.append(self.elements[self.plane[i][0]-1].T[3,0:3])
            else:
                if not self.plane[i][0]:
                    axis = self.globFrame
                else:
                    axis = self.elements[self.plane[i][0]-1]

                if self.plane[i][1]==1:
                    vect.append(inv(axis.T[0:3,0:3]).dot([1,0,0]))
                elif self.plane[i][1]==2:
                    vect.append(inv(axis.T[0:3,0:3]).dot([0,1,0]))
                else:
                    vect.append(inv(axis.T[0:3,0:3]).dot([0,0,1]))
                point.append(axis.T[3,0:3])
            vect[i] /= norm(vect[i])
                                    
        check = point[1]-point[0]
        if norm(check) > 0.0001 and abs((vect[1][0]*vect[0][1]-vect[1][1]*vect[0][0]))>0.0001:
            t = (vect[1][0]*check[1]-vect[1][1]*check[0])/(vect[1][0]*vect[0][1]-vect[1][1]*vect[0][0])
            r = (vect[0][0]*t-check[0])/vect[1][0]
            s = check[2]-vect[0][2]*t+vect[1][2]*r
        else:
            s = 0
        if norm(cross(vect[0],vect[1]))<0.01 or abs(s) > 0.2:
            print 'Cannot create the plane, line to not intersect'
        else:
            normal = cross(vect[0],vect[1])
            normal /= norm(normal)
            self.CreatePlane(normal,point[0], vect[0])
        self.parent.data.FlagReset('PLANE2')
        del self.plane[:]

    def CreatePlane(self, normal, point, line):
        self.cen = point
        
        up = cross(line,normal)
        self.up = up/norm(up)
        
        self.cen = self.cen + multiply(up,0.01)
        self.cam = add(self.cen,multiply(normal,5))
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
        
        T = inv(G).dot(T)
        T[3,0:3]=self.GetCoordinates(self.origin[0], self.origin[1])
        if my_type=='REVOLUTE' or my_type=='PRISMATIC':
            T[0:3,0:3] = self.EulerTransformation(-pi/2,[0,1,0]).dot(T[0:3,0:3])
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
        dy = multiply(up,screenY)
        dx = multiply(r,screenX)
        
        trans = dy+dx+self.cen
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
        u = self.u/norm(self.u)
        r = cross(self.up,self.u)
        r /= norm(r)
        up = cross(self.u,r)
        up /= norm(up)
        dx = multiply(dx*coefX*0.25,r)
        dy = multiply(coefY*dy*0.5,up)
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
            self.globFrame = SuperFixedJoint(0, identity(4), 0)
            self.globFrame.set_length(.5)
            self.globFrame.show_joint = False
            self.globFrame.theta = 0
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
        
        self.globFrame.draw_joint()

        if not self.parent.data.FlagGet('MODE'):
            for element in self.elements:
##                element.show_frame = False
                element.draw_joint()

        elif self.branches:
            gl.glPushMatrix()
            if self.structure[4][0]:
                gl.glMultMatrixf(self.elements[self.structure[4][0]-1].T)
            self.Transform(self.branches[self.structure[0]])
            gl.glPopMatrix()
        
        gl.glDisableClientState(gl.GL_VERTEX_ARRAY)
        gl.glDisableClientState(gl.GL_NORMAL_ARRAY)

    def Transform(self, branch):
        gl.glPushMatrix()
        for joint in branch:
            if joint==0 or not isinstance(self.elements[joint-1], Point):
                if joint:
                    self.elements[joint-1].draw()
                else :
                    self.globFrame.draw()
                
            for k in [i for i in self.branches[self.structure[0]+1:self.structure[1]+1] if i[0]==joint]:
                self.Transform(k[1:])
                
        gl.glPopMatrix()

    def GetParameters(self, branch, start, s_joint):
        old = s_joint
        print 'old', old
        self.old_T.append(start)
        br = 0
        
        for joint in branch:
            if joint==0 or not isinstance(self.elements[joint-1], Point):
                if not br and not (branch == self.branches[self.structure[0]][1:]):
                    self.elements[joint-1].param = 6
                elif joint:
                    self.elements[joint-1].param = 4
                if joint:
                    self.elements[joint-1].ant = old
                self.old_T[-1] = self.Parameters(joint,self.old_T[-1])
                old = joint
                if joint == self.branches[self.structure[0]][2]:
                    if not self.elements[joint-1].gamma==0 and not self.elements[joint-1].b==0:
                        self.elements[joint-1].param = 6
                
            for k in [i for i in self.branches[self.structure[0]+1:self.structure[1]+1] if i[0]==joint]:
                self.GetParameters(k[1:],self.old_T[-1], joint)
            br += 1
            
        del self.old_T[-1]

    def SetParameters(self):
        
        for branch in self.branches[self.structure[0]:self.structure[1]+1]:
            init = False
            for joint in reversed(branch):
                if (joint==0 or not isinstance(self.elements[joint-1], Point)) and not joint == self.branches[self.structure[0]][2] :
                    if not init:
                        init = True
                    elif (not joint == 0) and self.elements[old-1].param == 4:
                        self.elements[joint-1].theta += self.elements[old-1].gamma
                        self.elements[joint-1].r += self.elements[old-1].b
                        self.elements[old-1].b = 0
                        self.elements[old-1].gamma = 0
                    
                    else:
                        break
                    old = joint
                    
##        for branch in self.branches[self.structure[0]:self.structure[1]+1]:
##            for joint in branch:
##                if isinstance(self.elements[joint-1], SuperRevoluteJoint):
##                    self.elements[joint-1].theta = 0
##                if isinstance(self.elements[joint-1], SuperPrismaticJoint):
##                    self.elements[joint-1].r = 0.2    
                
    def Parameters(self,  new_id,old_T):
        
        T = dot(inv(old_T),transpose(self.elements[new_id-1].T))

        gamma = arctan2(-T[0,2],T[1,2])
        alpha = arctan2(sin(gamma)*T[0,2]-cos(gamma)*T[1,2],T[2,2])
        theta = arctan2(-cos(gamma)*T[0,1]-sin(gamma)*T[1,1],cos(gamma)*T[0,0]+sin(gamma)*T[1,0])
        d = T[1,3]*sin(gamma)+T[0,3]*cos(gamma)

        if not sin(alpha):
            r = T[2,3]
        elif not sin(gamma):
            r = T[0,3]/sin(alpha)
        else:
            r = (T[0,3]-d*cos(gamma))/sin(gamma)/sin(alpha)
            
        b =T[2,3]-r*cos(alpha)

        if new_id:
            element = self.elements[new_id-1]
        else:
            element = self.globFrame
        element.gamma = gamma
        element.alpha = alpha
        element.theta = theta
        element.d = d
        element.r = r
        element.b = b    

        
        new_T = [[cos(gamma)*cos(theta)-sin(gamma)*cos(alpha)*sin(theta),
                  -cos(gamma)*sin(theta)-sin(gamma)*cos(alpha)*cos(theta),
                  sin(gamma)*sin(alpha),
                  d*cos(gamma)+r*sin(gamma)*sin(alpha)],
                 [sin(gamma)*cos(theta)+cos(gamma)*cos(alpha)*sin(theta),
                  -sin(gamma)*sin(theta)+cos(gamma)*cos(alpha)*cos(theta),
                  -cos(gamma)*sin(alpha),
                  d*sin(gamma)-r*cos(gamma)*sin(alpha)],
                 [sin(alpha)*sin(theta),sin(alpha)*cos(theta),
                  cos(alpha),r*cos(alpha)+b],
                 [0,0,0,1]]

        return old_T.dot(new_T)
        
    
    def Redraw(self):
        gl.glFlush()
        self.SwapBuffers()
        self.Refresh(False)

    def DrawElements(self, my_type, T=identity(4), pos=[0,0,0]):
        if my_type=='POINT':
            self.elements.append(Point(pos, self.my_id,0))
            self.elements[-1].set_length(0.3)
        else:   
            if my_type=='FIXED':
                self.elements.append(SuperFixedJoint(0, my_id=self.my_id ,T=T))
            elif my_type=='PRISMATIC':
                self.elements.append(SuperPrismaticJoint(0, my_id=self.my_id, T=T))
            elif my_type=='REVOLUTE':
                self.elements.append(SuperRevoluteJoint(0, my_id=self.my_id, T=T))
            self.elements[-1].set_length(0.5)
        self.my_id += 1
        
        if self.my_id > self.buffer_size:
            if self.buffer_size*4 <  self.max_stack:
                self.buffer_size *= 4
            elif self.my_id <= self.max_stack:
                self.buffer_size = self.max_stack
            else:
                msg = wx.MessageDialog (None, 'Maximu value of indepentend elements has been achived. New elements will not be pickble', style=wx.OK|wx.CENTRE)
                msg.ShowModal()
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
        for b, n,m in my_buffer:
            print m
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
