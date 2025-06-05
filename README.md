# Sistema de Gestión de Citas Médicas

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Testing: pytest](https://img.shields.io/badge/testing-pytest-blue.svg)](https://docs.pytest.org/)

Sistema de gestión de citas médicas implementado con Python y FastAPI, siguiendo los principios de Clean Architecture.

## 🚀 Características Principales

- Gestión de pacientes, doctores y citas médicas
- Validación de datos y reglas de negocio
- API RESTful documentada
- Arquitectura limpia y desacoplada
- Almacenamiento en memoria (sin dependencias externas)
- Pruebas unitarias

## 🛠️ Tecnologías

- [Python 3.8+](https://www.python.org/)
- [FastAPI](https://fastapi.tiangolo.com/) - Framework web moderno y rápido para APIs
- [pytest](https://docs.pytest.org/) - Framework de pruebas
- [uvicorn](https://www.uvicorn.org/) - Servidor ASGI

## 📋 Requisitos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)

## 🚀 Instalación

1. Clonar el repositorio:
   ```bash
   git clone https://github.com/tu-usuario/medical-appointment-system.git
   cd medical-appointment-system
   ```

2. Crear y activar entorno virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```

3. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```

## ▶️ Ejecución

### Servidor de Desarrollo
```bash
uvicorn medical_system.interfaces.api.main:app --reload
```

### Ejecutar Pruebas
```bash
pytest tests/
```

## 📚 Documentación de la API

La API incluye documentación interactiva:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔍 Endpoints Principales

### Pacientes
- `POST /api/patients/` - Crear paciente
- `GET /api/patients/` - Listar pacientes
- `GET /api/patients/{id}` - Obtener paciente
- `PUT /api/patients/{id}` - Actualizar paciente

### Doctores
- `POST /api/doctors/` - Crear doctor
- `GET /api/doctors/` - Listar doctores
- `GET /api/doctors/specialty/{especialidad}` - Buscar por especialidad

### Citas
- `POST /api/appointments/` - Crear cita
- `GET /api/appointments/doctor/{id}` - Citas por doctor
- `GET /api/appointments/patient/{id}` - Citas por paciente
- `PUT /api/appointments/{id}/cancel` - Cancelar cita
- `PUT /api/appointments/{id}/complete` - Completar cita

## 🏗️ Estructura del Proyecto

```
medical-system/
├── medical_system/
│   ├── domain/           # Entidades y reglas de negocio
│   ├── usecases/         # Casos de uso
│   ├── infrastructure/   # Implementaciones concretas
│   └── interfaces/       # API y controladores
├── tests/               # Pruebas unitarias
├── requirements.txt      # Dependencias
└── README.md            # Documentación
```

## 🚀 ¿Por qué FastAPI?

Elegimos FastAPI sobre Django REST Framework por:
- **Rendimiento superior**: Más rápido gracias a su diseño asíncrono
- **Menos código**: Sintaxis más concisa y menos boilerplate
- **Validación integrada**: Tipado estático con Pydantic
- **Documentación automática**: Interfaz Swagger/ReDoc generada automáticamente
- **Moderno**: Soporte nativo para async/await

## 📝 Decisiones de Diseño

- **Clean Architecture**: Separación clara de responsabilidades
- **DTOs**: Transferencia segura de datos
- **Repositorios**: Abstracción del acceso a datos
- **Contenedor Simple**: Gestión básica de dependencias

## ⚠️ Limitaciones

- Sin autenticación/autorización
- Almacenamiento en memoria (se pierde al reiniciar)
- Sin manejo de concurrencia

## 📄 Licencia

MIT License
