from app import logger, engine
from app.helpers import import_excel_to_df, update_table_schema, export_df_to_db
from app.globalvars import table_schema_dict, input_folder
from app.models import create_table
import glob
from config import Config
import os

logger.info('Selecting input files')
for file in glob.iglob(os.path.join(input_folder, '*.xls*'), recursive=True):
    print('\n')
    logger.info('++++++++++++++++++++++++++++++++++\nChoosing file: {}'.format(file))
    # Get only the base file name without the extension
    file_name = os.path.basename(file).split('.')[0]
    value = None
    # Check if rules dict is populated, else put table name as the file name itself
    if bool(Config.TABLE_NAMES_DICT):
        logger.info('Table names dict is not empty. Proceeding to identify table name...')
        value = [val for key, val in Config.TABLE_NAMES_DICT.items() if key in file_name]
        if len(value) == 0:
            logger.info('Key not found')
            table_name = file_name
            logger.info('Chosen table_name is "{}" for file "{}" '.format(table_name, file_name))
        else:
            table_name = str(value).strip('[\'\']')
            logger.info('Chosen table_name is "{}" for file "{}" '.format(table_name, file_name))
    else:
        logger.info('Table name selection dict is empty')
        table_name = file_name
        logger.info('Chosen table_name is "{}" for file "{}" '.format(table_name, file_name))

    continue
    # TODO: Handle promotion step and application column difference
    # Read excel using pandas
    logger.info('Reading excel using pandas')
    excel_df = import_excel_to_df(filename=file)
    logger.debug('Successfully imported to dataframe -> rows: {}, columns:{}'.format(len(excel_df), len(excel_df.columns)))
    logger.debug('Columns identified: {}'.format(excel_df.columns))
    logger.info('File name is : {} and will be used as table name'.format(table_name))
    # Update database table schema #TODO: do a check, if table exists, before doing this
    logger.debug('Moving on to create database table from dataframe headers...')
    update_table_schema(excel_df=excel_df, zone_name=str(table_name))  # TODO: change to zone name
    logger.debug('Created table from the dataframe headers')

    # Create database table in database
    logger.debug('Updated table schema \n{}'.format(table_schema_dict))
    logger.debug('Creating table based on the new schema')
    create_table(table_schema_dict)

    # Dump excel data into the database table
    logger.info('Updating database table with the contents')
    export_df_to_db(engine=engine, dataframe=excel_df, tablename=str(table_name))
    logger.info('Successfully updated database table with the contents')

