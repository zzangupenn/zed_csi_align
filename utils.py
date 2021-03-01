import numpy as np
import struct

def float_to_4ints(num):
    packed = struct.pack('f', num)
    integers = np.array([c for c in packed])
    return integers

def main():
    out = np.array(list(map(float_to_4ints, np.array([1.0, 2.0]))))
    print(out)

if __name__ == "__main__":
   main()