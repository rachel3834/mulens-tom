from os import path, makedirs, chdir, getcwd
from sys import exit, stdout
import logging
import subprocess
from datetime import datetime
import log_utilities
import config_parser
import socket

def backup_database():
    """Function to automatically back-up the TOM database"""
    
    config = read_config()
    
    log = log_utilities.start_day_log( config, config['log_root_name'] )

    filetest = path.isfile(config['db_location'])
    dirtest = path.isdir(config['backup_dir'])
    log.info('Checking the DB file is accessible with status '+repr(filetest))
    log.info('Checking the backup directory is accessible with status '+repr(dirtest))

    log.info('Executing rsync command: '+config['rsync_command'])
    child = subprocess.Popen(config['rsync_command'].split(' '),
                                  shell=False, stderr=subprocess.PIPE)
    while True:
        err = child.stderr.readlines()
        for e in err:
            log.info(e)
        if child.poll() != None:
            break
    
    log.info('Completed DB back-up')
    log_utilities.end_day_log(log)

def read_config():
    """Function to read the back-up script configuration file.
    Returns a dictionary of the config parameters from the XML file. 
    """

    config = config_parser.read_config_for_code('backup')

    ts = datetime.utcnow()
    ts = ts.strftime("%Y-%m-%dT%H:%M:%S")
    db_path = config['db_location']
    db_file = path.basename(db_path)+'_'+ts
    bkup_path = path.join(config['backup_dir'], db_file)
    config['rsync_command'] = 'rsync -a ' + db_path + ' ' + bkup_path

    if path.isdir(config['backup_dir']) == False:
        makedirs(config['backup_dir'])
    if path.isdir(config['log_dir']) == False:
        makedirs(config['log_dir'])

    return config

if __name__ == '__main__':
    backup_database()