import psycopg2


def get_connection():
    return psycopg2.connect(
        host="localhost",
        database="microservice",
        user="postgres",
        password="admin@123"
    )

def run_query(query,parms=None,fetch=False,return_rowcount=False):
    conn=get_connection()
    cursor=conn.cursor()

    try:
        cursor.execute(query,parms)
        result= None
        if fetch:
            result=cursor.fetchall()
        if return_rowcount:
            result= cursor.rowcount
        conn.commit()
        return result
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()
        