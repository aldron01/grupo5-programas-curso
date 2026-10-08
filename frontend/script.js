document.addEventListener("DOMContentLoaded", () => {
  // ELEMENTOS PRINCIPALES
  const rol = document.getElementById("rol");
  const estadoPrograma = document.getElementById("estado-programa");
  const numeroVersion = document.getElementById("numero-version");
  const estadoGuardado = document.getElementById("estado-guardado");

  // Responsables
  const docente = document.getElementById("docente");
  const coordinador = document.getElementById("coordinador");
  const decano = document.getElementById("decano");

  // Botones
  const guardar = document.getElementById("guardar-seccion");
  const crearVersion = document.getElementById("crear-version");
  const enviarRevision = document.getElementById("enviar-revision");
  const devolver = document.getElementById("devolver");
  const aprobar = document.getElementById("aprobar");
  const autorizar = document.getElementById("autorizar");
  const vistaPreviaPdf = document.getElementById("vista-previa-pdf");
  const imprimirPdf = document.getElementById("imprimir-pdf");
  const cerrarVistaPrevia = document.getElementById("cerrar-vista-previa");
  const documentoPdf = document.getElementById("documento-pdf");
  const cancelar = document.getElementById("cancelar-cambios");

  // VARIABLES DEL SISTEMA

  let estado = "borrador";
  let version = 1;

  // SECCIONES

  const enlacesSecciones = document.querySelectorAll(".nav-secciones a");
  const secciones = document.querySelectorAll(".seccion");

  enlacesSecciones.forEach((enlace) => {
    enlace.addEventListener("click", (evento) => {
      evento.preventDefault();

      const id = enlace.getAttribute("href").substring(1);

      // Quitar activa de todos
      enlacesSecciones.forEach((item) => {
        item.classList.remove("activa");
      });

      secciones.forEach((seccion) => {
        seccion.classList.remove("activa");
      });

      // Activar seleccionada
      enlace.classList.add("activa");

      const seccion = document.getElementById(id);

      if (seccion) {
        seccion.classList.add("activa");
      }
    });
  });

  // CAMBIO DE ROL

  rol.addEventListener("change", () => {
    actualizarInterfaz();
    actualizarEdicionResponsables();

    mostrarMensaje("Rol cambiado a: " + obtenerNombreRol());
  });

  // GUARDAR BORRADOR

  guardar.addEventListener("click", () => {
    if (estado !== "borrador" && estado !== "devuelto") {
      alert("El programa no puede modificarse " + "en este estado.");

      return;
    }

    estado = "borrador";

    actualizarEstado();

    mostrarMensaje("Borrador guardado correctamente.");
  });

  // ENVIAR A REVISIÓN

  enviarRevision.addEventListener("click", () => {
    if (rol.value !== "docente") {
      alert("Solo el docente puede enviar " + "el programa a revisión.");

      return;
    }

    if (!docente.value.trim()) {
      alert("Escribe el nombre del docente antes de enviar a revisión.");

      return;
    }

    estado = "en-revision";
    actualizarEstado();
    mostrarMensaje("Programa enviado al coordinador para revisión.");
  });

  // DEVOLVER AL DOCENTE
  devolver.addEventListener("click", () => {
    if (rol.value !== "coordinador") {
      alert("Solo el coordinador puede devolver " + "el programa.");

      return;
    }

    if (estado !== "en-revision") {
      alert("El programa no está en revisión.");

      return;
    }

    if (!coordinador.value.trim()) {
      alert("Escribe el nombre del coordinador antes de revisar el programa.");

      return;
    }

    estado = "devuelto";
    actualizarEstado();
    mostrarMensaje("El programa fue devuelto al docente.");
  });

  // APROBAR

  aprobar.addEventListener("click", () => {
    if (rol.value !== "coordinador") {
      alert("Solo el coordinador puede aprobar " + "el programa.");
      return;
    }

    if (estado !== "en-revision") {
      alert("El programa debe estar en revisión.");
      return;
    }

    if (!coordinador.value.trim()) {
      alert("Escribe el nombre del coordinador antes de revisar el programa.");

      return;
    }

    estado = "aprobado";

    actualizarEstado();

    mostrarMensaje("Programa aprobado y enviado al decano.");
  });

  // AUTORIZAR

  autorizar.addEventListener("click", () => {
    if (rol.value !== "decano") {
      alert("Solo el decano puede autorizar " + "una versión.");

      return;
    }

    if (estado !== "aprobado") {
      alert("El programa debe estar aprobado " + "antes de autorizarlo.");

      return;
    }

    if (!decano.value.trim()) {
      alert("Escribe el nombre del decano antes de autorizar la versión.");

      return;
    }

    estado = "autorizado";

    actualizarEstado();

    mostrarMensaje("La versión fue autorizada y ahora es la versión vigente.");
  });

  // VISTA PREVIA E IMPRESIÓN PDF

  vistaPreviaPdf.addEventListener("click", () => {
    construirDocumentoPdf();
    documentoPdf.hidden = false;
    document.body.classList.add("vista-previa-pdf");
    actualizarInterfaz();
    mostrarMensaje(
      "Vista previa del programa. Puedes imprimirlo o volver al editor.",
    );
  });

  imprimirPdf.addEventListener("click", () => {
    window.print();
  });

  cerrarVistaPrevia.addEventListener("click", () => {
    document.body.classList.remove("vista-previa-pdf");
    documentoPdf.hidden = true;
    actualizarInterfaz();
    mostrarMensaje("Vista previa cerrada.");
  });

  function crearElemento(etiqueta, clase, texto) {
    const elemento = document.createElement(etiqueta);
    if (clase) elemento.className = clase;
    if (texto !== undefined) elemento.textContent = texto;
    return elemento;
  }

  function construirDocumentoPdf() {
    documentoPdf.replaceChildren();

    const asignatura = document.querySelector("#asignatura").value.trim();
    const facultad = document.querySelector("#facultad").value.trim();
    const encabezado = crearElemento("header", "pdf-encabezado");
    const institucion = crearElemento("div", "pdf-institucion");
    institucion.append(
      crearElemento("h2", "", "UNIVERSIDAD DA VINCI DE GUATEMALA"),
      crearElemento("p", "", facultad || "Facultad académica"),
    );

    const metadatos = crearElemento("div", "pdf-metadatos");
    metadatos.append(
      crearElemento("p", "", `Versión: ${version}`),
      crearElemento("p", "", `Fecha: ${new Date().toLocaleDateString("es-GT")}`),
      crearElemento("p", "", `Estado: ${estadoPrograma.textContent.trim()}`),
    );
    encabezado.append(institucion, metadatos);
    documentoPdf.append(
      encabezado,
      crearElemento("h1", "pdf-titulo", "PROGRAMA DE CURSO"),
      crearElemento("p", "pdf-asignatura", asignatura),
      crearElemento(
        "p",
        "pdf-leyenda",
        estado === "autorizado"
          ? "Documento autorizado"
          : "Documento de prueba - sin autorización vigente",
      ),
    );

    secciones.forEach((seccion) => {
      const copia = seccion.cloneNode(true);
      copia.classList.remove("activa");
      copia.classList.add("pdf-seccion");
      copia.removeAttribute("id");
      copia.querySelectorAll("[id]").forEach((elemento) => {
        elemento.removeAttribute("id");
      });
      copia.querySelectorAll("label[for]").forEach((etiqueta) => {
        etiqueta.removeAttribute("for");
      });
      copia.querySelectorAll("input, textarea, select").forEach((control) => {
        let valor = "";
        if (control instanceof HTMLSelectElement) {
          valor = control.selectedOptions[0]?.textContent.trim() || "";
        } else {
          valor = control.value;
        }
        control.replaceWith(crearElemento("span", "pdf-valor", valor));
      });
      documentoPdf.append(copia);
    });

    const autorizacion = crearElemento("section", "pdf-seccion");
    autorizacion.append(crearElemento("h3", "", "Autorización"));
    const tablaAutorizacion = crearElemento("table", "pdf-tabla-autorizacion");
    const cuerpoAutorizacion = crearElemento("tbody");
    [
      ["Elaborado por", docente.value.trim()],
      ["Revisor", coordinador.value.trim()],
      ["Autoridad", decano.value.trim()],
      ["Fecha", new Date().toLocaleDateString("es-GT")],
    ].forEach(([campo, valor]) => {
      const fila = crearElemento("tr");
      fila.append(
        crearElemento("th", "", campo),
        crearElemento("td", "", valor),
      );
      cuerpoAutorizacion.append(fila);
    });
    tablaAutorizacion.append(cuerpoAutorizacion);
    autorizacion.append(tablaAutorizacion);
    documentoPdf.append(autorizacion);

    const firmas = crearElemento("footer", "pdf-firmas");
    ["Elaborado por", "Revisor", "Autoridad"].forEach((cargo) => {
      const firma = crearElemento("div", "pdf-firma");
      firma.append(
        crearElemento("div", "pdf-linea-firma"),
        crearElemento("span", "", cargo),
      );
      firmas.append(firma);
    });
    documentoPdf.append(firmas);
  }

  // CREAR NUEVA VERSIÓN

  crearVersion.addEventListener("click", () => {
    if (rol.value !== "decano") {
      alert("Solo el decano puede crear una nueva versión.");
      return;
    }

    if (estado !== "autorizado") {
      alert(
        "Solo puedes crear una nueva versión " +
          "a partir de una versión autorizada.",
      );

      return;
    }

    version++;
    estado = "borrador";
    actualizarEstado();
    mostrarMensaje("Se creó la versión " + version + " como nuevo borrador.");
  });

  // CANCELAR CAMBIOS

  cancelar.addEventListener("click", () => {
    const confirmar = confirm("¿Deseas cancelar los cambios realizados?");
    if (!confirmar) {
      return;
    }
    mostrarMensaje("Cambios cancelados.");
  });

  // ACTUALIZAR ESTADO
  function actualizarEstado() {
    estadoPrograma.className = "udv-badge";

    switch (estado) {
      case "borrador":
        estadoPrograma.textContent = "BORRADOR";
        estadoPrograma.classList.add("badge-draft");

        break;

      case "en-revision":
        estadoPrograma.textContent = "EN REVISIÓN";
        estadoPrograma.classList.add("badge-under-review");

        break;

      case "devuelto":
        estadoPrograma.textContent = "DEVUELTO";
        estadoPrograma.classList.add("badge-returned");

        break;

      case "aprobado":
        estadoPrograma.textContent = "APROBADO";
        estadoPrograma.classList.add("badge-approved");

        break;

      case "autorizado":
        estadoPrograma.textContent = "AUTORIZADO";
        estadoPrograma.classList.add("badge-authorized");
        break;
    }
    numeroVersion.textContent = "Versión " + version;

    actualizarInterfaz();
    actualizarEdicionResponsables();
  }

  function actualizarEdicionResponsables() {
    docente.readOnly = !(
      rol.value === "docente" &&
      (estado === "borrador" || estado === "devuelto")
    );
    coordinador.readOnly = !(
      rol.value === "coordinador" && estado === "en-revision"
    );
    decano.readOnly = !(rol.value === "decano" && estado === "aprobado");
  }
  // MOSTRAR / OCULTAR BOTONES
  function actualizarInterfaz() {
    vistaPreviaPdf.style.display = "inline-block";
    imprimirPdf.style.display = "none";
    cerrarVistaPrevia.style.display = "none";

    // Ocultar todos primero
    guardar.style.display = "none";
    crearVersion.style.display = "none";
    enviarRevision.style.display = "none";
    devolver.style.display = "none";
    aprobar.style.display = "none";
    autorizar.style.display = "none";
    cancelar.style.display = "none";

    if (document.body.classList.contains("vista-previa-pdf")) {
      vistaPreviaPdf.style.display = "none";
      imprimirPdf.style.display = "inline-block";
      cerrarVistaPrevia.style.display = "inline-block";
      return;
    }
    // DOCENTE
    if (rol.value === "docente") {
      if (estado === "borrador" || estado === "devuelto") {
        guardar.style.display = "inline-block";

        enviarRevision.style.display = "inline-block";

        cancelar.style.display = "inline-block";
      }
    }
    // COORDINADOR
    if (rol.value === "coordinador") {
      if (estado === "en-revision") {
        devolver.style.display = "inline-block";

        aprobar.style.display = "inline-block";
      }
    }
    // DECANO
    if (rol.value === "decano") {
      if (estado === "aprobado") {
        autorizar.style.display = "inline-block";
      }
      if (estado === "autorizado") {
        crearVersion.style.display = "inline-block";
      }
    }
  }
  // NOMBRE DEL ROL
  function obtenerNombreRol() {
    switch (rol.value) {
      case "docente":
        return "Docente";

      case "coordinador":
        return "Coordinador";

      case "decano":
        return "Decano";

      default:
        return "Desconocido";
    }
  }
  // MENSAJE DE GUARDADO

  function mostrarMensaje(mensaje) {
    estadoGuardado.textContent = mensaje;

    estadoGuardado.style.opacity = "1";

    setTimeout(() => {
      estadoGuardado.textContent = "Cambios guardados localmente";
    }, 3000);
  }
  // INICIAR SISTEMA

  actualizarEstado();
  actualizarEdicionResponsables();
});
