import wx

class data():
    '''This Class keep informations identifying the widgets'''
    
    def __init__(self):
        self.widgets = {}
        self.flags = {}

##      Widgets Data
        #GUI
        self.widgets['MAIN'] = {'w_type':'sizer',
                                'parent':None,
                                'position':0,
                                'active':True,
                                'orientation':wx.HORIZONTAL
                                }
        #Canvas
        self.widgets['CANVAS'] = {'w_type':'canvas',
                                    'position':1,
                                    'parent':'PANEL_SIZE_V'
                                    }
        #PANEL TOP ELEMENTS
        #Joints
        self.widgets['ON_JOINTS'] = {'w_type':'static_sizer',
                                     'label':'Joints',
                                     'parent':'GRID',
                                     'horizontal':0,
                                     'vertical':0,
                                     'active':True,
                                     'panel':'PANEL_TOP',
                                     'orientation':wx.HORIZONTAL
                                    }
        self.widgets['ON_REVOLUTE'] = {'w_type':'button',
                                       'label':'Revoulte',
                                       'parent':'ON_JOINTS',
                                       'position':0,
                                       'panel':'PANEL_TOP',
                                       'callback':'OnRevolute'
                                       }
        self.widgets['ON_PRISMATIC'] = {'w_type':'button',
                                        'label':'Prismatic',
                                        'parent':'ON_JOINTS',
                                        'position':1,
                                        'panel':'PANEL_TOP',
                                        'callback':'OnPrismatic'
                                        }
        self.widgets['ON_FIXED'] = {'w_type':'button',
                                    'label':'Fixed',
                                    'parent':'ON_JOINTS',
                                    'panel':'PANEL_TOP',
                                    'position':2,
                                    'callback':'OnFixed'
                                    }
        
        #Planes
        self.widgets['ON_PLANES'] = {'w_type':'static_sizer',
                                     'label':'Planes',
                                     'panel':'PANEL_TOP',
                                     'parent':'GRID',
                                     'horizontal':1,
                                     'vertical':0,
                                     'active':True,
                                     'orientation':wx.HORIZONTAL
                                    }
        self.widgets['ON_PLANE3'] = {'w_type':'button',
                                    'label':'3 Points',
                                    'parent':'ON_PLANES',
                                    'position':2,
                                    'panel':'PANEL_TOP',
                                    'callback':'OnPlane3'
                                    }
        self.widgets['ON_PLANE2'] = {'w_type':'button',
                                    'label':'2 lines',
                                    'parent':'ON_PLANES',
                                     'position':1,
                                     'panel':'PANEL_TOP',
                                    'callback':'OnPlane2'
                                     
                                    }
        self.widgets['ON_PLANE1'] = {'w_type':'button',
                                    'label':'Point Line',
                                    'parent':'ON_PLANES',
                                     'position':0,
                                     'panel':'PANEL_TOP',
                                    'callback':'OnPlane1'
                                    }

        #Panels
        self.widgets['PANEL_V'] = {'w_type':'panel',
                                    'parent':'MAIN',
                                     'position':0
                                    }
        self.widgets['PANEL_SIZE_V'] = {'w_type':'sizer',
                                'parent':'PANEL_V',
                                'position':0,
                                'orientation':wx.VERTICAL
                                    }
        
        self.widgets['PANEL_TOP'] = {'w_type':'panel',
                                    'parent':'PANEL_SIZE_V',
                                     'position':0
                                    }
        self.widgets['PANEL_TOP_SIZER'] = {'w_type':'sizer',
                                'parent':'PANEL_TOP',
                                'position':0,
                                'orientation':wx.HORIZONTAL
                                    }
        self.widgets['GRID'] = {'w_type':'grid',
                                'parent':'PANEL_TOP_SIZER',
                                'position':0,
                                'horizontal':10,
                                'vertical':10
                                    }
        
        self.widgets['PANEL_SIDE'] = {'w_type':'panel',
                                    'parent':'MAIN',
                                     'position':1
                                      }
        self.widgets['PANEL_SIDE_SIZER'] = {'w_type':'sizer',
                                'parent':'PANEL_SIDE',
                                'position':0,
                                'orientation':wx.VERTICAL
                                    }
        self.widgets['GRID_SIDE'] = {'w_type':'grid',
                                'parent':'PANEL_SIDE_SIZER',
                                'position':0,
                                'horizontal':1,
                                'vertical':10,
                                'border':5,
                                'flag':wx.RIGHT
                                    }
        self.widgets['PANEL_JOINT_SIZER'] = {'w_type':'sizer',
                                'parent':'GRID_SIDE',
                                'horizontal':0,
                                'vertical':3,
                                'orientation':wx.VERTICAL
                                    }
        #Panel Side Elements       
        self.widgets['ON_DELETE'] = {'w_type':'button',
                                    'label':'Delete',
                                    'parent':'GRID_SIDE',
                                    'horizontal':0,
                                    'vertical':2,
                                    'panel':'PANEL_SIDE',
                                    'callback':'OnDelete'
                                    }
        self.widgets['ON_CHANGE_ANC'] = {'w_type':'button',
                                    'label':'Ancestor',
                                    'parent':'PANEL_JOINT_SIZER',
                                    'position':0,
                                    'panel':'PANEL_SIDE',
                                    'callback':'OnChangeAncestor',
                                    'checked':False,
                                    'active':False
                                    }
        self.widgets['ON_ACTIVE'] = {'w_type':'check_box',
                                    'label':'Active',
                                    'parent':'PANEL_JOINT_SIZER',
                                    'position':1,
                                    'panel':'PANEL_SIDE',
                                    'checked':False,
                                    'active':False
                                    }
        self.widgets['ON_CUT_JOINT'] = {'w_type':'check_box',
                                    'label':'Cut Joint',
                                    'parent':'PANEL_JOINT_SIZER',
                                    'position':2,
                                    'panel':'PANEL_SIDE',
                                    'checked':False,
                                    'active':False
                                    }
        


        #References
        self.widgets['ON_LINE'] = {'w_type':'button',
                                    'label':'Line',
                                    'parent':'ON_REFERENCES',
                                    'position':2, 
                                    'callback':'OnRefLine',
                                   'panel':'PANEL_TOP'
                                    }
        self.widgets['ON_POINT'] = {'w_type':'button',
                                    'label':'Point',
                                    'parent':'ON_REFERENCES',
                                     'position':1,
                                    'panel':'PANEL_TOP',
                                    'callback':'OnRefPoint'
                                    }
        self.widgets['ON_REFERENCES'] = {'w_type':'static_sizer',
                                         'label':'References',
                                     'parent':'GRID',
                                     'horizontal':2,
                                     'vertical':0,
                                      'panel':'PANEL_TOP',   
                                     'active':True,
                                     'orientation':wx.HORIZONTAL
                                    }
##        self.widgets['TEXT_REFERENCES'] = {'w_type':'static_text',
##                                           'label':'References',
##                                     'parent':'GRID',
##                                     'horizontal':4,
##                                     'vertical':0,
##                                    'panel':'PANEL',
##                                     'active':True
##                                    }
                                     
        #MENU
        self.widgets['MENU_BAR'] = {'w_type':'menu_bar',
                                'parent':None,
                                'position':0
                                    }
        #File
        self.widgets['FILE'] = {'w_type':'menu',
                                'parent':'MENU_BAR',
                                'label':'File',
                                'position':0,
                                'submenu':False
                                    }
        self.widgets['NEW'] = {'w_type':'menu_item',
                                'parent':'FILE',
                                'label':'New',
                                'id':wx.ID_NEW,
                                'position':0,
                               'callback':'OnNew'
                                    }
        self.widgets['EXPORT'] = {'w_type':'menu_item',
                                'parent':'FILE',
                                'label':'Export',
                                'position':1,
                               'callback':'OnExport'
                                    }
        self.widgets['EXIT'] = {'w_type':'menu_item',
                                'parent':'FILE',
                                'label':'New',
                                'id':wx.ID_CLOSE,
                                'position':2,
                               'callback':'OnClose'
                                    }
        #Draw
        self.widgets['DRAW'] = {'w_type':'menu',
                                'parent':'MENU_BAR',
                                'label':'Draw',
                                'position':1,
                                'submenu':False
                                    }
        self.widgets['JOINTS'] = {'w_type':'menu',
                                'parent':'DRAW',
                                'label':'Joints',
                                'position':0,
                                'submenu':True
                                    }
        self.widgets['PLANES'] = {'w_type':'menu',
                                'parent':'DRAW',
                                'label':'Planes',
                                'position':1,
                                'submenu':True
                                    }
        self.widgets['REFERENCES'] = {'w_type':'menu',
                                'parent':'DRAW',
                                'label':'Reference Object',
                                'position':2,
                                'submenu':True
                                    }
        self.widgets['J_PRISMATIC'] = {'w_type':'menu_item',
                                'parent':'JOINTS',
                                'label':'Prismatic',
                                'position':0,
                                'callback':'OnPrismatic'
                                    }
        self.widgets['J_REVOLUTE'] = {'w_type':'menu_item',
                                'parent':'JOINTS',
                                'label':'Revolute',
                                'position':1,
                                'callback':'OnRevolute'
                                    }
        self.widgets['J_FIXED'] = {'w_type':'menu_item',
                                'parent':'JOINTS',
                                'label':'Fixed',
                                'position':2,
                                'callback':'OnFixed'
                                    }
        self.widgets['P_1'] = {'w_type':'menu_item',
                                'parent':'PLANES',
                                'label':'Point and line',
                                'position':0,
                                'callback':'OnPlane1'
                                    }
        self.widgets['P_2'] = {'w_type':'menu_item',
                                'parent':'PLANES',
                                'label':'Two lines',
                                'position':1,
                                'callback':'OnPlane2'
                                }
        self.widgets['P_3'] = {'w_type':'menu_item',
                                'parent':'PLANES',
                                'label':'Three points',
                                'position':2,
                                'callback':'OnPlane3'
                                }
        self.widgets['R_LINE'] = {'w_type':'menu_item',
                                'parent':'REFERENCES',
                                'label':'Line',
                                'position':0,
                                'callback':'OnRefLine'
                                }
        self.widgets['R_POINT'] = {'w_type':'menu_item',
                                'parent':'REFERENCES',
                                'label':'Point',
                                'position':1,
                                'callback':'OnRefPoint'
                                }
##        #Toolbars
##        self.widgets['TOOLBARS'] = {'w_type':'menu',
##                                'parent':'MENU_BAR',
##                                'label':'Toolbars',
##                                'position':3,
##                                'submenu':False
##                                    }
##        self.widgets['T_DRAW'] = {'w_type':'menu_item',
##                                'parent':'TOOLBARS',
##                                'label':'Draw',
##                                'position':0,
##                                'callback':'OnShowDraw'
##                                    }
##        self.widgets['T_VIEW'] = {'w_type':'menu_item',
##                                'parent':'TOOLBARS',
##                                'label':'View',
##                                'position':1,
##                                'callback':'OnShowView'
##                                    }
        #View
        self.widgets['VIEW'] = {'w_type':'menu',
                                'parent':'MENU_BAR',
                                'label':'View',
                                'position':2,
                                'submenu':False
                                    }
        self.widgets['FRONT'] = {'w_type':'menu_item',
                                'parent':'VIEW',
                                'label':'Front',
                                'position':0,
                                'callback':'OnFront'
                                }
        
        self.widgets['TOP'] = {'w_type':'menu_item',
                                'parent':'VIEW',
                                'label':'Top',
                                'position':2,
                                'callback':'OnTop'
                                }
        
        self.widgets['RIGHT'] = {'w_type':'menu_item',
                                'parent':'VIEW',
                                'label':'Right',
                                'position':4,
                                'callback':'OnRight'
                                }
        self.widgets['BACK'] = {'w_type':'menu_item',
                                'parent':'VIEW',
                                'label':'Back',
                                'position':1,
                                'callback':'OnBack'
                                }
        
        self.widgets['BOTTOM'] = {'w_type':'menu_item',
                                'parent':'VIEW',
                                'label':'Bottom',
                                'position':3,
                                'callback':'OnBottom'
                                }
        
        self.widgets['LEFT'] = {'w_type':'menu_item',
                                'parent':'VIEW',
                                'label':'Left',
                                'position':5,
                                'callback':'OnLeft'
                                }
        
        self.widgets['ISOMETRIC'] = {'w_type':'menu_item',
                                'parent':'VIEW',
                                'label':'Isometric',
                                'position':6,
                                'callback':'OnIsometric'
                                }
##        self.widgets['SEP1'] = {'w_type':'menu_separator',
##                                'parent':'VIEW',
##                                'position':7
##                                }
        
##        self.widgets['ZOOM'] = {'w_type':'menu_item',
##                                'parent':'VIEW',
##                                'label':'Zoom',
##                                'position':8,
##                                'callback':'OnZoom'
##                                }
##        
##        self.widgets['PAN'] = {'w_type':'menu_item',
##                                'parent':'VIEW',
##                                'label':'Pan',
##                                'position':9,
##                                'callback':'OnPan'
##                                }
##        self.widgets['ROTATE'] = {'w_type':'menu_item',
##                                'parent':'VIEW',
##                                'label':'Rotate',
##                                'position':10,
##                                'callback':'OnRotate'
##                                }

##      Flags data

        self.flags['PRISMATIC'] = [0, 'joint']
        self.flags['REVOLUTE'] = [0, 'joint']
        self.flags['FIXED'] = [0, 'joint']
        self.flags['REF_POINT'] = [0, 'ref']
        self.flags['REF_LINE'] = [0, 'ref']
        self.flags['PLANE1'] = [0, 'plane']
        self.flags['PLANE2'] = [0, 'plane']
        self.flags['PLANE3'] = [0, 'plane']
        self.flags['PICK'] = [1, 'mouse']
        self.flags['DELETE'] = [0, 'button']
        self.flags['CHANGE_ANC'] = [0, 'button']
        self.flags['ACTIVE_JOINT'] = [0, 'active']

##  Methods widgets

    def GetValue(self, name, key):
            return self.widgets[name][key]

    def GetWidget(self, name):
            return self.widgets[name]

    def SetValue(self, name, key, value):
            self.widgets[name][key] = value

    def GetList(self):
            self.widget = []
            for key in self.widgets:
                    self.widget.append(key)
            return self.widget

    def GetTypedList(self, key, value):
            my_list = self.GetList()
            typed = []
            for widget in my_list:
                    if self.GetValue(widget,key) == value:
                            typed.append(widget)
            return typed
        
    def SortPosition(self, value):
            my_list = self.GetList()
            typed = []
            output = []

            for widget in my_list:
                     if self.GetValue(widget,'parent') == value:
                            typed.append([widget, self.GetValue(widget,'position')])
            sort = sorted(typed, key=lambda position: position[1])

            for element in sort:
                    output.append(element[0])

            return output

    def CheckKey(self, name, key):
            for label in self.widgets[name]:
                    if label == key:
                             return True
            return False

        
##  Methods Flags
    def FlagSet(self, name, value):
        self.flags[name][0] = value

    def FlagGet(self, name):
        return self.flags[name][0]

    def FlagType(self, name):
        return self.flags[name][1]

    def FlagList(self, f_type):
        typed = []
        for key in self.flags:
            if self.FlagType(key) == f_type:
                typed.append(key)
        return typed
                            
    def FlagIncrement(self, name):
            self.FlagSet(name,self.FlagGet(name)+1)

    def FlagDecrement(self, name):
            self.FlagSet(name,self.FlagGet(name)-1)

    def FlagReset(self, name):
            self.FlagSet(name,0)

    def FlagsChange(self, f_type):
            for key in self.FlagList(f_type):
                if self.FlagGet(key):
                    self.FlagReset(key)



            