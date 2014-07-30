import socket
import sys
import numpy
import threading

#Requires python-musical package
from musical.theory import Note, Scale, Chord
from musical.audio import playback, source
from timeline import Hit, Timeline

import phoneImu


def getIPAddr():
    return socket.gethostbyname(socket.getfqdn()) 

def play(data):
    playback.play(data)

def playtones(imu):
    notes = [Note('C6'), Note('C5'), Note('C4'), Note('C3')]
        
    amp = 0.5 #Amplitude
    sine = source.sine(notes[0], 1)
    arr = numpy.array(sine)
    
    thrd = None
    
    while True: 
        src = source.sine(notes[0], 1)*0
        acc = imu.getacc()
        #print "acc is {}".format(acc)
        
        ax, ay, az = acc
        if ax > 1.5:
            src+=source.sine(notes[0], 1)
        elif ax < -1.5:
            src+=source.sine(notes[1], 1)
        if ay > 1.5:
            src+=source.sine(notes[2], 1)
        elif ay < -1.5:
            src+=source.sine(notes[3], 1) 
    
        data = numpy.array(src) * amp
        
        if thrd == None or not thrd.isAlive():
            thrd = threading.Thread(target=play, args=(data,))
            thrd.start()

def playtonesvol(imu):
    notes = [Note('C6'), Note('C3')]
        
    amp = 0.5 #Amplitude
    sine = source.sine(notes[0], 1)
    arr = numpy.array(sine)
    
    thrd = None
    
    while True: 
        src = source.sine(notes[0], 1)*0
        acc = imu.getacc()
        #print "acc is {}".format(acc)
        
        ax, ay, az = acc
        if ax > 1.5:
            src+=source.sine(notes[0], 1)
        elif ax < -1.5:
            src+=source.sine(notes[1], 1)
        #volume buckets [-9<=, -8, ..., 0, ..., 8, 9>= ]
        vol = ay
        if vol <= -9:
            vol = -9
        elif vol >= 9:
            vol = 9
        vol = (vol + 9)/18.0 #shift and normalize                 
    
        data = numpy.array(src) * vol
        
        if thrd == None or not thrd.isAlive():
            thrd = threading.Thread(target=play, args=(data,))
            thrd.start()
    
    

def playchords(imu):
    
    key = Note('E3')
    scale = Scale(key, 'harmonic minor')
    progression = Chord.progression(scale, base_octave=key.octave)
    time = 0.0
    timeline = Timeline()    
    chord = progression[0]
    
    d = 3.0 #length of time (seconds)
    chords = [Hit(chord.notes[0], d), Hit(chord.notes[1], d), Hit(chord.notes[2], d), Hit(chord.notes[0], d)]
        
    amp = 0.25 #Amplitude
    thrd = None
    
    while True: 
        timeline = Timeline()
        acc = imu.getacc()
        #print "acc is {}".format(acc)
        
        ax, ay, az = acc
        if ax > 1.5:
            timeline.add(0.0, chords[0])
        elif ax < -1.5:
            timeline.add(0.0, chords[1])
        if ay > 1.5:
            timeline.add(0.0, chords[2])
        elif ay < -1.5:
            timeline.add(0.0, chords[3])
    
        data = timeline.render() * amp
        
        if thrd == None or not thrd.isAlive():
            thrd = threading.Thread(target=play, args=(data,))
            thrd.start()

if __name__ == '__main__':

    ipaddr = getIPAddr() 
    port = 5005
    imu = phoneImu.PhoneIMU(ipaddr=ipaddr,port=port)
    
    print "Listening on {}:{}".format(ipaddr,port)
    
    if len(sys.argv) == 1:
        playtones(imu)
    elif sys.argv[1] == "v":
        playtonesvol(imu)
    elif sys.argv[1] == "c":
        playchords(imu)        
    
    #while True: print imu.readimu() 
            
        
    
