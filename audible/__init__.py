import math
import numpy as np
import struct
import matplotlib.pyplot as plt


class SineAMCodec(object):
    depths = {
        1: 'b',
        2: 'h',
        4: 'l'
    }

    def __init__(self, encoding='utf-8'):
        self.encoding = encoding
        
    def set_encoding(self, encoding):
        self.encoding = encoding
                
    def am_sine(self, x, amp=1.0):
        return math.sin(x * 2.0 * math.pi) * amp
        
    def encode(self, data, byte_depth=2, sample_frequency=2000, wave_frequency=500, data_frequency=50):
        if isinstance(data, str):
            data = data.encode(self.encoding)
            
        res = b''
        dp = type(self).depths[byte_depth]
        char_samples = int(sample_frequency / data_frequency)
        char_bytes = char_samples * byte_depth
            
        i = 0
            
        for i, d in enumerate(data):
            sample_pos = i * char_samples
            byte_pos = i * char_bytes
            ch = struct.pack("=" + str(int(char_samples)) + dp, *[int(self.am_sine((sample_pos + x) / wave_frequency, float(d) / 255) * 2 ** (8 * byte_depth)) for x in range(int(char_samples))])
            print(d, d / 255, data[i: i + 1].decode(self.encoding))
            res += ch
            i += int(char_samples)
            
        assert len(res) == int(char_bytes * len(data)), "Expected result to have {} bytes, got {}!".format(len(res), int(char_bytes * len(data)))
            
        return res
        
    def decode(self, data, byte_depth=2, sample_frequency=2000, wave_frequency=500, data_frequency=50, decode=True, debug=False):
        wave = b''
        dp = type(self).depths[byte_depth]
        char_samples = math.ceil(sample_frequency / data_frequency)
        char_bytes = char_samples * byte_depth
    
        for i in range(math.ceil(len(data) / char_bytes)):
            sample = data[int(i * char_bytes): int((i + 1) * char_bytes)]
            a = np.array([x / 2 ** (8 * byte_depth) for x in struct.unpack("=" + str(int(len(sample) / byte_depth)) + dp, sample)])
            osc = np.array([min(1, a + 0.000001) for a in [self.am_sine((i * char_samples + x) / wave_frequency, 1.0) for x in range(int(len(sample) / byte_depth))]])
            
            res = math.ceil(np.mean(a / osc) * 255)
            print(res / 255, res, struct.pack('B', int(res)).decode(self.encoding))
            
            if debug:
                plt.plot(a, 'r-', osc, 'b-')
                plt.xlabel('samples')
                plt.show()
        
            wave += struct.pack('B', res)
                    
        if decode:
            return wave.decode(self.encoding)
            
        return wave