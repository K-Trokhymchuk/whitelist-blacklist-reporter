
class ReportHelper():
    def __init__(self, dconfig: dict):
        self._dconfig = dconfig

    # extracts 
    def extract_custom_webfilter(self):
        id_mapping = dict()
        local_cats = self._dconfig["webfilter"]["ftgd-local-cat"]
        for cat_name in local_cats:
            # reversed mappings so we can look up category name by id
            id_mapping[local_cats[cat_name]["id"]] = cat_name
        
        local_ratings = self._dconfig["webfilter"]["ftgd-local-rating"]
        catted_ratings = dict()
        for website in local_ratings:
            rating_id = id_mapping[local_ratings[website]["rating"]]
            if catted_ratings.get(rating_id) == None: 
                catted_ratings[rating_id] = list()
            
            catted_ratings[rating_id].append(website)

        return catted_ratings

    def extract_content_filter_settings(self):
        pass