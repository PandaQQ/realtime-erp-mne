from pylsl import StreamInfo, StreamOutlet
import numpy as np
import time
import mne
import pandas as pd

# DataFrame to store EEG data
eeg_data_pd = pd.DataFrame()
eeg_makers_pd = pd.DataFrame()

# Load your EEG dataset
eeg_data = mne.io.read_raw_eeglab('./data/att_006_game_ref_clean.set', preload=True)

# Define stream parameters for EEG
eeg_info = StreamInfo(name='EEG',
                      type='EEG',
                      channel_count=eeg_data.info['nchan'],
                      nominal_srate=eeg_data.info['sfreq'],
                      channel_format='float32',
                      source_id='eeg01')

eeg_outlet = StreamOutlet(eeg_info)

# Get events from annotations in the data
events, event_ids = mne.events_from_annotations(eeg_data)

# Define and setup Marker Stream
marker_info = StreamInfo(name='Markers', type='Markers', channel_count=1,
                         nominal_srate=0, channel_format='string', source_id='markers01')
marker_outlet = StreamOutlet(marker_info)

# Stream data
chunk_length = 1   # in seconds
chunk_samples = int(chunk_length * eeg_data.info['sfreq'])
event_type = 'S213'

start_time = time.time()
for i in range(0, len(eeg_data), chunk_samples):
    chunk = eeg_data[:, i:i+chunk_samples][0]
    current_time = time.time()
    print(f"Sending chunk {i} at {current_time} seconds")
    # eeg_outlet.push_chunk(chunk.tolist(), current_time)
    # save the data to csv chunk and time
    # also index with current time + i / eeg_data.info['sfreq']
    # add timestamp to the chunk
    chunk_df = pd.DataFrame(chunk.T,
                            columns=eeg_data.ch_names,
                            index=[current_time + j / eeg_data.info['sfreq'] for j in range(chunk_samples)])
    # chunk_df['timestamp'] = chunk_df.index
    # append index as timestamp into the chunk_df
    # eeg_data_pd = pd.concat([eeg_data_pd, chunk_df])
    # eeg_data_pd.to_csv('eeg_data.csv')
    # exit(0)
    # send chunk_df to outlet
    # for j in range(chunk_samples):
    #     eeg_outlet.push_sample(chunk[:, j].tolist(), current_time + j / eeg_data.info['sfreq'])
    # send chunk_df as a whole
    eeg_outlet.push_chunk(chunk_df.values.tolist(), chunk_df.index)

    # Check and send markers if any within this chunk
    chunk_events = events[(events[:, 0] >= i)
                          & (events[:, 0] < i + chunk_samples)
                          & (events[:, 2] == event_ids[event_type])]
    # if chunk_events
    for event in chunk_events:
        marker_time = current_time + ((event[0] - i) / eeg_data.info['sfreq'])
        # print(f"Sending marker {event_type} at {marker_time}")
        print(f"Sending marker {[str(event_type)]} at {marker_time}")
        # marker_outlet.push_sample([str(event_type)], marker_time)
        # save the data to csv
        # marker_df = pd.DataFrame([[marker_time, str(event_type)]], columns=['timestamp', 'marker'])
        # eeg_makers_pd = pd.concat([eeg_makers_pd, marker_df])
        # eeg_makers_pd.to_csv('eeg_markers.csv')
        # send  marker_df to outlet
        marker_outlet.push_sample([str(event_type)], marker_time)

    time.sleep(max(0, start_time + i / eeg_data.info['sfreq'] - time.time()))


    if i >= len(eeg_data):
        print("End of data")
        i = 0
    # time.sleep(1)