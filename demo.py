
from datetime import date, time, timedelta
from typing import List, Dict, Any

BUSINESS_HOURS = {
    'start': time(9, 0),   # 9:00 AM
    'end': time(18, 0)    # 6:00 PM
}

def main():
    print("=== Inicializando Sistema de Citas Médicas ===\n")

    # 1. Inicializar repositorios
    from medical_system.infrastructure.persistence.in_memory.in_memory_patient_repository import InMemoryPatientRepository
    from medical_system.infrastructure.persistence.in_memory.in_memory_doctor_repository import InMemoryDoctorRepository
    from medical_system.infrastructure.persistence.in_memory.in_memory_appointment_repository import InMemoryAppointmentRepository

    patient_repo = InMemoryPatientRepository()
    doctor_repo = InMemoryDoctorRepository()
    appointment_repo = InMemoryAppointmentRepository()

    # 2. Helper para imprimir títulos
    def print_section(title: str) -> None:
        """Imprime un título de sección formateado.
        
        Args:
            title: Título de la sección a mostrar.
        """
        print(f"\n{'='*50}")
        print(f" {title.upper()} ")
        print(f"{'='*50}")

    # 3. Crear algunos pacientes
    print_section("1. Registrando Pacientes")

    from medical_system.usecases.patient.create_patient import CreatePatientUseCase
    from medical_system.usecases.dtos.patient_dto import CreatePatientDTO

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

    from medical_system.usecases.doctor.create_doctor import CreateDoctorUseCase
    from medical_system.usecases.dtos.doctor_dto import CreateDoctorDTO

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

    from medical_system.usecases.doctor.list_doctors_by_specialty import ListDoctorsBySpecialtyUseCase

    find_doctors = ListDoctorsBySpecialtyUseCase(doctor_repo)
    cardiologos = find_doctors.execute("Cardiología")
    print("\nCardiólogos disponibles:")
    for doc in cardiologos:
        print(f"- {doc.name} ({doc.email})")

    # 6. Crear citas
    print_section("4. Programando Citas")

    from medical_system.usecases.appointment.create_appointment import CreateAppointmentUseCase
    from medical_system.usecases.dtos.appointment_dto import CreateAppointmentDTO

    create_appointment = CreateAppointmentUseCase(
        appointment_repo, 
        patient_repo, 
        doctor_repo
    )

    # Crear algunas citas para hoy y mañana
    today = date.today()
    tomorrow = today + timedelta(days=1)

    # Obtener información de pacientes y doctores
    patient1 = patient_repo.find_by_id(created_patients[0].id)
    patient2 = patient_repo.find_by_id(created_patients[1].id)
    doctor1 = doctor_repo.find_by_id(created_doctors[0].id)
    doctor2 = doctor_repo.find_by_id(created_doctors[1].id)

    appointments = [
        # Cita 1: Juan con el cardiólogo mañana a las 10:00
        {
            'patient_id': patient1.id,
            'doctor_id': doctor1.id,
            'date': tomorrow,
            'time': time(10, 0)
        },
        # Cita 2: María con la pediatra mañana a las 11:00
        {
            'patient_id': patient2.id,
            'doctor_id': doctor2.id,
            'date': tomorrow,
            'time': time(11, 0)
        }
    ]

    created_appointments = []
    for apt_data in appointments:
        try:
            appointment_dto = CreateAppointmentDTO(**apt_data)
            appointment = create_appointment.execute(appointment_dto)
            created_appointments.append(appointment)
            print(f"✓ Cita programada: {appointment.date} a las {appointment.time.strftime('%H:%M')} con {appointment.doctor_name}")
        except ValueError as e:
            print(f"✗ Validación fallida: {str(e)}")
        except Exception as e:
            print(f"✗ Error inesperado al programar cita: {str(e)}")

    # 7. Intentar crear una cita en horario no laboral (debe fallar)
    print_section("5. Validación: Horario No Laboral")
    try:
        invalid_appointment_data = {
            'patient_id': patient1.id,
            'doctor_id': doctor1.id,
            'date': today,
            'time': time(7, 0)  # Demasiado temprano
        }
        invalid_appointment = create_appointment.execute(CreateAppointmentDTO(**invalid_appointment_data))
    except ValueError as e:
        print(f"✓ Validación exitosa: {str(e)}")
    except Exception as e:
        print(f"✗ Error inesperado: {str(e)}")

    # 8. Listar citas de un doctor
    print_section("6. Citas del Dr. García")

    from medical_system.usecases.appointment.get_doctor_appointments import GetDoctorAppointmentsUseCase
    from medical_system.usecases.dtos.appointment_dto import GetDoctorAppointmentsDTO

    get_doctor_appointments = GetDoctorAppointmentsUseCase(
        appointment_repository=appointment_repo,
        doctor_repository=doctor_repo
    )
    
    # Buscar citas para mañana
    doctor_appointments = get_doctor_appointments.execute(
        doctor_id=doctor1.id,
        request_date=tomorrow,  # Buscar citas para mañana
        requesting_doctor_id=doctor1.id
    )

    print(f"\nCitas del Dr. {doctor1.name} para mañana ({tomorrow}):")
    if not doctor_appointments:
        print("No hay citas programadas para esta fecha.")
    else:
        for apt in doctor_appointments:
            status = "✓" if apt.status == "scheduled" else "✗" if apt.status == "cancelled" else "✓ (Completada)"
            print(f"{status} {apt.time.strftime('%H:%M')} - {apt.patient_name}")
    
    # Mostrar mensaje si no hay citas programadas
    if not created_appointments:
        print("\n⚠️ No se pudieron crear las citas de prueba. Verifica los mensajes de error anteriores.")

    # 9. Cancelar una cita
    print_section("7. Cancelando una cita")

    from medical_system.usecases.appointment.cancel_appointment import CancelAppointmentUseCase

    cancel_appointment = CancelAppointmentUseCase(
        appointment_repository=appointment_repo,
        patient_repository=patient_repo
    )

    if not created_appointments:
        print("⚠️ No hay citas disponibles para cancelar.")
    else:
        # Usar la primera cita creada
        appointment_to_cancel = created_appointments[0]
        
        # Mostrar información de la cita antes de cancelar
        print(f"\nIntentando cancelar cita ID {appointment_to_cancel.id}:")
        print(f"- Paciente: {appointment_to_cancel.patient_name}")
        print(f"- Doctor: {appointment_to_cancel.doctor_name}")
        print(f"- Fecha: {appointment_to_cancel.date}")
        print(f"- Hora: {appointment_to_cancel.time.strftime('%H:%M')}")
        print(f"- Estado actual: {appointment_to_cancel.status}")
        
        try:
            # Obtener el ID del paciente del objeto patient
            patient_id = None
            if hasattr(appointment_to_cancel, 'patient') and hasattr(appointment_to_cancel.patient, 'id'):
                patient_id = appointment_to_cancel.patient.id
            elif hasattr(appointment_to_cancel, 'patient_id'):
                patient_id = appointment_to_cancel.patient_id
            else:
                raise ValueError("No se pudo determinar el ID del paciente")
                
            # Intentar cancelar la cita
            canceled = cancel_appointment.execute(
                appointment_id=appointment_to_cancel.id, 
                patient_id=patient_id
            )
            
            # Mostrar confirmación de cancelación
            print("\n✅ Cita cancelada exitosamente:")
            print(f"- ID: {canceled.id}")
            print(f"- Fecha: {canceled.date}")
            print(f"- Hora: {canceled.time.strftime('%H:%M')}")
            print(f"- Nuevo estado: {canceled.status}")
            
        except ValueError as e:
            print(f"\n✗ No se pudo cancelar la cita: {str(e)}")
        except Exception as e:
            print(f"\n✗ Error inesperado al cancelar la cita: {str(e)}")

    # 9. Marcar cita como completada (como doctor)
    print_section("8. Marcar Cita como Completada (Doctor)")
    
    from medical_system.usecases.appointment.mark_appointment_completed import MarkAppointmentCompletedUseCase
    
    mark_completed = MarkAppointmentCompletedUseCase(appointment_repo)
    
    if created_appointments:
        # Tomar la primera cita creada
        appointment_to_complete = created_appointments[0]
        
        # Mostrar información de la cita antes de marcarla como completada
        print(f"\nIntentando marcar como completada la cita ID {appointment_to_complete.id}:")
        print(f"- Paciente: {appointment_to_complete.patient_name}")
        print(f"- Doctor: {appointment_to_complete.doctor_name}")
        print(f"- Fecha: {appointment_to_complete.date}")
        print(f"- Hora: {appointment_to_complete.time.strftime('%H:%M')}")
        print(f"- Estado actual: {appointment_to_complete.status}")
        
        try:
            # Obtener el ID del doctor (asumiendo que es el doctor de la cita)
            doctor_id = appointment_to_complete.doctor.id
            
            # Marcar como completada
            completed = mark_completed.execute(
                appointment_id=appointment_to_complete.id,
                doctor_id=doctor_id
            )
            
            # Mostrar confirmación
            print("\n✅ Cita marcada como completada exitosamente:")
            print(f"- ID: {completed.id}")
            print(f"- Fecha: {completed.date}")
            print(f"- Hora: {completed.time.strftime('%H:%M')}")
            print(f"- Nuevo estado: {completed.status}")
            
            # Actualizar la cita en la lista
            appointment_to_complete = completed
            
        except ValueError as e:
            print(f"\n✗ No se pudo marcar la cita como completada: {str(e)}")
        except UnauthorizedError as e:
            print(f"\n✗ No autorizado: {str(e)}")
        except Exception as e:
            print(f"\n✗ Error inesperado al marcar la cita como completada: {str(e)}")
    else:
        print("⚠️ No hay citas disponibles para marcar como completadas.")

    # 10. Listar todas las citas (como administrador)
    print_section("9. Listado Completo de Citas (Admin)")

    from medical_system.usecases.appointment.list_all_appointments import ListAllAppointmentsUseCase

    list_all = ListAllAppointmentsUseCase(appointment_repo)
    all_appointments = list_all.execute()

    if not all_appointments:
        print("\nNo hay citas registradas en el sistema.")
    else:
        print("\n📋 Todas las citas en el sistema:")
        print("-" * 80)
        print(f"{'Estado':<15} {'Fecha':<12} {'Hora':<8} {'Paciente':<20} {'Doctor':<20} Especialidad")
        print("-" * 80)
        
        for apt in all_appointments:
            # Determinar el estado con emoji
            if isinstance(apt, dict):
                # Si es un diccionario (formato antiguo)
                status = apt.get('status', 'unknown')
                status_emoji = "✅" if status == "scheduled" else "❌" if status == "cancelled" else "✓"
                date_str = str(apt.get('date', 'N/A'))
                time_str = str(apt.get('time', '')) if 'time' in apt else ''
                patient_name = apt.get('patient', {}).get('name', 'N/A')
                doctor_name = apt.get('doctor', {}).get('name', 'N/A')
                specialty = apt.get('doctor', {}).get('specialty', 'Sin especialidad')
            else:
                # Si es un objeto DTO
                status = getattr(apt, 'status', 'unknown')
                status_emoji = "✅" if status == "scheduled" else "❌" if status == "cancelled" else "✓"
                date_str = str(getattr(apt, 'date', 'N/A'))
                time_obj = getattr(apt, 'time', None)
                time_str = time_obj.strftime('%H:%M') if time_obj else ''
                patient_name = getattr(apt, 'patient_name', getattr(apt.patient, 'name', 'N/A') if hasattr(apt, 'patient') else 'N/A')
                doctor_name = getattr(apt, 'doctor_name', getattr(apt.doctor, 'name', 'N/A') if hasattr(apt, 'doctor') else 'N/A')
                specialty = getattr(apt.doctor, 'specialty', 'Sin especialidad') if hasattr(apt, 'doctor') else 'Sin especialidad'
            
            print(f"{status_emoji} {status.title():<12} {date_str:<12} {time_str:<8} {patient_name:<20} {doctor_name:<20} {specialty}")
    
    # Mostrar resumen final
    print("\n" + "=" * 50)
    print("¡Demostración completada con éxito! 🎉")
    print("=" * 50)
    
    print("\nResumen de acciones:")
    print(f"- Pacientes registrados: {len(patient_repo.find_all())}")
    print(f"- Doctores registrados: {len(doctor_repo.find_all())}")
    print(f"- Citas programadas: {sum(1 for a in appointment_repo.find_all() if a.status.value == 'Programada')}")
    print(f"- Citas completadas: {sum(1 for a in appointment_repo.find_all() if a.status.value == 'Completada')}")
    print(f"- Citas canceladas: {sum(1 for a in appointment_repo.find_all() if a.status.value == 'Cancelada')}")
    print("\n" + "=" * 50)

if __name__ == "__main__":
    main()
