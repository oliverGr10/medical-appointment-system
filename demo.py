"""
Demo del Sistema de Citas Médicas

Este script demuestra todas las funcionalidades implementadas:
1. Gestión de Pacientes
2. Gestión de Doctores
3. Gestión de Citas
4. Búsquedas y consultas
"""
from datetime import date, time, datetime, timedelta
from typing import List

# Configuración
print("=== Inicializando Sistema de Citas Médicas ===\n")

# 1. Inicializar repositorios
from medical_system.infrastructure.persistence.in_memory.in_memory_patient_repository import InMemoryPatientRepository
from medical_system.infrastructure.persistence.in_memory.in_memory_doctor_repository import InMemoryDoctorRepository
from medical_system.infrastructure.persistence.in_memory.in_memory_appointment_repository import InMemoryAppointmentRepository

patient_repo = InMemoryPatientRepository()
doctor_repo = InMemoryDoctorRepository()
appointment_repo = InMemoryAppointmentRepository()

# 2. Helper para imprimir títulos
def print_section(title: str):
    print(f"\n{'='*50}")
    print(f" {title.upper()} ")
    print(f"{'='*50}")

# 3. Crear algunos pacientes
print_section("1. Registrando Pacientes")

from medical_system.application.use_cases.patient.create_patient import CreatePatientUseCase
from medical_system.application.dtos.patient_dto import CreatePatientDTO

create_patient = CreatePatientUseCase(patient_repo)

patients = [
    CreatePatientDTO(
        name="Juan Pérez",
        email="juan@example.com",
        birth_date=date(1990, 1, 1)
    ),
    CreatePatientDTO(
        name="María López",
        email="maria@example.com",
        birth_date=date(1985, 5, 15)
    )
]

created_patients = []
for patient_data in patients:
    patient = create_patient.execute(patient_data)
    created_patients.append(patient)
    print(f"✓ Paciente registrado: {patient.name} (ID: {patient.id})")

# 4. Crear algunos doctores
print_section("2. Registrando Doctores")

from medical_system.application.use_cases.doctor.create_doctor import CreateDoctorUseCase
from medical_system.application.dtos.doctor_dto import CreateDoctorDTO

create_doctor = CreateDoctorUseCase(doctor_repo)

doctors = [
    CreateDoctorDTO(
        name="Dr. Carlos García",
        email="dr.garcia@example.com",
        specialty="Cardiología"
    ),
    CreateDoctorDTO(
        name="Dra. Ana Martínez",
        email="dra.martinez@example.com",
        specialty="Pediatría"
    )
]

created_doctors = []
for doctor_data in doctors:
    doctor = create_doctor.execute(doctor_data)
    created_doctors.append(doctor)
    print(f"✓ Doctor registrado: {doctor.name} - {doctor.specialty} (ID: {doctor.id})")

# 5. Buscar doctores por especialidad
print_section("3. Buscando Doctores por Especialidad")

from medical_system.application.use_cases.doctor.list_doctors_by_specialty import ListDoctorsBySpecialtyUseCase

find_doctors = ListDoctorsBySpecialtyUseCase(doctor_repo)
cardiologos = find_doctors.execute("Cardiología")
print("\nCardiólogos disponibles:")
for doc in cardiologos:
    print(f"- {doc.name} ({doc.email})")

# 6. Crear citas
print_section("4. Programando Citas")

from medical_system.application.use_cases.appointment.create_appointment import CreateAppointmentUseCase
from medical_system.application.dtos.appointment_dto import CreateAppointmentDTO

create_appointment = CreateAppointmentUseCase(
    appointment_repo, 
    patient_repo, 
    doctor_repo
)

# Crear algunas citas para hoy y mañana
today = date.today()
tomorrow = today + timedelta(days=1)

appointments = [
    # Cita 1: Juan con el cardiólogo hoy a las 10:00
    CreateAppointmentDTO(
        patient_id=created_patients[0].id,
        doctor_id=created_doctors[0].id,
        date=today,
        time=time(10, 0)
    ),
    # Cita 2: María con la pediatra mañana a las 11:00
    CreateAppointmentDTO(
        patient_id=created_patients[1].id,
        doctor_id=created_doctors[1].id,
        date=tomorrow,
        time=time(11, 0)
    )
]

created_appointments = []
for apt_data in appointments:
    try:
        appointment = create_appointment.execute(apt_data)
        created_appointments.append(appointment)
        print(f"✓ Cita programada: {appointment.date} a las {appointment.time.strftime('%H:%M')} con {appointment.doctor.name}")
    except Exception as e:
        print(f"✗ Error al programar cita: {str(e)}")

# 7. Intentar crear una cita en horario no laboral (debe fallar)
print_section("5. Validación: Horario No Laboral")
try:
    invalid_appointment = create_appointment.execute(CreateAppointmentDTO(
        patient_id=created_patients[0].id,
        doctor_id=created_doctors[0].id,
        date=today,
        time=time(7, 0)  # Demasiado temprano
    ))
except ValueError as e:
    print(f"✓ Validación exitosa: {str(e)}")

# 8. Listar citas de un doctor
print_section("6. Citas del Dr. García")

from medical_system.application.use_cases.appointment.get_doctor_appointments import GetDoctorAppointmentsUseCase
from medical_system.application.dtos.appointment_dto import GetDoctorAppointmentsDTO

get_doctor_appointments = GetDoctorAppointmentsUseCase(
    appointment_repository=appointment_repo,
    doctor_repository=doctor_repo
)
doctor_appointments = get_doctor_appointments.execute(
    doctor_id=created_doctors[0].id,
    request_date=today,
    requesting_doctor_id=created_doctors[0].id
)

print(f"\nCitas del Dr. {created_doctors[0].name} para hoy (ID: {created_doctors[0].id}):")
for apt in doctor_appointments:
    print(f"- {apt.time.strftime('%H:%M')} con {apt.patient.name}")

# 9. Cancelar una cita
print_section("7. Cancelando una cita")

from medical_system.application.use_cases.appointment.cancel_appointment import CancelAppointmentUseCase

cancel_appointment = CancelAppointmentUseCase(
    appointment_repository=appointment_repo,
    patient_repository=patient_repo
)

if created_appointments:
    appointment_to_cancel = created_appointments[0]
    try:
        canceled = cancel_appointment.execute(appointment_to_cancel.id, appointment_to_cancel.patient.id)
        print(f"✓ Cita cancelada: ID {canceled.id} - {canceled.date} a las {canceled.time.strftime('%H:%M')}")
        print(f"   Estado actual: {canceled.status}")
    except Exception as e:
        print(f"✗ Error al cancelar cita: {str(e)}")

# 10. Listar todas las citas (como administrador)
print_section("8. Listado Completo de Citas (Admin)")

from medical_system.application.use_cases.appointment.list_all_appointments import ListAllAppointmentsUseCase

list_all = ListAllAppointmentsUseCase(appointment_repo)
all_appointments = list_all.execute()

print("\nTodas las citas en el sistema:")
for apt in all_appointments:
    status = "✓" if apt.status == "scheduled" else "✗" if apt.status == "cancelled" else "✓ (Completada)"
    print(f"{status} {apt.date} {apt.time.strftime('%H:%M')} - {apt.patient.name} con {apt.doctor.name} ({apt.doctor.specialty})")

print("\n¡Demostración completada con éxito!")
print("="*50)
