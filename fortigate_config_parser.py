import re
from collections import deque

# parses a Fortigate .conf file into a Python nested dictionary object.
class FortigateConfigParser:
    def __init__(self, configLines: list[str], configName: str = "main"):
        self._configHelper = FortigateConfigHelper(configName=configName)
        self._configLines = configLines

    def parse(self) -> dict:
        for line in self._configLines:
            self._process_line(line)
        
        return self._configHelper.GetFinalConfig()


    def _process_line(self, line: str):
        if line.startswith('#'): return

        parseRegex = r"\s?(\"[^\"]*\"|[^\s]*)"
        matches = re.findall(parseRegex, line)
        
        while '' in matches:
            matches.remove('')

        while ' ' in matches:
            matches.remove(' ')

        command = ''
        args = list()
        if len(matches) > 0:
            command = matches[0].strip()
            for arg in matches[1:]:
                args.append(arg.strip('"'))
        
        if command == 'config' or command == 'edit':
            self._configHelper.AddConfigSections(args)
        elif command == 'next' or command == 'end':
            self._configHelper.EndCurrentConfigSection()
        elif command == 'set':
            self._configHelper.SetPropertyOnCurrentConfig(args[0], ' '.join(args[1:]))

    def get_config(self):
        return self._configHelper.GetFinalConfig()


class FortigateConfigHelper:

    def __init__(self, configName: str):
        self.configName = configName
        self._configChain = deque()
        self._configChain.append(
            {
                "config_section_name" : self.configName,
                "on_end_config": None
            }
        )


    def AddConfigSection(self, configSection: str, onConfigEnd: str | None):
        self._configChain.append({
                "config_section_name" : configSection,
                "on_end_config" : onConfigEnd
            })


    def AddConfigSections(self, configSections: list[str]):
        self.AddConfigSection(configSection=configSections[0], onConfigEnd=None)
        for subsection in configSections[1:]:
            self.AddConfigSection(configSection=subsection, onConfigEnd="chain_up")


    def SetPropertyOnCurrentConfig(self, propertyName: str, propertyValue: str):
        # if property exists and doesn't reference a dictionary, overwrite
        if propertyName in self._configChain[-1] and not isinstance(self._configChain[-1][propertyName], dict):
            self._configChain[-1][propertyName] = propertyValue

        # if property doesn't exist, add it
        elif propertyName not in self._configChain[-1]:
            self._configChain[-1][propertyName] = propertyValue

        # if property exists and references a dictionary, error out
        elif propertyName in self._configChain[-1] and isinstance(self._configChain[-1][propertyName], dict):
            print("[!] Tried to set an existing dictionary property.")


    def EndCurrentConfigSection(self):
        # protection in case something calls this method when it shouldn't
        if len(self._configChain) == 1: 
            return
        elif "on_end_config" in self._configChain[-1] and self._configChain[-1]["on_end_config"] == None:
            self._PopAndAppendConfig()
            return
        elif "on_end_config" in self._configChain[-1] and self._configChain[-1]["on_end_config"] == "chain_up":
            self._PopAndAppendConfig()
            self.EndCurrentConfigSection()


    def _PopAndAppendConfig(self):
        completedSection = self._configChain[-1]
        sectionName = completedSection["config_section_name"]
        if "config_section_name" in completedSection: 
            del completedSection["config_section_name"]
        if "on_end_config" in completedSection: 
            del completedSection["on_end_config"]

        self._configChain.pop()
        if (sectionName in self._configChain[-1]):
            self._configChain[-1][sectionName].update(completedSection)
        else:
            self._configChain[-1][sectionName] = completedSection


    def GetFinalConfig(self):
        if len(self._configChain) == 1:
            if "on_end_config" in self._configChain[0]: del self._configChain[0]["on_end_config"]
            if "config_section_name" in self._configChain[0]: del self._configChain[0]["config_section_name"]
            return self._configChain[0]
        else:
            return self._configChain