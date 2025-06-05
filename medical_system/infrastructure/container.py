from medical_system.infrastructure.persistence.in_memory.in_memory_appointment_repository import InMemoryAppointmentRepository
from medical_system.infrastructure.persistence.in_memory.in_memory_patient_repository import InMemoryPatientRepository
from medical_system.infrastructure.persistence.in_memory.in_memory_doctor_repository import InMemoryDoctorRepository
from medical_system.infrastructure.persistence.in_memory.in_memory_user_repository import InMemoryUserRepository

appointment_repo = InMemoryAppointmentRepository()
patient_repo = InMemoryPatientRepository()
doctor_repo = InMemoryDoctorRepository()
user_repo = InMemoryUserRepository()

def get_appointment_repository():
    return appointment_repo

def get_patient_repository():
    return patient_repo

def get_doctor_repository():
    return doctor_repo

def get_user_repository():
    return user_repo
