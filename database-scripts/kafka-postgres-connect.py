from kafka import KafkaConsumer
import psycopg2
from configparser import ConfigParser

def config(filename='database.ini', section='postgresql'):
    # create a parser
    parser = ConfigParser()
    # read config file
    parser.read(filename)

    # get section, default to postgresql
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))

    return db

def get_new_messages(topic):
    consumer = KafkaConsumer(bootstrap_servers='ec2-35-155-248-194.us-west-2.compute.amazonaws.com:9092,ec2-52-33-147-84.us-west-2.compute.amazonaws.com:9092,ec2-34-210-66-48.us-west-2.compute.amazonaws.com,ec2-54-200-46-124.us-west-2.compute.amazonaws.com')
    consumer.subscribe(['topic-receive-flight'])

    return consumer

def insert_status(record):
    """ insert a new record into the flying conditions table """
    sql = """INSERT INTO FLIGHT(FLIGHT_ID,INFO)
             VALUES(%s,%s);"""
    conn = None
    state_id = None
    try:
        # read database configuration
        params = config()
        # connect to the PostgreSQL database
        conn = psycopg2.connect(**params)
        # create a new cursor
        cur = conn.cursor()
        # execute the INSERT statement
        cur.execute(sql, (record['flight-id'],record['geoinfo'],))
        # commit the changes to the database
        conn.commit()
        # close communication with the database
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


all_messages = get_new_messages('topic-receive-flight')
for record in all_messages:
    print(record.value)
    idvalue = insert_status(record.value)
    print(idvalue)