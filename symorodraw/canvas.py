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

from objects import Frame, SuperRevoluteJoint, FixedJoint, SuperPrismaticJoint, JointObject, Point, Line, SuperFixedJoint


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
##        self.structure = []
        self.links = []


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
            self.DeactivateJoint()
        
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
            else:
                self.ActivateJoint(my_buffer)
            
        if self.parent.data.FlagGet('REF_POINT'):
                self.DrawElements(my_type='POINT', pos = self.GetCoordinates(self.lastx, self.lasty))
                self.OnDraw()
                self.Redraw()
                self.parent.data.FlagReset('REF_POINT')
                self.parent.data.FlagIncrement('PICK')

    def GetParameters(self, structures, branches):
        for i in range(len(structures)):
            print structures[i][4]
            l_joint = structures[i][4][0]
            
            for branch in branches[structures[i][0]:structures[i][1]+1]:
                for joint in branch:
                    if not joint==branch[0]:
                        continue
                    if not (joint==branch[-1] and [i for i in structures[i][5] if i[2]==joint]):
                        br = (joint==branch[1] and not branch==branches[structures[i][0]])
                        self.GetFrame(joint-1,self.elements[l_joint-1].T[0:3,0:3].dot([1,0,0]),
                                      self.elements[joint-1].T[0:3,0:3].dot([1,0,0]),
                                      self.elements[l_joint-1].vxaxis,
                                      self.elements[joint-1].vxaxis,
                                      self.elements[l_joint-1].T[3,0:3],
                                      self.elements[joint-1].T[3,0:3],
                                      self.elements[l_joint-1].pxaxis,
                                      self.elements[joint-1].pxaxis,
                                      br)
                    l_joint = joint
                    
            for cut in structures[i][5]:
                self.GetFrame(cut[1]-1, self.elements[cut[0]-1].T[0:3,0:3].dot([1,0,0]),
                              self.elements[cut[1]-1].T[0:3,0:3].dot([1,0,0]),
                              self.elements[cut[0]-1].vxaxis,
                              self.elements[cut[1]-1].vxaxis,
                              self.elements[cut[0]-1].T[3,0:3],
                              self.elements[cut[1]-1].T[3,0:3],
                              self.elements[cut[0]-1].pxaxis,
                              self.elements[cut[1]-1].pxaxis,                         
                              True)
                
                self.DrawElements(T=self.elements[cut[0]-1].T , my_type='FIXED')
                self.elements[-1].show_joint = False
                self.elements[-1].show_frame = False
                self.GetFrame(-1, self.elements[cut[2]-1].T[0:3,0:3].dot([1,0,0]),
                              self.elements[cut[1]-1].T[0:3,0:3].dot([1,0,0]),
                              self.elements[cut[0]-1].vxaxis,
                              self.elements[cut[1]-1].vxaxis,
                              self.elements[cut[2]-1].T[3,0:3],
                              self.elements[cut[1]-1].T[3,0:3],
                              self.elements[cut[0]-1].pxaxis,
                              self.elements[cut[1]-1].pxaxis,
                              True)

    
                

    def GetFrame(self, e_id, z0, z1, x0, x1, z0p, z1p, x0p, x1p, branch = False):
        if branch:
            u, u0 = self.CommonNormal(z0, z1)
            gamma = self.DefineAngle(u, x0, z0)
            self.elements[e_id].b = self.DefinetDistance(u0, u, x0p, x0, z0p, z0)
        self.elements[e_id].alpha = self.DefineAngle(x0, z0, z1)
        self.elements[e_id].d = self.DefineDistance(x0p, x0,z0p, z0,z1p, z1)
        self.elements[e_id].theta = self.DefineAngle(z1, x0, x1)
        self.elements[e_id].r = self.DefineDistance(z1p, z1, x0p, x0, x1p, x1)

    def Export(self):
        pass

    def GetAxises(self, structures, branches):
        print structures
        print branches
        for struct in range(len(structures)):
            pass
        return structures, branches
            
        

    def DefineStructure(self):
##        NJ = len([i for i in self.elements if not isinstance(i, Point)])
##        NL = len(self.links)
##        NF = NJ+2*(NL-NJ)

        
        branches = []
        links = self.links
        start = 0
        cut_joints = []
        L = 0
        structs = []
        
        while len(links) and not (start == -1):
            start = self.FindStart(links, branches)
            structs.append([])
            branches.append([])
            used = []
            joints = []
            fixed = [start]
            branches[-1], links, used, joints, fixed = self.GetBranch(start, links, used, joints, fixed, [])
            structs[-1].append(len(branches)-1)

            while len(branches[-1])>1:
                key = self.FindKey(links, branches)
                branches.append([])
                branches[-1], links, used, joints, fixed = self.GetBranch(key, links, used, joints, fixed, [])
            structs[-1].append(len(branches)-2)
            structs[-1].append(used)
            structs[-1].append(joints)
            structs[-1].append(fixed)

            if (len(structs[-1][2])-len(structs[-1][3])):
                structs[-1].append(self.ChooseCutJoints(structs[-1]))
                branches.append([])
                used = []
                joints = structs[-1][3]
                fixed = structs[-1][4]
                branches[-1], links, used, joints, fixed = self.GetBranch(structs[-1][4][0], structs[-1][2], used, structs[-1][3], structs[-1][4], structs[-1][5])
                structs[-1][0]=(len(branches)-1)

                while len(branches[-1])>1:
                    key = self.FindKey(links, branches[structs[-1][0]::])
                    branches.append([])
                    branches[-1], links, used, joints, fixed = self.GetBranch(key, links, used, structs[-1][3], structs[-1][4], structs[-1][5])
                    if [i for i in structs[-1][5] if i[1]==branches[-1][0] and (i[0]==branches[-1][1] or i[2]==branches[-1][1])]:
                        branches[-1] = branches[-1][::-1]
                structs[-1][1]=(len(branches)-2)
            
            
##        print 'links', links
##        for branch in branches:
##            print 'branch', branch
##        print 'branch start, branch last, links, joints, fixed'
##        for struct in structs:
##            print 'struct', struct
##        print 'free links', len(links)
        return structs, branches

    def ChooseCutJoints(self, struct):
        start = struct[4][0]
        links = struct[2]
        joints = struct[3]+struct[4]
        cut_joints = []
        check = 0

        while check < len(struct[2])-len(struct[3]):
            print 'len', len(struct[2])-len(struct[3])
            used = []
            possible_links = links
            used.append(start)
            
            if possible_links[0][0]==start:
                joint = possible_links[0][1]
            else:
                joint = possible_links[0][0]
                
            cut_joint = False
            used.append(joint)
            possible_links = possible_links[1::]
            checked = 0
            free = possible_links
            actual_link = []
            while not cut_joint:
                if_break = False
                for link in free:
                    for i in range(0,2):
                        if link[i]==joint and not ([used[-2],link[i],link[i-1]] in cut_joints) and not ([link[i-1],link[i],used[-2]] in cut_joints):
                            joint = link[i-1]
                            if_break = True
##                            print 'link'
                            actual_link = link
                            if joint in used and len(used[used.index(joint)::])>2:
                                cut_joint = True
                            elif joint in used:
                                checked == 2
                            elif isinstance(self.elements[joint-1], SuperFixedJoint):
                                used.append(joint)
                                cut_joint = True
                            else:
                                used.append(joint)
                                checked = 0
                            break
                    if if_break:
                        free = [i for i in free if not (i==link)]
##                        print free
                        break
                    
                checked += 1
                if checked==3:
                    free = [i for i in free if not (i==actual_link)]
                    del used[-1]
                    print 'usss', used
                    joint = used[-1]
                    checked = 0
                    if len(used)>1:
                        actualt_link = [used[-2],used[-1]]
                    if not free:
                        possible_links = [i for i in possible_links if not i==actual_link]
                        free = possible_links
                if not possible_links:
                    check += 1
                    used = []
                    break
            
            check += 1
            print 'used1', used
            if not isinstance(self.elements[joint-1], SuperFixedJoint):
                used = used[used.index(joint)::]
            cut = [i for i in used if self.elements[i-1].cut_joint]

            if cut and not used.index(cut[0])==0 and not used.index(cut[0])==len(used)-1:
                cut_joints.append([used[used.index(cut[0])-1], used[used.index(cut[0])], used[used.index(cut[0])+1]])
            elif cut and used.index(cut[0])==0:
                cut_joints.append([used[-1], used[0], used[1]])
            elif cut:
                cut_joints.append([used[-2], used[-1], used[0]])
            else:
                if not isinstance(self.elements[joint-1], SuperFixedJoint):
                    used.append(used[0])  
                if len(used) & 1:
                    cut = (len(used)-1)/2
                else:
                    cut = len(used)/2-1
                j = -1
                
                for i in range(0,cut+1):
                    if not self.elements[used[cut+i]-1].active:
                        j = cut+i
                    elif not self.elements[used[cut-i]-1].active:
                        j = cut-i
                    if not j==-1 and not isinstance(self.elements[j-1], SuperFixedJoint):
                        if not i == cut or j==len(used)-2:
                            cut_joints.append([used[j-1], used[j], used[j+1]])
                        elif j==0:
                            cut_joints.append([used[-2], used[0], used[1]])
                        else:
                            cut_joints.append([used[j-1], used[j], used[1]]) 
                        break

        print 'cut', cut_joints
        return cut_joints

    def DefineAngle(self, u,s1,s2):
        s1 /= norm(s1)
        s2 /= norm(s2)
        u /= norm(u)
        s1 = multiply(u.dot(s1),s1)
        s2 = multiply(u.dot(s2),s2)
        w1 = subtract(u,s1)
        w2 = subtract(u,s2)
        w1 /= norm(w1)
        w2 /= norm(w2)
        return atan2(norm(cross(w1,w2)),dot(w1,w2))

    def DefineDistance(self, u0, u, s10, s1, s20, s2):
        check = u0-s10
        
        t1 = (s1[0]*check[1]-s1[1]*check[0])/(s1[0]*u[1]-s1[1]*u[0])
        t2 = (s2[0]*check[1]-s2[1]*check[0])/(s2[0]*u[1]-s2[1]*u[0])

        return norm(t1,t2)

    def CommonNormal(self, z1, z2):
        pass    
        

    def FindKey(self, links, branches):
        key = -1
        for branch in branches:
            for link in links:
                if link[0] in branch:
                    return link[0]
                elif link[1] in branch:
                    return link[1]
        return key        

    def FindStart(self, links, branches):
        i = [i[0] for i in links if i[0] and isinstance(self.elements[i[0]-1], SuperFixedJoint) and not i[1]]
        if len(i):
            if branches:
                for branch in branches:
                    for j in i:
                        if not j in branch:
                            return j
            else:
                return i[0]
        i = [i[0] for i in links if i[0] and isinstance(self.elements[i[0]-1], SuperFixedJoint)]
        if len(i):
            if branches:
                for branch in branches:
                    for j in i:
                        if not j in branch:
                            return j
            else:
                return i[0]
        i = [i[1] for i in links if i[1] and isinstance(self.elements[i[1]-1], SuperFixedJoint)]
        if len(i):
            if branches:
                for branch in branches:
                    for j in i:
                        if not j in branch:
                            return j
            else:
                return i[0]
        i = [i[1] for i in links if not i[1]]
        if len(i):
            if branches:
                for branch in branches:
                    for j in i:
                        if not j in branch:
                            return j
            else:
                return i[0]
        
        return -1

    def GetBranch(self, key, links, used, joints, fixed, cut_joints):
        branch = []
        check = True
        branch.append(key)
        while check:
            check = False
            if_break = False
            for link in links:
                for i in range(0,2):
                    if link[i]==key and (len(branch)<2 or (not ([branch[-2],key,link[i-1]] in cut_joints) and not ([key,link[i-1],branch[-2]] in cut_joints))):
                        branch.append(link[i-1])
                        key = link[i-1]
                        check = True
                        if_break = True
                        remove = link
                        used.append(remove)
                        if not key in joints and not isinstance(self.elements[key-1], SuperFixedJoint) and not key==0:
                            joints.append(key)
                        elif not key in fixed and (isinstance(self.elements[key-1], SuperFixedJoint) or key==0):
                            fixed.append(key)
                        break
                if if_break:
                    links = [i for i in links if not i==remove]
                    break
        return  branch, links, used, joints, fixed

    def ActivateJoint(self, my_buffer):
        for min_d, max_d, name in my_buffer:
            if len(name)==2:
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

    def AddAncestor(self, my_buffer):
        for a, b, name in my_buffer:
            if not isinstance(self.elements[name[0]-1],Point) or not name[0]:
                if not name[0]:
                    self.elements[self.parent.data.FlagGet('ACTIVE_JOINT')-1].anc_pos.append([0,0,0])
                else:
                    self.elements[self.parent.data.FlagGet('ACTIVE_JOINT')-1].anc_pos.append(self.elements[name[0]-1].T[3,0:3])
                if not [self.parent.data.FlagGet('ACTIVE_JOINT'),name[0]] in self.links:
                    self.links.append([self.parent.data.FlagGet('ACTIVE_JOINT'),name[0]])
                self.parent.data.FlagReset('ADD_ANC')
                print self.links
                break

    def RemAncestor(self, my_buffer):
        for a, b, name in my_buffer:
            if not isinstance(self.elements[name[0]-1],Point):
                self.links=[i for i in self.links if not (i==[self.parent.data.FlagGet('ACTIVE_JOINT'),name[0]] or i==[name[0],self.parent.data.FlagGet('ACTIVE_JOINT')])]

                if name[0]:
                    self.elements[self.parent.data.FlagGet('ACTIVE_JOINT')-1].anc_pos = [
                        i for i in self.elements[self.parent.data.FlagGet('ACTIVE_JOINT')-1].anc_pos if not all(i==self.elements[name[0]-1].T[3,0:3])]   
                else:
                    self.elements[self.parent.data.FlagGet('ACTIVE_JOINT')-1].anc_pos = [
                        i for i in self.elements[self.parent.data.FlagGet('ACTIVE_JOINT')-1].anc_pos if not all(i==[0,0,0])]
                if self.parent.data.FlagGet('ACTIVE_JOINT'):
                    self.elements[name[0]-1].anc_pos = [
                        i for i in self.elements[name[0]-1].anc_pos if not all(i==self.elements[self.parent.data.FlagGet('ACTIVE_JOINT')-1].T[3,0:3])]
                else:
                    self.elements[name[0]-1].anc_pos = [
                        i for i in self.elements[name[0]-1].anc_pos if not all(i==[0,0,0])]
                self.parent.data.FlagReset('REM_ANC')
                print self.links
                break
                        

    def OnDelete(self, my_buffer):
        for a, b, name in my_buffer:
            if name and name[0]:
                if not name[0]==1:
                    for element in self.elements:
                        element.anc_pos = [i if not all(i==self.elements[name[0]-1].T[3,0:3]) else self.elements[name[0]-2].T[3,0:3] for i in element.anc_pos ]
                        element.anc_pos = [i for i in element.anc_pos if not all(i==element.T[3,0:3])]
                    self.links = [i if not i[0]==name[0] or
                                  [self.elements[name[0]-2].my_id, i[1]] in self.links or
                                  [i[1], self.elements[name[0]-2].my_id] in self.links else
                                  [self.elements[name[0]-2].my_id, i[1]] for i in self.links]
                    self.links = [i if not i[1]==name[0] or
                                  [self.elements[name[0]-2].my_id, i[0]] in self.links or
                                  [i[0], self.elements[name[0]-2].my_id] in self.links else
                                  [i[0], self.elements[name[0]-2].my_id] for i in self.links]
                else:
                    for element in self.elements:
                        element.anc_pos = [i if not all(i==self.elements[name[0]-1].T[3,0:3]) else [0,0,0] for i in element.anc_pos ]
                        element.anc_pos = [i for i in element.anc_pos if not all(i==element.T[3,0:3])]
                    self.links = [i if not i[0]==1 or
                                  [0, i[1]] in self.links or
                                  [i[1], 0] in self.links else
                                  [0, i[1]] for i in self.links]
                    self.links = [i if not i[1]==1 or
                                  [i[0], 0] in self.links or
                                  [0, i[0]] in self.links else
                                  [i[0], 0] for i in self.links]
                    
                self.links = [i for i in self.links if not (i[0]==name[0] or i[1]==name[0] or i[0]==i[1])]
                    

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
                print self.links
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
                        print 'plane2'
                        print self.plane
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
            vect1 = inv(self.elements[self.plane[1][0]-1].T[0:3,0:3]).dot([1,0,0])
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
                vect.append(inv(self.elements[self.plane[i][0]-1].T[0:3,0:3]).dot([1,0,0]))
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
            print 's', s
        else:
            s = 0
        print s
        print 'var1', norm(check)
        print 'var2', (vect[1][0]*vect[0][1]-vect[1][1]*vect[0][0])
        if norm(cross(vect[0],vect[1]))<0.01 or abs(s) > 0.2:
            print 'Cannot create the plane, line to not intersect'
        else:
            normal = cross(vect[0],vect[1])
            normal /= norm(normal)
            self.CreatePlane(normal,point[0], vect[0])
        self.parent.data.FlagReset('PLANE2')
        del self.plane[:]

    def CreatePlane(self, normal, point, line):
        print 'Creating plane'
            
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
##        T3 = T
##        T3[0:3,0:3] = self.EulerTransformation(pi, [0,1,0]).dot(T[0:3,0:3])
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
        for element in self.elements:
##            print element
            if isinstance(element, JointObject):
##                print 'joint'
                element.draw_joint()     
        
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
                self.elements.append(SuperFixedJoint(0, my_id=self.my_id ,T=T))
            elif my_type=='PRISMATIC':
                self.elements.append(SuperPrismaticJoint(0, my_id=self.my_id, T=T))
            elif my_type=='REVOLUTE':
                self.elements.append(SuperRevoluteJoint(0, my_id=self.my_id, T=T))
            self.elements[-1].set_length(0.5)
            self.elements[-1].show_frame = False
            if not len(self.elements)==1:    
                self.elements[-1].anc_pos.append(self.elements[-2].T[3,0:3])
            else:
                self.elements[-1].anc_pos.append([0,0,0])
            self.links.append([self.my_id,len(self.elements)-1])
            self.elements[-1].show_frame = True
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
