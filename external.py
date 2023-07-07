
import sys
import os
import getopt


argv: list = sys.argv[1:]


class External():
    open: str = "open"

    def __init__(self, argv: list) -> None:
        self.argv = argv

    # 执行命令
    def do(self):
        (dir, file) = os.path.split(__file__)

        action: str = None
        try:
            opts, args = getopt.getopt(self.argv, "ha:", ["help", "action="])
        except getopt.GetoptError:
            print("\nError:")
            print("Use: python3 " + file + " -a <action>")
            sys.exit(2)
        for opt, arg in opts:
            if opt in ("-h", "--help"):
                print("Use: python3 " + file + " -a <action>")
                sys.exit(2)
            elif opt in ("-a", "--action"):
                action = arg

        # 执行
        if not action or len(action) == 0:
            sys.exit(2)

        if action == External.open:
            os.system(sys.executable + " " + dir + "/setup.py")


External(argv=argv).do()
