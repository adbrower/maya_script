currentSceneName = pm.sceneName().split('/')[-1]
currentpath = '/'.join(pm.sceneName().split('/')[:-1]) + '/'

wip = currentSceneName.split('.')[1]
version = wip.split('p')[-1]
new_version = 'wip{:03d}'.format(int(version) + 1)
newSceneName = currentSceneName.replace(wip,new_version)

# pm.saveAs('{}{}'.format(currentpath, newSceneName))
# sys.stdout.write('file saved: {}{}\n'.format(currentpath, newSceneName))