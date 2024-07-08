from pylsl import StreamInlet, resolve_stream
import numpy as np
import time
import mne
import pandas as pd
import offline_erp as my_erp

n_channels = 32  # Adjust based on your EEG cap setup
channel_types = 'eeg'
#  ,Fp1,Fz,F3,F7,FT9,FC5,FC1,C3,T7,TP9,CP5,CP1,Pz,P3,P7,O1,Oz,O2,P4,P8,TP10,CP6,CP2,Cz,C4,T8,FT10,FC6,FC2,F4,F8,Fp2
channel_names = ['Fp1', 'Fz', 'F3', 'F7', 'FT9', 'FC5', 'FC1', 'C3', 'T7', 'TP9', 'CP5', 'CP1', 'Pz', 'P3', 'P7', 'O1',
                 'Oz', 'O2', 'P4', 'P8', 'TP10', 'CP6', 'CP2', 'Cz', 'C4', 'T8', 'FT10', 'FC6', 'FC2', 'F4', 'F8', 'Fp2']


# Function to find and create an inlet for a specific type of stream
def create_inlet(stream_type):
    print(f"Looking for a {stream_type} stream...")
    streams = resolve_stream('type', stream_type)
    if streams:
        inlet = StreamInlet(streams[0])
        print(f"{stream_type} stream found and connected!")
        return inlet
    else:
        print(f"No {stream_type} stream found.")
        return None


# Create inlets for both EEG and Marker streams
eeg_inlet = create_inlet('EEG')
marker_inlet = create_inlet('Markers')

# DataFrame to store EEG data
eeg_data = pd.DataFrame()
eeg_makers = pd.DataFrame()

# Define the duration of each data chunk in seconds for EEG data (e.g., 0.5 seconds)
chunk_duration = 1
if eeg_inlet:
    samples_per_chunk = int(chunk_duration * eeg_inlet.info().nominal_srate())

# Receive data in chunks
index = 0
while True:
    if eeg_inlet:
        # Get a chunk of EEG data
        eeg_chunk, eeg_timestamps = eeg_inlet.pull_chunk(timeout=0.5)
        if eeg_timestamps:
            print("Received EEG chunk at time:", time.time())
            print("EEG chunk shape:", np.shape(eeg_chunk))
            # Append new data to the DataFrame
            chunk_df = pd.DataFrame(eeg_chunk, columns=channel_names, index=eeg_timestamps)
            chunk_df['timestamp'] = eeg_timestamps
            eeg_data = pd.concat([eeg_data, chunk_df])
            # save the data to csv
            eeg_data.to_csv('eeg_data_r.csv')

    if marker_inlet:
        # Get markers
        marker, marker_timestamps = marker_inlet.pull_sample(timeout=0.0)
        if marker_timestamps:
            print("Received marker:", marker, "at time:", marker_timestamps)
            # Append new data to the DataFrame
            marker_df = pd.DataFrame({'timestamp': [marker_timestamps], 'marker': marker[0]})
            eeg_makers = pd.concat([eeg_makers, marker_df])
            # save the data to csv
            eeg_makers.to_csv('eeg_markers_r.csv')
            # print(eeg_makers)

    # here to generate the ERP
    if my_erp.checking_range_for_erp(eeg_data, eeg_makers, index):
        print("Generating ERP... with index: ", index)
        my_erp.load_and_process_eeg(eeg_data, eeg_makers)
        index += 1

    # Add a small sleep to prevent the loop from consuming too much CPU if no data is available
    # time.sleep(0.01)
