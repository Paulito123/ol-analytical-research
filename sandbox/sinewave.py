import numpy as np
import librosa
import wave
import struct

A=1
fs = 44100
f0 = 440
sec = 10

def create_wave(A,f0,fs,t):
    point = np.arange(0,fs*t)
    sin_wave =A* np.sin(2*np.pi*f0*point/fs)

    sin_wave = [int(x * 32767.0) for x in sin_wave]

    bin_wave = struct.pack("h" * len(sin_wave), *sin_wave)

    w = wave.Wave_write("sin.wav")
    p = (1, 2, fs, len(bin_wave), 'NONE', 'not compressed')
    w.setparams(p)
    w.writeframes(bin_wave)
    w.close()
    print(len(sin_wave))

if __name__=='__main__':
    print("beeping...")
    create_wave(A, f0, fs, sec) 
    print("HUH?")