import maya.cmds as mc
import pymel.core as pm

def create_driver_setup(driver=None,
                        driver_channels=list(),
                        driver_axis=list(),
                        driven=None,
                        driven_channels=list(),
                        driven_axis=list(),
                        axis_factors=list(),
                        attributes_control=None,
                        min=list(),
                        max=list(),
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
        mc.error('driver or driven objects are not specified')
    if len(driver_channels) != len(driven_channels):
        mc.error('Driver and driven channels length does not match')
    if len(driver_axis) != len(driven_axis):
        mc.error('Driver and driven axis length does not match')
    if len(driven_axis) != len(axis_factors):
        mc.error('Check the axis factors. The length does not match with the driven axis.')
    if not attributes_control:
        attributes_control = driven

    mc.addAttr(attributes_control, ln='___SETTINGS___', at='enum', en='___')
    if show_attributes:
        mc.setAttr('{}.___SETTINGS___'.format(attributes_control), edit=1, cb=1)

    for i in xrange(len(driven_channels)):
        for axis in ((driver_axis[i])):
            cond_switch = pm.createNode('condition', n='{}_{}_condition_switch'.format(driven, axis))

        for channel in driver_channels:
            mc.connectAttr('{}.{}{}'.format(driver, channel, axis), '{}.colorIfTrueR'.format(cond_switch))

    for i in xrange(len(driven_channels)):

        mc.addAttr(attributes_control, ln='{}_SETTINGS'.format(driven_channels[i]), at='enum', en='___')
        if show_attributes:
            mc.setAttr('{}.{}_SETTINGS'.format(attributes_control, driven_channels[i]), edit=1, cb=1)

        remaps = []
        for j in xrange(len(driven_axis[i])):

            remap = pm.createNode('remapValue', n='{}_{}_{}_remap'.format(driven, driven_channels[i], driven_axis[i][j]))
            remaps.append(remap)

            factor = pm.createNode('multiplyDivide',
                                   n='{}_{}_{}_factor'.format(driven, driven_channels[i], driven_axis[i][j]))
            cond = pm.createNode('condition',
                                 n='{}_condition_{}_{}'.format(driven, driven_channels[i], driven_axis[i][j]))
            mc.setAttr('{}.operation'.format(cond), 2)


            mc.connectAttr('{}.outColorR'.format(cond_switch), '{}.inputValue'.format(remap))
            # mc.connectAttr('{}.{}{}'.format(driver, driver_channels[i], driver_axis[i][j]),
            #                '{}.inputValue'.format(remap))

            mc.connectAttr('{}.outColorR'.format(remap), '{}.input1X'.format(factor))
            mc.connectAttr('{}.outColorG'.format(remap), '{}.input1Y'.format(factor))

            mc.connectAttr('{}.{}{}'.format(driver, driver_channels[i], driver_axis[i][j]), '{}.firstTerm'.format(cond))
            mc.connectAttr('{}.outputX'.format(factor), '{}.colorIfFalseR'.format(cond))
            mc.connectAttr('{}.outputY'.format(factor), '{}.colorIfTrueR'.format(cond))
            mc.connectAttr('{}.outColorR'.format(cond), '{}.{}{}'.format(driven, driven_channels[i], driven_axis[i][j]))

            for value_type, input, position in zip(['pos', 'neg'], ['input2X', 'input2Y'], [0, 1]):
                attribute_name = '{}_{}_{}'.format(driven_channels[i], driven_axis[i][j], value_type)
                mc.addAttr(attributes_control, ln=attribute_name, at='float')
                if show_attributes:
                    mc.setAttr('{}.{}'.format(attributes_control, attribute_name), edit=1, cb=1, k=1)
                mc.setAttr('{}.{}'.format(attributes_control, attribute_name), axis_factors[i][j][position])
                mc.connectAttr('{}.{}'.format(attributes_control, attribute_name), '{}.{}'.format(factor, input))

        if min:
            value = []
            for i in xrange(len(min)):
                _value =min[i]
                value.append(_value)
            for remap ,val in zip(remaps, value):
                 remap.inputMin.set(val[0])
                 remap.outputMin.set(val[1])

        if max:
            value = []
            for i in xrange(len(max)):
                _value =max[i]
                value.append(_value)
            for remap ,val  in zip(remaps, value):
                 remap.inputMax.set(val[0])
                 remap.outputMax.set(val[1])

        else:
            mc.connectAttr('{}.{}{}'.format(driver, driver_channels[i], driver_axis[i][j]),
                           '{}.inputMax'.format(remap))
            mc.connectAttr('{}.{}{}'.format(driver, driver_channels[i], driver_axis[i][j]),
                           '{}.outputMax'.format(remap))

                        
                        

