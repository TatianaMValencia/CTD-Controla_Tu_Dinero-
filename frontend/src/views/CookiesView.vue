<template>
  <main class="page">
    <h2>Política de cookies</h2>
    <p class="sub">CTD guarda datos solo en tu dispositivo. No usamos rastreadores ni publicidad.</p>
    <div class="card" style="margin-top: 12px; display: grid; gap: 10px">
      <div><strong>Sesión</strong><p class="sub">Tokens de acceso en almacenamiento local para mantenerte dentro de la app. Se borran al cerrar sesión.</p></div>
      <hr class="divider" />
      <div><strong>Preferencias</strong><p class="sub">Tema claro/oscuro, inicio de semana y decisiones como este aviso.</p></div>
      <hr class="divider" />
      <div><strong>Sin terceros</strong><p class="sub">No hay analítica ni cookies de terceros en esta versión.</p></div>
    </div>
    <button class="btn-primary" style="margin-top: 16px" @click="$router.back()">Volver</button>
  </main>
</template>
