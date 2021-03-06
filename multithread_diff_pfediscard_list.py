#!/usr/bin/python
## Importing free packages
from jnpr.junos import Device
import re
import os
import sys
import argparse
import time
import warnings
import threading
from lxml import etree
from xml.dom.minidom import parse, parseString
from xml.etree import ElementTree
import xml.etree.ElementTree as ET

## This function returns, array of pfe discards per fpc
def fediscard(dev,fpclist):
    # Input: This function gets fpclist and dev pointer.
    # Output: returns array of pfe discards per fpc.
    fpcs_fdiscard = []
    fpcs_brdiscard = []
    fpcs_derror = []
    fpcs_tdiscard = []
    fpcs_tkdiscard = []
    fpcs_bttdiscard = []
    fpcs_sudiscard = []
    fpcs_sodiscard = []
    fpcs_nhdiscard = []
    fpcs_iidiscard = []
    fpcs_icdiscard = []
    fpcs_ichecksum = []
    fpcs_omtu = []
    for num in fpclist:
        fpc_lxml_elements = dev.rpc.get_pfe_statistics(fpc=num)
        string = etree.tostring(fpc_lxml_elements)
        dom = parseString(string)
        #pfehwdiscard = dom.getElementsByTagName("pfe-hardware-discard-statistics")
        #for var in pfehwdiscard:
        fdiscard = int(dom.getElementsByTagName("fabric-discard")[0].firstChild.data)
        brdiscard = int(dom.getElementsByTagName("bad-route-discard")[0].firstChild.data)
        derror = int(dom.getElementsByTagName("data-error-discard")[0].firstChild.data)
        tdiscard = int(dom.getElementsByTagName("timeout-discard")[0].firstChild.data)
        tkdiscard = int(dom.getElementsByTagName("truncated-key-discard")[0].firstChild.data)
        bttdiscard = int(dom.getElementsByTagName("bits-to-test-discard")[0].firstChild.data)
        sudiscard = int(dom.getElementsByTagName("stack-underflow-discard")[0].firstChild.data)
        sodiscard = int(dom.getElementsByTagName("stack-overflow-discard")[0].firstChild.data)
        nhdiscard = int(dom.getElementsByTagName("nexthop-discard")[0].firstChild.data)
        iidiscard = int(dom.getElementsByTagName("invalid-iif-discard")[0].firstChild.data)
        icdiscard = int(dom.getElementsByTagName("info-cell-discard")[0].firstChild.data)
        ichecksum = int(dom.getElementsByTagName("input-checksum")[0].firstChild.data)
        omtu = int(dom.getElementsByTagName("output-mtu")[0].firstChild.data)
        fpcs_fdiscard.append(fdiscard)
        fpcs_brdiscard.append(brdiscard)
        fpcs_derror.append(derror)
        fpcs_tdiscard.append(tdiscard)
        fpcs_tkdiscard.append(tkdiscard)
        fpcs_bttdiscard.append(bttdiscard)
        fpcs_sudiscard.append(sudiscard)
        fpcs_sodiscard.append(sodiscard)
        fpcs_nhdiscard.append(nhdiscard)
        fpcs_iidiscard.append(iidiscard)
        fpcs_icdiscard.append(icdiscard)
        fpcs_ichecksum.append(ichecksum)
        fpcs_omtu.append(omtu)
    return fpcs_fdiscard,fpcs_brdiscard,fpcs_derror, fpcs_tdiscard, fpcs_tkdiscard, fpcs_bttdiscard, fpcs_sudiscard, fpcs_sodiscard, fpcs_nhdiscard, fpcs_iidiscard, fpcs_icdiscard, fpcs_ichecksum, fpcs_omtu

## This function returns, online fpc in specific device
def onlinefpcs(dev):
    # Input: Dev Pointer
    # Output: Array of FPC sloat which are online 
    fpc_lxml_elements = dev.rpc.get_fpc_information()
    string_fpc = etree.tostring(fpc_lxml_elements)
    dom_fpc = parseString(string_fpc)
    cms = dom_fpc.getElementsByTagName("fpc")
    print 'Number of FPCs Sloat', len(cms)
    fpcsloat = []
    for cm in cms:
        state = str(cm.getElementsByTagName("state")[0].firstChild.data)
        fpcsn = cm.getElementsByTagName("slot")[0].firstChild.data
        fpc = re.match(r"Online", state)
        if fpc:
            fpcsloat.append(str(fpcsn))
    return fpcsloat

## This function, first calls function onlinefpcs and retrieves number of online FPCs 
## Based on output from onlinefpcs - it calls function fediscard two time with wait been passed from main function
## And lastly it calculates diff of array retrieved from 2 set of fediscard and present diff if any count is > 0
def checkfedrops_devices(dev,iteration,wait):
    #Input: Dev Pointer,iteration and Wait time
    #Output: Print FE discard diff for each FPC for list of devices
    print "Function been called %sdev" %(dev)
    dev = Device(host=dev.strip(), user="a.b.c.d", passwd="pass123")
    try:
        dev.open()
        warnings.filterwarnings('ignore')
    except Exception, e:
        print "Unable to connect to host:", e
    fpclist = onlinefpcs(dev)
    for count in xrange(iteration):
        print "Collecting first set of data %s" % (dev)
        fpcs_fdiscard,fpcs_brdiscard,fpcs_derror, fpcs_tdiscard, fpcs_tkdiscard, fpcs_bttdiscard, fpcs_sudiscard, fpcs_sodiscard, fpcs_nhdiscard, fpcs_iidiscard, fpcs_icdiscard, fpcs_ichecksum, fpcs_omtu  = fediscard(dev,fpclist)
        print "Sleeping for %s second on device %s" % (wait,dev)
        time.sleep(wait)
        print "Collecting second set of data %s" % (dev)
        fpcs_fdiscard2,fpcs_brdiscard2,fpcs_derror2, fpcs_tdiscard2, fpcs_tkdiscard2, fpcs_bttdiscard2, fpcs_sudiscard2, fpcs_sodiscard2, fpcs_nhdiscard2, fpcs_iidiscard2, fpcs_icdiscard2, fpcs_ichecksum2, fpcs_omtu2  = fediscard(dev,fpclist) 
        i=0
        for fpc in fpclist:
            diff_fdiscard = fpcs_fdiscard2[i] - fpcs_fdiscard[i]
            diff_brdiscard = fpcs_brdiscard2[i] - fpcs_brdiscard[i]
            diff_derror = fpcs_derror2[i] - fpcs_derror[i]
            diff_tdiscard = fpcs_tdiscard2[i] - fpcs_tdiscard[i]
            diff_tkdiscard = fpcs_tkdiscard2[i] - fpcs_tkdiscard[i]
            diff_bttdiscard = fpcs_bttdiscard2[i] - fpcs_bttdiscard[i]
            diff_sudiscard = fpcs_sudiscard2[i] - fpcs_sudiscard[i]
            diff_sodiscard = fpcs_sodiscard2[i] - fpcs_sodiscard[i]
            diff_nhdiscard = fpcs_nhdiscard2[i] - fpcs_nhdiscard[i]
            diff_iidiscard = fpcs_iidiscard2[i] - fpcs_iidiscard[i]
            diff_icdiscard = fpcs_icdiscard2[i] - fpcs_icdiscard[i]
            diff_ichecksum = fpcs_ichecksum2[i] - fpcs_ichecksum[i]
            diff_omtu = fpcs_omtu2[i] - fpcs_omtu[i]
            if diff_fdiscard > 0:
                print "dev %s For FPC %s, Fabric Drop count increases %s" % (dev, fpc,diff_fdiscard)
            if diff_brdiscard > 0:
                print "dev %s For FPC %s, Bad Route Discard count increases %s" % (dev,fpc,diff_brdiscard)
            if diff_derror > 0:
                print "dev %s For FPC %s, Data Error count increases %s" % (dev,fpc,diff_derror) 
            if diff_tdiscard > 0:
                print "dev %s For FPC %s, Timeout Discard increases %s" % (dev,fpc,diff_tdiscard)   
            if diff_tdiscard > 0:
                print "dev %s For FPC %s, Timeout Discard increases %s" % (dev,fpc,diff_tdiscard)  
            if diff_tkdiscard > 0:
                print "dev %s For FPC %s, Truncated Key Discard increases %s" % (dev,fpc,diff_tkdiscard)
            if diff_bttdiscard > 0:
                print "dev %s For FPC %s, Bit to test Discard increases %s" % (dev,fpc,diff_bttdiscard)
            if diff_sudiscard > 0:
                print "dev %s For FPC %s, Stack Underflow Discard increases %s" % (dev,fpc,diff_sudiscard)
            if diff_sodiscard > 0:
                print "dev %s For FPC %s, Stack Overflow Discard increases %s" % (dev,fpc,diff_sodiscard)
            if diff_nhdiscard > 0:
                print "dev %s For FPC %s, Nexthop Discard increases %s" % (dev,fpc,diff_nhdiscard)
            if diff_iidiscard > 0:
                print "dev %s For FPC %s, Invalid iif Discard increases %s" % (dev,fpc,diff_iidiscard)
            if diff_icdiscard > 0:
                print "dev %s For FPC %s, Info Cell Discard increases %s" % (dev,fpc,diff_icdiscard)
            if diff_ichecksum > 0:
                print "dev %s For FPC %s, Input Checksum Drop increases %s" % (dev,fpc,diff_ichecksum)
            if diff_omtu > 0:
                print "dev %s For FPC %s, Output MTU Drop increases %s" % (dev,fpc,diff_omtu)
            i+=1
        count+=1
    dev.close()

## This class is to create multithread environment
## Logic is - to troubleshoot list of device at same time and for each device, we are creating saperate thread 
## With this - we can faster our investigation on list of devices at same time

class newthread (threading.Thread):
    def __init__(self,threadID,dev,nus,wait):
        print "In init %s" % (dev)
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.dev = dev
        self.nus = nus
        self.wait = wait
    def run(self):
        print "In newthread %s" % (self.dev)
        checkfedrops_devices(self.dev,self.nus,self.wait)

## This is main function, and with arparser, I am passing a file name called devices
##% cat devices 
##172.22.146.105
##172.22.146.51
##172.22.146.106
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Enter File Name for devices")
    parser.add_argument('-f', action='store',dest='devfile', help='Enter File Name for Device')
    result = parser.parse_args()
    dfile = open(result.devfile,'r')
    nthread = 1
    nus = 5
    wait = 5
    threadfun = []
    iteration = 1
    nes = []
    for devices in dfile:
        dev = devices.strip()
        nes.append(dev)
    dfile.close()
    print nes
    for ne in nes:
        thread = ne+str(nthread)
        print thread
        try:
            thread = newthread(nthread,ne,nus,wait)
            thread.start()
        except:
            print "Error: unable to start thread" 
        nthread+=1
