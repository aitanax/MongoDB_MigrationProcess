import pandas as pd
import numpy as np
from unidecode import unidecode
import re
from datetime import datetime, timedelta
import warnings
import sys
import os

def delete_duplicates(df, id_column):
    return df.drop_duplicates(subset=id_column, keep='first')

def extract_data(file_path):
    return pd.read_csv(file_path)

def standardize_text(df, columns):
    for col in columns:
        df[col] = df[col].astype(str).str.strip().str.upper().apply(unidecode)

def format_date(date):
    if isinstance(date, str):
        for fmt in [
            '%Y-%m-%d', '%d-%m-%Y', '%Y-%m-%d %H:%M:%S', '%m-%d-%Y', '%m/%d/%Y', '%y-%m-%d','%Y/%m/%d', '%d/%m/%Y', '%d/%m/%y', '%m/%d/%y'
        ]:
            try:
                return pd.to_datetime(date, format=fmt).strftime('%Y-%m-%dT%H:%M:%SZ')
            except ValueError:
                continue
    return date
def format_date2(date):
    if isinstance(date, pd.Timestamp):
        return date.strftime('%Y-%m-%dT%H:%M:%SZ')
    return date

def update_codigo_interno(row):
    tipo, codigo_interno, clasificacion = row['TIPO'], str(row['CODIGO_INTERNO']).strip(), row['DESC_CLASIFICACION']
    codigo_numero = codigo_interno.split('_', 1)[-1] if '_' in codigo_interno else codigo_interno
    if clasificacion == "AREA DE JUEGOS/ESPECIAL":
        return f"A{tipo[0]}{codigo_numero}"
    return f"{tipo[0]}{codigo_numero}" if not codigo_interno.startswith(tipo[0]) else codigo_numero

def completar_cod_postal(df):
    for index, row in df[df['COD_POSTAL'].isna()].iterrows():
        match = df[
            (df['COD_BARRIO'] == row['COD_BARRIO']) &
            (df['BARRIO'] == row['BARRIO']) &
            (df['COD_DISTRITO'] == row['COD_DISTRITO']) &
            (df['DISTRITO'] == row['DISTRITO']) &
            df['COD_POSTAL'].notna()
        ]
        if not match.empty:
            cod_postal = match.iloc[0]['COD_POSTAL']
            df.at[index, 'COD_POSTAL'] = cod_postal
    
    return df

def completar_distrito(df):
    for index, row in df[df['DISTRITO'].str.lower() == 'nan'].iterrows():
        match = df[
            (df['COD_DISTRITO'] == row['COD_DISTRITO']) &
            (df['DISTRITO'].str.lower() != 'nan')
        ]
        if not match.empty:
            distrito = match.iloc[0]['DISTRITO']
            df.at[index, 'DISTRITO'] = distrito
    return df

def completar_cod_distrito(df):
    nan_rows = df[df['COD_DISTRITO'].isna()]
    if not nan_rows.empty:
        print(nan_rows)
    else:
        print("No se encontraron filas con COD_DISTRITO como NaN.")
    for index, row in df[df['COD_DISTRITO'].isna()].iterrows():
        match = df[
            (df['DISTRITO'] == row['DISTRITO']) &  # Coincidir DISTRITO
            (df['COD_DISTRITO'].notna())  # Asegurarse de que COD_DISTRITO no sea NaN
        ]
        if not match.empty:
            cod_distrito = match.iloc[0]['COD_DISTRITO']
            df.at[index, 'COD_DISTRITO'] = cod_distrito
        else:
            print(f'No se encontró coincidencia para fila {index}.')
    return df

def clean_address_column(df, column='DIRECCION_AUX'):
    abreviaturas = {
        r'\bAVND\b': 'AVENIDA', r'\bAVDA\b': 'AVENIDA', r'\bPARRQUE\b': 'PARQUE', r'\bAV(?:\.)?\b': 'AVENIDA',
        r'\bC(?:\.)?\b': 'CALLE', r'\bPLZ\b': 'PLAZA', r'\bPJE\b': 'PASAJE'
    }
    for abreviatura, completo in abreviaturas.items():
        df[column] = df[column].str.replace(abreviatura, completo, regex=True)
    
    df[column] = (
        df[column]
        .astype(str)
        .str.strip()  # Eliminar espacios en blanco al principio y al final
        .str.replace(r'\b(?:C\/|CALLE\/|C\.|Pza|PZ|PZ\.|CV|C.|CV\.|AVDA|Av|AV)\b', '', regex=True)
        .str.replace(r'^\w+\s·\s', '', regex=True)
        .str.replace(r'^\s*\·\s*', '', regex=True)
        .str.replace(r'^\w+\s.\s', '', regex=True)
        .str.replace(r'\s*\.\s*$', '', regex=True)
        .str.replace(r'\s*\.\s*', ' ', regex=True)
    )
    return df

def fill_columns(df_target, df_source, columns_to_fill):
    for ndp in df_target['NDP'].unique():
        filtered_source_df = df_source[df_source['NDP'] == ndp][columns_to_fill].dropna()
        if not filtered_source_df.empty:
            fill_values = filtered_source_df.iloc[0]
            for col in columns_to_fill:
                df_target.loc[df_target['NDP'] == ndp, col] = df_target.loc[df_target['NDP'] == ndp, col].replace('', fill_values[col])
                df_target.loc[df_target['NDP'] == ndp, col] = df_target.loc[df_target['NDP'] == ndp, col].fillna(fill_values[col])
        else:
            print(f'No hay valores disponibles para NDP: {ndp} en el DataFrame fuente.')

def fill_missing_tipo_fecha(row, column, id_row):
    if pd.isnull(row[column]) or (column == "FECHA_INSTALACION" and row[column] == "fecha_incorrecta"):
        start_date = datetime(2000, 1, 1)
        end_date = datetime(2023, 12, 31)
        random_days = np.random.randint(0, (end_date - start_date).days + 1)
        random_date = start_date + timedelta(days=random_days)
        return random_date.strftime('%Y-%m-%d %H:%M:%S')
    return row[column]

def fill_missing_fecha(df):
    df['FECHA_INSTALACION'] = df.apply(lambda row: fill_missing_tipo_fecha(row, 'FECHA_INSTALACION', 'ID'), axis=1)
    return df

def rename_id_column(df):
    df = df.rename(columns={'ID': '_id'})
    return df

def completar_direccion_aux(df):
    for index, row in df.iterrows():
        if not pd.notna(row['DIRECCION_AUX']) or row['DIRECCION_AUX'].strip().lower() == 'nan':
            tipo_via = row['TIPO_VIA'] if pd.notna(row['TIPO_VIA']) else ''
            nom_via = row['NOM_VIA'] if pd.notna(row['NOM_VIA']) else ''
            num_via = row['NUM_VIA'] if pd.notna(row['NUM_VIA']) else ''
            direccion_aux = f"{tipo_via} {nom_via} {num_via}".strip()
            df.at[index, 'DIRECCION_AUX'] = direccion_aux if direccion_aux else ''
    return df

def rellenar_con_direccion_aux(df):
    posibles_tipos_via = ["PARQUE", "PLAZA", "AVENIDA", "CALLE", "PASEO", "CAMINO", 
                          "CARRERA", "RONDA", "BULEVAR", "CARRETERA", "TRAVESÍA", "VIA", "PASAJE"]
    for index, row in df.iterrows():
        direccion_aux = row['DIRECCION_AUX']
        if pd.notna(direccion_aux):
            tipo_via = row['TIPO_VIA'] if pd.notna(row['TIPO_VIA']) and row['TIPO_VIA'] != '' else None
            nom_via = row['NOM_VIA'] if pd.notna(row['NOM_VIA']) and row['NOM_VIA'] != '' else None
            num_via = row['NUM_VIA'] if pd.notna(row['NUM_VIA']) and row['NUM_VIA'] != '' else None
            tipo_via = next((via for via in posibles_tipos_via if via in direccion_aux.upper()), None)
            direccion_tokens = direccion_aux.split()
            nom_via = ""
            num_via = None
            for i, token in enumerate(direccion_tokens):
                if re.match(r'^\d+$', token):  # Número de vía encontrado
                    num_via = token
                    nom_via = " ".join(direccion_tokens[:i])  # Resto de tokens como nombre de vía
                    break
                elif 'Nº' in token:  # Buscar patrón "Nº" seguido de número
                    num_match = re.search(r'Nº\s*(\d+)', ' '.join(direccion_tokens[i:]), re.IGNORECASE)
                    if num_match:
                        num_via = num_match.group(1)
                        nom_via = " ".join(direccion_tokens[:i])  # Resto de tokens como nombre de vía
                    break
            else:
                nom_via = " ".join(direccion_tokens)
            nom_via = re.sub(r'[^\w\s]', '', nom_via).strip()  # Solo letras y espacios
            num_via = re.sub(r'[^\d]', '', num_via) if num_via else None  # Solo números
            if row['TIPO_VIA'] == '' or pd.isna(row['TIPO_VIA']):
                df.at[index, 'TIPO_VIA'] = tipo_via

            if row['NOM_VIA'] == '' or pd.isna(row['NOM_VIA']):
                df.at[index, 'NOM_VIA'] = nom_via

            if row['NUM_VIA'] == '' or pd.isna(row['NUM_VIA']):
                df.at[index, 'NUM_VIA'] = num_via     
    return df

def transform_areas_data(df, juegos_df):
    df['TIPO'] = df.pop('tipo')
    standardize_text(df, ['BARRIO', 'DISTRITO', 'TIPO', 'TIPO_VIA', 'NOM_VIA', 'DESC_CLASIFICACION'])
    df = clean_address_column(df)
    df[['TIPO_VIA', 'NOM_VIA']] = df[['TIPO_VIA', 'NOM_VIA']].replace(['NAN', 'nan', '0', ''], '')
    df = fill_missing_fecha(df)
    df['FECHA_INSTALACION'] = df['FECHA_INSTALACION'].apply(format_date)
    df['CODIGO_INTERNO'] = df.apply(update_codigo_interno, axis=1)
    columns_to_fill = ['TIPO_VIA', 'NUM_VIA', 'NOM_VIA', 'COD_POSTAL']
    fill_columns(juegos_df, df, columns_to_fill)  # Llenar valores desde df_juegos
    fill_columns(df, juegos_df, columns_to_fill)   # Llenar valores desde df_areas
    df = rellenar_con_direccion_aux(df)
    df = completar_direccion_aux(df)
    df = completar_distrito(df)
    df = completar_cod_distrito(df) 
    df = completar_cod_postal(df)
    return df

def clean_areas_data(csv_input, csv_output):
    # Generar las rutas completas para los archivos de entrada
    areas_file_path = os.path.join(csv_input, "AreasSucio.csv")
    juegos_file_path = os.path.join(csv_input, "JuegosSucio.csv")
    
    # Extraer los datos de los archivos CSV
    df = extract_data(areas_file_path)
    juegos_df = extract_data(juegos_file_path)
    
    # Procesar los datos y ordenarlos
    df_cleaned = transform_areas_data(df, juegos_df).sort_values(by='ID')
    
    # Generar la ruta para el archivo de salida limpio
    cleaned_file_path = os.path.join(csv_output, "AreasLimpio.csv")
    
    # Guardar el archivo limpio
    df_cleaned.to_csv(cleaned_file_path, index=False)
    print(f"Archivo procesado y guardado en: {cleaned_file_path}")

# Función para limpiar los datos de mantenimiento
def clean_mantenimiento_data(csv_input, csv_output):
    # Generar la ruta completa para el archivo de entrada
    mantenimiento_file_path = os.path.join(csv_input, "MantenimientoSucio.csv")
    
    # Extraer los datos del archivo CSV
    df = extract_data(mantenimiento_file_path)
    
    # Procesar los datos
    df.columns = [col.upper() for col in df.columns]
    df['FECHA_INTERVENCION'] = df['FECHA_INTERVENCION'].apply(format_date)
    standardize_text(df, ['TIPO_INTERVENCION', 'ESTADO_PREVIO', 'ESTADO_POSTERIOR', 'TIPO', 'COMENTARIOS'])
    df['ID'] = df['ID'].str.extract('(\d+)')  # Extraer el número del ID original
    df['ID'] = df['ID'].astype(int).apply(lambda x: f'MNT-{str(x).zfill(5)}') 
    
    # Generar la ruta de salida para el archivo limpio
    cleaned_file_path = os.path.join(csv_output, "MantenimientoLimpio.csv")
    
    # Renombrar la columna ID y guardar el archivo procesado
    df = rename_id_column(df)
    df.to_csv(cleaned_file_path, index=False)
    
    print(f"Archivo de mantenimiento procesado y guardado en: {cleaned_file_path}")


def fill_missing_tipo(row, column, string_missing, id_row):
    value = row[column]
    if isinstance(value, str):
        value = value.strip()
    if pd.isnull(value) or value in ['nan', '0', '']:
        return f'{string_missing}_{row[id_row]}'
    return value

def fill_missing(df, optionals:list):
    for c in df.columns.tolist():
        if c not in optionals:
            df[c] = df.apply(lambda row: fill_missing_tipo(row, c, f'{c}_DESCONOCIDO', "ID"), axis=1)
    return df

def fusionar_dataframes(df1, df2, columnas_clave, columna_nueva):
    df1[columna_nueva] = None
    for i, fila_df2 in df2.iterrows():
        coincidencia = None
        for columna in columnas_clave:
            if coincidencia is None:
                coincidencia = (df1[columna] == fila_df2[columna])
            else:
                coincidencia |= (df1[columna] == fila_df2[columna])
        df1.loc[coincidencia, columna_nueva] = fila_df2["ID"]
        for columna in df1.columns:
            if columna in df2.columns:
                if pd.notna(fila_df2[columna]):
                    with warnings.catch_warnings(record=True) as _:
                        warnings.simplefilter("ignore")
                        if pd.isna(df1.loc[coincidencia, columna]).all():
                            df1.loc[df1[columna_nueva] == fila_df2["ID"], columna] = fila_df2[columna]
                else:
                    for j, fila_df1 in df1.iterrows():
                        if pd.notna(fila_df1[columna]) and pd.isna(df2.at[i, columna]):
                            df2.at[i, columna] = fila_df1[columna]
                            break

def transform_juegos_data(df, df_mantenimiento, df_areas):
    df['TIPO_JUEGO'] = df.pop('tipo_juego')
    standardize_text(df, ['BARRIO', 'DISTRITO', 'TIPO_JUEGO','DESC_CLASIFICACION'])
    df = clean_address_column(df)
    mantenimiento_count = df_mantenimiento['_id'].value_counts().to_dict()
    df['NUMERO_DE_MANTENIMIENTOS'] = df['ID'].map(mantenimiento_count).fillna(0).astype(int)
    df.columns = [col.upper() for col in df.columns]
    df = fill_missing_fecha(df)
    df['FECHA_INSTALACION'] = df['FECHA_INSTALACION'].apply(format_date)
    df['DIRECCION_AUX'] = df['DIRECCION_AUX'].astype(str).str.strip().str.replace('"', '')
    df['DIRECCION_AUX'] = df['DIRECCION_AUX'].str.replace(r'^\w+\s·\s', '', regex=True)
    df['MODELO'] = df.apply(lambda row: f"{row['ID']}-MODELO-AUSENTE" if pd.isna(row['MODELO']) else row['MODELO'], axis=1)
    df['ACCESIBLE'] = df.apply(lambda row: f"{row['ID']}-ACCESIBLE-AUSENTE" if pd.isna(row['ACCESIBLE']) else row['ACCESIBLE'], axis=1)
    df['INDICADOREXPOSICION'] = np.random.choice(['BAJO', 'MEDIO', 'ALTO'], size=len(df))
    missing_values_ndp = df['NDP'].isnull().sum()
    df['TIEMPO_DE_USO'] = np.random.randint(1, 16, size=len(df))
    mantenimiento_count = df_mantenimiento['_id'].value_counts().to_dict()
    df['NUMERO_DE_MANTENIMIENTOS'] = df['ID'].map(mantenimiento_count).fillna(0).astype(int)
    exposicion_values = {'BAJO': 1, 'MEDIO': 2, 'ALTO': 3}
    df['INDICADOREXPOSICION_VAL'] = df['INDICADOREXPOSICION'].map(exposicion_values)
    df['DESGASTE_ACUMULADO'] = (df['TIEMPO_DE_USO'] * df['INDICADOREXPOSICION_VAL']) - (df['NUMERO_DE_MANTENIMIENTOS'] * 100)
    df.drop(columns=['INDICADOREXPOSICION_VAL'], inplace=True)
    df.drop(columns=['TIEMPO_DE_USO'], inplace=True)
    df.drop(columns=['NUMERO_DE_MANTENIMIENTOS'], inplace=True)
    df['TIPO_JUEGO'].replace(['NAN', 'nan', '0', ''], np.nan, inplace=True)
    df['TIPO_JUEGO'] = df['TIPO_JUEGO'].replace("INFANTILES", "INFANTIL")
    columns_to_fill = ['TIPO_VIA', 'NUM_VIA', 'NOM_VIA', 'COD_POSTAL']
    fill_columns(df_areas, df, columns_to_fill)
    fill_columns(df, df_areas, columns_to_fill)
    ndp_cambiados, df = assignar_ndp_existente_y_dir(df, df_areas)
    print(f"\nTotal de juegos a los que se les ha cambiado el NDP: {ndp_cambiados}")
    juegos_sin_ndp_en_areas = df[df['NDP'].isna() | ~df['NDP'].isin(df_areas['NDP'])]
    print(f"\nTotal de juegos sin NDP en áreas: {len(juegos_sin_ndp_en_areas)}")
    print(juegos_sin_ndp_en_areas[['ID', 'NDP', 'BARRIO', 'TIPO_JUEGO']].head(10))
    fusionar_dataframes(df, df_areas, ["CODIGO_INTERNO", "NDP"], "NDP_AREA") 
    df = rellenar_con_direccion_aux(df)
    df = completar_direccion_aux(df)
    df = completar_distrito(df)
    df = completar_cod_distrito(df) 
    df = completar_cod_postal(df)
    df_areas = fill_missing(df_areas,[])
    df['NOM_VIA'] = df['NOM_VIA'].replace(['NAN', 'nan', '0', ''], '')
    df['DIRECCION_AUX'] = df['DIRECCION_AUX'].replace(['NAN', 'nan', '0', ''], '')
    print(f"Tipo de dato de NOM_VIA después de fillna: {df['NOM_VIA'].dtype}")
    print(f"Tipo de dato de DIRECCION_AUX después de fillna: {df['DIRECCION_AUX'].dtype}")

    def count_game_types(area_id):
        juegos_area = df[df['NDP_AREA'] == area_id]
        tipo_juego_counts = juegos_area['TIPO_JUEGO'].value_counts().reset_index()
        tipo_juego_counts.columns = ['TIPO_JUEGO', 'COUNT']
        result = [(str(tipo), str(count)) for tipo, count in zip(tipo_juego_counts['TIPO_JUEGO'], tipo_juego_counts['COUNT'])]
        return str(result)
    
    capacidad_counts = df['NDP'].value_counts().reset_index()
    capacidad_counts.columns = ['NDP', 'CAPACIDAD_MAX']
    df_areas = df_areas.merge(capacidad_counts, on='NDP', how='left')
    df_areas['CAPACIDAD_MAX'] = df_areas['CAPACIDAD_MAX'].fillna(0).astype(int)
    df_areas['CANTIDAD_POR_TIPO_JUEGO'] = df_areas['ID'].apply(count_game_types)
    df = fill_missing(df,[])
    return df, df_areas

def assignar_ndp_existente_y_dir(df, df_areas):
    df_areas['BARRIO_NORM'] = df_areas['BARRIO'].apply(lambda x: unidecode(x).upper())
    df_areas['TIPO_NORM'] = df_areas['TIPO'].apply(lambda x: unidecode(x).upper())
    juegos_sin_ndp = df[df['NDP'].isna() | ~df['NDP'].isin(df_areas['NDP'])]
    print(f"Total juegos sin NDP inicial: {len(juegos_sin_ndp)}")
    ndp_cambiados = 0
    for idx, juego in juegos_sin_ndp.iterrows():
        tipo_juego = unidecode(juego['TIPO_JUEGO']).upper()
        barrio_juego = unidecode(juego['BARRIO']).upper()
        area_coincidente = df_areas[(df_areas['BARRIO_NORM'] == barrio_juego) & (df_areas['TIPO_NORM'] == tipo_juego)]
        if not area_coincidente.empty:
            nuevo_ndp = area_coincidente.iloc[0]['NDP']
            df.at[idx, 'NDP'] = nuevo_ndp
            ndp_cambiados += 1
            print(f"Asignado NDP {nuevo_ndp} al juego ID {juego['ID']}")
            for col in ['TIPO_VIA', 'NOM_VIA', 'NUM_VIA']:
                if pd.isna(juego[col]) or juego[col] == '':
                    nuevo_valor = area_coincidente.iloc[0][col]
                    if not pd.isna(nuevo_valor) and nuevo_valor != '':
                        df.at[idx, col] = nuevo_valor
                        print(f"Asignado {col} '{nuevo_valor}' al juego ID {juego['ID']}")
                    else:
                        print(f"Sin valor de {col} disponible en área para juego ID {juego['ID']}")
        else:
            print(f"No se encontró un área compatible para el juego ID {juego['ID']} con tipo '{tipo_juego}' y barrio '{barrio_juego}'")
    return ndp_cambiados, df

def clean_juegos_data(csv_input, csv_output):
    # Generar las rutas completas para los archivos de entrada
    juegos_file_path = os.path.join(csv_input, "JuegosSucio.csv")
    mantenimiento_file_path = os.path.join(csv_output, "MantenimientoLimpio.csv")
    areas_file_path = os.path.join(csv_output, "AreasLimpio.csv")
    
    # Extraer los datos de los archivos CSV
    df = extract_data(juegos_file_path)
    df_mantenimiento = extract_data(mantenimiento_file_path)
    df_areas = extract_data(areas_file_path)
    
    # Procesar los datos y transformarlos
    df_cleaned, df_areas = transform_juegos_data(df, df_mantenimiento, df_areas)
    
    # Ordenar por ID y limpiar los datos
    df_cleaned = df_cleaned.sort_values(by='ID')
    df_cleaned = rename_id_column(df_cleaned)
    df_cleaned = delete_duplicates(df_cleaned, "_id")
    
    # Generar las rutas de salida para los archivos limpios
    cleaned_file_path = os.path.join(csv_output, "JuegosLimpio.csv")
    cleaned_file_path_areas = os.path.join(csv_output, "AreasLimpio.csv")
    
    # Guardar los archivos procesados
    df_cleaned.to_csv(cleaned_file_path, index=False)
    df_areas.drop(columns=['BARRIO_NORM', 'TIPO_NORM'], inplace=True)
    df_areas.to_csv(cleaned_file_path_areas, index=False)
    
    print(f"Archivo de juegos procesado y guardado en: {cleaned_file_path}")
    print(f"Archivo de áreas procesado y guardado en: {cleaned_file_path_areas}")

def standardize_text2(column):
    return column.astype(str).str.upper().apply(unidecode)

def handle_duplicates(df):
    duplicated_ids = df[df['ID'].duplicated(keep=False)]
    if not duplicated_ids.empty:
        df = df.drop_duplicates(subset='ID', keep='first')
    else:
        print("No se encontraron registros duplicados en la columna ID.")
    return df

def add_prefix_to_id(df, prefix):
    df['ID'] = prefix + df['ID'].astype(str)
    return df

def transform_data(df, date_columns=[], text_columns=[], prefix=""):
    for col in date_columns:
        df[col] = df[col].apply(format_date)
    for col in text_columns:
        df[col] = standardize_text2(df[col])
    df.columns = [col.upper() for col in df.columns]
    if prefix:
        df = add_prefix_to_id(df, prefix)
    return handle_duplicates(df)

# Función para limpiar los datos
def clean_data(csv_input, csv_output, file_name, date_columns, text_columns, prefix=""):
    # Construir la ruta completa del archivo de entrada
    file_path = os.path.join(csv_input, file_name)
    
    # Extraer los datos del archivo CSV
    df = extract_data(file_path)
    
    # Limpiar los datos utilizando la transformación
    df_cleaned = transform_data(df, date_columns, text_columns, prefix)
    
    # Ordenar los datos por la columna 'ID'
    df_cleaned = df_cleaned.sort_values(by='ID')
    
    # Renombrar la columna ID
    df_cleaned = rename_id_column(df_cleaned)
    
    # Generar la ruta del archivo limpio
    cleaned_file_path = os.path.join(csv_output, file_name.replace('Sucio', 'Limpio'))
    
    # Guardar el archivo limpio
    df_cleaned.to_csv(cleaned_file_path, index=False)
    
    print(f"Archivo limpio guardado en: {cleaned_file_path}")

def clean_data_iu(csv_input, csv_output, file_name, date_columns, text_columns, prefix=""):
    # Construir la ruta completa del archivo de entrada
    file_path = os.path.join(csv_input, file_name)
    
    # Extraer los datos del archivo CSV
    df = extract_data(file_path)
    
    # Limpiar los datos utilizando la transformación
    df_cleaned = transform_data(df, date_columns, text_columns, prefix)
    
    # Ordenar los datos por la columna 'ID'
    df_cleaned = df_cleaned.sort_values(by='ID')
    
    # Renombrar la columna ID
    df_cleaned = rename_id_column(df_cleaned)

    df_cleaned = df_cleaned.rename(columns={'MANTENIMEINTOID': 'MANTENIMIENTOID'})
    
    # Generar la ruta del archivo limpio
    cleaned_file_path = os.path.join(csv_output, file_name.replace('Sucio', 'Limpio'))
    
    # Guardar el archivo limpio
    df_cleaned.to_csv(cleaned_file_path, index=False)
    
    print(f"Archivo limpio guardado en: {cleaned_file_path}")


def rename_nif_column(df):
    df = df.rename(columns={'NIF': '_id'})
    return df

def transform_users_data(df):
    df.drop_duplicates(subset='NIF', keep='first')
    df['NOMBRE'] = df['NOMBRE'].astype(str).str.upper().apply(unidecode)
    df['EMAIL'] = df['EMAIL'].fillna('DESCONOCIDO@DESCONOCIDO.com')
    df['EMAIL'] = df['EMAIL'].astype(str).str.upper().apply(unidecode)
    def format_phone_number(phone):
        phone_cleaned = re.sub(r'\D', '', phone)
        if len(phone_cleaned) >= 9: 
            return f'+34 {phone_cleaned[-9:]}'
        return phone
    df['TELEFONO'] = df['TELEFONO'].apply(format_phone_number)
    del df['Email']
    duplicated_ids = df[df['NIF'].duplicated(keep=False)]
    num_duplicates = duplicated_ids.shape[0]
    if num_duplicates > 0:
        print(f'Se encontraron {num_duplicates} registros duplicados en la columna NIF:')
        print(duplicated_ids[['NIF']])  # Mostrar los IDs duplicados
        df = df.drop_duplicates(subset='NIF', keep='first')
        print(f'Se eliminaron los duplicados. Número de registros restantes: {len(df)}')
    else:
        print('No se encontraron registros duplicados en la columna NIF.')
    return df

def clean_users_data(csv_input, csv_output):
    # Generar la ruta completa para el archivo de entrada
    users_file_path = os.path.join(csv_input, "UsuariosSucio.csv")
    
    # Extraer los datos del archivo CSV
    df = extract_data(users_file_path)
    
    # Procesar los datos
    df_cleaned = transform_users_data(df)
    df_cleaned = df_cleaned.sort_values(by='NIF')
    
    # Generar la ruta de salida para el archivo limpio
    cleaned_file_path = os.path.join(csv_output, "UsuariosLimpio.csv")
    
    # Renombrar la columna NIF y guardar el archivo procesado
    df_cleaned = rename_nif_column(df_cleaned)
    df_cleaned.to_csv(cleaned_file_path, index=False)
    
    print(f'Datos limpios guardados en {cleaned_file_path}')

# Función para limpiar los datos de meteología 24
def clean_meteo24_data(csv_input, csv_output):
    # Generar la ruta completa para el archivo de entrada
    csv_input_path = os.path.join(csv_input, "meteo24.csv")
    
    # Leer el archivo CSV
    df_meteo = pd.read_csv(csv_input_path, delimiter=';')
    df_cleaned_meteo = pd.DataFrame(columns=["ID", "FECHA", "TEMPERATURA", "PRECIPITACION", "VIENTO", "PUNTO_MUESTREO"])
    magnitudes = {89: "PRECIPITACION", 83: "TEMPERATURA", 81: "VIENTO"}
    count_id = 1
    
    # Procesar los datos
    for _, row in df_meteo.iterrows():
        magnitud = row["MAGNITUD"]
        if magnitud in magnitudes:
            año = row["ANO"]
            mes = row["MES"]
            estacion = row["PUNTO_MUESTREO"]
            for dia in range(1, 32):
                try:
                    fecha = datetime(año, mes, dia)
                except ValueError:
                    continue
                valor = row.iloc[7 + (dia - 1) * 2]
                if not ((df_cleaned_meteo["FECHA"] == fecha) & (df_cleaned_meteo["PUNTO_MUESTREO"] == str(estacion)[:8])).any():
                    new_row = {"ID": count_id, "FECHA": fecha, "PUNTO_MUESTREO": str(estacion)[:8], magnitudes[magnitud]: valor}
                    df_cleaned_meteo.loc[len(df_cleaned_meteo.index)] = new_row
                else:
                    df_cleaned_meteo.loc[(df_cleaned_meteo["FECHA"] == fecha) & (df_cleaned_meteo["PUNTO_MUESTREO"] == str(estacion)[:8]), magnitudes[magnitud]] = valor
                count_id += 1

    # Procesar la fecha y otros campos
    df_cleaned_meteo["FECHA"] = pd.to_datetime(df_cleaned_meteo["FECHA"], errors='coerce')
    df_cleaned_meteo["FECHA"] = df_cleaned_meteo["FECHA"].apply(format_date2)
    df_cleaned_meteo = df_cleaned_meteo.astype(object)
    
    for i, row in df_cleaned_meteo.iterrows():
        df_cleaned_meteo.loc[i, 'VIENTO'] = 1 if row['VIENTO'] > 10 else 0
    
    fill_missing(df_cleaned_meteo, [])
    df_cleaned_meteo = df_cleaned_meteo.rename(columns={'ID': '_id', 'PUNTO_MUESTREO': 'DISTRITO'})
    df_cleaned_meteo = delete_duplicates(df_cleaned_meteo, "_id")

    # Guardar el archivo limpio en la ruta de salida
    csv_output_path = os.path.join(csv_output, "Meteo24Limpio.csv")
    df_cleaned_meteo.to_csv(csv_output_path, index=False)
    print(f"Archivo procesado y guardado en: {csv_output_path}")

# Función para limpiar las estaciones de meteorología y código postal
def clean_estaciones_meteo_codigo_postal(csv_input, csv_output):
    # Generar la ruta completa para el archivo de entrada
    csv_input_path = os.path.join(csv_input, "estaciones_meteo_CodigoPostal.csv")
    
    # Leer el archivo CSV
    input_csv = pd.read_csv(csv_input_path, delimiter=";")
    
    # Procesar el archivo
    input_csv.at[0, "Codigo Postal"] = input_csv.at[0, "Codigo Postal"].split(',')[0]
    input_csv = input_csv.rename(columns={'ID': '_id'})
    
    # Guardar el archivo limpio
    csv_output_path = os.path.join(csv_output, "EstacionesMeteoCodigoPostalLimpio.csv")
    input_csv.to_csv(csv_output_path, index=False)
    print(f"Archivo procesado y guardado en: {csv_output_path}")

def change_id_area(csv_input, csv_output):
    # Generar la ruta completa para el archivo de entrada
    areas_file_path = os.path.join(csv_output, "AreasLimpio.csv")
    
    # Extraer los datos del archivo CSV
    df = extract_data(areas_file_path)
    
    # Renombrar la columna ID
    df = rename_id_column(df)
    
    # Generar la ruta de salida para el archivo procesado
    cleaned_file_path = os.path.join(csv_output, "AreasLimpio.csv")
    
    # Guardar el archivo procesado
    df.to_csv(cleaned_file_path, index=False)
    
    print(f"Archivo de áreas procesado y guardado en: {cleaned_file_path}")

def main():
    if len(sys.argv) != 3:
        print(f'[ERROR] Uso: python3 {sys.argv[0]} <directorio de entrada> <directorio de salida>')
        return
    
    # Obtener los directorios de entrada y salida desde los argumentos
    input_path = sys.argv[1]
    output_path = sys.argv[2]
    
    # Crear el directorio de salida si no existe
    if not os.path.exists(output_path):
        print(f'[INFO] Creando directorio de salida: {output_path}')
        os.makedirs(output_path)
    
    # Llamar a las funciones de limpieza de datos
    clean_areas_data(input_path, output_path)
    clean_mantenimiento_data(input_path, output_path)
    clean_juegos_data(input_path, output_path)
    clean_data_iu(input_path, output_path, 'IncidenciasUsuariosSucio.csv', 
               date_columns=['FECHA_REPORTE'], 
               text_columns=['TIPO_INCIDENCIA', 'ESTADO'],
               prefix='INC-')
    
    clean_data(input_path, output_path, 'EncuestasSatisfaccionSucio.csv', 
               date_columns=['FECHA'], 
               text_columns=['COMENTARIOS'],
               prefix='ES-')
    
    clean_data(input_path, output_path, 'IncidentesSeguridadSucio.csv', 
               date_columns=['FECHA_REPORTE'], 
               text_columns=['TIPO_INCIDENTE', 'GRAVEDAD'],
               prefix='IS-')
    
    clean_users_data(input_path, output_path)
    clean_meteo24_data(input_path, output_path)
    clean_estaciones_meteo_codigo_postal(input_path, output_path)
    change_id_area(input_path, output_path)

if __name__ == "__main__":
    main()
