

suffixDic = {
    'nurbsCurve':  '__CTRL',
    'mesh':  '__MSH',
             'joint':  '__JNT',
             'transform':  '__GRP',
             'nurbsSurface':  '__NRBS',
             'locator':  '__LOC',
             'clusterHandle':  '__CLS',
             'nRigid':  '__nRigid',
             'nCloth':  '__nCloth',
}

attrDic = {
    'tx': ['translateX'], 'ty': ['translateY'], 'tz': ['translateZ'],
    'rx': ['rotateX'], 'ry': ['rotateY'], 'rz': ['rotateZ'],
    'sx': ['scaleX'], 'sy': ['scaleY'], 'sz': ['scaleZ'],
    'v': ['visibility'],
    'Translate': ['translateX', 'translateY', 'translateZ'],
    'Rotate': ['rotateX', 'rotateY', 'rotateZ'],
    'Scale': ['scaleX', 'scaleY', 'scaleZ'],
    'Transforms': ['translateX', 'translateY', 'translateZ', 'rotateX', 'rotateY', 'rotateZ', 'scaleX', 'scaleY', 'scaleZ'],
    'All': ['translateX', 'translateY', 'translateZ', 'rotateX', 'rotateY', 'rotateZ', 'scaleX', 'scaleY', 'scaleZ', 'visibility']
}


pysideColorDic = {

    'colorWhite': '#FFFFFF',
    'colorBlack': '#190707',

    'colorBlue':      '#84939B',
    'colorBluelabel': '#00cdff',

    'colorBlue2': 'rgb(55,59,73)',
    'colorBlue3': 'rgb(122,122,135)',
    'colorBlue4': 'rgb(55,59,70)',

    'colorGreen': '#597a59',
    'colorGreen2': 'rgb(72,96,80)',
    'colorGreen3': '#597A59',

    'colorRed': '#745a54',
    'colorDarkRed1': 'rgb(80,55,55)',
    'colorDarkRed2': 'rgb(70,55,55)',

    'colorOrange': 'rgb(192,147,122)',

    'colorGrey': '#606060',
    'colorLightGrey': '#F2F2F2',

    'colorYellowlabel': '#E5C651',
    'colorYellow': '#ffe100',

    'colorDarkGrey2': '#373737',
    'colorDarkGrey3': '#2E2E2E',
    'colorGrey2': '#4A4949',
}


colordic = {

    'grey':        (0.17, 0.17, 0.17),
    'grey1':        (0.365, 0.365, 0.365),
    'grey2':        (0.336, 0.376, 0.397),
    'grey4':        (0.702, 0.702, 0.702),
    'grey5':        (0.12, 0.12, 0.12),

    'blue':         (0.182, 0.567, 0.710),
    'blue2':        (0.260, 0.419, 1.000),
    'blue3':        (0.517, 0.576, 0.608),
    'blue4':        (0.214, 0.503, 0.610),
    'blue5':        (0.00, 0.610, 0.610),

    'darkblue':     (0.195, 0.207, 0.247),
    'lightblue':    (0.429, 0.545, 0.623),

    'lightpurple':  (0.515, 0.515, 0.555),
    'lightpurple2':  (0.289, 0.289, 0.338),

    'green':        (0.000, 0.610, 0.430),
    'green2':        (0.301, 0.591, 0.381),
    'green3':        (0.349, 0.478, 0.349),
    'greenish':     (0.340, 0.390, 0.390),

    'lightgreen':  (0.600, 0.631, 0.586),

    'red':          (0.642, 0.108, 0.090),
    'lightred':    (0.62, 0.456, 0.466),
    'darkred':      (0.312, 0.222, 0.222),
    'darkred2':     (0.360, 0.000, 0.000),
    'darkred3':     (0.244, 0.180, 0.180),

    'orange':      (0.714, 0.605, 0.529),
    'orange2':       (0.800, 0.500, 0.200),
    'orange3':       (0.8, 0.366, 0.200),
    'orange4':       (1, 0.623, 0.390),

    'yellow':        (0.900, 0.850, 0.000),

    'pink':         (1.000, 0.700, 0.700),
    'pink2':         (1.000, 0.176, 0.293),

    'purple':       (0.582, 0.516, 0.751),

    'darkbrown':    (0.364, 0.309, 0.264),
    'black':        (0.000, 0.000, 0.000),

}


indexToRGB = {

    'index1': (.000, .000, .000),
    'index2': (.247, .247, .247),
    'index3': (.498, .498, .498),
    'index4': (0.608, 0, 0.157),
    'index5': (0, 0.016, 0.373),
    'index6': (0, 0, 1),
    'index7': (0, 0.275, 0.094),
    'index8': (0.145, 0, 0.263),
    'index9': (0.78, 0, 0.78),
    'index10': (0.537, 0.278, 0.2),
    'index11': (0.243, 0.133, 0.122),
    'index12': (0.6, 0.145, 0),
    'index13': (1, 0, 0),
    'index14': (0, 1, 0),
    'index15': (0, 0.255, 0.6),
    'index16': (1, 1, 1),
    'index17': (1, 1, 0),
    'index18': (0.388, 0.863, 1),
    'index19': (0.263, 1, 0.635),
    'index20': (1, 0.686, 0.686),
    'index21': (0.89, 0.675, 0.475),
    'index22': (1, 1, 0.384),
    'index23': (0, 0.6, 0.325),
    'index24': (0.627, 0.412, 0.188),
    'index25': (0.62, 0.627, 0.188),
    'index26': (0.408, 0.627, 0.188),
    'index27': (0.188, 0.627, 0.365),
    'index28': (0.188, 0.627, 0.627),
    'index30': (0.188, 0.404, 0.627),
    'index30': (0.435, 0.188, 0.627),
    'index31': (0.507, 0.041, 0.277),

}
