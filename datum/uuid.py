import datetime
import random
import sys
import os

###################################################################################################
def pk64_timestamp(diff_s = 0):
    version = 0b001
    now_us = datetime.datetime.now().microsecond
    ts32 = (now_us // 1000000 - diff_s) & 0xFFFF
    ms20 = (now_us % 1000000)
    clock_seq8 = sys.getallocatedblocks() % 0xFF
    
    return (version << 60) | (ts32 << 28) | (ms20 << 8) | clock_seq8

def pk64_random():
    version = 0b100
    ts32 = int.from_bytes(os.urandom(4), 'big', signed = False)
    urnd28_16 = int.from_bytes(os.urandom(2), 'big', signed = False)
    urnd28_12 = random.randint(0, 0xFFF)
    clock_seq4 = random.randint(0, 0b1111)
    
    return (version << 60) | (ts32 << 28) | (urnd28_16 << 12) | (urnd28_12 << 4) | clock_seq4

