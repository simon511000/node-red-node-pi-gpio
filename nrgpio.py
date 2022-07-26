
# Import library functions we need
import RPi.GPIO as GPIO
import struct
import sys
import os
import subprocess
from time import sleep

try:
    raw_input          # Python 2
except NameError:
    raw_input = input  # Python 3

bounce = 25

if len(sys.argv) > 2:
    cmd = sys.argv[1].lower()
    pin = int(sys.argv[2])
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    if cmd == "pwm":
        #print("Initialised pin "+str(pin)+" to PWM")
        try:
            freq = int(sys.argv[3])
        except:
            freq = 100

        GPIO.setup(pin,GPIO.OUT)
        p = GPIO.PWM(pin, freq)
        p.start(0)

        while True:
            try:
                data = raw_input()
                if 'close' in data:
                    sys.exit(0)
                p.ChangeDutyCycle(float(data))
            except (EOFError, SystemExit):        # hopefully always caused by us sigint'ing the program
                GPIO.cleanup(pin)
                sys.exit(0)
            except Exception as ex:
                print("bad data: "+data)

    elif cmd == "buzz":
        #print("Initialised pin "+str(pin)+" to Buzz")
        GPIO.setup(pin,GPIO.OUT)
        p = GPIO.PWM(pin, 100)
        p.stop()

        while True:
            try:
                data = raw_input()
                if 'close' in data:
                    sys.exit(0)
                elif float(data) == 0:
                    p.stop()
                else:
                    p.start(50)
                    p.ChangeFrequency(float(data))
            except (EOFError, SystemExit):        # hopefully always caused by us sigint'ing the program
                GPIO.cleanup(pin)
                sys.exit(0)
            except Exception as ex:
                print("bad data: "+data)

    elif cmd == "out":
        #print("Initialised pin "+str(pin)+" to OUT")
        GPIO.setup(pin,GPIO.OUT)
        if len(sys.argv) == 4:
            GPIO.output(pin,int(sys.argv[3]))

        while True:
            try:
                data = raw_input()
                if 'close' in data:
                    sys.exit(0)
                data = int(data)
            except (EOFError, SystemExit):        # hopefully always caused by us sigint'ing the program
                GPIO.cleanup(pin)
                sys.exit(0)
            except:
                if len(sys.argv) == 4:
                   data = int(sys.argv[3])
                else:
                   data = 0
            if data != 0:
                data = 1
            GPIO.output(pin,data)

    elif cmd == "in":
        #print("Initialised pin "+str(pin)+" to IN")
        bounce = float(sys.argv[4])
        def handle_callback(chan):
            if bounce > 0:
                sleep(bounce/1000.0)
            print(GPIO.input(chan))

        if sys.argv[3].lower() == "up":
            GPIO.setup(pin,GPIO.IN,GPIO.PUD_UP)
        elif sys.argv[3].lower() == "down":
            GPIO.setup(pin,GPIO.IN,GPIO.PUD_DOWN)
        else:
            GPIO.setup(pin,GPIO.IN)

        if bounce > 0:
            GPIO.add_event_detect(pin, GPIO.BOTH, callback=handle_callback, bouncetime=int(bounce))
        else :
            GPIO.add_event_detect(pin, GPIO.BOTH, callback=handle_callback)
        sleep(0.1)
        print(GPIO.input(pin))

        while True:
            try:
                data = raw_input()
                if 'close' in data:
                    sys.exit(0)
            except (EOFError, SystemExit):        # hopefully always caused by us sigint'ing the program
                GPIO.cleanup(pin)
                sys.exit(0)

    elif cmd == "byte":
        #print("Initialised BYTE mode - "+str(pin)+)
        list = [7,11,13,12,15,16,18,22]
        GPIO.setup(list,GPIO.OUT)

        while True:
            try:
                data = raw_input()
                if 'close' in data:
                    sys.exit(0)
                data = int(data)
            except (EOFError, SystemExit):        # hopefully always caused by us sigint'ing the program
                GPIO.cleanup()
                sys.exit(0)
            except:
                data = 0
            for bit in range(8):
                if pin == 1:
                    mask = 1 << (7 - bit)
                else:
                    mask = 1 << bit
                GPIO.output(list[bit], data & mask)

    elif cmd == "borg":
        #print("Initialised BORG mode - "+str(pin)+)
        GPIO.setup(11,GPIO.OUT)
        GPIO.setup(13,GPIO.OUT)
        GPIO.setup(15,GPIO.OUT)
        r = GPIO.PWM(11, 100)
        g = GPIO.PWM(13, 100)
        b = GPIO.PWM(15, 100)
        r.start(0)
        g.start(0)
        b.start(0)

        while True:
            try:
                data = raw_input()
                if 'close' in data:
                    sys.exit(0)
                c = data.split(",")
                r.ChangeDutyCycle(float(c[0]))
                g.ChangeDutyCycle(float(c[1]))
                b.ChangeDutyCycle(float(c[2]))
            except (EOFError, SystemExit):        # hopefully always caused by us sigint'ing the program
                GPIO.cleanup()
                sys.exit(0)
            except:
                data = 0

    elif cmd == "mouse":  # catch mice button events
        f = open( "/dev/input/mice", "rb" )
        oldbutt = 0

        while True:
            try:
                buf = f.read(3)
                pin = pin & 0x07
                button = struct.unpack('3b',buf)[0] & pin # mask out just the required button(s)
                if button != oldbutt:  # only send if changed
                    oldbutt = button
                    print(button)
            except:
                f.close()
                sys.exit(0)

    elif cmd == "kbd":  # catch keyboard button events
        try:
            while not os.path.isdir("/dev/input/by-path"):
                sleep(10)
            infile = subprocess.check_output("ls /dev/input/by-path/ | grep -m 1 'kbd'", shell=True).strip()
            infile_path = "/dev/input/by-path/" + infile.decode("utf-8")
            EVENT_SIZE = struct.calcsize('llHHI')
            file = open(infile_path, "rb")
            event = file.read(EVENT_SIZE)
            while event:
                (tv_sec, tv_usec, type, code, value) = struct.unpack('llHHI', event)
                #if type != 0 or code != 0 or value != 0:
                if type == 1:
                    # type,code,value
                    print("%u,%u" % (code, value))
                event = file.read(EVENT_SIZE)
            print("0,0")
            file.close()
            sys.exit(0)
        except:
            file.close()
            sys.exit(0)

elif len(sys.argv) > 1:
    cmd = sys.argv[1].lower()
    if cmd == "rev":
        print(GPIO.RPI_REVISION)
    elif cmd == "ver":
        print(GPIO.VERSION)
    elif cmd == "info":
        print(GPIO.RPI_INFO)
    else:
        print("Bad parameters - in|out|pwm|buzz|byte|borg|mouse|kbd|ver|info {pin} {value|up|down}")
        print("  only ver (gpio version) and info (board information) accept no pin parameter.")

else:
    print("Bad parameters - in|out|pwm|buzz|byte|borg|mouse|kbd|ver|info {pin} {value|up|down}")
