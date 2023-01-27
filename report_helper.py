import json
import env
class ReportHelper():
    def __init__(self, dconfig: dict):
        self._dconfig = dconfig
        with open(env.CONTENT_FILTER_DEFS_PATH) as cfFile:
            self._cfCats = json.load(cfFile)

    # extracts 
    def extract_custom_webfilter(self):
        idMapping = dict()
        localCats = self._dconfig["webfilter"]["ftgd-local-cat"]
        for catName in localCats:
            # reversed mappings so we can look up category name by id
            idMapping[localCats[catName]["id"]] = catName
        
        localRatings = self._dconfig["webfilter"]["ftgd-local-rating"]
        cattedRatings = dict()
        for website in localRatings:
            ratingId = idMapping[localRatings[website]["rating"]]
            if cattedRatings.get(ratingId) == None: 
                cattedRatings[ratingId] = list()
            
            cattedRatings[ratingId].append(website)

        return cattedRatings

    def extract_content_filter_settings(self):
        

        profiles = self._dconfig["webfilter"]["profile"]
        reports = dict()

        for profile in profiles:
            filters = profiles[profile]["ftgd-wf"]["filters"]
            
            report = dict()
            for cat in self._cfCats:
                report[cat] = dict()
            report["UNDEFINED"] = dict()

            for filter in filters:
                entryDetails = filters[filter]
                entryCat = entryDetails.get("category")
                if entryCat != None:
                    mapping = self._get_cat_mapping(entryCat)
                    report[mapping[0]][mapping[1]] = entryDetails.get("action")
                reports[profile] = report
        
        return reports

    def _get_cat_mapping(self, entryCatId):
        for cat in self._cfCats:
            catMapping = self._cfCats[cat].get(entryCatId)
            if catMapping != None:
                return (cat, catMapping)
        return ("UNDEFINED", f"{entryCatId} NOT DEFINED")