#!/usr/bin/python3.7
'''The entry point of the scheduler program

This program needs 4 positional command line arguments. Them being 
(in order):
    doctorsFile: [input] A JSON file containing the information related
        to the doctors
    shiftConfsFile: [input]: A JSON file containing the information
        related to the shift configurations of the doctors
    calendarFile: [input]: A JSON file containing the information
        realted to the schedule to be generated
    scheduleFile: [output]: A JSON file containing the generated 
        schedule information

    NOTE: the fields needed by these files are specified in the 
    scheduler.schedule function (as the json will be converted into 
    dicts)

    An example call to the program would be:
        python3.7 src/main.py doctors.json shiftConf.json \
            calendar.json schedule.json

Author: miggoncan
'''
import json
import sys
import traceback
from pathlib import Path
import logging
import logging.config

import scheduler

# Resolve will return the absolute path
# The first parent refest to the src dir
SCHEDULER_DIR = Path(__file__).resolve().parent.parent

LOGGING_CONFIG_FILE = SCHEDULER_DIR / 'config/logging.json'
SCHEDULER_CONFIG_FILE = SCHEDULER_DIR / 'config/scheduler.json'


def main():
    # First, load the logging configuration
    with LOGGING_CONFIG_FILE.open() as loggingConfFile:
        loggingConf = json.loads(loggingConfFile.read())
    # Change the filename of the file handler to be relative to the
    # scheduler dir
    handlers = loggingConf.get('handlers', None)
    if handlers:
        file = handlers.get('file', None)
        if file:
            filename = file.get('filename', None)
            if filename:
                file['filename'] = SCHEDULER_DIR / filename
    logging.config.dictConfig(loggingConf)

    log = logging.getLogger('main')
    log.info('Starting main program')

    # Extract the needed arguments
    if len(sys.argv) != 5:
        # To know the format of these files, see the scheduler.schedule
        # function. As the arguments passed to it will be dict directly 
        # generated from the given given json files
        log.error(f'Usage: {sys.argv[0]} doctorsFile shiftConfFile '
            + 'calendarFile scheduleFile\n\n' 
            + 'To know the format of these files, see the scheduler.schedule '
            + 'function. As the arguments passed to it will be dicts directly '
            + 'generated from the given json files\n\n'
            + 'Note that the scheduleFile will be the output file, so this '
            + 'process must have permissions to write to it')
        log.error(f'Provided args are: {sys.argv}')
        sys.exit(1)
    doctorsFilePath = sys.argv[1]
    shiftConfsFilePath = sys.argv[2]
    calendarFilePath = sys.argv[3]
    scheduleFilePath = sys.argv[4]

    # Read the scheduler configuration
    with SCHEDULER_CONFIG_FILE.open() as schedulerConfFile:
        schedulerConf = json.loads(schedulerConfFile.read())

    # First, read the data from the files
    with open(doctorsFilePath) as doctorsFile:
        log.debug('Reading the doctors file: {}'.format(doctorsFilePath))
        doctors = json.loads(doctorsFile.read())
        log.debug('The doctors dict is: {}'.format(doctors))
    with open(shiftConfsFilePath) as shiftConfsFile:
        log.debug('Reading the shiftConfs file: {}'.format(shiftConfsFilePath))
        shiftConfs = json.loads(shiftConfsFile.read())
        log.debug('The shiftConfs dict is: {}'.format(shiftConfs))
    with open(calendarFilePath) as calendarFile:
        log.debug('Reading the calendar file: {}'.format(calendarFilePath))
        calendarDict = json.loads(calendarFile.read())
        log.debug('The calendar dict is: {}'.format(calendarDict))

    log.info('Generating the schedule')
    try:
        schedule = scheduler.schedule(doctors, shiftConfs, calendarDict, 
            schedulerConf)
    except Exception as e:
        log.error('An unexpected exception occurred: {}'.format(traceback.format_exc()))
        raise e
    
    log.debug('The generated schedule is: {}'.format(schedule))

    log.debug('Attemting to store the resulting schedule at: {}'
        .format(scheduleFilePath))
    with open(scheduleFilePath, mode='w') as scheduleFile:
        scheduleFile.write(json.dumps(schedule))

    log.info('Finishing the main program')


if __name__ == '__main__':
    main()
