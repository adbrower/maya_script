import maya.cmds as mc
import pymel.core as pm

# TO DO : set the min and max for each axe
    
    
def create_driver_setup(driver=None,
                      driver_channels=list(),
                      driver_axis=list(),
                      driven=None,
                      driven_channels=list(),
                      driven_axis=list(),
                      axis_factors=list(),
                      attributes_control=None,
                      min = None,
                      max = None,
                      show_attributes=True):
    """
    Method that creates makes an object attribute drive another object attribute
    Args:
        driver: (str) Object that will drive
        driver_channels: (list) of channels that are use to drive the driven object
        driver_axis: (list) list of axis that will be use to drive the driven object
        driven: (str) Object that will be driven
        driven_channels: (list) list of channels to be driven
        driven_axis: (list) list of axis to be driven
        axis_factors: (list) list of values per axis
        attributes_control: (str) Object that where the attributes will be created, if None is specified they will be created
        on the driven object
        show_attributes: (bool) Option to show or hide the attributes on the channel box

    Example:
        create_flap_setup(driver='L_Arm_clavicle_clav_JNT',
                                    driven='L_shoulderFlap_generic_0__OFFSET',
                                    driver_channels=['rotate', 'rotate'],
                                    driver_axis=[['Y'], ['Y', 'Z']],
                                    driven_channels=['translate', 'rotate'],
                                    driven_axis=[['Z'], ['Y', 'Z']],
                                    axis_factors=[[[-0.050, 0.0]], [[.5, .1], [.2, .4]]],
                                    attributes_control='L_shoulderFlap_generic_0_CTRL')

    Returns:

    """
    if not driver or not driven:
        pm.error('driver or driven objects are not specified')
    if len(driver_channels) != len(driven_channels):
        pm.error('Driver and driven channels length does not match')
    if len(driver_axis) != len(driven_axis):
        pm.error('Driver and driven axis length does not match')
    if len(driven_axis) != len(axis_factors):
        pm.error('Check the axis factors. The length does not match with the driven axis.')
    if not attributes_control:
        attributes_control = driven
    
    pm.addAttr(attributes_control, ln='___SETTINGS___', at='enum', en='___')
    if show_attributes:
        pm.setAttr('{}.___SETTINGS___'.format(attributes_control), edit=1, cb=1)
    
    for i in xrange(len(driven_channels)):
        
        pm.addAttr(attributes_control, ln='{}_SETTINGS'.format(driven_channels[i]), at='enum', en='___')
        if show_attributes:
            pm.setAttr('{}.{}_SETTINGS'.format(attributes_control, driven_channels[i]), edit=1, cb=1)
        
        for j in xrange(len(driven_axis[i])):
            
            factor = pm.createNode('multiplyDivide',
                                   n='{}_{}_{}_factor'.format(driven, driven_channels[i], driven_axis[i][j]))
            cond = pm.createNode('condition',
                                 n='{}_condition_{}_{}'.format(driven, driven_channels[i], driven_axis[i][j]))
            pm.setAttr('{}.operation'.format(cond), 2)
            
            remap = pm.createNode('remapValue',
                                  n='{}_{}_{}_remap'.format(driven, driven_channels[i], driven_axis[i][j]))
            
            pm.connectAttr('{}.{}{}'.format(driver, driver_channels[i], driver_axis[i][j]), '{}.inputValue'.format(remap))
            
            if min:
                remap.outputMin.set(min)
                remap.inputMin.set(min)
                remap.inputMax.set(0)                
                pm.connectAttr('{}.{}{}'.format(driver, driver_channels[i], driver_axis[i][j]), '{}.outputMax'.format(remap))
                
            if max:
                remap.outputMax.set(max)
                remap.inputMax.set(max) 
                remap.inputMin.set(0) 
                pm.connectAttr('{}.{}{}'.format(driver, driver_channels[i], driver_axis[i][j]), '{}.outputMin'.format(remap))
                                 
            else:
                pm.connectAttr('{}.{}{}'.format(driver, driver_channels[i], driver_axis[i][j]), '{}.inputMax'.format(remap))
                pm.connectAttr('{}.{}{}'.format(driver, driver_channels[i], driver_axis[i][j]), '{}.outputMax'.format(remap))
            
            pm.connectAttr('{}.outColorR'.format(remap), '{}.input1X'.format(factor))
            pm.connectAttr('{}.outColorG'.format(remap), '{}.input1Y'.format(factor))
            
            pm.connectAttr('{}.{}{}'.format(driver, driver_channels[i], driver_axis[i][j]), '{}.firstTerm'.format(cond))
            pm.connectAttr('{}.outputX'.format(factor), '{}.colorIfFalseR'.format(cond))
            pm.connectAttr('{}.outputY'.format(factor), '{}.colorIfTrueR'.format(cond))
            
            pm.connectAttr('{}.outColorR'.format(cond), '{}.{}{}'.format(driven, driven_channels[i], driven_axis[i][j]))
            
            for value_type, input, position in zip(['pos', 'neg'], ['input2X', 'input2Y'], [0, 1]):
                attribute_name = '{}_{}_{}'.format(driven_channels[i], driven_axis[i][j], value_type)
                pm.addAttr(attributes_control, ln=attribute_name, at='float')
                if show_attributes:
                    pm.setAttr('{}.{}'.format(attributes_control, attribute_name), edit=1, cb=1, k=1)
                pm.setAttr('{}.{}'.format(attributes_control, attribute_name), axis_factors[i][j][position])
                pm.connectAttr('{}.{}'.format(attributes_control, attribute_name), '{}.{}'.format(factor, input))




create_driver_setup(driver='pSphere1',
                        driven='pCube1',
                        driver_channels=['translate', 'rotate'],
                        driver_axis=[['X', 'Y', 'Z'], ['X', 'Y', 'Z']],
                        driven_channels=['translate', 'rotate'],
                        driven_axis=[['X', 'Y', 'Z'], [ 'X', 'Y', 'Z']],
                        axis_factors=[[[1, 1],[1, 1], [1, 1]], [[1, 0.2],[.8, .5], [.1, 1]]],
                        min = None,
                        max = 10,
                        attributes_control='pSphere1')                        
                        
                           
                        
                        

