"""
Sistema Experto para el Diagnóstico de Viabilidad de Lanzamiento Espacial.
Este módulo contiene la lógica de negocio, las plantillas y el motor de reglas
basado en CLIPS para determinar el estado de un lanzamiento.
"""
import clips

def crear_entorno():
    """
        Inicializa el entorno CLIPS, define las plantillas de hechos y las reglas de producción.

        Returns:
            tuple: (env, disparadas) Donde 'env' es el objeto Environment de CLIPS
                   y 'disparadas' es la lista que almacenará el historial de reglas.
        """
    # Creamos un entorno CLIPS
    env = clips.Environment()

    # Lista donde se guardarán las reglas disparadas
    disparadas = []

    # Función para registrar cada regla que se dispara
    def regla_disparada(nombre, hecho, detalle):
        # Guardamos un diccionario con toda la información
        disparadas.append({
            "regla": nombre,
            "hecho": hecho,
            "detalle": detalle
        })

    # Registramos la función en CLIPS para poder llamarla desde reglas
    env.define_function(regla_disparada, "regla_disparada")

    # PLANTILLA LANZAMIENTO
    # Definimos los slots que representan el estado del lanzamiento
    env.build("""
    (deftemplate lanzamiento
        (slot nivel_combustible (type INTEGER))
        (slot motor_principal (type SYMBOL) (allowed-values yes no))
        (slot presion_tanques (type SYMBOL) (allowed-values ok fail))
        (slot sistema_navegacion (type SYMBOL) (allowed-values ok fail))
        (slot sistema_comunicacion (type SYMBOL) (allowed-values ok fail))
        (slot sistema_electrico (type SYMBOL) (allowed-values ok fail))
        (slot software_control (type SYMBOL) (allowed-values ok fail))
        (slot prob_precipitaciones (type INTEGER))
        (slot estado_clima (type SYMBOL) (allowed-values despejado nublado))
        (slot sensores (type SYMBOL) (allowed-values ok fail))
        (slot aerodinamica (type SYMBOL) (allowed-values ok fail))
    )
    """)

    # PLANTILLA CONCLUSIÓN
    # Definimos cómo se estructuran las conclusiones del sistema experto
    env.build("""
    (deftemplate conclusion
        (slot tipo (type SYMBOL))
        (slot detalle (type STRING))
    )
    """)

    # FUNCIÓN AUXILIAR PARA ABORTAR
    # Esta función decide si el lanzamiento debe abortarse basándose en criterios técnicos
    def abort_launch(c, m, p, n, co, e, s, pr, cl, se, ae):
        return (
                c <= 95 or m == "no" or p == "fail" or n == "fail" or
                co == "fail" or e == "fail" or s == "fail" or
                se == "fail" or ae == "fail" or
                pr >= 60 or (pr >= 30 and cl == "nublado") or
                (co == "fail" and s == "fail")
        )

    # Registramos la función en CLIPS
    env.define_function(abort_launch, name="abort_launch")

    # REGLAS
    # Combustible insuficiente
    env.build("""
    (defrule combustible_bajo
        (declare (salience 10))
        (lanzamiento (nivel_combustible ?n))
        (test (<= ?n 95))
        =>
        (regla_disparada "combustible_bajo"(str-cat "nivel_combustible = " ?n) "Combustible insuficiente")
        (assert (conclusion (tipo critico) (detalle "Combustible insuficiente"))))
    """)

    # Combustible cercano al mínimo
    env.build("""
    (defrule combustible_alerta
        (declare (salience 5))
        (lanzamiento (nivel_combustible ?n))
        (test (and (> ?n 95) (<= ?n 99)))
        (not (conclusion (tipo critico)))
        =>
        (regla_disparada "combustible_alerta" (str-cat "nivel_combustible = " ?n) "Se recomienda retraso de 2 horas para lanzamiento.")
        (assert (conclusion (tipo retraso) (detalle "Retraso de 2 horas, repostaje de seguridad en curso..."))))
    """)

    # Fallo del motor principal
    env.build("""
    (defrule fallo_motor
        (declare (salience 10))
        (lanzamiento (motor_principal no))
        =>
        (regla_disparada "fallo_motor" "motor_principal = no" "Fallo del motor principal")
        (assert (conclusion (tipo critico) (detalle "Fallo del motor principal"))))
    """)

    # Fallo en la presión de los tanques
    env.build("""
    (defrule fallo_presion
        (declare (salience 10))
        (lanzamiento (presion_tanques fail))
        =>
        (regla_disparada "fallo_presion" "presion_tanques = fail" "Presión de tanques incorrecta")
        (assert (conclusion (tipo critico) (detalle "Presión de tanques incorrecta"))))
    """)

    # Fallo en navegación
    env.build("""
    (defrule fallo_navegacion
        (declare (salience 10))
        (lanzamiento (sistema_navegacion fail))
        =>
        (regla_disparada "fallo_navegacion" "sistema_navegacion = fail" "Sistema de navegación fallando")
        (assert (conclusion (tipo critico) (detalle "Sistema de navegación fallando"))))
    """)

    # Fallo en comunicación
    env.build("""
    (defrule fallo_comunicacion
        (declare (salience 10))
        (lanzamiento (sistema_comunicacion fail))
        =>
        (regla_disparada "fallo_comunicacion" "sistema_comunicacion = fail" "Sistema de comunicación no operativo")
        (assert (conclusion (tipo critico) (detalle "Sistema de comunicación no operativo"))))
    """)

    # Fallo en sistema eléctrico
    env.build("""
    (defrule fallo_electrico
        (declare (salience 10))
        (lanzamiento (sistema_electrico fail))
        =>
        (regla_disparada "fallo_electrico" "sistema_electrico = fail" "Fallo en sistema eléctrico")
        (assert (conclusion (tipo critico) (detalle "Fallo en sistema eléctrico"))))
    """)

    # Fallo en software de control
    env.build("""
    (defrule fallo_software
        (declare (salience 10))
        (lanzamiento (software_control fail))
        =>
        (regla_disparada "fallo_software" "software_control = fail" "Fallo en software de control")
        (assert (conclusion (tipo critico) (detalle "Fallo en software de control"))))
    """)

    # Riesgo climático
    env.build("""
    (defrule riesgo_climatico
        (declare (salience 10))
        (lanzamiento (prob_precipitaciones ?p) (estado_clima nublado))
        (test (>= ?p 30))
        =>
        (regla_disparada "riesgo_climatico" (str-cat "prob_precipitaciones = " ?p) "Riesgo meteorológico elevado")
        (assert (conclusion (tipo critico) (detalle "Riesgo meteorológico elevado"))))
    """)

    # Fallo en sensores
    env.build("""
    (defrule fallo_sensores
        (declare (salience 10))
        (lanzamiento (sensores fail))
        =>
        (regla_disparada "fallo_sensores" "sensores = fail" "Fallo en sensores del sistema")
        (assert (conclusion (tipo critico) (detalle "Fallo en sensores del sistema"))))
    """)

    # Fallo múltiple de sistemas electrónicos
    env.build("""
    (defrule fallo_electronico_multiple
        (declare (salience 10))
        (lanzamiento (sistema_navegacion fail) 
                     (sistema_comunicacion fail) 
                     (sistema_electrico fail) 
                     (sensores fail))
        =>
        (regla_disparada "fallo_electronico_multiple"
                         "sistema_navegacion = fail, sistema_comunicacion = fail, sistema_electrico = fail, sensores = fail"
                         "Fallo crítico en sistemas electrónicos/consola")
        (assert (conclusion (tipo critico)
                            (detalle "Fallo múltiple en sistemas electrónicos: posible cancelación del lanzamiento"))))
    """)

    # Fallo de combustión (motor + presión)
    env.build("""
    (defrule fallo_combustion
        (declare (salience 10))
        (lanzamiento (motor_principal no) 
                     (presion_tanques fail))
        =>
        (regla_disparada "fallo_combustion"
                         "motor_principal = no, presion_tanques = fail"
                         "Problema crítico de combustión detectado")
        (assert (conclusion (tipo critico)
                            (detalle "Fallo de combustión: motor principal y presión de tanques afectados"))))
    """)

    # Fallo en aerodinámica
    env.build("""
    (defrule fallo_aerodinamica
        (declare (salience 10))
        (lanzamiento (aerodinamica fail))
        =>
        (regla_disparada "fallo_aerodinamica"
                         "aerodinamica = fail"
                         "Problema crítico en sistemas de aerodinámica")
        (assert (conclusion (tipo critico)
                            (detalle "Fallo en aerodinámica, posible cancelación del lanzamiento"))))
    """)

    # Riesgo de Tormenta Eléctrica (Clima + Sistema Eléctrico)
    env.build("""
            (defrule riesgo_tormenta_electrica
                (declare (salience 15))
                (lanzamiento (prob_precipitaciones ?p) (sistema_electrico ?e))
                (test (and (>= ?p 40) (eq ?e fail)))
                =>
                (regla_disparada "riesgo_tormenta_electrica" 
                                 (str-cat "precipitaciones = " ?p "% + fallo eléctrico") 
                                 "Riesgo extremo de impacto por rayo y fallo total")
                (assert (conclusion (tipo critico) 
                                    (detalle "Peligro de tormenta eléctrica, integridad del vehículo en riesgo"))))
            """)

    # Degradación General del Sistema (Fallo múltiple no crítico individualmente)
    # Si fallan al menos dos sistemas de soporte, aunque no sea aborto inmediato por cada uno
    env.build("""
            (defrule degradacion_sistemas_soporte
                (declare (salience 12))
                (lanzamiento (sistema_comunicacion fail) (software_control fail))
                =>
                (regla_disparada "degradacion_sistemas_soporte" 
                                 "comunicación = fail, software = fail" 
                                 "Degradación crítica de la capacidad de respuesta")
                (assert (conclusion (tipo critico) 
                                    (detalle "Degradación general, múltiples fallos en sistemas de soporte detectados"))))
            """)

    # Revisión global de abort
    env.build("""
    (defrule revision_abort
        (declare (salience 0))
        (lanzamiento
            (nivel_combustible ?c)
            (motor_principal ?m)
            (presion_tanques ?p)
            (sistema_navegacion ?n)
            (sistema_comunicacion ?co)
            (sistema_electrico ?e)
            (software_control ?s)
            (prob_precipitaciones ?pr)
            (estado_clima ?cl)
            (sensores ?se)
            (aerodinamica ?ae))
        (test (abort_launch ?c ?m ?p ?n ?co ?e ?s ?pr ?cl ?se ?ae))
        =>
        (regla_disparada "revision_abort" (str-cat "Estado crítico detectado") "Aborto recomendado por el sistema experto")
        (assert (conclusion (tipo critico) (detalle "Aborto recomendado por el sistema experto"))))
    """)

    # Todo correcto, sin hechos críticos
    env.build("""
    (defrule lanzamiento_ok
        (not (conclusion))
        =>
        (regla_disparada "lanzamiento_ok" "ningún hecho crítico" "Todo correcto, listo para el lanzamiento")
        (assert (conclusion (tipo info) (detalle "Todo correcto, listo para el lanzamiento"))))
    """)

    return env, disparadas


def inferir_recomendacion(env, disparadas, nivel_combustible, motor_principal, presion_tanques, sistema_navegacion, sistema_comunicacion, sistema_electrico, software_control, prob_precipitaciones, estado_clima, sensores, aerodinamica):
    """
        Realiza la inferencia lógica basándose en los parámetros de entrada.

        Args:
            env (clips.Environment): El entorno CLIPS configurado.
            disparadas (list): Lista para almacenar la trazabilidad de las reglas.
            ... (resto de parámetros de telemetría) ...

        Returns:
            tuple: (texto_conclusion, lista_disparadas)
        """
    # Reseteamos el entorno para cada inferencia
    env.reset()

    # Creamos el hecho de lanzamiento con todos los slots
    hecho_lanzamiento = f"""
    (lanzamiento
        (nivel_combustible {nivel_combustible})
        (motor_principal {motor_principal})
        (presion_tanques {presion_tanques})
        (sistema_navegacion {sistema_navegacion})
        (sistema_comunicacion {sistema_comunicacion})
        (sistema_electrico {sistema_electrico})
        (software_control {software_control})
        (prob_precipitaciones {prob_precipitaciones})
        (estado_clima {estado_clima})
        (sensores {sensores})
        (aerodinamica {aerodinamica}) 
    )
    """

    # Insertamos el hecho en CLIPS
    env.assert_string(hecho_lanzamiento)

    # Limpiamos la lista de reglas disparadas para esta inferencia
    disparadas.clear()

    # Ejecutamos todas las reglas
    env.run()

    # Recolectamos todas las conclusiones
    conclusiones = []
    for fact in env.facts():
        if fact.template.name == "conclusion":
            conclusiones.append(f"{fact['tipo'].upper()}: {fact['detalle']}")

    # Retornamos la concatenación de conclusiones y la lista de reglas disparadas
    return "\n".join(conclusiones) if conclusiones else "No se ha podido generar una conclusión final", disparadas