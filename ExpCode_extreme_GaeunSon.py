# Overlook of the experiment procedure (Gaeun's experiment - study session)
# 1. Get subject number and session number with a pop-up window (put any numbers you like).
# 2. Show the instruction for informing the task and how to respond.
# 3. Show inter-trial-interval between images (500ms).
# 4. Show a stream of natual scene images (1sec/img). Participants should press spacebar when an image rotated on its side.
# 5. Show feedback (500ms).
# ** total 10 trials and 3 target trials (rotated images) in this version.
# ** final output would be printed in the Output window (including accuracy & mean RT accumulated in the trial).

# required set up
import numpy as np
import pandas as pd
import os, sys
from psychopy import visual, core, event, gui, logging, data
event.globalKeys.add(key='escape', func=core.quit) # to force quit the experiment

# create a gui object for general expInfo.
subgui = gui.Dlg()
subgui.addField("Subject ID:")
subgui.addField("Session Number:")
subgui.show()

# put the inputted data in easy to use variables
sbjID = subgui.data[0]
sessNum = subgui.data[1]

# set output frame
outFileName = 'data' + os.sep + 'sub' + sbjID + '_sess' + sessNum + '.csv'
outVars = ['sbj', 'trial', 'stim', 'resp', 'rt', 'stimOn', 'accuracy_soFar']
out = pd.DataFrame(columns=outVars)

# window setup
win = visual.Window(fullscr=True, allowGUI=False, color=(0,0,0), unit='height') 
win.recordFrameInterval = True
win.refreshThreshold = 1/60 + 0.005
logging.console.setLevel(logging.WARNING)

# Exp ingredient
trialInfo = pd.read_csv('ExpCond.csv') #read in experiment info
trialInfo = trialInfo.sample(frac=1) # randomize trials
trialInfo = trialInfo.reset_index()
fixation = visual.TextStim(win, text='+', height=.05, color = 'black') # prepare fixation cross (ITI)
fbCorrect = visual.TextStim(win, text='correct', height=.05, color ='green') # prepare feedback text
fbWrong = visual.TextStim(win, text='Wrong', height=.05, color ='red')
oris = [0,90] # image rotation options
itiDur = 0.5
stimDur = 1
fbDur = 0.5

#--------------EXP start-------------#
# Instruction
myInst = visual.TextStim(win, text="""Carefully look at the images, and press space when you see an image rotated on its side.
    
Press any key to start.""", height=.03, color='black')
myInst.draw()
event.clearEvents()
win.flip()
event.waitKeys()

# clock setting
expClock = core.Clock() # won't reset
trialClock = core.Clock() # will reset at the beginning of each trial
stimClock = core.Clock() # will reset when stim are presented
fbClock = core.Clock() # will reset when feeback presented

# Image stream (for loop)
nTrials = len(trialInfo)
correct = [] # for trial-by-trial accuracy
rt = []
for currTrial in np.arange(0,nTrials):
    
    trialClock.reset()
    
    # Initial fixation
    fixation.draw()
    win.flip()
    
    # record trial prarameters
    out.loc[currTrial, 'sbj'] = sbjID
    out.loc[currTrial,'trial'] = currTrial + 1
    out.loc[currTrial,'stim'] = trialInfo.loc[currTrial,'stim']
    
    # scene image drawing (while iti)
    currImg = visual.ImageStim(win, image=trialInfo.loc[currTrial,'stim'],
                              ori = oris[trialInfo.loc[currTrial,'target']],
                              size= [0.5, 0.5], pos=(0,0), interpolate=True)
    currImg.draw()
    
    # end iti and show the current image
    while trialClock.getTime() < itiDur:
        core.wait(0.001)
    win.flip()
    stimClock.reset()
    out.loc[currTrial, 'stimOn'] = expClock.getTime()
    
    # record response while the image presented
    event.clearEvents()
    while stimClock.getTime() < stimDur:
        Clock = stimClock.getTime()
        key = event.getKeys(keyList=['space'], timeStamped=Clock)
        # save responses
        if len(key): #if response was made
            out.loc[currTrial, 'resp'] = 1
            out.loc[currTrial, 'rt'] = Clock
            rt.append(Clock)
    
    # feedback & get accuracy 
    if out.loc[currTrial, 'resp'] == 1:
        if trialInfo.loc[currTrial,'target'] == 1:
            correct.append(1)
            fbCorrect.draw()
        else:
            correct.append(0)
            fbWrong.draw()
    else:
        if trialInfo.loc[currTrial,'target'] == 0:
            correct.append(1)
            fbCorrect.draw()
        else:
            correct.append(0)
            rt.append(Clock)
            fbWrong.draw()
    win.flip()
    # feedback disply
    fbClock.reset()
    core.wait(fbDur)
    out.loc[currTrial, 'accuracy_soFar'] = np.mean(correct)


print('overall accuracy:', np.mean(correct))
print('mean RT:', np.mean(rt))
print('details:','\n', out)
win.close()
