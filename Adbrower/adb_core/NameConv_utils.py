import pymel.core as pm


# SIDES AND AXIS

mirrorableSideNameDico = {'L': 'R', 'R': 'L'}
valideSideNames = ['L', 'R', 'C', 'X']


NO_SIDE_PREFIX             = 'X'
MID_SIDE_PREFIX            = 'C'
LEFT_SIDE_PREFIX           = 'L'
RIGTH_SIDE_PREFIX          = 'R'


# ===================================================
#                FUNCTIONS UTILS
# ===================================================

def renameBasename(_transform, newName):
    """ Changed the basename while keeping the naming convention

    Arguments:
        _transform {object} -- [description]
        newName {String} -- New basename

    Returns:
        String -- new full name
    """
    if isinstance(_transform, list):
            transform = str(_transform[0])
    else:
        transform = str(_transform)

    for valid_side in valideSideNames:
        validator = transform.startswith('{}__'.format(valid_side))
        if validator:
             _basename = transform.split('__')[1]
             _side = transform.split('__')[0]
        else:
            name_conv_validator = len(transform.split('__'))
            if name_conv_validator == 3:
                _basename = transform.split('__')[1]
                _side = transform.split('__')[0]
                _suffix = transform.split('__')[-1]
            else:
                _basename = transform.split('__')[0]
                _side = ''
                _suffix = ''

    _newName = '{}__{}__{}'.format(_side, newName, _suffix)
    pm.rename(_transform, _newName)

    return _newName


def getSideFromPosition(_transform):
    """
    @param _transform. Get the side value of this Transform from is world position
    """

    if isinstance(_transform, list):
        transform = _transform[0]
    else:
        transform = pm.PyNode(_transform)

    worldPos = transform.getRotatePivot(space='world')
    if worldPos[0] > 0.0:
        _side = LEFT_SIDE_PREFIX

    elif worldPos[0] < 0.0:
        _side = RIGTH_SIDE_PREFIX

    else: 
        _side = MID_SIDE_PREFIX

    return _side


def getBasename(_transform):
    """
    Get the base Name of a transfrom.
    Name without Prefix or Suffix

    returns string
    """
    if isinstance(_transform, list):
        transform = str(_transform[0])
    else:
        transform = str(_transform)

    for valid_side in valideSideNames:
        validator = transform.startswith('{}__'.format(valid_side))
        if validator:
             _basename = transform.split('__')[1]
        else:
            name_conv_validator = len(transform.split('__'))
            if name_conv_validator == 3:
                _basename = transform.split('__')[1]
            else:
                _basename = transform.split('__')[0]

    return _basename


def getSideFromName(_transform):
    """
    @param _transform. Get the side value of this Transform
    """
    if isinstance(_transform, list):
        transform = str(_transform[0])
    else:
        transform = str(_transform)

    validations =  [transform.startswith('{}'.format(valid_side)) for valid_side in valideSideNames]

    for val, names in zip (validations, valideSideNames):
        if val == True:
            return names + '__'
    return ''


def getNameNoSuffix(_transform):
    """
    Get name without the suffix
    """
    if isinstance(_transform, list):
        transform = str(_transform[0])
    else:
        transform = str(_transform)

    nameSplit = transform.split('__')[:-1]
    if nameSplit is []:
        return transform
    else:
        shortName =  '__'.join(nameSplit)
        return shortName


def getSuffix(_transform):
    if isinstance(_transform, list):
            transform = str(_transform[0])
    else:
        transform = str(_transform)

    suffix = transform.split('__')[-1]
    return suffix


def getNameSpace(_name):
    """
    @param _name: (string)
    """
    nameSplit = _name.split(':')
    nameSpace = ''
    for elem in nameSplit[:-1]:
        nameSpace = nameSpace + elem + ':'

    if nameSpace == '':
        nameSpace = ':'

    return nameSpace


def getNameSpaceFreeName(_name):
    """
    @param _name: (string)
    """
    nameSplit = _name.split(':')
    return(nameSplit[-1])



# ===================================================

#               PREFIX AND SUFFIX

# ===================================================


# TRANSFORMS
MESH                          = 'MESH'
JOINT                         = 'JNT'
BIND_JOINT                    = 'SKN'
END_JOINT                     = 'END'
CTRL                          = 'CTRL'
GRP                           = 'GRP'
LOC                           = 'LOC'


# TAGS
TAG_GlOBAL_SCALE              = 'tag_global_scale'

TAG_LEG                       = 'tag_LEG'
TAG_ARM                       = 'tag_ARM'
TAG_SPINE                     = 'tag_SPINE'


#SUFFIX

SYSTEM                        = 'SYS'
NO_TOUCH                      = 'DO_NOT_TOUCH'
VISRULE                       = 'VISRULE'

PARENT_CONSTRAINT_SUFFIX      = 'PAC'
POINT_CONSTRAINT_SUFFIX       = 'POC'
ORIENT_CONSTRAINT_SUFFIX      = 'ORC'
AIM_CONSTRAINT_SUFFIX         = 'AIMC'

MID_SUFFIX                    = 'mid'
UP_SUFFIX                     = 'up'
DOWN_SUFFIX                   = 'down'

MIN_SUFFIX                    = 'min'
MAX_SUFFIX                    = 'max'

IK_SUFFIX                     = 'ik'
FK_SUFFIX                     = 'fk'
IK_FK_SUFFIX                  = 'ikFk'
SWITCH_SUFFIX                 = 'switch'

STRETCH_SUFFIX                = 'stretch'
SQUASH_SUFFIX                 = 'squash'


# NODES
SKINCLUSTER_SUFFIX            = 'SKCLS'
FOLL_SUFFIX                   = 'FOLL'
BLENDSHAPE_SUFFIX             = 'BLS'
WRAP_SUFFIX                   = 'WRP'
MULTIPLY_DIVIDE_SUFFIX        = 'MD'
REMAP_VALUE_SUFFIX            = 'RM'
REMAP_COLOR_SUFFIX            = 'RMC'
REVERSE_SUFFIX                = 'REV'
ADDLINEAR_SUFFIX              = 'ADDL'
MULTLINEAR_SUFFIX             = 'MULTL'
CONDITION_SUFFIX              = 'COND'
PLUS_MIN_AVER_SUFFIX          = 'PMA'
BLENDCOLOR_SUFFIX             = 'BC'
NETWORK                       = 'NETWORK'
IKHANDLE_SUFFIX               = 'IKHDL'
CLAMP_SUFFIX                  = 'CLMP'
DECOMPOSEMAT_SUFFIX           = 'DCPM'


# NOMENCLATURE
UNDER                         = '_'
DUNDER                        = '__'

def extract_TAGS(tag_name):
    extract = [x.split('.')[0] for x in pm.ls('*.{}'.format(tag_name))]
    return extract
