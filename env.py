DEBUG = False
RELEASE = True
if (DEBUG):
    CONFIG_FOLDER = "./tests"
elif (RELEASE):
    CONFIG_FOLDER = "./conf_files"

CONTENT_FILTER_DEFS_PATH = "./fortigate-cf-cats.json"
REPORT_FOLDER = "./reports"