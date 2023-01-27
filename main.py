# system packages
import json, os
from pprint import pformat, pprint

# installed packages
import pandas as pd

# our files
import env
from report_helper import ReportHelper
import fortigate_config_parser as fcp

def load_config(path: str) -> dict:
    abs_path = os.path.abspath(path)
    with open(abs_path) as raw_conf:
        return fcp.FortigateConfigParser(configLines=raw_conf.readlines(), configName=os.path.split(abs_path)[1]).parse()


def generate_whitelist_blacklist(filename, rhelper):
    df = pd.DataFrame(dict([ (k, pd.Series(v)) for k,v in rhelper.extract_custom_webfilter().items() ]))
    df.to_excel(os.path.join(env.REPORT_FOLDER, '.'.join([filename.strip(".conf") + "_whitelist-blacklist", "xlsx"])))

def _prepare_category_report(jsonReport):
    flattenedReport = list()
    for category in jsonReport:
        for subcategory in jsonReport[category]:
            flattenedReport.append((category, subcategory, jsonReport[category][subcategory]))
    return flattenedReport

def generate_category_report(filename, helper):
    reports = rhelper.extract_content_filter_settings()
    for report in reports:
        pprint(reports[report])
        df = pd.DataFrame(_prepare_category_report(reports[report]))
        df.to_excel(os.path.join(env.REPORT_FOLDER, '.'.join([filename.strip(".conf") + f"_content-filter-settings_{report}", "xlsx"])))
    pass

if (__name__ == "__main__"):

    # we only look in the folder, no subdirectories. then iterate through each file.
    for dirpath, dirnames, filenames in os.walk(top=env.CONFIG_FOLDER,topdown=True):
        # can't subscript the generator os.walk returns, so we just manually skip all subfolders
        if (os.path.abspath(dirpath) != os.path.abspath(env.CONFIG_FOLDER)): continue

        for file in filenames:
            # Loading file
            full_path = os.path.join(dirpath, file)
            if (os.path.splitext(full_path)[1] != ".conf"): continue

            dconfig = load_config(full_path)
            out_json_name = file.strip(".conf") + ".json"
            with open(f"./{out_json_name}", "w") as json_file:
                json_file.write(json.dumps(obj=dconfig, indent=4))

            # Processing file
            rhelper = ReportHelper(dconfig)
            generate_whitelist_blacklist(file, rhelper)
            generate_category_report(file, rhelper)