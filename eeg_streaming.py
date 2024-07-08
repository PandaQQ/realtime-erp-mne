import time
from random import random
from pylsl import StreamInfo, StreamOutlet

# Create a new stream info for EEG data
# - name: Name of the stream
# - channel_count: Number of channels
# - nominal_srate: The sampling rate (in Hz).
# - channel_format: Data type of the data transmitted (e.g., float32)
# - source_id: An identifier for the data source
eeg_info = StreamInfo('SimulatedEEG',
                      'EEG',
                      8,
                      100,
                      'float32',
                      'myuid34234')

# Create an outlet to send data
outlet = StreamOutlet(eeg_info)

print("Streaming simulated EEG data...")

# Generate and send data continuously
while True:
    # Create a sample which is a list of random numbers (simulating EEG data)
    sample = [random() for _ in range(8)]
    # Send the sample via LSL
    outlet.push_sample(sample)
    # Sleep for 10 milliseconds before the next sample
    time.sleep(0.01)