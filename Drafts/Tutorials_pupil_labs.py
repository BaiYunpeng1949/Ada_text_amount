import zmq
import time
import msgpack as serializer
import msgpack


"""
Learning materials:   https://docs.pupil-labs.com/developer/core/network-api/
Network API.
"""

# Commands enumerators.
"""
'R'  # start recording with auto generated session name
'R rec_name'  # start recording named "rec_name"
'r'  # stop recording
'C'  # start currently selected calibration
'c'  # stop currently selected calibration
'T 1234.56'  # resets current Pupil time to given timestamp
't'  # get current Pupil time; returns a float as string.
'v'  # get the Pupil Core software version string

# IPC Backbone communication
'PUB_PORT'  # return the current pub port of the IPC Backbone
'SUB_PORT'  # return the current sub port of the IPC Backbone
"""

#################################################### Section 1: Pupil Remote 1 ####################################################################
# # Primary tests
# ctx = zmq.Context()
# pupil_remote = zmq.Socket(ctx, zmq.REQ)
# pupil_remote.connect('tcp://127.0.0.1:50020')
#
# # start recording
# pupil_remote.send_string('R')
# print(pupil_remote.recv_string())
#
# time.sleep(5)
# pupil_remote.send_string('r')
# print(pupil_remote.recv_string())

"""
The python scripts example is from:
https://github.com/pupil-labs/pupil-helpers/blob/master/python/pupil_remote_control.py
"""
####################################################### Section 2: Pupil Groups #################################################################
# # Senior tests.
# if __name__ == "__main__":
#     from time import sleep, time
#
#     # Setup zmq context and remote helper
#     ctx = zmq.Context()
#     socket = zmq.Socket(ctx, zmq.REQ)
#     socket.connect("tcp://127.0.0.1:50020")
#
#     # Measure round trip delay
#     t = time()
#     socket.send_string("t")
#     print(socket.recv_string())
#     print("Round trip command delay:", time() - t)
#
#     # set current Pupil time to 0.0
#     socket.send_string("T 0.0")
#     print(socket.recv_string())
#
#     # start recording
#     sleep(1)
#     socket.send_string("R")
#     print(socket.recv_string())
#
#     sleep(5)
#     socket.send_string("r")
#     print(socket.recv_string())
#
#     # send notification:
#     def notify(notification):
#         """Sends ``notification`` to Pupil Remote"""
#         topic = "notify." + notification["subject"]
#         payload = serializer.dumps(notification, use_bin_type=True)
#         socket.send_string(topic, flags=zmq.SNDMORE)
#         socket.send(payload)
#         return socket.recv_string()
#
#     # test notification, note that you need to listen on the IPC to receive notifications!
#     notify({"subject": "calibration.should_start"})
#     sleep(5)
#     notify({"subject": "calibration.should_stop"})

####################################################### Section 3: IPC Backbone #################################################################
import zmq

ctx = zmq.Context()
# The REQ talks to Pupil remote and receives the session unique IPC SUB PORT
pupil_remote = ctx.socket(zmq.REQ)

ip = 'localhost'  # If you talk to a different machine use its IP.
port = 50020  # The port defaults to 50020. Set in Pupil Capture GUI.

pupil_remote.connect(f'tcp://{ip}:{port}')

# Request 'SUB_PORT' for reading data
pupil_remote.send_string('SUB_PORT')
sub_port = pupil_remote.recv_string()   # sub stands for subscriber.

# Request 'PUB_PORT' for writing data
pupil_remote.send_string('PUB_PORT')
pub_port = pupil_remote.recv_string()   # pub stands for publisher.
# Some following up knowledge: The publishers are the ones which publish messages regarding certain “topics”. The subscribers can then “subscribe” to any of these topics and receive the messages published by the publishers for that topic. The broker is the central authority responsible for maintaining and managing the message flows, topics, and data abstraction.

# ...continued from above
# Assumes `sub_port` to be set to the current subscription port
subscriber = ctx.socket(zmq.SUB)
subscriber.connect(f'tcp://{ip}:{sub_port}')
subscriber.subscribe('pupil.')  # receive all gaze messages

# we need a serializer
while True:
    """
    All messages on the IPC Backbone are multipart messages containing (at least) two message frames:
    Frame 1 contains the topic string, e.g. pupil.0, logging.info, notify.recording.has_started
    Frame 2 contains a msgpack encoded key-value mapping. This is the actual message. We choose msgpack as the serializer due to its efficient format (45% smaller than json, 200% faster than ujson) and because encoders exist for almost every language.
    """
    topic, payload = subscriber.recv_multipart()
    message = msgpack.loads(payload)
    # print(f"{topic}: "
    #       f"{message[b'timestamp']},"   # Timestamp.
    #       f"{message[b'base_data'][0][b'id']}, "    # Eye ID.
    #       f"{message[b'base_data'][0][b'diameter']}, "  # Pupil Diameter.
    #       f"{message[b'base_data'][0][b'confidence']}"  # Confidence.
    #       )
    print(f"{topic}: "
          f"{message}"
          )
