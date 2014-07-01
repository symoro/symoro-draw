#!/usr/bin/env python
# -*- coding: utf-8 -*-


import OpenGL.GL as gL
import OpenGL.GLU as gLu


from numpy import degrees, identity, array

from primitives import Primitives


class Frame(object):
    def __init__(self, index=0, T=identity(4), show_frame=True, my_id=0):
        self.children = []
        self.T = T
        self.show_frame = show_frame
        self.index = index
        self.points = [[0,0,0],[0,0,0]]
        self.my_id = my_id
        self.named = False
        self.anc_pos = [0,0,0]
##        if named:
##            gL.glPushName(self.my_id)

    def draw_frame(self):
        if self.show_frame:
            if not self.named:
                gL.glPushName(self.my_id)
                self.named = True

            gL.glPushMatrix()
            gL.glLoadName(self.my_id)    
            gL.glMultMatrixf(self.T)
            gL.glColor3f(1, 0, 0)
            gL.glPushName(1)
            self.draw_arrow()
            gL.glPopName()
            gL.glRotatef(90, 0, 0, 1)
            gL.glColor3f(0, 1, 0)
            gL.glPushName(2)
            self.draw_arrow()
            gL.glPopName()
            gL.glRotatef(-90, 0, 1, 0)
            gL.glColor3f(0, 0, 1)
            gL.glPushName(3)
            self.draw_arrow()
            gL.glPopName()
            gL.glPopMatrix()
            gL.glPopName()
            gL.glColor3f(1., 1, 1.)
            gL.glBegin(gL.GL_LINES)
            gL.glVertex3f(self.T[3][0], self.T[3][1], self.T[3][2])
            gL.glVertex3f(self.anc_pos[0], self.anc_pos[1], self.anc_pos[2])
            gL.glEnd()

    


    def draw_arrow(self):
        gL.glVertexPointer(3, gL.GL_FLOAT, 0, self.arr_vertices)
        gL.glNormalPointer(gL.GL_FLOAT, 0, self.arr_normals)
        gL.glDrawElements(gL.GL_TRIANGLES, len(self.arr_indices),
                          gL.GL_UNSIGNED_INT, self.arr_indices)

    def set_show_frame(self, show=True):
        self.show_frame = show

    def add_child(self, child):
        self.children.append(child)
        
        
    def draw_frames(self):
        gL.glPushMatrix()
        gL.glMultMatrixf(self.T)
        self.draw_frame()
        for child in self.children:
            child.draw_frames()
        gL.glPopMatrix()

    def draw(self):
        gL.glPushMatrix()
        gL.glMultMatrixf(self.T)
        for child in self.children:
            child.draw()
        gL.glPopMatrix()

    def __str__(self):
        return '{0} Children: {1}'.format(self.index, self.children)

    def set_length(self, new_length):
        self.arr_vertices, self.arr_indices, self.arr_normals = \
            Primitives.arr_array(new_length)

    


class JointObject(Frame):

    def __init__(self, index, theta=0., r=0., alpha=0., d=0., gamma=0., b=0., my_id = 0, T = identity(4)):
        super(JointObject, self).__init__(index)
        self.theta = theta
        self.r = r
        self.alpha = alpha
        self.d = d
        self.gamma = gamma
        self.b = b
        self.shift = 0.
        self.init_length = 0.
        
        self.named = False
        self.T = T
        self.my_id = my_id
        self.vxaxis = [0,0,0]
        self.pxaxis = [0,0,0]
        self.anc_pos = []
        self.active = False
        self.cut_joint = False
        self.color_j = [1,1,1]
        self.color_l = [1,1,1]
        self.show_joint = True

    def draw_rod(self, length):
        gL.glPushMatrix()
##        gL.glMultMatrixf(array([[1., 0., 0., 0.], [0., 1., 0., 0.],
##                                [0., 0., length, 0.], [0., 0., 0., 1.]]))
        gL.glMultMatrixf(self.T)
        gL.glColor3f(0.8, 0.51, 0.25)
        gL.glVertexPointer(3, gL.GL_FLOAT, 0, self.rod_vertices)
        gL.glNormalPointer(gL.GL_FLOAT, 0, self.rod_normals)
        gL.glDrawElements(gL.GL_TRIANGLES, len(self.rod_indices),
                          gL.GL_UNSIGNED_INT, self.rod_indices)
        gL.glPopMatrix()

    def draw_frames(self):
               
        gL.glPushMatrix()
        gL.glLoadIdentity()
        gL.glRotatef(degrees(self.gamma), 0, 0, 1)
        gL.glTranslatef(0, 0, self.b)
        gL.glRotatef(degrees(self.alpha), 1, 0, 0)
        gL.glTranslatef(self.d, 0, 0)
        gL.glRotatef(degrees(self.theta), 0, 0, 1)
        gL.glTranslatef(0, 0, self.r)
        self.draw_frame()
        for child in self.children:
            child.draw_frames()
        gL.glPopMatrix()

    def draw(self):
        gL.glPushMatrix()
        if self.b:
            self.draw_rod(self.b)
            gL.glTranslatef(0, 0, self.b)
        gL.glRotatef(degrees(self.gamma), 0, 0, 1)
        if self.d:
            gL.glPushMatrix()
            gL.glRotatef(90, 0, 1, 0)
            self.draw_rod(self.d)
            gL.glPopMatrix()
            gL.glTranslatef(self.d, 0, 0)
        gL.glRotatef(degrees(self.alpha), 1, 0, 0)
        if self.r:
            self.draw_rod(self.r)
            gL.glTranslatef(0, 0, self.r)
        gL.glRotatef(degrees(self.theta), 0, 0, 1)
        if self.shift:
            gL.glPushMatrix()
            shift = self.shift*self.length
            self.draw_rod(shift)
            gL.glTranslatef(0, 0, shift)
            self.draw_joint()
            gL.glPopMatrix()
        else:
            self.draw_joint()
        for child in self.children:
            child.draw()
        gL.glPopMatrix()

    def set_length(self, new_length):
        if not self.init_length:
            self.rod_vertices, self.rod_indices, self.rod_normals = \
                Primitives.rod_array(new_length)
            self.init_length = new_length
        self.length = new_length
        super(JointObject, self).set_length(new_length)


    def draw_frame(self):
            gL.glColor3f(1, 0, 0)
            gL.glPushName(1)
            self.draw_arrow()
            gL.glPopName()
            gL.glRotatef(90, 0, 0, 1)
            gL.glColor3f(0, 1, 0)
            gL.glPushName(2)
            self.draw_arrow()
            gL.glPopName()
            gL.glRotatef(-90, 0, 1, 0)
            gL.glColor3f(0, 0, 1)
            gL.glPushName(3)
            self.draw_arrow()
            gL.glPopName() 

class RevoluteJoint(JointObject):

    def __init__(self, *args, **kwargs):
        super(RevoluteJoint, self).__init__(*args, **kwargs)
        self.q_init = self.theta
        self.color_j = [1,1,0]

    def draw_joint(self):
        gL.glColor3f(self.color_j[0], self.color_j[1], self.color_j[2])
        gL.glVertexPointer(3, gL.GL_FLOAT, 0, self.cyl_vertices)
        gL.glNormalPointer(gL.GL_FLOAT, 0, self.cyl_normals)
        gL.glDrawElements(gL.GL_TRIANGLES, len(self.cyl_indices),
                          gL.GL_UNSIGNED_INT, self.cyl_indices)

    @property
    def q(self):
        return self.theta

    @q.setter
    def q(self, theta):
        self.theta = theta

    def set_length(self, new_length):
        self.cyl_vertices, self.cyl_indices, self.cyl_normals = \
            Primitives.cyl_array(new_length)
        super(RevoluteJoint, self).set_length(new_length)


class PrismaticJoint(JointObject):

    def __init__(self, *args, **kwargs):
        super(PrismaticJoint, self).__init__(*args, **kwargs)
        self.q_init = self.r
        self.color_j = [1,0.6,0]
        
    def draw_joint(self):
        gL.glColor3f(self.color_j[0], self.color_j[1], self.color_j[2])
        gL.glVertexPointer(3, gL.GL_FLOAT, 0, self.box_vertices)
        gL.glNormalPointer(gL.GL_FLOAT, 0, self.box_normals)
        gL.glDrawArrays(gL.GL_QUADS, 0, 24)


    @property
    def q(self):
        return self.r

    @q.setter
    def q(self, r):
        self.r = r

    def set_length(self, new_length):
        self.box_vertices, self.box_normals = Primitives.box_array(new_length)
        super(PrismaticJoint, self).set_length(new_length)

    def draw(self):
        gL.glPushMatrix()
        if self.b:
            self.draw_rod(self.b)
            gL.glTranslatef(0, 0, self.b)
        gL.glRotatef(degrees(self.gamma), 0, 0, 1)
        if self.d:
            gL.glPushMatrix()
            gL.glRotatef(90, 0, 1, 0)
            self.draw_rod(self.d)
            gL.glPopMatrix()
            gL.glTranslatef(self.d, 0, 0)
        gL.glRotatef(degrees(self.alpha), 1, 0, 0)
        if self.shift:
            gL.glPushMatrix()
            shift = self.shift*self.length
            self.draw_rod(shift)
            gL.glTranslatef(0, 0, shift)
            self.draw_joint()
            gL.glPopMatrix()
        else:
            self.draw_joint()
        if self.r:
            self.draw_rod(self.r)
            gL.glTranslatef(0, 0, self.r)
        gL.glRotatef(degrees(self.theta), 0, 0, 1)
        for child in self.children:
            child.draw()
        gL.glPopMatrix()



class FixedJoint(JointObject):

    def __init__(self, *args, **kwargs):
        super(FixedJoint, self).__init__(*args, **kwargs)
        self.color_j = [1,0,1]

    def draw_joint(self):
        gL.glColor3f(self.color_j[0], self.color_j[1], self.color_j[2])
        gL.glVertexPointer(3, gL.GL_FLOAT, 0, self.sph_vertices)
        gL.glNormalPointer(gL.GL_FLOAT, 0, self.sph_normals)
        gL.glDrawElements(gL.GL_TRIANGLES, len(self.sph_indices),
                          gL.GL_UNSIGNED_INT, self.sph_indices)

    def set_length(self, new_length):
        self.sph_vertices, self.sph_indices, self.sph_normals = \
            Primitives.sph_array(new_length)
        super(FixedJoint, self).set_length(new_length)

class SuperRevoluteJoint(RevoluteJoint):
    def __init__(self, *args, **kwargs):
        super(SuperRevoluteJoint, self).__init__(*args, **kwargs)

    def draw_joint(self):
        if not self.named:
            gL.glPushName(self.my_id)
            self.named = True
            
        gL.glLoadName(self.my_id)
        gL.glPushMatrix()
        gL.glMultMatrixf(self.T)
        
        if self.show_joint: 
            
            gL.glColor3f(self.color_j[0], self.color_j[1], self.color_j[2])
            gL.glPushName(4)
            self.draw_arrow()
            gL.glPopName()
##            gL.glRotatef(90,0,1,0)
            gL.glPushName(0)
            super(SuperRevoluteJoint, self).draw_joint()
            gL.glPopName()
        if self.show_frame:
            self.draw_frame()
            
        gL.glPopMatrix()
        gL.glPopName()
        gL.glColor3f(self.color_l[0], self.color_l[1], self.color_l[2])
        for link in self.anc_pos:
            gL.glBegin(gL.GL_LINES)
            gL.glVertex3f(self.T[3][0], self.T[3][1], self.T[3][2])
            gL.glVertex3f(link[0], link[1], link[2])
            gL.glEnd()

class SuperPrismaticJoint(PrismaticJoint):
    def __init__(self, *args, **kwargs):
        super(SuperPrismaticJoint, self).__init__(*args, **kwargs)


    def draw_joint(self):
        if not self.named:
            gL.glPushName(self.my_id)
            self.named = True
            
        gL.glLoadName(self.my_id)
        gL.glPushMatrix()
        gL.glMultMatrixf(self.T)
        
        if self.show_joint: 
            gL.glColor3f(self.color_j[0], self.color_j[1], self.color_j[2])
            gL.glPushName(4)
            self.draw_arrow()
            gL.glPopName()
##            gL.glRotatef(90,0,1,0)
            gL.glPushName(0)
            super(SuperPrismaticJoint, self).draw_joint()
            gL.glPopName()
        if self.show_frame:
            self.draw_frame()
            
        gL.glPopMatrix()
        gL.glPopName()
        gL.glColor3f(self.color_l[0], self.color_l[1], self.color_l[2])
        for link in self.anc_pos:
            gL.glBegin(gL.GL_LINES)
            gL.glVertex3f(self.T[3][0], self.T[3][1], self.T[3][2])
            gL.glVertex3f(link[0], link[1], link[2])
            gL.glEnd()


class SuperFixedJoint(FixedJoint):
    def __init__(self, *args, **kwargs):
        super(SuperFixedJoint, self).__init__(*args, **kwargs)

    def draw_joint(self):
        if not self.named:
            gL.glPushName(self.my_id)
            self.named = True

        gL.glLoadName(self.my_id)
        gL.glPushMatrix()
        gL.glMultMatrixf(self.T)
        if self.show_joint:
            gL.glPushName(0)
            super(SuperFixedJoint, self).draw_joint()
            gL.glPopName()
        if self.show_frame:
            self.draw_frame()

        gL.glPopMatrix()
        gL.glPopName()
        gL.glColor3f(self.color_l[0], self.color_l[1], self.color_l[2])
        for link in self.anc_pos:
            gL.glBegin(gL.GL_LINES)
            gL.glVertex3f(self.T[3][0], self.T[3][1], self.T[3][2])
            gL.glVertex3f(link[0], link[1], link[2])
            gL.glEnd()

    

class Point(FixedJoint):
    def __init__(self, pos, my_id, *args):
        super(FixedJoint, self).__init__(*args)
        self.pos = pos
        self.named = False
        self.my_id = my_id 

    def draw_joint(self):
        if not self.named:
            gL.glPushName(self.my_id)
            self.named = True
            
        gL.glPushMatrix()
        gL.glTranslatef(self.pos[0],self.pos[1],self.pos[2],0)
        gL.glColor3f(1., 1., 0.)
        super(Point, self).draw_joint()
        gL.glPopMatrix()
        gL.glPopName()

class Line(FixedJoint):
    def __init__(self, pos, my_id, *args):
        super(FixedJoint, self).__init__(*args)
        self.pos = pos
        self.named = False
        self.my_id = my_id 

##    def draw_joint(self):
##        if not self.named:
##            gL.glPushName(self.my_id)
##            self.named = True
##            
##        gL.glPushMatrix()
##        gL.glTranslatef(self.pos[0],self.pos[1],self.pos[2],0)
##        gL.glColor3f(1., 1., 0.)
##        super(Point, self).draw_joint()
##        gL.glPopMatrix()
##        gL.glPopName()        
        


