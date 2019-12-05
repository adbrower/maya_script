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



def hiearchy_setup(module_name, _mod):
    """
    MOD_GRP : Module grp
    RIG__GRP: Constains all the rigs stuff
    INPUT__GRP : contains all the ctrls and offset groups attach to those ctrls
    OUTPUT__GRP : contains all the joints who will be skinned

    Returns: RIG_GRP, INPUT_GRP, OUTPUT_GRP
    """
    if _mod:
        MOD_GRP = pm.group(n='{}_MOD__GRP'.format(module_name), em=1)
    else:
        MOD_GRP = pm.group(n='{}_SYS__GRP'.format(module_name), em=1)
    RIG_GRP = pm.group(n='{}_RIG__GRP'.format(module_name), em=1)
    INPUT_GRP = pm.group(n='{}_INPUT__GRP'.format(module_name), em=1)
    OUTPUT_GRP = pm.group(n='{}_OUTPUT__GRP'.format(module_name), em=1)

    [pm.parent(grp, MOD_GRP) for grp in [RIG_GRP, INPUT_GRP, OUTPUT_GRP]]

    return MOD_GRP, RIG_GRP, INPUT_GRP, OUTPUT_GRP


def setFinalHiearchy(MODULE_NAME,
                     RIG_GRP_LIST = [],
                     INPUT_GRP_LIST = [],
                     OUTPUT_GRP_LIST = [],
                     mod=True,
                    ):

    _MOD_GRP, _RIG_GRP, _INPUT_GRP, _OUTPUT_GRP = hiearchy_setup(MODULE_NAME, _mod=mod)
    [pm.parent(child, _RIG_GRP) for child in RIG_GRP_LIST]
    [pm.parent(child, _INPUT_GRP) for child in INPUT_GRP_LIST]
    [pm.parent(child, _OUTPUT_GRP) for child in OUTPUT_GRP_LIST]

    return _MOD_GRP, _RIG_GRP, _INPUT_GRP, _OUTPUT_GRP


def getSideFromPosition(_transform):
    """
    @param _transform. Get the side value of this Transform from is world position

    """

    if isinstance(_transform, list):
        transform = _transform[0]
    else:
        transform = pm.PyNode(_transform)

    totalBox = transform.getBoundingBox()
    if totalBox.center()[0] > 0.0:
        _side = LEFT_SIDE_PREFIX

    elif totalBox.center()[0] < 0.0:
        _side = RIGTH_SIDE_PREFIX

    else:
        _side = MID_SIDE_PREFIX

    return _side


def getBasename(_transform):
    """
    Get the base Name of a transfrom.
    Name without Previx of Suffix

    returns sting
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

PARENT_CONSTRAINT_SUFFIX      = 'parentconstraint'
POINT_CONSTRAINT_SUFFIX       = 'pointconstraint'
ORIENT_CONSTRAINT_SUFFIX      = 'orientconstraint'
AIM_CONSTRAINT_SUFFIX         = 'aimconstraint'

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
MULTIPLY_DIVIDE_SUFFIX        = 'MD'
REMAP_VALUE_SUFFIX            = 'RM'
REVERSE_SUFFIX                = 'REV'
CONDITION_SUFFIX              = 'COND'
PLUS_MIN_AVER_SUFFIX          = 'PMA'


def extract_TAGS(tag_name):
    extract = [x.split('.')[0] for x in pm.ls('*.{}'.format(tag_name))]
    return extract
