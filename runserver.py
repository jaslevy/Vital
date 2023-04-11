import views
import sys
import argparse

def get_args():
    parser = argparse.ArgumentParser(
        description = "Beta VitalMap",
        allow_abbrev=False
    )
    parser.add_argument('port', type=int,
        help = 'the port at which the server should listen')
    _args = parser.parse_args()
    return _args


def main():
    try:
        args = get_args()
    except Exception as ex:
        print(ex, file=sys.stderr)
        sys.exit(2)
    views.app.run(host = '0.0.0.0', port = args.port, debug=True)

#-----------------------------------------------------------------------

if __name__ == '__main__':
    main()