import math, pywt, numpy as np
import csv
import sys
import os
import xml.etree.ElementTree

from datetime import datetime

import zmq
from msgpack import loads

import time
from threading import Thread
from queue import Queue

import keyboard
import datetime

from socket import *
import json

"""
To use this established data processing file, simply plug the pupil core onto a laptop/PC and run the "pupil capture.exe" on it.
"""


host = '255.255.255.255'
port = 50000    # Randomly choose a portal.

confidenceThreshold = .2
windowLengthSeconds = 60
maxSamplingRate = 60    # Changed to 60Hz due to our hardware limitations.
minSamplesPerWindow = maxSamplingRate * windowLengthSeconds
# wavelet = 'sym8'
wavelet = 'sym16'

MODE_2D = '2d c++'
MODE_3D = 'pye3d 0.3.0 real-time'
INDEX_EYE_0 = 0
INDEX_EYE_1 = 1

global is_3D, is_2_pupils
is_3D = False
is_2_pupils = False


class ProcessingThread(Thread):
    def __init__(self, pupilData, targetsocket):
        Thread.__init__(self)
        self.data = pupilData
        self.targetsocket = targetsocket

    def run(self):
        global threadRunning
        processData(self.data, self.targetsocket)
        threadRunning = False


class ProcessingThread2Pupils(Thread):
    def __init__(self, pupilData, pupilData1, targetsocket):
        Thread.__init__(self)
        self.data = pupilData
        self.data_1 = pupilData1
        self.targetsocket = targetsocket

    def run(self):
        global threadRunning
        processData1(self.data, self.data_1, self.targetsocket)
        threadRunning = False


class PupilData(float):
    def __init__(self, dia):
        self.X = dia
        self.timestamp = 0
        self.confidence = 0


def ipa(d):
    # obtain 2-level DWT of pupil diameter signal d
    try:
        (cA2, cD2, cD1) = pywt.wavedec(d, wavelet, 'per', level=2)
    # (cA2,cD2,cD1) = pywt.wavedec(d, 'db8','per',level=2)
    except ValueError:
        return

    # get signal duration (in seconds)
    tt = d[-1].timestamp - d[0].timestamp
    # print("timestamp", tt)

    # using data from Pedrotti et al
    # tt = 1.0

    # normalize by 1=2j , j = 2 for 2-level DWT
    cA2[:] = [x / math.sqrt(4.0) for x in cA2]
    cD1[:] = [x / math.sqrt(2.0) for x in cD1]
    cD2[:] = [x / math.sqrt(4.0) for x in cD2]

    # detect modulus maxima , see Listing 2
    cD2m = modmax(cD2)

    # threshold using universal threshold lambda_univ = s*sqrt(p(2 log n))
    lambda_univ = np.std(cD2m) * math.sqrt(2.0 * np.log2(len(cD2m)))
    # where s is the standard deviation of the noise
    cD2t = pywt.threshold(cD2m, lambda_univ, mode="hard")

    # compute IPA
    ctr = 0
    for i in range(len(cD2t)):
        # print(cD2t[i])
        if math.fabs(cD2t[i]) > 0:
            ctr += 1

    # print(ctr)
    IPA = float(ctr) / tt

    return IPA


def modmax(d):
    # compute signal modulus
    m = [0.0] * len(d)
    for i in range(len(d)):
        m[i] = math.fabs(d[i])

    # if value is larger than both neighbours , and strictly
    # larger than either , then it is a local maximum
    t = [0.0] * len(d)

    for i in range(len(d)):
        ll = m[i - 1] if i >= 1 else m[i]
        oo = m[i]
        rr = m[i + 1] if i < len(d) - 2 else m[i]

        if (ll <= oo and oo >= rr) and (ll < oo or oo > rr):
            # compute magnitude
            t[i] = math.sqrt(d[i] ** 2)
        else:
            t[i] = 0.0

    return t


def lhipa(d):
    """
    Calculate the LHIPA from https://dl-acm-org.libproxy1.nus.edu.sg/doi/pdf/10.1145/3313831.3376394.
    :param d:
    :return:
    """
    # find max decomposition level
    w = pywt.Wavelet(wavelet)
    maxlevel = pywt.dwt_max_level(len(d), filter_len=w.dec_len)

    # set high and low frequency band indeces
    hif, lof = 1, int(maxlevel / 2)

    # get detail coefficients of pupil diameter signal d
    cD_H = pywt.downcoef('d', d, wavelet, 'per', level=hif)
    cD_L = pywt.downcoef('d', d, wavelet, 'per', level=lof)

    # normalize by 1/ 2j
    cD_H[:] = [x / math.sqrt(2 ** hif) for x in cD_H]
    cD_L[:] = [x / math.sqrt(2 ** lof) for x in cD_L]

    # obtain the LH:HF ratio
    cD_LH = cD_L
    for i in range(len(cD_L)):
        cD_LH[i] = cD_L[i] / cD_H[((2 ** lof) // (2 ** hif)) * i]   # Used a '//' instead of '/' to make sure the index is an integer.

    # detect modulus maxima , see Duchowski et al. [15]
    cD_LHm = modmax(cD_LH)

    # threshold using universal threshold λuniv = σˆ (2logn)
    # where σˆ is the standard deviation of the noise
    lambda_univ = np.std(cD_LHm) * math.sqrt(2.0*np.log2(len(cD_LHm)))
    cD_LHt = pywt.threshold(cD_LHm, lambda_univ, mode="less")

    # get signal duration (in seconds)
    # tt = d[-1].timestamp() - d[0].timestamp()
    tt = d[-1].timestamp - d[0].timestamp

    # compute LHIPA
    ctr = 0
    for i in range(len(cD_LHt)):
        if math.fabs(cD_LHt[i]) > 0:
            ctr += 1
    LHIPA = float(ctr) / tt
    return LHIPA


def createSendSocket():
    backlog = 5
    size = 1024
    sock = socket(AF_INET, SOCK_DGRAM)
    sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    sock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
    return sock


def createPupilConnection():
    context = zmq.Context()
    # open a req port to talk to pupil
    addr = '127.0.0.1'  # remote ip or localhost
    req_port = "50020"  # same as in the pupil remote gui
    req = context.socket(zmq.REQ)
    req.connect("tcp://{}:{}".format(addr, req_port))
    # ask for the sub port
    req.send_string('SUB_PORT')
    sub_port = req.recv_string()

    # open a sub port to listen to pupil
    sub = context.socket(zmq.SUB)
    sub.connect("tcp://{}:{}".format(addr, sub_port))

    sub.setsockopt_string(zmq.SUBSCRIBE, 'pupil.')  # See Pupil Lab website, don't need to change here. "Pupil Datum Format": https://docs.pupil-labs.com/developer/core/overview/.

    return sub


def cleanup(old_data):
    stddev = np.std(old_data)
    mean = np.mean(old_data)

    filtered = []
    runner = 0.0

    for i in range(len(old_data)):
        currentData = PupilData(old_data[i].X)
        currentData.timestamp = old_data[i].timestamp
        distanceToMean = abs(currentData.X - mean)

        if distanceToMean < stddev * 2:
            filtered.append(currentData)
            runner += 1

    # print(str(stddev) + " / " + str(mean) + ' / ' + str(len(filtered)))

    return filtered


def cleanBlinks(data):
    blinks = []

    minNumForBlinks = 2
    numSamples = len(data)
    i = 0
    minConfidence = .25

    while i < numSamples:
        if data[i].confidence < minConfidence and i < numSamples - 1:
            runner = 1
            nextData = data[i + runner]
            while nextData.confidence < minConfidence:
                runner = runner + 1

                if i + runner >= numSamples:
                    break

                nextData = data[i + runner]

            if runner >= minNumForBlinks:
                blinks.append((i, runner))

            i = i + runner
        else:
            i = i + 1

    durationsSampleRemoveMS = 200
    numSamplesRemove = int(math.ceil(120 / (1000 / durationsSampleRemoveMS)))

    blinkMarkers = np.ones(numSamples)
    for i in range(len(blinks)):
        blinkIndex = blinks[i][0]
        blinkLength = blinks[i][1]

        for j in range(0, blinkLength):
            blinkMarkers[blinkIndex + j] = 0

        for j in range(0, numSamplesRemove):
            decrementIndex = blinkIndex - j
            incrementIndex = blinkIndex + blinkLength + j

            if decrementIndex >= 0:
                blinkMarkers[decrementIndex] = 0

            if incrementIndex < numSamples:
                blinkMarkers[incrementIndex] = 0

    newSamplesList = []

    for i in range(0, numSamples):
        if blinkMarkers[i] == 1:
            newSamplesList.append(data[i])

    return newSamplesList


def fixTimestamp(data):
    runner = 0.0
    for i in range(len(data)):
        data[i].timestamp = runner / 60.0   # Changed this from 120 to 60
        runner += 1


def processData(data, socket):
    blinkedRemoved = cleanBlinks(data)
    cleanedData = cleanup(blinkedRemoved)
    fixTimestamp(cleanedData)
    currentIPA = lhipa(cleanedData)

    valueString = ' ipa ' + str(currentIPA)
    # print(str(datetime.datetime.now()) + '  ' + valueString + '; ' + str(len(cleanedData)) + ' / ' + str(len(data)) + ' samples')
    socket.sendto(str.encode(str(round(currentIPA, 3))), (host, port))    # Send to their equipment.


def processData1(data, data_1, socket):
    blinkedRemoved = cleanBlinks(data)
    cleanedData = cleanup(blinkedRemoved)
    fixTimestamp(cleanedData)
    currentIPA = lhipa(cleanedData)

    blinkedRemoved1 = cleanBlinks(data_1)
    cleanedData1 = cleanup(blinkedRemoved1)
    fixTimestamp(cleanedData1)
    currentIPA1 = lhipa(cleanedData1)

    averagedCurrentIPA = 0.5 * (currentIPA1 + currentIPA1)
    socket.sendto(str.encode(str(round(averagedCurrentIPA, 3))), (host, port))


def receivePupilData(udp, pupilSocket):     # The "udp" is for "user datagram protocol".
    while True:
        try:
            topic = pupilSocket.recv_string()
            msg = pupilSocket.recv()
            msg = loads(msg, encoding='utf-8')
            # print("\n{}: {}".format(topic, msg))

            method = msg['method']
            id_eye = msg['id']

            # Check whether splitting 2 pupil data.
            global is_2_pupils
            if is_2_pupils is False:    # Default: don't split 2 pupils' data.
                # Check whether apply the 3D mode.
                global is_3D
                if is_3D is False:
                    data = PupilData(msg['diameter'])  # Collect the 2-D pixel data.
                    data.timestamp = msg['timestamp']
                    data.confidence = msg['confidence']

                    currentPupilData.append(data)
                elif is_3D is True:
                    if method == MODE_3D:
                        data = PupilData(msg['diameter_3d'])    # Calculate the 3-D mm model data.  Sometimes lacks this data.
                        data.timestamp = msg['timestamp']
                        data.confidence = msg['confidence']

                        currentPupilData.append(data)

                # currentPupilData.append(data)

                # Calculate and send out ipa data.
                while len(currentPupilData) > minSamplesPerWindow:
                    currentPupilData.pop(0)     # Remove the first element in the list.

                global threadRunning

                if len(currentPupilData) == minSamplesPerWindow and threadRunning is False:     # Wait for reaching 1-minute's windows length; enough data points.
                    threadRunning = True
                    processingThread = ProcessingThread(list(currentPupilData), udp)    # Iteratively apply and start threads.
                    processingThread.start()

            elif is_2_pupils:   # Split 2 pupils and average corresponding ipa data.
                # Check whether apply the 3D mode.
                if is_3D is False:
                    if id_eye == INDEX_EYE_0:
                        data_0 = PupilData(msg['diameter'])  # Collect the 2-D pixel data.
                        data_0.timestamp = msg['timestamp']
                        data_0.confidence = msg['confidence']

                        currentPupilData.append(data_0)
                    elif id_eye == INDEX_EYE_1:
                        data_1 = PupilData(msg['diameter'])  # Collect the 2-D pixel data.
                        data_1.timestamp = msg['timestamp']
                        data_1.confidence = msg['confidence']

                        currentPupilData1.append(data_1)
                elif is_3D:
                    if method == MODE_3D and id_eye == INDEX_EYE_0:
                        data = PupilData(msg['diameter_3d'])    # Calculate the 3-D mm model data.  Sometimes lacks this data.
                        data.timestamp = msg['timestamp']
                        data.confidence = msg['confidence']

                        currentPupilData.append(data)
                    elif method == MODE_3D and id_eye == INDEX_EYE_1:
                        data_1 = PupilData(
                            msg['diameter_3d'])  # Calculate the 3-D mm model data.  Sometimes lacks this data.
                        data_1.timestamp = msg['timestamp']
                        data_1.confidence = msg['confidence']

                        currentPupilData1.append(data_1)

                # Calculate and send out the ipa data.
                while len(currentPupilData) > minSamplesPerWindow:
                    currentPupilData.pop(0)     # Remove the first element in the list.
                while len(currentPupilData1) > minSamplesPerWindow:
                    currentPupilData1.pop(0)  # Remove the first element in the list.

                if len(currentPupilData) == minSamplesPerWindow and len(currentPupilData1) == minSamplesPerWindow and threadRunning is False:     # Wait for reaching 1-minute's windows length; enough data points.
                    threadRunning = True
                    processingThread = ProcessingThread2Pupils(list(currentPupilData), list(currentPupilData1), udp)    # Iteratively apply and start threads. TODO: make a new thread cope 2 pupils.
                    processingThread.start()

        except KeyboardInterrupt:
            break


def run_IPA_collection(is_3D_method, is_averaging_2_pupils):
    global threadRunning, currentPupilData, currentPupilData1, is_3D, is_2_pupils
    threadRunning = False
    currentPupilData = list()
    currentPupilData1 = list()     # Added to apply 2 pupil analysis.
    is_3D = is_3D_method
    is_2_pupils = is_averaging_2_pupils

    print(datetime.datetime.now())
    socket = createSendSocket()
    pupilSocket = createPupilConnection()  # Subscribe pupil data "Pupil Datum Format".

    receivePupilData(socket, pupilSocket)


if __name__ == '__main__':
    threadRunning = False
    currentPupilData = list()

    print(datetime.datetime.now())
    socket = createSendSocket()
    pupilSocket = createPupilConnection()   # Subscribe pupil data "Pupil Datum Format".

    receivePupilData(socket, pupilSocket)
