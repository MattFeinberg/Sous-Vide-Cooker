Matt Feinberg, Fall 2020, Tufts University

NOTE: Watch the .mp4 video in the repo for a video demonstration of my Sous Vide Cooker

Background:
  For my final project in my introductor engineering course, Engineering in the 
  Kitchen, I was tasked with modifying, trasnforming, or creating a kitchen 
  appliance. I chose to convert a basic old crock pot that had been in my basement
  for a long time into a sous vide cooker. I used an ESP32 microcontroller with
  MicroPython to build my Sous Vide cooker. Users interact with capacitive touch
  sensors to specify cooking temperatures and times. I also used a Raspberry Pi to
  run an MQTT broker to interact with a smart plug that powers on/off depending on
  values sent by the ESP32. The Raspberry Pi also makes it easier to gather cooking
  data like temperature and timestamps.

Files/Directories:
  Sous-Vide-Video.mp4: Video demonstration of the machine in use
  Python Files:
    SousVide_code.py: The main script for the machine, which is run on the ESP32.
    Subscribe_and_write.py: This script is run on the Raspberry Pi to catch data
                            sent by the ESP32 and writes it to a csv file.
  First Steak Analysis:
    first_steak_analysis.py: This script generates graphs of the data from the
                             first steak I cooked
    first_steak_graph.png: graph of temperature vs time for the first steak I cooked
                           (note that the desired cooking temperature was 55)
    graph_with_power.png: The same as the previously listed graph, but also has vertical
                          lines indicating when the machine was turned on/off to maintain
                          temperature
    Two .csv files containing data from the first steak I cooked
