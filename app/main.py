from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
import docker
from docker.errors import APIError, NotFound
import logging
from fastapi.middleware.cors import CORSMiddleware
from docker.errors import ContainerError


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # This is for development only; adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve index.html at the root
@app.get("/")
async def root():
    return FileResponse('static/index.html')

# Docker client initialization
client = docker.from_env()

# Pydantic models
class DeployContainer(BaseModel):
    image: str
    command: Optional[str] = ""

class ExecuteCommand(BaseModel):
    container_id: str
    command: str


# Endpoint to deploy a new Docker container
@app.post("/deploy/")
async def deploy_container(deploy_request: DeployContainer):
    try:
        container = client.containers.run(deploy_request.image, deploy_request.command, detach=True)
        logger.info(f"Container deployed with image {deploy_request.image} and ID: {container.id}")
        return {"message": "Container deployed", "id": container.id}
    except APIError as e:
        logger.error(f"Error deploying container: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint to execute a command in an existing Docker container
@app.post("/execute/")
async def execute_command(exec_request: ExecuteCommand):
    try:
        container = client.containers.get(exec_request.container_id)
        # Wrap the command to ensure it's executed in a shell
        command_to_execute = f"/bin/sh -c '{exec_request.command}'"
        exit_code, output = container.exec_run(command_to_execute)
        if exit_code == 0:
            formatted_output = output.decode().splitlines()
            return {"exit_code": exit_code, "output": formatted_output}
        else:
            # Handle non-zero exit codes (indicating command failure)
            formatted_output = output.decode().splitlines()
            return {"exit_code": exit_code, "error": formatted_output}
    except NotFound:
        return {"error": "Container not found"}, 404
    except ContainerError as e:
        return {"error": str(e)}, 500
@app.get("/container_status/{container_id}")
async def get_container_status(container_id: str):
    try:
        container = client.containers.get(container_id)
        status = container.status
        return {"status": status}
    except NotFound:
        raise HTTPException(status_code=404, detail="Container not found")
    except APIError as e:
        logger.error(f"Error fetching container status: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
