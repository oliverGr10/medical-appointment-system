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
   git clone https://git@github.com:oliverGr10/medical-appointment-system.git
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

## 🧪 Pruebas

El proyecto incluye pruebas unitarias para garantizar la calidad del código. A continuación se detallan los comandos para ejecutar las pruebas:

### Ejecutar todas las pruebas
```bash
# Ejecutar todos los tests
pytest

# Mostrar salida detallada
pytest -v

# Detener en el primer error
pytest -x
```

### Ejecutar pruebas específicas
```bash
# Ejecutar tests de un archivo específico
pytest tests/unit/patient/test_update_patient.py

# Ejecutar una clase de test específica
pytest tests/unit/patient/test_update_patient.py::TestUpdatePatientUseCase

# Ejecutar un test específico
pytest tests/unit/patient/test_update_patient.py::TestUpdatePatientUseCase::test_should_update_patient_when_admin_and_data_valid
```

### Cobertura de código
```bash
# Instalar pytest-cov si no está instalado
pip install pytest-cov

# Ejecutar pruebas con cobertura
pytest --cov=medical_system tests/

# Incluir informe HTML
pytest --cov=medical_system --cov-report=html tests/
```

### Depuración de tests
```bash
# Mostrar salida de print() en los tests
pytest -s

# Ejecutar con el depurador (pdb)
pytest --pdb
```

## 📚 Documentación de la API

### Documentación Interactiva
La API incluye documentación interactiva que puedes explorar directamente desde tu navegador:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Autenticación
El sistema utiliza JWT (JSON Web Tokens) para la autenticación. Los endpoints de autenticación están bajo el prefijo `/api/auth/`.

### Uso con Postman
Puedes probar fácilmente la API usando Postman. Aquí tienes algunos ejemplos:

#### 1. Autenticación
```
POST http://localhost:8000/api/auth/login
Content-Type: application/json

{
  "email": "admin@clinica.com",
  "password": "Admin123!"
}
```

#### 2. Obtener perfil de usuario
```
GET http://localhost:8000/api/auth/me
Authorization: Bearer <tu_token_acceso>
```

#### 3. Crear una cita
```
POST http://localhost:8000/api/appointments/
Authorization: Bearer <tu_token_acceso>
Content-Type: application/json

{
  "doctor_id": 1,
  "patient_id": 1,
  "scheduled_time": "2025-06-10T10:00:00",
  "reason": "Consulta general"
}
```

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

## 🚀 Instalación y Ejecución

### Requisitos previos
- Python 3.8+
- pip (gestor de paquetes de Python)

### Instalación

1. Clona el repositorio:
   ```bash
   git clone https://github.com/tu-usuario/medical-appointment-system.git
   cd medical-appointment-system
   ```

2. Crea y activa un entorno virtual (recomendado):
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: .\venv\Scripts\activate
   ```

3. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

### Configuración

Crea un archivo `.env` en la raíz del proyecto con las siguientes variables de autenticación:

```bash
# Configuración de autenticación
SECRET_KEY=tu_clave_secreta_muy_segura
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

> **Nota:** Este proyecto utiliza almacenamiento en memoria. Todos los datos se perderán al reiniciar el servidor.

### Ejecución

Puedes iniciar el servidor de desarrollo de dos formas:

1. Usando el script `run.py` (recomendado):
   ```bash
   python run.py
   ```

2. O directamente con uvicorn:
   ```bash
   uvicorn medical_system.interfaces.api.main:app --reload
   ```

El servidor estará disponible en: http://127.0.0.1:8000

### Documentación de la API

Una vez ejecutando el servidor, puedes acceder a:
- Documentación interactiva: http://127.0.0.1:8000/docs
- Documentación alternativa: http://127.0.0.1:8000/redoc

## 🚀 ¿Por qué FastAPI?

Elegimos FastAPI sobre Django REST Framework por:
- **Rendimiento superior**: Más rápido gracias a su diseño asíncrono
- **Menos código**: Sintaxis más concisa y menos boilerplate
- **Validación integrada**: Tipado estático con Pydantic
- **Documentación automática**: Interfaz Swagger/ReDoc generada automáticamente
- **Moderno**: Soporte nativo para async/await

> **Nota sobre Swagger UI**:
> Si experimentas problemas con la autenticación en Swagger UI, prueba lo siguiente:
> 1. Usa el botón "Authorize" (candado) en la esquina superior derecha
> 2. Ingresa el token sin la palabra "Bearer"
> 3. O mejor aún, usa Postman para pruebas más confiables

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
