from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from linked_roles import LinkedRolesOAuth2, RoleConnection
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(title="Custom Linked Roles Bot")

client = LinkedRolesOAuth2(
    client_id=os.getenv("DISCORD_CLIENT_ID"),
    client_secret=os.getenv("DISCORD_CLIENT_SECRET"),
    redirect_uri=os.getenv("DISCORD_REDIRECT_URI"),
    scopes=("role_connections.write", "identify"),
)

# ✅ Ensure client session is started properly
@app.on_event("startup")
async def startup():
    await client.start()

@app.on_event("shutdown")
async def shutdown():
    await client.close()

@app.get("/linked-role")
async def linked_roles():
    url = client.get_oauth_url()
    return RedirectResponse(url=url)

@app.get("/verified-role")
async def verified_role(code: str):
    token = await client.get_access_token(code)
    user = await client.fetch_user(token)

    if user is None:
        return {"error": "User not found"}

    role = await user.fetch_role_connection()
    if role is None:
        role = RoleConnection(platform_name="Test", platform_username=str(user))
        role.add_metadata(key="custom_stat", value=100)
        await user.edit_role_connection(role)

    return "Linked Role assigned successfully!"
