import time
import shutil
import filecmp
import os
import datetime
import ctypes, sys
import logging

BASE_DIR = '\\\\server.local\\folder\\exampledir'
DEST_DIR = '\\\\server.local\\folder\\exampledest'
EXTENSIONS = ['doc','docx','xls','xlsx','ppt','pptx','txt']

TIME = time.strftime('%H_%M_%S')  # HH_MM_SS
DAY = int(time.strftime('%d'))
DATE = time.strftime('%Y_%m_%d')  # YYYY_MM_DD

DIFF_DIR = DEST_DIR + '/Modified Files'
DATE_DIR = DEST_DIR + '/' + DATE
DATE_DIFF_DIR = DIFF_DIR + '/' + DATE
RUN_DIFF_DIR = DATE_DIFF_DIR + '/' + TIME
yesterday = str(datetime.date.fromordinal(datetime.date.today().toordinal()-1)).replace('-', '_')
OLD_DIR = DEST_DIR + '\\' + yesterday

if not os.path.exists('Logs'):
    os.mkdir('Logs')
logpath = 'Logs' + '/' + DATE + '_' + TIME
logging.basicConfig(filename=logpath, level=logging.DEBUG)
logging.debug('Logging working...')

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def isInt(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

def setup():
    logging.debug('Setup...')
    if not os.path.exists(DEST_DIR):
        logging.debug('Creating destination directory...')
        os.mkdir(DEST_DIR)
        logging.debug('Done.')
    if not os.path.exists(DIFF_DIR):
        logging.debug('Creating difference directory...')
        os.mkdir(DIFF_DIR)
        os.mkdir(OLD_DIR)
        logging.debug('Done.')
    if not os.path.exists(DATE_DIR):
        logging.debug('Creating date directory...')
        os.mkdir(DATE_DIR)
        logging.debug('Done.')
    else:
        logging.debug('Overwriting current day files...')
        shutil.rmtree(DATE_DIR, ignore_errors=True)  # Need ignore_errors flag when deleting non-empty dirs
        logging.debug('Done.')
        os.mkdir(DATE_DIR)
        logging.debug('Done.')
    if not os.path.exists(DATE_DIFF_DIR):
        logging.debug('Creating date difference directory...')
        os.mkdir(DATE_DIFF_DIR)
        logging.debug('Done.')
    logging.debug('Creating run difference directory...')
    os.mkdir(RUN_DIFF_DIR)
    logging.debug('Done.')
    for root, dirs, files in os.walk(DEST_DIR):
        for name in dirs:
            if isInt(name[0]) and int(name[-2:]) == (DAY-2):
                logging.debug('Found files from two days ago. Deleting...')
                shutil.rmtree(os.path.join(root, name), ignore_errors=True)
                logging.debug('Done.')
    logging.debug('Setup done.')

def copy_base(folder, dest):
    logging.debug('Copying files from base directory to destination directory...')
    for root, dirs, files in os.walk(folder):
        for name in files:
            for ext in EXTENSIONS:
                if name[-3:] == ext:
                    filepath = os.path.join(root, name)
                    shutil.copy2(filepath, dest)
    logging.debug('Done')

def compare2(old_dir, new_dir):
    logging.debug('Comparing old directory files with new directory files...')
    modified = []
    p, d, f = next(os.walk(new_dir))
    old_p, old_d, old_f = next(os.walk(old_dir))
    for fi in f:
        modified.append(os.path.join(p, fi))  # Everyone is guilty until proven innocent
    for old_file in old_f:
        for new_file in modified:
            if filecmp.cmp(new_file, os.path.join(old_p, old_file)):
                modified.remove(new_file)
                break
    if len(modified) == 0:
        open(RUN_DIFF_DIR + '\\NONE', 'a').close()
        logging.debug('No modified files found.')
    else:
        logging.debug('Modified fies: ')
        logging.debug(modified)
    for modified_file in modified:
        mod_name = RUN_DIFF_DIR + '/' + modified_file.split('\\')[-1]
        shutil.copy2(modified_file, mod_name)
    logging.debug('Done.')
    
if is_admin():
    logging.debug('Running as administrator...')
    setup()
    copy_base(BASE_DIR, DATE_DIR)
    yesterday = str(datetime.date.fromordinal(datetime.date.today().toordinal()-1)).replace('-', '_')
    OLD_DIR = DEST_DIR + '\\' + yesterday
    compare2(OLD_DIR, DATE_DIR)
    logging.debug('Finished with no errors raised.')
else:
    logging.debug('Restarting as administrator...')
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, "", None, 1)
