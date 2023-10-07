from fastapi_auth_user.database import db_helper

if __name__ == "__main__":
	db_helper.create_all_tables()
	db_helper.create_role_initial()
	