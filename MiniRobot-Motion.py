import serial
import time
from threading import Thread

MOTION = {
    "SIGNAL": {"INIT": 17, "INIT2": 10},
    "MODE": {"WALK": 0, "MOVE": 19, "VIEW": 31, "TURN": 7, "SOUND": 60},
    # 머리 상하좌우 회전
    "VIEW": {"DOWN80": 0, "DOWN75": 4, "DOWN70": 1, "DOWN60": 2, "DOWN45": 3, "DOWN30": 5, "DOWN10": 6, "DOWN18": 17,
             "DOWN54": 49, "DOWN35": 50, "DOWN90": 51, "DOWN95": 52, "DOWN97": 53, "DOWN100": 54, "DOWN85": 55},
    # 로봇 몸 전체 회전 10도/머리 좌우 회전
    "DIR": {"LEFT": 0, "RIGHT": 2, "LEFT30": 7, "LEFT45": 8, "LEFT60": 9, "LEFT75": 22, "LEFT90": 10, "LEFT3": 47,
            "RIGHT30": 13, "RIGHT45": 14, "RIGHT60": 15, "RIGHT75": 23, "RIGHT90": 16, "RIGHT5": 48, "CENTER": 42},
    "SCOPE": {"NORMAL": 0, "SHORT": 9},
    "SPEED": {"FAST": 0, "RUN": 1, "SLOW": 2},

    "WALK": {
        "START": 9,
        "END": 400,
        "BACK": 10,
        "OPEN": 71,
        "LINE": 8
    },
    "SENSOR": {"DISTANCE": 5},
    "GRAB": {"ON": 29, "OFF": 27, "WALK": 41, "TURN": {"RIGHT": 51, "LEFT": 52},
             "MOVE": {"LEFT": 31, "RIGHT": 32}},
    "SOUND": {"SAY": {"EUN": 0, "A": 1, "B": 2, "C": 3, "D": 4, "E": 5, "W": 6, "S": 7, "N": 8, "GREEN": 9, "BLACK": 10,
                      "IS": 11}},
    "DOOR": {"INIT1": 71, "INIT2": 72, "WALK": 73, "WALK2": 20},
    "ARM": {"E": 74, "W": 75, "S": 76, "N": 77}
}


class Motion:
    def __init__(self):
        self.serial_use = 1
        self.serial_port = None
        self.Read_RX = 0
        self.receiving_exit = 1
        self.threading_Time = 0.01
        self.lock = False
        self.distance = 0
        BPS = 4800  # 4800,9600,14400, 19200,28800, 57600, 115200

        # ---------local Serial Port : ttyS0 --------
        # ---------USB Serial Port : ttyAMA0 --------
        self.serial_port = serial.Serial('/dev/ttyS0', BPS, timeout=0.01)
        self.serial_port.flush()  # serial cls
        self.serial_t = Thread(target=self.Receiving, args=(self.serial_port,))
        self.serial_t.daemon = True
        self.serial_t.start()
        time.sleep(0.1)

    def TX_data_py2(self, one_byte):  # one_byte= 0~255
        self.lock = True
        self.serial_port.write(serial.to_bytes([one_byte]))  # python3
        time.sleep(0.01)
        
    def TX_data_py3(self, one_byte):  # one_byte= 0~255
        #self.lock = True
        self.serial_port.write(serial.to_bytes([one_byte]))  # python3
        #time.sleep(0.05)
        
    def RX_data(self):
        if self.serial_port.inWaiting() > 0:
            result = self.serial_port.read(1)
            RX = ord(result)
            return RX
        else:
            return 0

    def getRx(self):
        return self.lock

    def Receiving(self, ser):
        self.receiving_exit = 1
        while True:
            if self.receiving_exit == 0:
                break
            time.sleep(self.threading_Time)
            # 수신받은 데이터의 수가 0보다 크면 데이터를 읽고 출력
            while ser.inWaiting() > 0:
                # Rx, 수신
                result = ser.read(1)
                RX = ord(result)
                if RX == 200:
                # print("motion end")
                    self.lock = False
                # print("RX=" + str(RX))
                else:
                    self.distance = RX
                # -----  remocon 16 Code  Exit ------
                if RX == 16:
                    self.receiving_exit = 0
                    break

    def init(self):
        if not self.lock:
            self.TX_data_py2(MOTION["SIGNAL"]["INIT"])
            while self.getRx():
                continue
        pass

    def init2(self):
        if not self.lock:
            self.TX_data_py2(MOTION["SIGNAL"]["INIT2"])
            while self.getRx():
                continue
        pass

    def walk(self, grab=None, walk_signal=MOTION["WALK"]["START"], scope=MOTION["SCOPE"]["NORMAL"],
             speed=MOTION["SPEED"]["SLOW"]):
        if not self.lock:
            if grab is None:
                self.TX_data_py2(MOTION["MODE"]["WALK"] + walk_signal + speed + scope)
            elif grab is "GRAB":
                self.TX_data_py2(MOTION["MODE"]["WALK"] + MOTION["GRAB"]["WALK"] + speed + scope)
                time.sleep(1)
            while self.getRx():  # Until true wait
                continue
        pass

    def WalkInLine(self):
        if not self.lock:
            self.TX_data_py3(MOTION["WALK"]["LINE"])
            '''
            a = self.getRx()
            while a:
                print(a)
                a = self.getRx()
                continue
                '''
        pass
    
    def head(self, view=MOTION["VIEW"]["DOWN80"], direction=MOTION["DIR"]["CENTER"]):
        if not self.lock:
            if direction == MOTION["DIR"]["CENTER"]:
                self.TX_data_py2(direction)
                time.sleep(1)
            else:
                self.TX_data_py2(MOTION["MODE"]["VIEW"] + direction)
                time.sleep(1)
            while self.getRx():
                continue
        if not self.lock:
            self.TX_data_py2(MOTION["MODE"]["VIEW"] + view)
            time.sleep(1)
            while self.getRx():
                continue
        pass

    def move(self, grab=None, direction=None, scope=MOTION["SCOPE"]["NORMAL"], repeat=1):
        if not self.lock:
            if grab is None:
                if direction is "LEFT":
                    for _ in range(repeat):
                        time.sleep(1)
                        self.TX_data_py2(MOTION["MODE"]["MOVE"] + scope + MOTION["DIR"]["LEFT"])
                        # time.sleep(0.5)
                elif direction is "RIGHT":
                    for _ in range(repeat):
                        time.sleep(1)
                        self.TX_data_py2(MOTION["MODE"]["MOVE"] + scope + MOTION["DIR"]["RIGHT"])
                        # time.sleep(0.5)
            elif grab is "GRAB":
                if direction is "LEFT":
                    for _ in range(repeat):
                        self.TX_data_py2(MOTION["MODE"]["MOVE"] + scope + MOTION["GRAB"]["MOVE"]["LEFT"])
                        time.sleep(0.5)
                elif direction is "RIGHT":
                    for _ in range(repeat):
                        self.TX_data_py2(MOTION["MODE"]["MOVE"] + scope + MOTION["GRAB"]["MOVE"]["RIGHT"])
                        time.sleep(0.5)
            while self.getRx():
                continue
        pass

    def turn(self, grab=None, direction=None, repeat=1):
        if not self.lock:
            if grab is None:
                if direction is "LEFT":
                    for _ in range(repeat):
                        time.sleep(1)
                        self.TX_data_py2(MOTION["DIR"]["LEFT"] + MOTION["MODE"]["TURN"])
                elif direction is "RIGHT":
                    for _ in range(repeat):
                        time.sleep(1)
                        self.TX_data_py2(MOTION["DIR"]["RIGHT"] + MOTION["MODE"]["TURN"])
            elif grab is "GRAB":
                if direction is "LEFT":
                    for _ in range(repeat):
                        self.TX_data_py2(MOTION["MODE"]["TURN"] + MOTION["GRAB"]["TURN"]["LEFT"])
                        time.sleep(0.2)
                elif direction is "RIGHT":
                    for _ in range(repeat):
                        self.TX_data_py2(MOTION["MODE"]["TURN"] + MOTION["GRAB"]["TURN"]["RIGHT"])
                        time.sleep(0.2)
            while self.getRx():
                continue
        pass

    def grab(self, switch="ON"):
        if not self.lock:
            self.TX_data_py2(MOTION["GRAB"][switch])
            while self.getRx():
                continue
        pass

    def check_distance(self):
        if not self.lock:
            self.TX_data_py2(MOTION["SENSOR"]["DISTANCE"])
            while self.getRx():
                continue
        return self.distance

    def sound_module(self, zone=None, alphabet=None, repeat=1):
        if not self.lock:
            if zone is "GREEN" or zone is "BLACK":  # 안전지역과 확진지역 그리고 방 이름을 말할 때
                self.TX_data_py2(60 + MOTION["SOUND"]["SAY"][zone])
                while self.getRx():
                    continue

                if alphabet is not None:
                    if not self.lock:
                        self.TX_data_py2(60 + MOTION["SOUND"]["SAY"]["EUN"])
                        while self.getRx():
                            continue

                    if not self.lock:
                        self.TX_data_py2(60 + MOTION["SOUND"]["SAY"][alphabet])
                        while self.getRx():
                            continue
            else:  # 방위를 말할 때
                for i in range(repeat):
                    self.TX_data_py2(60 + MOTION["SOUND"]["SAY"][alphabet])
                while self.getRx():
                    continue

    def OpenTheDoor_init(self):
        if not self.lock:
            self.TX_data_py2(MOTION["DOOR"]["INIT1"])
            while self.getRx():
                continue

        if not self.lock:
            self.TX_data_py2(MOTION["DOOR"]["INIT2"])
            while self.getRx():
                continue
                
    def OpenTheDoor(self, repeat=1):
        if not self.lock:
            for _ in range(repeat):
                self.TX_data_py2(MOTION["DOOR"]["WALK"])
                time.sleep(1)
            while self.getRx():
                continue
            
    def OpenTheDoor2(self, repeat=1):
        #curr_distance = self.check_distance()
        #if curr_distance < 100:
        if not self.lock:
            for _ in range(repeat):
                self.TX_data_py2(MOTION["DOOR"]["WALK2"])
                time.sleep(1)
            while self.getRx():
                continue  

    def ActionByDirection(self, mode=None):
        if not self.lock:
            self.TX_data_py2(MOTION["ARM"][mode])
            while self.getRx():
                continue


if __name__ == '__main__':
    temp = Motion()
    x = temp.check_distance()
    print("거리: ", x)
    print("거리+10: ", x + 10)
    pass


