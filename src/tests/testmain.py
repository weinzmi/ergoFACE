class Config:
    def load_config(self):

        global dirName
        global cycletime
        global rpm_limit
        global max_watt

        self.myconfigload = yaml.load(open('config.yaml'))
        self.dirName = myconfigload['Daum8008TRS']['WATT']['dirName']
        self.cycletime = myconfigload['Daum8008TRS']['WATT']['cycletime']
        self.rpm_limit = myconfigload['Daum8008TRS']['WATT']['rpm_limit']
        self.max_watt = myconfigload['Daum8008TRS']['WATT']['max_watt']