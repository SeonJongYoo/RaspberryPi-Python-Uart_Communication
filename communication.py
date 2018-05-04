import serial
import time


def main():
    with serial.Serial('/dev/tty.usbserial-AL03ERTX', 56700, timeout=1) as ser:
        line = [0, 0, 0, 0, 0, 0]
        while True:
            found = False
            while not found:
                tmp = ser.read(1)
                if (tmp == b'\xff'):
                    line[0] = str(tmp)
                    for i in range(1, 6):
                        line[i] = ser.read(1)
                        pass
                    pass
                    print("\t".join((str(b) for b in line)))
                    if line[2] != b'\x00':
                        found = True
                        break
                    pass
                pass
            pass
            s = input()
            b = [b'\xff', b'U', b'\x00', b'\xff', b'\x00', b'\xff'] if s == "1" else [
                b'\xff', b'U', b'\x02', b'\xfe',  b'\x02', b'\xfe']
            for i in range(1):
                for item in b:
                    ser.write(item)
                    pass
                pass
            pass
        pass


if __name__ == '__main__':
    main()
