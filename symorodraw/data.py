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
##        self.widgets['ON_FIXED'] = {'w_type':'button',
##                                    'label':'Fixed',
##                                    'parent':'ON_JOINTS',
##                                    'panel':'PANEL_TOP',
##                                    'position':2,
##                                    'callback':'OnFixed'
##                                    }
        
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
                                    'label':'2 Lines',
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
        #Constrains
        self.widgets['ON_CONSTRAINS'] = {'w_type':'static_sizer',
                                     'label':'Constraints',
                                     'panel':'PANEL_TOP',
                                     'parent':'GRID',
                                     'horizontal':3,
                                     'vertical':0,
                                     'active':True,
                                     'orientation':wx.HORIZONTAL
                                    }
        self.widgets['ON_PARALLEL'] = {'w_type':'button',
                                    'label':'Parallel',
                                    'parent':'ON_CONSTRAINS',
                                    'position':0,
                                    'panel':'PANEL_TOP',
                                    'callback':'OnParallel'
                                    }
        self.widgets['ON_PERPENDICULAR'] = {'w_type':'button',
                                    'label':'Perpendicular',
                                    'parent':'ON_CONSTRAINS',
                                    'position':1,
                                    'panel':'PANEL_TOP',
                                    'callback':'OnPerpendicular'
                                    }
        self.widgets['ON_AT_ANGLE'] = {'w_type':'button',
                                    'label':'At angle',
                                    'parent':'ON_CONSTRAINS',
                                    'position':2,
                                    'panel':'PANEL_TOP',
                                    'callback':'OnAtAngle'
                                    }
        self.widgets['ON_AT_DISTANCE'] = {'w_type':'button',
                                    'label':'At Distance',
                                    'parent':'ON_CONSTRAINS',
                                    'position':3,
                                    'panel':'PANEL_TOP',
                                    'callback':'OnAtDistance'
                                    }
        #References
        self.widgets['ON_POINT'] = {'w_type':'button',
                                    'label':'Link',
                                    'parent':'ON_REFERENCES',
                                     'position':1,  
                                    'panel':'PANEL_TOP',
                                    'callback':'OnRefPoint'
                                    }
        self.widgets['ON_REFERENCES'] = {'w_type':'static_sizer',
                                         'label':'Links',
                                     'parent':'GRID',
                                     'horizontal':2,
                                     'vertical':0,
                                      'panel':'PANEL_TOP',   
                                     'active':True,
                                     'orientation':wx.HORIZONTAL
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
                                'vertical':6,
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
        self.widgets['ON_ANCESTORS'] = {'w_type':'static_sizer',
                                     'label':'Link',
                                     'panel':'PANEL_SIDE',
                                     'parent':'PANEL_JOINT_SIZER',
                                     'position':0,
                                     'active':False,
                                     'orientation':wx.VERTICAL
                                    }
        self.widgets['ON_ADD_ANC'] = {'w_type':'button',
                                    'label':'Add',
                                    'parent':'ON_ANCESTORS',
                                    'position':0,
                                    'panel':'PANEL_SIDE',
                                    'callback':'OnAddAncestor',
                                    'checked':False,
                                    'active':True
                                    }
        self.widgets['ON_REM_ANC'] = {'w_type':'button',
                                    'label':'Remove',
                                    'parent':'ON_ANCESTORS',
                                    'position':1,
                                    'panel':'PANEL_SIDE',
                                    'callback':'OnRemoveAncestor',
                                    'checked':False,
                                    'active':True
                                    }
        self.widgets['ON_PARAMETERS'] = {'w_type':'static_sizer',
                                     'label':'Parameters',
                                     'panel':'PANEL_SIDE',
                                     'parent':'PANEL_JOINT_SIZER',
                                     'position':4,
                                     'active':False,
                                     'orientation':wx.VERTICAL,
                                    'flag':wx.RIGHT
                                    }
        
        self.widgets['ON_PARAM_S_D'] = {'w_type':'sizer',
                                     'panel':'PANEL_SIDE',
                                     'parent':'ON_PARAMETERS',
                                     'position':2,
                                     'active':False,
                                     'orientation':wx.HORIZONTAL
                                    }
        self.widgets['TEXT_D'] = {'w_type':'static_text',
                                           'label':'d',
                                     'parent':'ON_PARAM_S_D',
                                     'position':0,
                                    'panel':'PANEL_SIDE',
                                     'active':True,
                                  'size':(20,-1)
                                    }
        
        self.widgets['ON_D'] = {'w_type':'float_spin',
                                 'parent':'ON_PARAM_S_D',
                                 'panel':'PANEL_SIDE',
                                 'callback':'OnD',
                                 'position':1,
                                 'min_val':None,
                                 'max_val':None,
                                 'increment':0.01,
                                 'size':(60,-1)
                                 }
        self.widgets['ON_PARAM_S_ALPHA'] = {'w_type':'sizer',
                                     'panel':'PANEL_SIDE',
                                     'parent':'ON_PARAMETERS',
                                     'position':3,
                                     'active':False,
                                     'orientation':wx.HORIZONTAL
                                    }
        self.widgets['TEXT_ALPHA'] = {'w_type':'static_text',
                                           'label':'al',
                                     'parent':'ON_PARAM_S_ALPHA',
                                     'position':0,
                                    'panel':'PANEL_SIDE',
                                     'active':False,
                                      'size':(20,-1)
                                    }
        
        self.widgets['ON_ALPHA'] = {'w_type':'float_spin',
                                 'parent':'ON_PARAM_S_ALPHA',
                                 'panel':'PANEL_SIDE',
                                 'callback':'OnAlpha',
                                 'position':1,
                                 'min_val':None,
                                 'max_val':None,
                                 'increment':0.01,
                                 'size':(60,-1)
                                 }
        
        self.widgets['ON_PARAM_S_THETA'] = {'w_type':'sizer',
                                     'panel':'PANEL_SIDE',
                                     'parent':'ON_PARAMETERS',
                                     'position':5,
                                     'active':False,
                                     'orientation':wx.HORIZONTAL
                                    }
        self.widgets['TEXT_THETA'] = {'w_type':'static_text',
                                           'label':'th',
                                     'parent':'ON_PARAM_S_THETA',
                                     'position':0,
                                    'panel':'PANEL_SIDE',
                                     'active':True,
                                      'size':(20,-1)
                                    }
        
        self.widgets['ON_THETA'] = {'w_type':'float_spin',
                                 'parent':'ON_PARAM_S_THETA',
                                 'panel':'PANEL_SIDE',
                                 'callback':'OnTheta',
                                 'position':1,
                                 'min_val':None,
                                 'max_val':None,
                                 'increment':0.01,
                                 'size':(60,-1)
                                 }
        
        self.widgets['ON_PARAM_S_R'] = {'w_type':'sizer',
                                     'panel':'PANEL_SIDE',
                                     'parent':'ON_PARAMETERS',
                                     'position':4,
                                     'active':False,
                                     'orientation':wx.HORIZONTAL
                                    }
        self.widgets['TEXT_R'] = {'w_type':'static_text',
                                           'label':'r',
                                     'parent':'ON_PARAM_S_R',
                                     'position':0,
                                    'panel':'PANEL_SIDE',
                                     'active':True,
                                  'size':(20,-1)
                                    }
        self.widgets['ON_R'] = {'w_type':'float_spin',
                                 'parent':'ON_PARAM_S_R',
                                 'panel':'PANEL_SIDE',
                                 'callback':'OnR',
                                 'position':1,
                                 'min_val':None,
                                 'max_val':None,
                                 'increment':0.01,
                                 'size':(60,-1)
                                 }
        self.widgets['ON_PARAM_S_GAMMA'] = {'w_type':'sizer',
                                     'panel':'PANEL_SIDE',
                                     'parent':'ON_PARAMETERS',
                                     'position':1,
                                     'active':False,
                                     'orientation':wx.HORIZONTAL
                                    }
        self.widgets['TEXT_GAMMA'] = {'w_type':'static_text',
                                           'label':'g',
                                     'parent':'ON_PARAM_S_GAMMA',
                                     'position':0,
                                    'panel':'PANEL_SIDE',
                                     'active':True,
                                      'size':(20,-1)
                                    }
        
        self.widgets['ON_GAMMA'] = {'w_type':'float_spin',
                                 'parent':'ON_PARAM_S_GAMMA',
                                 'panel':'PANEL_SIDE',
                                 'callback':'OnGamma',
                                 'position':1,
                                 'min_val':None,
                                 'max_val':None,
                                 'increment':0.01,
                                 'size':(60,-1)
                                 }
        self.widgets['ON_PARAM_S_B'] = {'w_type':'sizer',
                                     'panel':'PANEL_SIDE',
                                     'parent':'ON_PARAMETERS',
                                     'position':0,
                                     'active':False,
                                     'orientation':wx.HORIZONTAL
                                    }
        
        self.widgets['TEXT_B'] = {'w_type':'static_text',
                                           'label':'b',
                                     'parent':'ON_PARAM_S_B',
                                     'position':0,
                                    'panel':'PANEL_SIDE',
                                     'active':True,
                                  'size':(20,-1)
                                    }
        
        self.widgets['ON_B'] = {'w_type':'float_spin',
                                 'parent':'ON_PARAM_S_B',
                                 'panel':'PANEL_SIDE',
                                 'callback':'OnB',
                                 'position':1,
                                 'min_val':None,
                                 'max_val':None,
                                 'increment':0.01,
                                 'size':(60,-1)
                                 }
        
        
        self.widgets['ON_CHANGE_DIR'] = {'w_type':'button',
                                    'label':'Z Direction',
                                    'parent':'PANEL_JOINT_SIZER',
                                    'position':1,
                                    'panel':'PANEL_SIDE',
                                    'callback':'OnChangeZAxis',
                                    'active':False
                                    }
        self.widgets['ON_ACTIVE'] = {'w_type':'check_box',
                                    'label':'Active',
                                    'parent':'PANEL_JOINT_SIZER',
                                    'position':2,
                                    'panel':'PANEL_SIDE',
                                    'checked':False,
                                    'active':False,
                                    'callback':'OnActive'
                                    }
        self.widgets['ON_CUT_JOINT'] = {'w_type':'check_box',
                                    'label':'Cut Joint',
                                    'parent':'PANEL_JOINT_SIZER',
                                    'position':3,
                                    'panel':'PANEL_SIDE',
                                    'checked':False,
                                    'active':False,
                                    'callback':'OnCut'
                                    }
        self.widgets['ON_ANALYSIS'] = {'w_type':'static_sizer',
                                     'label':'Parmeters',
                                     'panel':'PANEL_SIDE',
                                     'parent':'GRID_SIDE',
                                     'horizontal':0,
                                     'vertical':4,
                                     'active':True,
                                     'orientation':wx.VERTICAL,
                                    'flag':wx.RIGHT
                                    }
        self.widgets['ON_DEFINE_D_H'] = {'w_type':'button',
                                    'label':'Define',
                                    'parent':'ON_ANALYSIS',
                                    'position':0,
                                    'panel':'PANEL_SIDE',
                                    'callback':'OnDefineD_H',
                                    'active':True
                                    }
        self.widgets['ON_CHECK_D_H'] = {'w_type':'button',
                                    'label':'Check',
                                    'parent':'ON_ANALYSIS',
                                    'position':1,
                                    'panel':'PANEL_SIDE',
                                    'callback':'OnCheckParameters',
                                    'active':True
                                    }
        self.widgets['ON_CONFIGURATION'] = {'w_type':'button',
                                    'label':'Configuration',
                                    'parent':'ON_ANALYSIS',
                                    'position':2,
                                    'panel':'PANEL_SIDE',
                                    'callback':'OnConfiguration',
                                    'active':True
                                    }
        self.widgets['ON_STRUCTURE'] = {'w_type':'button',
                                    'label':'Structure',
                                    'parent':'ON_ANALYSIS',
                                    'position':3,
                                    'panel':'PANEL_SIDE',
                                    'callback':'OnStructure',
                                    'active':True
                                    }
                                     
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
##        self.widgets['J_FIXED'] = {'w_type':'menu_item',
##                                'parent':'JOINTS',
##                                'label':'Fixed',
##                                'position':2,
##                                'callback':'OnFixed'
##                                    }
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
        self.flags['ADD_ANC'] = [0, 'button']
        self.flags['REM_ANC'] = [0, 'button']
        self.flags['ACTIVE_JOINT'] = [0, 'active']
        self.flags['ACTIVE_LINK'] = [0, 'active']
        self.flags['MODE'] = [0, 'mode'] # 0 -structure, 1-parameters
        self.flags['PARALLEL'] = [0, 'constraints']
        self.flags['PERPENDICULAR'] = [0, 'constraints']
        self.flags['AT_DISTANCE'] = [0, 'constraints']
        self.flags['AT_ANGLE'] = [0, 'constraints']
        self.flags['PARAMETERS'] = [0, 'initalization']

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



            
