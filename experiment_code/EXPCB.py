
#!/usr/bin/env python2

from __future__ import division

import sys
from psychopy import visual, core, event, data, gui,logging,monitors
import numpy as np #for maths on arrays
from numpy import random #we only need these two commands from this lib

from itertools import product
from numpy import linspace
import math, codecs
import copy

from pyglet.gl import gl_info as info
import cpuinfo
import platform

#monitorName = 'ASUS ML 239'
monitorName = 'testMonitor'
debug = 1

resolution = [800,600] if debug == 1 else [800,600]

expName = 'orientation_search' 
expInfo = {u'session': u'001', u'participant': u''}
dlg = gui.DlgFromDict(dictionary=expInfo, title=expName)
if dlg.OK == False: core.quit()  # user pressed cancel
expInfo['date'] = data.getDateStr()  # add a simple timestamp
expInfo['expName'] = expName

expInfo['graphic_card'] = info.get_renderer()
cpu_info = cpuinfo.get_cpu_info()
expInfo['cpu_info'] = cpu_info['brand']
expInfo['pc_name'] = platform.node() 
expInfo['monitorName'] = monitorName
expInfo['resolution'] = '_'.join(str(x) for x in resolution)


mon = monitors.Monitor(monitorName)
win = visual.Window(resolution, units='deg', monitor=mon, fullscr = True)

if 0:
    if (mon.getSizePix()!=resolution):
        print 'Resolution in monitor center is different from the one requested for this experiment. Please make them equal to make sure that the computations of visual angle will be correct for the resolution you want.'
        core.quit()
        win.close()
    
    if (not np.array_equal(win.size,resolution)):
        print 'Actual display resolution differs from requested. PsychoPy cannot change resolution for you. Please do it yourself before running the script or correct requested resolution.'
        core.quit()
        win.close()

#################################
# Load instruction images
#################################
        
image_folder = r'C:\Users\user\Desktop\lisa_lemmens\ruimte_experiment\Ruimte'
instruction_images = {}
for i in range(1,28): ##Hier heb ik nu 1 - 29 van gemaakt, dus dat zijn alle afbeeldingen, ook diegene tussen de blokken door. 
    im = visual.ImageStim(win, image = image_folder + "\\Slide" + str(i) + ".PNG",units='pix')
    instruction_images[str(i)] = im
    
lineSize = 1 #deg - this is NOT the actual line size, but rather a size of the square in which the line is a diagonal (historical reasons)

circleArray = []
radii =[4]
for i in range(len(radii)):
    r = radii[i]
    circleArray.append(visual.Circle(win, radii[i], pos=(-320, 0), units='pix',fillColor='#dadaff',lineWidth=0))
    circleArray.append(visual.Circle(win, radii[i], pos=(320, 0),units='pix',fillColor='#dadaff',lineWidth=0))

   
# line texture
smoothMask = -np.ones([16,16], 'f')
smoothMask[0:8,:]=np.reshape(np.repeat(np.linspace(-1,1,8),16,0),(8,16))
smoothMask[8:16,:]=np.reshape(np.repeat(np.linspace(1,-1,8),16,0),(8,16))

# array for lines textures/coordinates
globForms = {}

# loop through possible set sizes, set line arrays
for fieldSizeN in [36]:
    print fieldSizeN
    fieldSize = 3.2*(math.sqrt(fieldSizeN)-1)
    seq = linspace(0, fieldSize, int(math.sqrt(fieldSizeN)))
    coordinates = np.asarray(list(product(seq, seq)))-fieldSize/2.0
    
    # two arrays are created - they are populated later and swapped on each trial to reduce drawing time
    globForms[fieldSizeN] = {}
    globForms[fieldSizeN][0] = visual.ElementArrayStim(win, nElements=fieldSizeN, sizes=[math.sqrt(2*(lineSize*lineSize)),0.1], 
            sfs=0,elementTex = np.ones([16,16]), xys = coordinates, colors=[1,1,1],oris=0, 
            texRes=16, colorSpace='rgb',elementMask= smoothMask, units='deg', interpolate=True)
    globForms[fieldSizeN][1] = visual.ElementArrayStim(win, nElements=fieldSizeN, sizes=[math.sqrt(2*(lineSize*lineSize)),0.1], 
            sfs=0,elementTex = np.ones([16,16]), xys = coordinates, colors=[1,1,1],oris=0, 
            texRes=16, colorSpace='rgb',elementMask= smoothMask, units='deg', interpolate=True)
    
    
# function to save data into the open file after each trial - a failsafe mechanism in case psychopy internal autosave fails
def please_keep_data(exp, f, delim=',', addNames = False):
    names = exp._getAllParamNames()
    names.extend(exp.dataNames)
    names.extend(exp._getExtraInfo()[0]) 
    #print(exp.entries)
    if addNames:
        for heading in names:
            f.write(u'%s%s' %(heading,delim))
        f.write('\n')
    for entry in exp.entries[-2:-1]:
        for name in names:
            entry.keys()
            if name in entry.keys():
                if ',' in unicode(entry[name]) or '\n' in unicode(entry[name]):
                    f.write(u'"%s"%s' %(entry[name],delim))
                else:
                    f.write(u'%s%s' %(entry[name],delim))
            else:
                f.write(delim)
        f.write('\n')

# this function draws orientations from a (restricted) random distribution, then adds target orientation to it at a given position
def drawOris(nNew, dmean, dtype, dsd, targetPos, targetOri):
    if dsd == 0:
        newOris = np.asarray([dmean]*nNew)
    else:
        dmult=2
        if dtype=='norm':
            newOris = random.normal(dmean, dsd, nNew)
            outliers = [x for x in newOris if x < dmean-dmult*dsd or x > dmean+dmult*dsd]
            while (len(outliers)>0):
                for key, x in enumerate(newOris):
                    if x < dmean-dmult*dsd or x > dmean+dmult*dsd:
                        newOris[key] = random.normal(dmean, dsd)
                outliers = [x for x in newOris if x < dmean-dmult*dsd or x > dmean+dmult*dsd]
        elif dtype=='uni':
            newOris = random.uniform(dmean-dmult*dsd, dmean+dmult*dsd, nNew)
        elif dtype=='bimod':
            newOris =np.concatenate( [random.uniform(dmean-dmult*dsd, dmean-dsd, nNew/2),random.uniform(dmean+dsd, dmean+dmult*dsd, nNew/2)])
        newOris[0:2]=[dmean-dmult*dsd, dmean+dmult*dsd]
        random.shuffle(newOris)

    if targetPos!=-1:
        newOris[targetPos] = targetOri

    return newOris

mouse = event.Mouse()

error_feedback = visual.TextStim(win, 'Oeps, de foute richting!', color='red')
correct_feedback= visual.TextStim(win, 'Goed zo, dat was de juiste richting!', color='green')
filename = 'data%s/%s_%s_%s_%s' % ('_debug' if debug else '',expInfo['date'],expName, expInfo['participant'],expInfo['session'])
exp = data.ExperimentHandler(name=expName,
                version='0.1',
                extraInfo=expInfo,
                runtimeInfo=None,
                originPath=None,
                savePickle=False,
                saveWideText=True,
                autoLog = False,
                dataFileName=filename)

temp_file = codecs.open(filename+'_temp.csv', 'w+', 'utf-8')

# number of repetitions for all conditions
nReps = 5

condsList = data.createFactorialTrialList({'ctpd_prime':[-80,-60,-40,-30,-20,-10,0,10,20,30,40,60,80], 
    'dsd_prime': [10], 'dsd_test':[5], 'dtype_prime':['norm'], 'dtype_test':['norm'], 'streak_length_prime':[5,6], 'prime_set_size':[36],'test_set_size':[36]})



trialsList = []
totBlockN=0
curTrialN=0
coordinates_by_trial = {}
oris_by_trial = {}
colors_by_trial = {}
set_sizes = {}
totalTrials = 0

   
###############################################################################
# Populate trial parameters
###############################################################################
# 1. Practice trial

# 2. Experimental sequence
for blockRepN in range(nReps):
    random.shuffle(condsList)
    conds = []

    # create prime and test sequences parameters from conditions list
    for i, cond in enumerate(condsList):
        testSeq = copy.copy(cond)
        
        primeSeq = copy.copy(cond)
        
        primeSeq['nextProbe'] = cond['streak_length_prime'] 
        primeSeq['dtype'] = cond['dtype_prime'] 
        primeSeq['dsd'] = cond['dsd_prime'] 
        primeSeq['ctpd'] = cond['ctpd_prime'] 
        primeSeq['ctpd'] = cond['ctpd_prime'] 
        primeSeq['set_size'] = cond['prime_set_size']
        primeSeq['seq_type'] = 'prime'
        testSeq['nextProbe'] = random.choice([1,2])
        testSeq['ctpd'] = condsList[len(condsList)-i-1]['ctpd_prime']
        testSeq['dtype'] = cond['dtype_test'] 
        testSeq['dsd'] = cond['dsd_test']
        testSeq['seq_type'] = 'probe'
        testSeq['set_size'] = cond['test_set_size']
        totalTrials+=primeSeq['nextProbe']+testSeq['nextProbe']
        conds.append(primeSeq)
        conds.append(testSeq)
    
    for blockN, block in enumerate(conds):
        block['blockN'] = blockN
        block['blockRepN'] = blockRepN
        block['totBlockN'] = totBlockN
        totBlockN+=1
        if block['seq_type']=='prime':
            dmean = random.uniform(0, 360)
        else:
            # we use different bin sizes at different CTPDs so we have a bit more precision closer to the mean, where we actually expect to see differences
            if abs(prev_ctpd)==80:
                targetOri = prev_dmean+np.sign(prev_ctpd)*random.uniform(70,90)
            elif abs(prev_ctpd)==60:
                targetOri = prev_dmean+np.sign(prev_ctpd)*random.uniform(50,70)
            elif abs(prev_ctpd)==40:
                targetOri = prev_dmean+np.sign(prev_ctpd)*random.uniform(35,50)
            else:
                targetOri = prev_dmean+prev_ctpd+random.uniform(-5,5)
        if totBlockN>1:
            block['prevDistrMean'] = prev_dmean
            block['prevDistrCTPD'] = prev_ctpd
            block['prevDistrType'] = prev_dtype
        prev_dmean = dmean
        prev_ctpd = block['ctpd']
        prev_dtype = block['dtype']
        for trialN in range(block['nextProbe']):
            
            trial = copy.deepcopy(block)
            trial['trialN']=trialN
            targetDist = random.randint(60,120)
            if block['seq_type']=='prime':
                targetOri = dmean+targetDist
            else:
                dmean = targetOri+targetDist
            
            N = block['set_size']
            
            fieldSizeN = N
            fieldSize = 3.2*(math.sqrt(fieldSizeN)-1)
            seq = linspace(0, fieldSize, math.sqrt(fieldSizeN))
            coordinates = np.asarray(list(product(seq, seq)))-fieldSize/2.0
            matrix_dim = int(math.sqrt(N))
            half_matrix_dim = int(matrix_dim/2)
            
            targetCol = random.randint(0, matrix_dim)
            targetRow = random.randint(0, matrix_dim)
            
            targetPos =  int(targetRow+math.sqrt(N)*targetCol)
            
#            colors = np.ones([N,3])
            newOris=drawOris(N, dmean, block['dtype'], block['dsd'], targetPos, targetOri)
            for i in range(N):
                if i!=targetPos:
                    trial['d_ori_%i'%i] = round(newOris[i],1)
                else:
                    trial['d_ori_%i'%i] = ''
                    trial['correctResponse'] = 'up' if coordinates[i][1]>0 else 'down'
                coordinates[i]=coordinates[i]+(-0.5+random.random_sample(),-0.5+random.random_sample())
                trial['stim_pos_x_%i'%i] = round(coordinates[i][0],3)
                trial['stim_pos_y_%i'%i] = round(coordinates[i][1],3)
#            colors[targetPos,:] = (1, 0,0)
            coordinates_by_trial[curTrialN] = coordinates
            oris_by_trial[curTrialN] = newOris-45
            set_sizes[curTrialN] = N
#            colors_by_trial[curTrialN] = colors
                
            trial['targetDist'] = targetDist
            trial['distrMean'] = dmean

            trial['targetOri'] = round(targetOri,1)
            
            trial['targetCol'] = targetCol
            trial['targetRow'] = targetRow
            trial['targetPos'] = targetPos
            trialsList.append(trial)
            curTrialN+=1
            
            
trials=data.TrialHandler(trialList=trialsList, nReps=1, name='trials', method='sequential')
exp.addLoop(trials)

print totalTrials
print len(conds)

restText=visual.TextStim(win, 'Now you can rest. Press "space" when you feel ready to go on.',color='white')
score = visual.TextStim(win, 'Score: 0',color=[1,1,1], colorSpace='rgb', height = 0.07, pos=(-0.9, 0.9), units='norm', alignHoriz='left')
trialNtext = visual.TextStim(win, '',color=[1,1,1], colorSpace='rgb', height = 0.07, pos=(-0.9, 0.8), units='norm', alignHoriz='left')
endPracticeText = visual.TextStim(win,'Dit waren alle oefenbeurten. Nu begint onze echte reis! Wanneer je juist antwoord, zal je score omhoog gaan. Enkel wanneer je fout antwoordt, krijg je feedback.  Druk op de spatiebalk als je er klaar voor bent.',color='white')
###############################################################################
# Display initial instructions
###############################################################################
for i in range(1,11):
    instruction_images[str(i)].draw()
    win.flip()
    event.waitKeys(keyList=['space'])
    
###############################################################################
# Practice part of the experiment: present a few trials with feedback, but
# no score is updated
###############################################################################
nPracticeTrials   = 10
muDistractor      = 20
sigmaDistractor   = 10
targetOffsetRange = [60,90]

for i in range(nPracticeTrials):
    # 1. Sample orientations and set target location
    oris = [np.random.normal(muDistractor, sigmaDistractor,1)[0] for _ in range(36)]
    targetIndex = np.random.randint(0,len(oris))
    meanDistractor = np.mean(oris[:targetIndex] + oris[(targetIndex+1):])
    
    targetOffset = np.random.uniform(targetOffsetRange[0], targetOffsetRange[1])
    oris[targetIndex] = meanDistractor + np.random.choice([-1,1],1)[0]*targetOffset
    
    # 2. Set and draw stimulus
    globForms[36][0].oris = np.array(oris)
    globForms[36][0].draw()
    for c in circleArray:
        c.draw()
    win.flip()
    
    # 3. Wait for a response
    keysPressed = event.waitKeys(keyList=['up','down'])
    responseLocation = 1 if 'up' in keysPressed else -1
    targetLocation = -1 if targetIndex % 6 < 3 else 1
    
    # 4. Show response feedback
    if responseLocation == targetLocation:
        correct_feedback.draw()
    else:
        error_feedback.draw()
    win.flip()
    core.wait(1)
    
endPracticeText.draw()
win.flip()
event.waitKeys(['space'])

###############################################################################
# Real part of the experiment: present all trials
###############################################################################
totalScore = 0
curTrialN=0
event.Mouse(visible=False) 
firstInstructionImage = 11  
for trial in trials:
    
    trials.addData('timeStart', round(core.getTime(), 3))
    
    # breaks are hardcoded on each 20th block (set whatever you think is good here)
    if  trial.totBlockN%18==0 and trial.trialN==0:
        if trial.totBlockN==0:
            pass
        else:
            #################################
            # Nagaan of de hoogste blok overeenkomt met aantal prentjes
            #################################
            instruction_images[str(firstInstructionImage)].draw()
            win.flip()
            event.waitKeys(keyList=['space'])
            firstInstructionImage+=1
            print firstInstructionImage
    
        win.flip()
        if not debug:
            pass
            #event.waitKeys(keyList=['space'])
    
    trialNtext.text='Trial %i/%i' %(curTrialN+1,totalTrials)
    trials.addData('timeBeforeDraw', round(core.getTime(), 3))
    N = trial['set_size']
    if curTrialN==0:
        globForms[N][0].oris = oris_by_trial[curTrialN]
        globForms[N][0].xys = coordinates_by_trial[curTrialN]#+(-10,0)
        globForms[N][0].draw()
    elif curTrialN % 2 == 0:
        globForms[N][0].draw()
    elif curTrialN % 2 == 1:
        globForms[N][1].draw()
    
    for c in circleArray:
        c.draw()
    score.draw()
    #trialNtext.draw()

    start_time= win.flip()
    trials.addData('timeDraw', start_time)
    mouse.clickReset()
    
    # we start preparing next trial after drawing the current one
    trials.addData('timeAfterSaving', round(core.getTime(), 3))
    if curTrialN==1:
        please_keep_data(exp, f=temp_file, addNames=True)
    elif curTrialN>1:
        please_keep_data(exp, f=temp_file)
    trials.addData('timeAfterWritingToTemp', round(core.getTime(), 3))
    if curTrialN < (totalTrials-1):
        if curTrialN % 2 == 0:
            globForms[set_sizes[curTrialN+1]][1].oris = oris_by_trial[curTrialN+1]
            globForms[set_sizes[curTrialN+1]][1].xys = coordinates_by_trial[curTrialN+1]
        elif curTrialN % 2 == 1:
            globForms[set_sizes[curTrialN+1]][0].oris = oris_by_trial[curTrialN+1]
            globForms[set_sizes[curTrialN+1]][0].xys = coordinates_by_trial[curTrialN+1]
            
    trials.addData('timeAfterPreparingNext', round(core.getTime(), 3))
    
    
    continueRoutine = True
    event.clearEvents()
    start_time = core.getTime()
    if trial.blockN==1000 and debug:
        # just a failsafe for debug went to infinity
        core.quit()
    while continueRoutine:
        # use odd and even globForms on different trials
        if curTrialN % 2 == 0:
            globForms[N][0].draw()
        elif curTrialN % 2 == 1:
            globForms[N][1].draw()
        score.draw()
        #trialNtext.draw()
        events = event.getKeys(keyList=['up','down','minus','escape','q'])
        if debug:
            continueRoutine=False
        for e in events:
            key = e
            print(key)
            if key in ['up','down']:
                if key==trial['correctResponse']:
                    correct = 1
                else:
                    correct = 0
                rt =core.getTime()-start_time
                trials.addData('answer', key)
                trials.addData('correct', correct)
                trials.addData('rt', rt)
                trialScore = 10 - rt 
                if correct==0:
                    trialScore = - 10

                
                trials.addData('trialScore', trialScore)
                
                totalScore += trialScore   
                score.text = 'Score : %+d' % (totalScore)
                if trialScore < 0:
                    score.color = [0, 1, 0]
                else:
                    score.color = [0, 1, 0]
                if correct ==0:
                    win.flip()

                    error_feedback.draw()
                    win.flip()
                    if not debug:
                        core.wait(1)
                continueRoutine = False
            if key in ['minus']:
                linesArr[targetPos].ori-=3
            if key in ['escape','q']:
                win.close()
                core.quit()

        win.flip()
    curTrialN+=1

    exp.nextEntry()

            
instruction_images[str(26)].draw()
win.flip()
event.waitKeys(keyList=['space'])

instruction_images[str(27)].draw()
win.flip()
event.waitKeys(keyList=['space'])

print totalScore
#io.quit()
temp_file.close()
win.close()