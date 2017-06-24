import xml.sax.handler
from os import path
from sys import argv
import socket

class ConfigHandler(xml.sax.handler.ContentHandler):
    """Configuation Handler class for generic XML files in 
    parameter:value pair format."""

    def __init__(self):
        self.ivalue = False
        self.par_name = None
        self.par_value = None
        self.mapping = {}

    def startElement(self,name,attributes):
        if name == 'parameter':
            self.par_name = attributes['name']
        elif name == 'value':
            self.ivalue = True

    def characters(self,data):
        if self.ivalue == True: self.par_value = data

    def endElement(self,name):
        if name == 'value':
            self.ivalue = False
            self.mapping[self.par_name] = self.par_value

def read_config(config_file_path):

    config = {}
    if path.isfile(config_file_path) == False: return config

    parser = xml.sax.make_parser( )
    config_handler = ConfigHandler( )

    parser.setContentHandler(config_handler)
    parser.parse(config_file_path)
    config = config_handler.mapping

    return config

def read_config_for_code(code_name):
    """Function to read XML configuration files
    code_name = { 'backup' }    
    """
    
    configs = { 'backup': 'backup_config.xml' }
    if code_name in configs.keys():
        config_file = configs[code_name]
    
    host_name = socket.gethostname()
    if 'rachel' in str(host_name).lower():
        config_file_path = path.join('/Users/rstreet/software/mulens_tom/configs/',\
                                         configs[code_name])
    else:
        config_file_path = path.join('/data/rstreet/spitzermicrolensing/configs/',configs[code_name])
    
    if path.isfile(config_file_path) == False:
        raise IOError('Cannot find configuration file, looking for:'+config_file_path)
    script_config = read_config(config_file_path)
    
    return script_config

if __name__ == '__main__':

    if len(argv) > 1: config_file_path = argv[1]
    else: config_file_path = raw_input('Please input path to an XML config file: ')

    config = read_config(config_file_path)

    if config == None: print 'ERROR: Cannot read file '+config_file_path
    else:
        print 'Input configuration:'
        for par,par_value in config.items(): print '    ',par, ':', par_value
