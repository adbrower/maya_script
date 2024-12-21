import maya.cmds as cmds

def curve_from_cylinder():
    """
    Creates a curve from a single edge of a cylinder
    """

    _selection = cmds.ls(sl=True)[0]
    if not cmds.filterExpand(selectionMask=32):
        raise RuntimeError("You must select an edge or edgeloop!")

    _cylinder = _selection.split(".")[0]
    _curveName = _cylinder.replace(_cylinder.split("_")[-1], "curve")
    _firstEdge = int(_selection.replace(_cylinder, "")[3:-1])

    _ringIDs = cmds.polySelect(_cylinder, edgeRing=_firstEdge)
    _cvPositions = []

    for _ringID in _ringIDs:
        cmds.select(clear=True)
        cmds.polySelect(_cylinder, edgeLoopOrBorder=_ringID)
        _loopCurve = cmds.polyToCurve(
            form=2, degree=1, constructionHistory=False
        )[0]
        cmds.xform(_loopCurve, centerPivots=True)
        _centrePos = cmds.xform(
            _loopCurve, query=True, worldSpace=True, rotatePivot=True
        )
        _cvPositions.append(_centrePos)
        cmds.delete(_loopCurve)

    _knots = []
    for i in range(len(_ringIDs)):
        _knots.append(i / (len(_ringIDs) - 1))
    _extractedCurve = cmds.curve(
        name=_curveName, degree=1, p=_cvPositions, k=_knots
    )
    cmds.xform(_extractedCurve, centerPivots=True)
    centrePos = cmds.xform(
        _extractedCurve, query=True, worldSpace=True, rotatePivot=True
    )
    cmds.move(
        _centrePos[0],
        _centrePos[1],
        _centrePos[2],
        _extractedCurve,
        absolute=True,
        worldSpace=True,
    )
    cmds.move(
        (_centrePos[0] * -1),
        (_centrePos[1] * -1),
        (_centrePos[2] * -1),
        _extractedCurve + ".cv[*]",
        relative=True,
        worldSpace=True,
    )
    cmds.xform(_extractedCurve, centerPivots=True)

    return _extractedCurve