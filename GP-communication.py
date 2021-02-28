import serial
import time


def main():
    with serial.Serial('/dev/tty.usbserial-AL03ERTX', 56700, timeout=1) as ser:
        while True:
            line = [0, 0, 0, 0, 0, 0]
            s = input()
            b = [b'\xff', b'U', b'\x00', b'\xff', b'\x00', b'\xff'] if s == "1" else [
                b'\xff', b'U', b'\x02', b'\xfd', b'\x00', b'\xff']
            for i in range(1):
                for item in b:
                    ser.write(item)

            found = False
            while not found:
                tmp = ser.read(1)
                if (tmp == b'\xff'):
                    line[0] = tmp
                    for i in range(1, 6):
                        line[i] = ser.read(1)

                    rString = integerToBytes(line)
                    print(rString)
                    if line[2] == b'c':
                        found = True


def integerToBytes(line):
    return "\t".join(str(int.from_bytes(b, byteorder='big', signed=True)) for b in line)


if __name__ == '__main__':
    main()
