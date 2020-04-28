class File:

    def __init__(self, fYear, fPeriod, funding, folderQuery, fileName):
        self.fYear = fYear
        self.fPeriod = fPeriod
        self.funding = funding
        self.folderQuery = folderQuery
        self.fileName = fileName

    def __init__(self):
        pass

    def get_fYear(self):
        return self.__fYear

    def set_fYear(self, fYear):
        self.__fYear = fYear

    def get_fPeriod(self):
        return self.__fPeriod

    def set_fPeriod(self, fPeriod):
        self.__fPeriod = fPeriod

    def get_funding(self):
        return self.__funding

    def set_funding(self, funding):
        self.__funding = funding

    def get_folderQuery(self):
        return self.__folderQuery

    def set_folderQuery(self, folderQuery):
        self.__folderQuery = folderQuery

    def get_fileName(self):
        return self.__fileName

    def set_fileName(self, fileName):
        self.__fileName = fileName
