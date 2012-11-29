import logging


if __name__=='__main__':
    logging.basicConfig(filename='example.log',level=logging.DEBUG, format='%(asctime)s %(message)s')
    logging.debug('This message should go to the log file')
    logging.info('So should this')
    logging.warning('And this, too')
    try:
        print 4/0
    except Exception as e:
        logging.exception('except')