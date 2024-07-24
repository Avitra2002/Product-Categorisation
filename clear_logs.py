from authentification import access_secret_version, download_file_from_bucket, execute_postgres_query

def clear_logs(db_user, db_password, db_host, db_name):
    # SQL query to delete all records from logs table
    query = "DELETE FROM logs"
    
    # Execute the query
    try:
        execute_postgres_query(db_user, db_password, db_name, db_host, query)
        print("Logs cleared successfully.")
    except Exception as e:
        print(f"Failed to clear logs: {e}")