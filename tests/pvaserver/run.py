import time

from pvaserver import PvaServer


def main():
    srv = PvaServer("ET_SASAKI:GFHTTPVA:TEST:")
    try:
        srv.run()
        while(True):
            time.sleep(1)
    except KeyboardInterrupt:
        srv.stop()


if __name__ == "__main__":
    main()
