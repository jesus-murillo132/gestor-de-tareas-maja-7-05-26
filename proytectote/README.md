# Aplicación básica Flask + MongoDB Atlas

1. Configura las variables de entorno:
   - `MONGO_URI`: tu cadena de conexión de MongoDB Atlas
   - `MONGO_DBNAME`: nombre de la base de datos (por ejemplo, `appdb`)
   - `FLASK_SECRET_KEY`: clave secreta para sesiones

2. Instala dependencias:
   ```bash
   pip install -r requirements.txt
   ```

3. Instala el proyecto usando `pyproject.toml`:
   ```bash
   pip install -e .
   ```

4. Ejecuta con uvicorn:
   ```bash
   uvicorn app:app --reload --host 0.0.0.0 --port 8000
   ```

5. Abre el navegador en `http://127.0.0.1:8000`
