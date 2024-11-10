use bbdd2;

db.areas.aggregate([
    {
        $addFields: {
            _id: {
                $convert: {
                    input: "$_id",
                    to: "string",
                    onError: null,
                    onNull: null
                }
            }
        }
    },
    {
        $addFields: {
            COD_POSTAL: {
                $convert: {
                    input: "$COD_POSTAL",
                    to: "string",
                    onError: null,
                    onNull: null
                }
            },
            COD_DISTRITO: {
                $convert: {
                    input: "$COD_DISTRITO",
                    to: "int",
                    onError: null,
                    onNull: null
                }
            }
        }
    },
    {
        $addFields: {
            LATITUD: {
                $convert: {
                    input: "$LATITUD",
                    to: "string",
                    onError: null,
                    onNull: null
                }
            },
            LONGITUD: {
                $convert: {
                    input: "$LONGITUD",
                    to: "string",
                    onError: null,
                    onNull: null
                }
            },
            NUM_VIA: {
                $convert: {
                    input: "$NUM_VIA",
                    to: "string",
                    onError: null,
                    onNull: null
                }
            }
        }
    },
    {
        $addFields: {
          // Paso 1: Eliminar los caracteres `[` y `]` para facilitar el procesamiento
          CANTIDAD_POR_TIPO_JUEGO: {
            $replaceAll: {
              input: "$CANTIDAD_POR_TIPO_JUEGO",
              find: "[",
              replacement: ""
            }
          }
        }
      },
      {
        $addFields: {
            CANTIDAD_POR_TIPO_JUEGO: {
            $replaceAll: {
              input: "$CANTIDAD_POR_TIPO_JUEGO",
              find: "]",
              replacement: ""
            }
          }
        }
      },
      {
        $addFields: {
          // Paso 2: Dividir el string por "), (" para obtener cada par tipo-cantidad
          CANTIDAD_POR_TIPO_JUEGO: { $split: ["$CANTIDAD_POR_TIPO_JUEGO", "), ("] }
        }
      },
      {
        $addFields: {
          // Paso 3: Limpiar y mapear cada par "tipo-cantidad" a un objeto eliminando caracteres extra
          CANTIDAD_POR_TIPO_JUEGO: {
            $map: {
              input: "$CANTIDAD_POR_TIPO_JUEGO",
              as: "tipoCantidad",
              in: {
                $let: {
                  vars: {
                    // Dividir cada par en tipo y cantidad
                    tipoYcantidad: { $split: ["$$tipoCantidad", "', '"] }
                  },
                  in: {
                    k: { 
                      // Eliminar caracteres innecesarios de la clave (tipo de juego)
                      $trim: { input: { $arrayElemAt: ["$$tipoYcantidad", 0] }, chars: "('" }
                    },
                    v: { 
                      // Convertir el valor (cantidad) a entero después de eliminar caracteres extra
                      $toInt: { 
                        $trim: { input: { $arrayElemAt: ["$$tipoYcantidad", 1] }, chars: "') " }
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
        $addFields: {
          // Paso 4: Convertir la lista de pares clave-valor en un objeto
          CANTIDAD_POR_TIPO_JUEGO: { $arrayToObject: "$CANTIDAD_POR_TIPO_JUEGO" }
        }
      },
    {
        $out: {
            db: "bbdd2",
            coll: "areas"
        }
    }
]);

db.juegos.aggregate([
    {
        $addFields: {
            _id: {
                $convert: {
                    input: "$_id",
                    to: "string",
                    onError: null,
                    onNull: null
                }
            }
        }
    },
    {
        $addFields: {
            COD_DISTRITO: {
                $convert: {
                    input: "$COD_DISTRITO",
                    to: "int",
                    onError: null,
                    onNull: null
                }
            },
            COD_POSTAL: {
                $convert: {
                    input: "$COD_POSTAL",
                    to: "string",
                    onError: null,
                    onNull: null
                }
            },
            CONTRATO_COD: {
                $convert: {
                    input: "$CONTRATO_COD",
                    to: "string",
                    onError: null,
                    onNull: null
                }
            },
            LATITUD: {
                $convert: {
                    input: "$LATITUD",
                    to: "string",
                    onError: null,
                    onNull: null
                }
            },
            LONGITUD: {
                $convert: {
                    input: "$LONGITUD",
                    to: "string",
                    onError: null,
                    onNull: null
                }
            },
            MODELO: {
                $convert: {
                    input: "$MODELO",
                    to: "string",
                    onError: null,
                    onNull: null
                }
            },
            ACCESIBLE: {
                $convert: {
                    input: "$ACCESIBLE",
                    to: "bool",
                    onError: null,
                    onNull: null
                }
            },
            NUM_VIA: {
                $convert: {
                    input: "$NUM_VIA",
                    to: "string",
                    onError: null,
                    onNull: null
                }
            },
            NDP: {
                $convert: {
                    input: "$NDP",
                    to: "string",
                    onError: null,
                    onNull: null
                }
            },
            DIRECCION_AUX: {
                $convert: {
                    input: "$DIRECCION_AUX",
                    to: "string",
                    onError: null,
                    onNull: null
                }
            },
            NDP_AREA: {
                $convert: {
                    input: "$NDP_AREA",
                    to: "string",
                    onError: null,
                    onNull: null
                }
            }
        }
    },
    {
        $out: {
            db: "bbdd2", coll: "juegos"
        }
    }
]);

db.encuestas_satisfaccion.aggregate([
    {
        $addFields: {
            AREARECREATIVAID: {
                $convert: {
                    input: "$AREARECREATIVAID",
                    to: "string",
                    onError: null,
                    onNull: null
                }
            }
        } 
    },
    {$out: {
        db: "bbdd2", coll:"encuestas_satisfaccion"
    }}
]);

db.incidentes_seguridad.aggregate([
    {
        $addFields: {
            AREARECREATIVAID: {
                $convert: {
                    input: "$AREARECREATIVAID",
                    to: "string",
                    onError: null,
                    onNull: null
                }
            }
        } 
    },
    {$out: {
        db: "bbdd2", coll:"incidentes_seguridad"
    }}
]);

db.usuarios.aggregate([
    {
        $out: {
            db: "bbdd2",
            coll: "usuarios"
        }
    }
])

db.meteo24.aggregate([
    {
        $addFields: {
            VIENTO: {
                $convert: {
                    input: "$VIENTO",
                    to: "bool",
                    onError: null,
                    onNull: null
                }
            }

        }
    },
    {
        $out: {db: "bbdd2",coll: "meteo24"}
    }
]);

db.estaciones_meteo_codigo_postal.aggregate([

    {
        $out: {db: "bbdd2",coll: "estaciones_meteo_codigo_postal"}
    }
]);

db.mantenimiento.aggregate([
    {
        $addFields: {
            JUEGOID: {
                $convert: {
                    input: "$JUEGOID",
                    to: "string",
                    onError: null,
                    onNull: null
                }
            }
        } 
    },
    {
        $out: {
            db: "bbdd2",
            coll: "mantenimiento"
        }
    }
]);

db.incidentes_seguridad.aggregate([
    {
        $addFields: {
            AREARECREATIVAID: {
                $convert: {
                    input: "$AREARECREATIVAID",
                    to: "string",
                    onError: null,
                    onNull: null
                }
            }
        } 
    },
    {
        $out: {
        db: "bbdd2", coll:"incidentes_seguridad"
    }}
]);

db.incidencias_usuarios.aggregate([
    {
        $addFields: {
            MANTENIMIENTOID: {
                $split: [
                    {
                        $replaceAll: {
                            input: {
                                $replaceAll: {
                                    input: {
                                        $replaceAll: {
                                            input:
                                            {
                                                $replaceAll: {
                                                    input: "$MANTENIMIENTOID",
                                                    find: " ",
                                                    replacement: ""
                                                }
                                            },
                                            find: "'",
                                            replacement: ""
                                        }
                                    },
                                    find: "]",
                                    replacement: ""
                                }
                            },
                            find: "[",
                            replacement: ""
                        }
                    }, ","]
            },
            USUARIOID: {
                $split: [
                    {
                        $replaceAll: {
                            input: {
                                $replaceAll: {
                                    input: {
                                        $replaceAll: {
                                            input:
                                            {
                                                $replaceAll: {
                                                    input: "$USUARIOID",
                                                    find: " ",
                                                    replacement: ""
                                                }
                                            },
                                            find: "'",
                                            replacement: ""
                                        }
                                    },
                                    find: "]",
                                    replacement: ""
                                }
                            },
                            find: "[",
                            replacement: ""
                        }
                    }, ","]
            }
        }
    },
    {
        $project: {
            _id: 1,
            TIPO_INCIDENCIA: 1,
            FECHA_REPORTE: 1,
            ESTADO: 1,
            USUARIOID: 1,
            MANTENIMIENTOID: 1
        }
    },
    {
        $out: { db: "bbdd2", coll: "incidencias_usuarios" }
    }
]);
