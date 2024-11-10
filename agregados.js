// --------- AGREGADO 1---------

db.areas.aggregate([
    // Paso 1: Lookup para agregar juegos 
    {
        $lookup: {
            from: 'juegos',
            localField: '_id',
            foreignField: 'NDP_AREA',
            as: 'ref_juegos'
        }
    },
    // Paso 2: Lookup para agregar incidentes de seguridad
    {
        $lookup: {
            from: 'incidentes_seguridad',
            localField: '_id',
            foreignField: 'AREARECREATIVAID',
            as: 'ref_incidentes_seguridad'
        }
    },
    // Paso 3: Lookup para encuestas de satisfacción
    {
        $lookup: {
            from: 'encuestas_satisfaccion',
            localField: '_id',
            foreignField: 'AREARECREATIVAID',
            as: 'ref_encuestas_satisfaccion'
        }
    },
    // Paso 4: Lookup para estaciones meteorológicas
    {
        $lookup: {
            from: 'estaciones_meteo_codigo_postal',
            localField: 'COD_POSTAL',
            foreignField: 'Codigo Postal',
            as: 'ref_estaciones_meteo_codigo_postal'
        }
    },
    // Paso 5: Lookup para datos meteorológicos asociados
    {
        $lookup: {
            from: 'meteo24',
            localField: 'ref_estaciones_meteo_codigo_postal.CÓDIGO',
            foreignField: 'DISTRITO',
            as: 'ref_estaciones_meteo_codigo_postal.ref_meteo'
        }
    },
    // Paso 6: Calcular métricas de encuestas y mantenimiento
    {
        $addFields: {
            encuestas_accesibilidad: "$PUNTUACION_CALIDAD",
            encuestas_calidad: "$PUNTUACION_ACCESIBILIDAD"
        }
    },
    {
        $addFields: {
            nota_encuestas_area: {
                $sum: { $concatArrays: ["$encuestas_accesibilidad", "$encuestas_calidad"] }
            },
            numero_incidencias_ponderado: { $multiply: [{ $size: "$ref_incidentes_seguridad" }, 4] },
            juegos_mantenimiento: { 
                $size: { 
                    $filter: { 
                        input: { $ifNull: ["$ref_juegos", []] },  // Verificamos si ref_juegos es un array
                        as: "juego", 
                        cond: { $eq: ["$$juego.ESTADO", "EN REPARACION"] } 
                    } 
                } 
            }
        }
    },
    {
        $addFields: {
            nota_total_area: { $sum: ["$nota_encuestas_area", "$numero_incidencias_ponderado", "$juegos_mantenimiento"] }
        }
    },
    // Paso 7: Agrupar para calcular la nota máxima
    {
        $group: {
            _id: null,
            max_nota_global: { $max: "$nota_total_area" },
            areas: { $push: "$$ROOT" }
        }
    },
    // Paso 8: Desagregar para aplicar la nota máxima
    {
        $unwind: "$areas"
    },
    {
        $replaceRoot: {
            newRoot: {
                $mergeObjects: ["$areas", { max_nota: "$max_nota_global" }]
            }
        }
    },
    // Paso 9: Calcular estado global del área
    {
        $addFields: {
            ESTADO_GLOBAL_AREA: {
                $round: [
                    {
                        $multiply: [
                            {
                                $divide: [
                                    { $ifNull: ["$nota_total_area", 0] },
                                    { $cond: { if: { $eq: ["$max_nota", 0] }, then: 1, else: "$max_nota" } }
                                ]
                            },
                            10
                        ]
                    },
                    2
                ]
            }
        }
    },
    {
        $addFields: {
            ESTADO_GLOBAL_AREA: { $subtract: [10, "$ESTADO_GLOBAL_AREA"] }
        }
    },
    // Paso 10: Proyecto final para incluir todos los datos relevantes
    {
        $project: {
            _id: 1,
            SISTEMA_COORD: 1,
            LATITUD: 1,
            LONGITUD: 1,
            BARRIO: 1,
            DISTRITO: 1,
            FECHA_INSTALACION: 1,
            ESTADO: 1,
            TOTAL_ELEM: 1,
            CAPACIDAD_MAX: 1,
            CANTIDAD_POR_TIPO_JUEGO: 1,
            ESTADO_GLOBAL_AREA: 1,
            ref_juegos: 1,
            ref_incidentes_seguridad: { _id: 1, GRAVEDAD: 1, FECHA_REPORTE: 1 },
            ref_encuestas_satisfaccion: { _id: 1 },
            ref_estaciones_meteo_codigo_postal: { _id: 1, ref_meteo: 1 }
        }
    },
    // Paso 11: Salida a la colección final
    {
        $out: { db: "bbdd2", coll: "agregado_area_recreativa_clima" }
    }
]);



// --------- AGREGADO 2 ---------

// Agregado de juego
db.juegos.aggregate([
    {
        $lookup: {
            from: 'mantenimiento',
            localField: '_id',
            foreignField: 'JUEGOID',
            as: 'ref_mantenimiento'
        }
    },
    {
        $lookup: {
            from: "incidencias_usuarios",
            localField: "ref_mantenimiento._id",
            foreignField: "MANTENIMIENTOID",
            as: "res_incidencias_usuarios"
        }
    },
    {
        $out: { db: "bbdd2", coll: "agregado_juego" }
    }
]);

db.agregado_juego.aggregate([
    {
        $addFields: {
            // Obtener la fecha más reciente de intervención
            "ULTIMAFECHAMANTENIMIENTO": {
                $max: "$ref_mantenimiento.FECHA_INTERVENCION"
            },
            // Reestructurar res_incidencias_usuarios
            "res_incidencias_usuarios": {
                $map: {
                    input: "$res_incidencias_usuarios",
                    as: "ref",
                    in: {
                        _id: "$$ref._id",
                        TIPO_INCIDENCIA: "$$ref.TIPO_INCIDENCIA",
                        FECHA_REPORTE: "$$ref.FECHA_REPORTE",
                        ESTADO: "$$ref.ESTADO",
                        tiempoResolucion: {
                            $max: {
                                $map: {
                                    input: "$$ref.MANTENIMIENTOID",
                                    as: "mantenimiento_id",
                                    in: {
                                        $subtract: [
                                            {
                                                $arrayElemAt: [
                                                    {
                                                        $map: {
                                                            input: {
                                                                $filter: {
                                                                    input: "$ref_mantenimiento",
                                                                    as: "mantenimiento",
                                                                    cond: {
                                                                        $eq: [
                                                                            "$$mantenimiento._id",
                                                                            "$$mantenimiento_id"
                                                                        ]
                                                                    }
                                                                }
                                                            },
                                                            as: "man",
                                                            in: "$$man.FECHA_INTERVENCION"
                                                        }
                                                    },
                                                    0
                                                ]
                                            },
                                            "$$ref.FECHA_REPORTE"
                                        ]
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    },
    {
        // Extraer solo los IDs de ref_mantenimiento
        $addFields: {
            "ref_mantenimiento": {
                $map: {
                    input: "$ref_mantenimiento",
                    in: "$$this._id"
                }
            }
        }
    },
    {
        $out: {
            db: "bbdd2",
            coll: "agregado_juego"
        }
    }
]);


// --------- AGREGADO 3 ---------

db.incidencias_usuarios.aggregate([
    {
        $lookup: {
            from: 'usuarios',
            localField: 'USUARIOID',
            foreignField: '_id',
            as: 'emb_usuarios'
        }
    },
    {
        $addFields: {
            NIVELESCALAMIENTO: {
                $add: [
                    { $floor: { $multiply: [{ $rand: {} }, 10] } },
                    1
                ]
            }
        }
    },
    {
        $project: {
            USUARIOID: 0,
            MANTENIMIENTOID: 0
        }
    },
    {
        $out: { db: "bbdd2", coll: "agregado_incidencia" }
    }
]);
