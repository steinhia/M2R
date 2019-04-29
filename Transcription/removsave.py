import os,glob
path='AudioList/'
for i in range(20):
    path='AudioList/id'+str(i).zfill(2)+'/'

    for filename in glob.glob(os.path.join(path, '*.TextGrid.save')):
        os.remove(filename)
