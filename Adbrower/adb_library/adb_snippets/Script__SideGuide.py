
for sel in pm.selected():
    def getSide(sub = pm.selected()[0]):
        """ Find the side according to the selection """

        totalBox = sub.getBoundingBox()  
        print(totalBox.center()[0] )  
        if totalBox.center()[0] > 0.0:
            _side = 'l'
            # print('l')
            
        elif totalBox.center()[0] < 0.0:
            _side = 'r'
            # print('r')
                
        else:
            _side = 'm'
            # print('m')    

        return _side
          
    def getBasename(sub = pm.selected()[0]):
        try:
            _basename = sub.name().split('__')[1]
        except IndexError:
            _basename = sub.name()
            
        return _basename

    side = getSide(sel)  
    basename = getBasename(sel)       

    nameStructure = {
                     'Side':side,
                     'Basename': basename
                     }
    
    for item in nameStructure.items(): print item

