import mne
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

fig, ax = plt.subplots()
print("Plotting ERP...")

def load_and_process_eeg(my_eeg_data, makers_data, tmin=-0.2, tmax=1.5, sfreq=250):
    # Load EEG data

    # eeg_data = pd.read_csv('eeg_data.csv')
    eeg_data_temp = pd.read_csv('eeg_data_r.csv')
    channel_names = eeg_data_temp.columns[1:].tolist()
    data = eeg_data_temp[channel_names].values.T

    # Create MNE Info object and Raw object
    info = mne.create_info(ch_names=channel_names, sfreq=sfreq, ch_types='eeg')
    raw = mne.io.RawArray(data, info)

    # Load markers and create events array
    # markers = pd.read_csv('eeg_makers.csv')
    markers_temp = pd.read_csv('eeg_markers_r.csv')
    events = []
    eeg_timestamps = eeg_data_temp.iloc[:, 0].values
    for _, row in markers_temp.iterrows():
        nearest_idx = np.abs(eeg_timestamps - row['timestamp']).argmin()
        event_id = int(row['marker'][1:])
        events.append([nearest_idx, 0, event_id])
    events = np.array(events, dtype=int)
    # picks = ['EEG024']
    picks = ['Cz']
    # Create epochs and compute ERP
    epochs = mne.Epochs(raw, events,
                        event_id=None,
                        tmin=tmin,
                        tmax=tmax,
                        baseline=(None, 0),
                        preload=True,
                        picks=picks,
                        event_repeated='drop')
    #
    erp = epochs.average()
    # erp.plot()
    # Update plot
    ax.clear()
    ax.plot(erp.times, erp.data.T)  # Convert times back to ms for plotting
    ax.set_title(f'Trial no.: {len(events)}')
    plt.pause(1)


def checking_range_for_erp(my_eeg_data, makers_data, index=0, tmin=-0.2, tmax=1.5, sfreq=250):
    # length of the makers_data is > 0
    if len(makers_data) == 0:
        print("No markers found in the data")
        return False

    if len(makers_data) <= index:
        print("The index is out of range")
        return False

    # get the markers at index 0
    # print(makers_data)
    marker = makers_data.iloc[0]
    # get the timestamp of the marker
    marker_timestamp = marker['timestamp']
    # print(marker_timestamp)
    # checking whether the marker is within the range of the data
    start_time = marker_timestamp + tmin
    end_time = marker_timestamp + tmax
    # get the eeg_timestamps from index
    eeg_timestamps = my_eeg_data.index
    # print(eeg_timestamps)
    # print(eeg_timestamps[0], eeg_timestamps[-1])
    if start_time < eeg_timestamps[0] or end_time > eeg_timestamps[-1]:
        print("The marker is not within the range of the EEG data")
        return False
    else:
        return True


# # Example usage
if __name__ == '__main__':
    # Load your EEG data here (update with your data path and format)
    # eeg data with hunk_df = pd.DataFrame(eeg_chunk, columns=channel_names, index=eeg_timestamps)
    eeg_data = pd.read_csv('./Using_sending_scv_data/eeg_data.csv')
    # eeg_data = pd.read_csv('eeg_data_r.csv')
    # print(eeg_data)
    # Load your marker data here (update with your data path
    marker_data = pd.read_csv('./Using_sending_scv_data/eeg_markers.csv')
    # marker_data = pd.read_csv('eeg_markers_r.csv')
    # print(marker_data)
    load_and_process_eeg(eeg_data, marker_data)
    # print(checking_range_for_erp(eeg_data, marker_data, index=3))

