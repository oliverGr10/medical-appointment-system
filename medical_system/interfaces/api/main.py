from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import appointments, doctors, patients, admin

app = FastAPI(
    title="Sistema de Gestión de Citas Médicas",
    description="API para gestionar citas médicas siguiendo Clean Architecture",
    version="1.0.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(patients.router, prefix="/api/patients", tags=["Pacientes"])
app.include_router(doctors.router, prefix="/api/doctors", tags=["Doctores"])
app.include_router(appointments.router, prefix="/api/appointments", tags=["Citas"])
app.include_router(admin.router, prefix="/api/admin", tags=["Administración"])

@app.get("/")
async def root():
    return {
        "message": "Bienvenido al Sistema de Gestión de Citas Médicas",
        "docs": "/docs",
        "redoc": "/redoc"
    }
