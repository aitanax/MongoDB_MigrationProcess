use bbdd2;

db.runCommand({
    collMod: "areas", 
    validator: {
        $jsonSchema: {
            bsonType: "object",
            title: "Validator Areas",
            required: ["_id", "DESC_CLASIFICACION", "COD_BARRIO", "BARRIO", "COD_DISTRITO", "DISTRITO", "ESTADO", "COORD_GIS_X", "COORD_GIS_Y", "LATITUD", "LONGITUD", "TIPO_VIA", "NOM_VIA", "NUM_VIA", "COD_POSTAL", "FECHA_INSTALACION"],
            properties: {
                _id: {
                    bsonType: "string",
                    description: "ID del área"
                },
                DESC_CLASIFICACION: {
                    bsonType: "string",
                    enum: ["AREA DE JUEGOS/ESPECIAL", "AREA DE MAYORES", "AREA INFANTIL", "CIRCUITO DEPORTIVO ELEMENTAL"],
                    description: "Descripción del tipo de área recreativa"
                },
                COD_BARRIO: {
                    bsonType: "int",
                    description: "Código del barrio del área"
                },
                BARRIO: {
                    bsonType: "string",
                    description: "Barrio del área"
                },
                COD_DISTRITO: {
                    bsonType: "int",
                    description: "Código del distrito del área"
                },
                DISTRITO: {
                    bsonType: "string",
                    description: "Distrito del área"
                },
                ESTADO: {
                    bsonType: "string",
                    enum: ["OPERATIVO"],
                    description: "Estado del área"
                },
                COORD_GIS_X: {
                    bsonType: "number",
                    description: "Coordenadas en el eje X del área"
                },
                COORD_GIS_Y: {
                    bsonType: "number",
                    description: "Coordenadas en el eje Y del área"
                },
                LATITUD: {
                    bsonType: "string",
                    description: "Latitud del área"
                },
                LONGITUD: {
                    bsonType: "string",
                    description: "Longitud del área"
                },
                TIPO_VIA: {
                    bsonType: "string",
                    description: "Tipo del vía del área"
                },
                NOM_VIA: {
                    bsonType: "string",
                    description: "Nombre de la vía del área"
                },
                NUM_VIA: {
                    bsonType: "string",
                    description: "Número de la vía del área"
                },
                COD_POSTAL: {
                    bsonType: "string",
                    description: "Código postal de la zona donde se encuentra el área"
                },
                FECHA_INSTALACION: {
                    bsonType: "date",
                    description: "Fecha en la que se instaló el área"
                },
                TOTAL_ELEM: {
                    bsonType: "int",
                    description: "Número de juegos"
                },
                TIPO: {
                    bsonType: "string",
                    description: "Tipo de área"
                },
                CAPACIDAD_MAX: {
                    bsonType: "int",
                    description: "Capacidad máxima"
                },
                CANTIDAD_POR_TIPO_JUEGO: {
                    bsonType: "string",
                    description: "Capacidad de juegos por tipo"
                }
            }
        }
    }
});

db.runCommand({ 
    collMod: "juegos", 
    validator: {
        $jsonSchema: {
            bsonType: "object",
            title: "Validator Juegos",
            required: ["ID", "DESC_CLASIFICACION", "COD_BARRIO", "BARRIO", "COD_DISTRITO", "DISTRITO", "ESTADO", "COORD_GIS_X", "COORD_GIS_Y", "LATITUD", "LONGITUD", "TIPO_VIA", "NOM_VIA", "NUM_VIA", "COD_POSTAL", "FECHA_INSTALACION", "MODELO", "TIPO_JUEGO", "ACCESIBLE", "NDP_AREA", "INDICADOREXPOSICION","DESGASTE_ACUMULADO"],
            properties: {
                _id: {
                    bsonType: "string",
                    description: "Id del juego"
                },
                DESC_CLASIFICACION: {
                    bsonType: "string",
                    description: "Descripción del tipo de juego recreativa"
                },
                COD_BARRIO: {
                    bsonType: "int",
                    description: "Código del barrio del juego"
                },
                BARRIO: {
                    bsonType: "string",
                    description: "Barrio Del juego"
                },
                COD_DISTRITO: {
                    bsonType: "int",
                    description: "Código del distrito del juego"
                },
                DISTRITO: {
                    bsonType: "string",
                    description: "Distrito del juego"
                },
                ESTADO: {
                    bsonType: "string",
                    description: "Estado del juego"
                },
                COORD_GIS_X: {
                    bsonType: "double",
                    description: "Coordenadas en el eje X del juego"
                },
                COORD_GIS_Y: {
                    bsonType: "double",
                    description: "Coordenadas en el eje Y del juego"
                },
                LATITUD: {
                    bsonType: "string",
                    description: "Latitud del juego"
                },
                LONGITUD: {
                    bsonType: "string",
                    description: "Longitud del juego"
                },
                TIPO_VIA: {
                    bsonType: "string",
                    description: "Tipo del vía del juego"
                },
                NOM_VIA: {
                    bsonType: "string",
                    description: "Nombre de la vía del juego"
                },
                NUM_VIA: {
                    bsonType: "string",
                    description: "Número de la vía del juego"
                },
                COD_POSTAL: {
                    bsonType: "string",
                    description: "Código postal de la zona donde se encuentra el juego"
                },
                FECHA_INSTALACION: {
                    bsonType: "date",
                    description: "Fecha en la que se instaló el juego"
                },
                MODELO: {
                    bsonType: "string",
                    description: "Modelo de juego"
                },
                TIPO_JUEGO: {
                    bsonType: "string",
                    description: "Tipo de juego"
                },
                ACCESIBLE: {
                    bsonType: "bool",
                    description: "Indica si el juego es accesible"
                },
                NDP_AREA: {
                    bsonType: ["string", "int"],
                    description: "Area del juego"
                },
                INDICADOREXPOSICION: {
                    bsonType: "string",
                    enum: ["ALTO","MEDIO","BAJO"],
                    description: "Estado del juego"
                },
                DESGASTE_ACUMULADO: {  
                    bsonType: "int",
                    description: "Desgaste acumulado"
                }
            }
        }
    },
    validationLevel: "strict"
});

db.runCommand({collMod: "mantenimiento",
    validator: {
        $jsonSchema: {
            bsonType: "object",
            title: "Validation Maintenance",
            required: ["_id", "FECHA_INTERVENCION", "TIPO_INTERVENCION", "ESTADO_PREVIO", "ESTADO_POSTERIOR", "JUEGOID", "TIPO", "COMENTARIOS"],
            properties: {
                _id: {
                    bsonType: "string",
                    description: "ID del mantenimiento",
                },
                FECHA_INTERVENCION: {
                    bsonType: "date",
                    description: "Fecha en la que se realizaón la intervención",
                },
                TIPO_INTERVENCION: {
                    bsonType: "string",
                    enum: ["CORRECTIVO", "EMERGENCIA", "PREVENTIVO"],
                    description: "Tipo de intervención realizada"
                },
                ESTADO_PREVIO: {
                    bsonType: "string",
                    enum: ["MALO", "REGULAR", "BUENO"],
                    description: "Estado previo a la revisión"
                },
                ESTADO_POSTERIOR: {
                    bsonType: "string",
                    enum: ["MALO", "REGULAR", "BUENO"],
                    description: "Estado posterior a la revisión",
                },
                JUEGOID: {
                    bsonType: "int",
                    description: "Identificador del juego al que se le realizó el mantenimiento",
                },
                TIPO: {
                    bsonType: "string",
                    description: "Tipo de mantenimiento",
                },
                COMENTARIOS: {
                    bsonType: "string",
                    description: "Comentario realizado sobre el mantimiento",
                },
            }
        }
    }
});


db.runCommand({collMod: "encuestas_satisfaccion",
    validator: {
        $jsonSchema: {
            bsonType: "object",
            title: "encuestas_satisfaction_validation",
            required: ["_id", "PUNTUACION_ACCESIBILIDAD", "PUNTUACION_CALIDAD", "COMENTARIOS", "FECHA", "AREARECREATIVAID"],
            properties: {
                _id: {
                    bsonType: "string",
                    description: "ID de la encuesta"
                },
                PUNTUACION_ACCESIBILIDAD: {
                    bsonType: "int",
                    description: "Puntuación de la accesibilidad del area asociada a la encuesta"
                },
                PUNTUACION_CALIDAD: {
                    bsonType: "int",
                    description: "Puntuación de la calidad del area asociada a la encuesta"
                },
                COMENTARIOS: {
                    bsonType: "string",
                    description: "Comentarios adicionales de los usuarios"
                },
                FECHA: {
                    bsonType: "date",
                    description: "Fecha de realización de la encuesta"
                },
                AREARECREATIVAID: {
                    bsonType: "int",
                    description: "ID del área recreativa evaluada"
                }
            }
        }
    }
});

db.runCommand({
    collMod: "incidentes_seguridad", 
    validator: {
        $jsonSchema: {
            bsonType: "object",
            title: "Validator Security Incidences",
            required: [
                "_id",
                "FECHA_REPORTE",
                "TIPO_INCIDENTE",
                "GRAVEDAD",
                "AREARECREATIVAID",
            ],
            properties: {
                _id: {
                    bsonType: "string",
                    description: "ID del incidente registrado",
                },
                FECHA_REPORTE: {
                    bsonType: "date",
                    description:"Fecha en la que se realizó el reporte",
                },
                TIPO_INCIDENTE: {
                    bsonType: "string",
                    enum: ["ROBO","VANDALISMO","ACCIDENTE","CAIDA","DANO ESTRUCTURAL"],
                    description:"Tipo de incidente reportado",
                },
                GRAVEDAD: {
                    bsonType: "string",
                    enum: ["CRITICA", "ALTA", "MEDIA", "BAJA"],
                    description:"Nivel de gravedad del incidente",
                },
                AREARECREATIVAID: {
                    bsonType: "string",
                    description: "ID del área a la que corresponde el reporte del incidente",
                },
            },
        },
    },
});

db.runCommand({ collMod: "incidencias_usuarios", 
    validator: {
        $jsonSchema: {
            bsonType: "object",
            title: "Validator Users Incidences",
            required: [
                "_id",
                "TIPO_INCIDENCIA",
                "FECHA_REPORTE",
                "ESTADO",
                "USUARIOID",
                "MANTENIMIENTOID",
            ],
            properties: {
                _id: {
                    bsonType: "string",
                    description: "Número identificativo de la fila",
                },
                TIPO_INCIDENCIA: {
                    bsonType: "string",
                    enum: ["DESGASTE", "ROTURA", "VANDALISMO", "MAL FUNCIONAMIENTO"],
                    description: "Tipo de incidencia reportada",
                },
                FECHA_REPORTE: {
                    bsonType: "date",
                    description: "Fecha en la que se reportó la incidencia",
                },
                ESTADO: {
                    bsonType: "string",
                    enum: ["CERRADA", "ABIERTA"],
                    description: "Estado actual de la incidencia",
                },
                USUARIOID: {
                    bsonType: ["array"],
                    description: "Listado de usuarios",
                },
                MANTENIMIENTOID: {
                    bsonType: ["array"],
                    description: "ID de mantenimiento",
                }
            },
        },
    },
});

db.runCommand({collMod: "meteo24",
    validator: {
        $jsonSchema: {
            bsonType: "object",
            title: "Validator Meteo",
            required: ["FECHA", "TEMPERATURA", "PRECIPITACION", "VIENTO", "DISTRITO"],
            properties: {
                FECHA: {
                    bsonType: "date",
                    description: "Fecha en la que se recoge el clima"
                },
                TEMPERATURA: {
                    bsonType: ["number", "string"],
                    description: "Temperatura"
                },
                PRECIPITACION: {
                    bsonType: ["number", "string"],
                    description: "Cantidad de precipitación"
                },
                VIENTO: {
                    bsonType: 'bool',
                    description: "Indica si ha habido vientos fuertes"
                },
                DISTRITO: {
                    bsonType: "int",
                    description: "Area asociada"
                }
            }
        }
    }
});

db.runCommand({collMod: "usuarios",
    validator: {
        $jsonSchema: {
            bsonType: "object",
            title: "Validator Users",
            required: ["_id", "NOMBRE", "EMAIL", "TELEFONO"],
            properties: {
                _id: {
                    bsonType: "string",
                    description: "Número NIF del usuario",
                },
                NOMBRE: {
                    bsonType: "string",
                    description: "Nombre del usuario",
                },
                EMAIL: {
                    bsonType: "string",
                    description: "Email del usuario",
                },
                TELEFONO: {
                    bsonType: "string",
                    description: "Telefono del usuario",
                },
            },
        },
    },
});