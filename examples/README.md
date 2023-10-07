<p align="center">
 <img width="300px" src="https://cdn-icons-png.flaticon.com/512/5650/5650380.png" alt="Example">
</p>
<p align="center">
    <b>EXAMPLES</b>
</p>

### User Service

<div class="termy">

```Python
from fastapi_auth_user.models import RoleNameEnum
from fastapi_auth_user.users import user_service
from fastapi_auth_user.users.schema import UserCreate, UserTokenResponse, UserRoles

if __name__ == "__main__":
	user: UserCreate = UserCreate(        # Create user (pedantic model) with next fields:
		name="SomeName",              # Name
		email="Some_name@gmail.com",  # Email (has validator)
		password="Aa1!LongPassword"   # Password (has validator)
	)
	user_response: UserTokenResponse = user_service.create(user)  # Create user on db and return response
	user_roles: UserRoles = user_service.add_role_for_user(user_response.id,
	                                                       RoleNameEnum.ADMIN)  # Add for him role 'Admin'


```

</div>