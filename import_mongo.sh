#!/bin/bash

# Ejecutar el script Python
python script_python.txt DatosSucios DatosLimpios

# Eliminar la base de datos
mongosh --eval "use bbdd2" --eval "db.dropDatabase()"

# Importar los archivos CSV a MongoDB
mongoimport --db bbdd2 --collection areas --type csv --file ./DatosLimpios/AreasLimpio.csv --headerline
mongoimport --db bbdd2 --collection juegos --type csv --file ./DatosLimpios/JuegosLimpio.csv --headerline
mongoimport --db bbdd2 --collection incidentes_seguridad --type csv --file ./DatosLimpios/IncidentesSeguridadLimpio.csv --headerline
mongoimport --db bbdd2 --collection mantenimiento --type csv --file ./DatosLimpios/MantenimientoLimpio.csv --headerline
mongoimport --db bbdd2 --collection encuestas_satisfaccion --type csv --file ./DatosLimpios/EncuestasSatisfaccionLimpio.csv --headerline
mongoimport --db bbdd2 --collection incidencias_usuarios --type csv --file ./DatosLimpios/IncidenciasUsuariosLimpio.csv --headerline
mongoimport --db bbdd2 --collection meteo24 --type csv --file ./DatosLimpios/Meteo24Limpio.csv --headerline
mongoimport --db bbdd2 --collection estaciones_meteo_codigo_postal --type csv --file ./DatosLimpios/EstacionesMeteoCodigoPostalLimpio.csv --headerline
mongoimport --db bbdd2 --collection usuarios --type csv --file ./DatosLimpios/UsuariosLimpio.csv --headerline

# Ejecutar el script de migración
mongosh --quiet < migracion_mongo.txt
