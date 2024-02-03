#!/usr/bin/python3

import argparse
import json
import requests
import time

# For debug purposes only
#import sys
#sys.argv.extend(['-c', "M7TLB"])
#sys.argv.extend(['Another test of the script... I think it''s almost ready to ship now. I''ll push it to GitHub tomorrow and let people break it.'])
#sys.argv.extend(['--send'])


def get_settings(json_file):

  with open(json_file) as settings_file:
    file_contents = settings_file.read()

  return json.loads(file_contents)


def get_args():
  parser = argparse.ArgumentParser(
                    prog='sendpage.py',
                    description='Send a message to one or more subscribers via the DAPNET service.',
                    epilog='Text at the bottom of help')  

  parser.add_argument("-c", "--calls", required=True, help="A list of callsigns or aliases, separated by commas - NO SPACES.  These will be deduplicated, in case multiples of the same callsign appear in the callsign or aliases lists.")
  parser.add_argument("message", help="The message you want to send \"IN QUOTES\".  If the total message (including your own callsign) goes beyond 80 characters, your message will be split into multiple parts.")
  parser.add_argument("--send", action="store_true", required=False, help="Specify this switch to actually send the message, otherwise this script will just show you what might happen.  Really useful to see how your messages will be sent before they actually are.")

  return parser.parse_args()


def get_callsign_list(calls):

  final_list = []
  temp_list = []

  callsign_list = calls.replace(" ", "").split(",")
  callsign_list = list(dict.fromkeys(callsign_list))

  for call in callsign_list:

    found = 0
    for node in settings["aliases"]:
      if node.upper() == call.upper():
        temp_list = settings["aliases"][node].split(",")
        final_list += temp_list
        found = 1
    if found == 0:
        final_list.append(call.upper())

  return list(dict.fromkeys(final_list))


def get_message_list(message, settings):

  mycall = settings["user"]["mycall"].upper()                                 # Get my own callsign from the settings

                                                                              # Work out various values and lengths
  prefix_length = len(mycall) + 2
  counter_length = 3
  message_length = len(message)
  message_max_length = 80
  multimessage_count = 0
  multimessage_prefix_length = prefix_length + counter_length
  multimessage_max_length = message_max_length - multimessage_prefix_length

  message_words = []
  interim_messages = []
  final_messages = []
  temp_message = ""

                                                                                # Clean up message string
  message = message.replace("  ", " ").replace("  ", " ").replace("  ", " ").strip()

  if prefix_length + message_length <= 80:                                      # If this is only a single-part message
    multimessage_count = 1                                                      # Just add it to the list
    interim_messages.append(mycall + ": " + message)
  else:                                                                         # But if it's multi-part
    message_words = message.split(" ")                                          # Split the message into words and then rebuild
                                                                                # it so that full words don't breach the maximum
    for word in message_words:
      if len(temp_message + " " + word) <= multimessage_max_length:
        temp_message += " " + word
      else:                                                                     # and then put a counter in the message as well
        multimessage_count += 1
        interim_messages.append(mycall + ": " + str(multimessage_count) + "/{?}" + temp_message)
        temp_message = " " + word

    multimessage_count += 1
    interim_messages.append(mycall + ": " + str(multimessage_count) + "/{?}" + temp_message)

  for message in interim_messages:                                              # Replace the total token with the actual number
    final_messages.append(message.replace("{?}", str(multimessage_count)))      # of messages in the multi-part, now we know it

  return final_messages, multimessage_count


def send_messages(callsign_list, message_list, send, settings):

                                                                                # Get all of the DAPNET config from the settings
  dapnet_user = settings["dapnetapi"]["user"]
  dapnet_pass = settings["dapnetapi"]["pass"]
  dapnet_txarea = list(dict.fromkeys(settings["dapnetapi"]["txarea"].replace(" ", "").split(",")))
  dapnet_api = settings["dapnetapi"]["api"]

  if send:
    print("================")
    print("SENDING MESSAGES")
    print("================")
  else:
    print("====================================")
    print("TEST MODE - displaying messages only")
    print("====================================")

  print("")

  print("Messages " + ("will be" if send else "would have been") + " sent to the following callsigns:")
  print(callsign_list)

  print("")

  # Actually send (or not) the derived messages
  messages_sent = 0
  response_text = "test"
  
  for message in message_list:
    dapnet_message = {}

    dapnet_message["text"] = message
    dapnet_message["callSignNames"] = callsign_list
    dapnet_message["transmitterGroupNames"] = dapnet_txarea
    dapnet_message["emergency"] = False

    dapnet_json = json.dumps(dapnet_message).encode("utf-8")
    dapnet_headers = {'Content-type': 'application/json'}

    if send:
      response = requests.post(dapnet_api, headers=dapnet_headers, auth=(dapnet_user, dapnet_pass), data=dapnet_json)
      response_text = str(response.status_code)

    print ("[" + response_text + "] " + message)

    messages_sent += 1

    if message_count != messages_sent and send == 1:
      print("        ** Waiting 5 seconds before sending the next part...")
      time.sleep(5)

  print("")
  print("** Done!")


args = get_args()                                                               # Get arguments
settings = get_settings('sendpage.json')                                        # Get settings 
callsign_list = get_callsign_list(args.calls)                                           # Get final calls list
message_list, message_count = get_message_list(args.message, settings)          # Get final messages list

send_messages(callsign_list, message_list, args.send, settings)                 # Send the final messages to the final calls list
