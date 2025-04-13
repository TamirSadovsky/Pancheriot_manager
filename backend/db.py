import os
import pyodbc
from google.cloud import storage
from dotenv import load_dotenv
from contextlib import contextmanager

load_dotenv()

DB_CONNECTION_STRING = os.getenv("DB_CONNECTION_STRING")
BUCKET_NAME = os.getenv("BUCKET_NAME")
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

storage_client = storage.Client()
bucket = storage_client.bucket(BUCKET_NAME)

@contextmanager
def db_cursor():
    conn = pyodbc.connect(DB_CONNECTION_STRING)
    cursor = conn.cursor()
    try:
        yield cursor
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()

def find_daily_appointments(branch_id: int, appointment_date: str):
    with db_cursor() as cursor:
        cursor.execute("""
            EXEC [dbo].[FindDailyAppointmentList] @BranchID = ?, @AppointmentDate = ?
        """, branch_id, appointment_date)
        rows = cursor.fetchall()
        columns = [column[0] for column in cursor.description]
        return [dict(zip(columns, row)) for row in rows]


def update_driver_database(appointment_id: int):
    try:
        with db_cursor() as cursor:
            cursor.execute("EXEC [dbo].[DriverArraived] @AppointmentID = ?", appointment_id)
        print(f"✅ Appointment {appointment_id} marked as arrived.")
        return {"success": True}
    except Exception as e:
        print(f"❌ Error updating appointment arrival: {e}")
        return {"success": False, "error": str(e)}


def update_signature(appointment_id: int, url: str):
    try:
        with db_cursor() as cursor:
            cursor.execute("EXEC [dbo].[SetSig] @AppointmentID = ?, @Signeture = ?", appointment_id, url)
        print(f"✅ Appointment {appointment_id} marked with signature.")
        print(f"✅ Signature URL: {url}")
        return {"success": True}
    except Exception as e:
        print(f"❌ Error updating signature: {e}")
        return {"success": False, "error": str(e)}
    

def find_daily_appointments_all(appointment_date: str):
    try:
        with db_cursor() as cursor:
            cursor.execute("""
                EXEC [dbo].[FindDailyAppointmentListAll] @AppointmentDate = ?""", appointment_date)

            rows = cursor.fetchall()
            columns = [column[0] for column in cursor.description]
            results = [dict(zip(columns, row)) for row in rows]

            return results

    except Exception as e:
        print(f"❌ Error fetching all daily appointments: {e}")
        return {"success": False, "error": str(e)}

    


