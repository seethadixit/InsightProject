from kafka import KafkaConsumer
import psycopg2
from configparser import ConfigParser
import sys

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
    consumer = KafkaConsumer(bootstrap_servers='ec2-35-160-138-85.us-west-2.compute.amazonaws.com:9092,ec2-34-218-19-12.us-west-2.compute.amazonaws.com:9092,ec2-54-148-69-162.us-west-2.compute.amazonaws.com:9092,ec2-54-149-61-226.us-west-2.compute.amazonaws.com:9092')
    consumer.subscribe([topic])

    return consumer

def insert_status(topic,key,value):
    """ insert a new record into the flying conditions table """
    if topic == 'topic-flying-conditions':
        sql = """INSERT INTO POSTGRES.FLIGHT(FLIGHT_ID,INFO, CREATE_DATE)
                 VALUES(%s,%s,current_timestamp);"""
    else:
        sql = """INSERT INTO POSTGRES.WEATHER(STATION_ID,INFO, CREATE_DATE)
                        VALUES(%s,%s,current_timestamp);"""
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
        cur.execute(sql, (key,value,))
        # commit the changes to the database
        conn.commit()
        # close communication with the database
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

topic=sys.argv[1]
all_messages = get_new_messages(topic)
for record in all_messages:
    print(record.key,record.value)
    insert_status(topic,record.key.decode("utf-8") ,record.value.decode("utf-8") )
