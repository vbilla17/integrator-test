def interpolate(data1, data1_timestamps, data1_packets, data2, data2_timestamps, data2_packets):
    start_packet = min(data1_packets[0], data2_packets[0])
    end_packet = max(data1_packets[-1], data2_packets[-1])
    num_packets = end_packet - start_packet

    data1_interp = []
    data2_interp = []
    data1_timestamps_interp = []
    data2_timestamps_interp = []

    for i in range(num_packets):
        if start_packet + i in data1_packets and data2_packets: # if packet exists for both data sets
            data1_interp.append(data1[i])
            data1_timestamps_interp.append(data1_timestamps[i])
            data2_interp.append(data2[i])
            data2_timestamps_interp.append(data2_timestamps[i])
        elif start_packet + i in data1_packets: # if packet is in data set 1 only
            data1_interp.append(data1[i])
            data1_timestamps_interp.append(data1_timestamps[i])
            data2_interp.append(data2[closestNeighbor(data1_packets.index(start_packet + i))])
            data2_timestamps_interp.append(data2_timestamps[closestNeighbor(data1_packets.index(start_packet + i))])
        elif start_packet + 1 in data2_packets:  # if packet is in data set 2 only
            data2_interp.append(data2[i])
            data2_timestamps_interp.append(data2_timestamps[i])
            data1_interp.append(data1[closestNeighbor(data2_packets.index(start_packet + i))])
            data1_timestamps_interp.append(data1_timestamps[closestNeighbor(data2_packets.index(start_packet + i))])

    return data1_interp, data1_timestamps_interp, data2_interp, data2_timestamps_interp

# returns index of closest neighbor based on timestamps
def closestNeighbor(target_timestamp, timestamps):
    diff = lambda timestamps : abs(timestamps - target_timestamp)
    return timestamps.index(min(timestamps, key=diff))