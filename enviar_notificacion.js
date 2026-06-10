// enviar_notificacion.js
// Uso: node enviar_notificacion.js "Titulo" "Mensaje"

const webpush = require('web-push');
const { createClient } = require('@supabase/supabase-js');

const VAPID_PUBLIC  = 'BHEg1OHTNkWaTeZaxN4fm0GUP1eChkUZlx7PmmzMKGIGlZFQtF9NeJ60KG_wHs8Gl-7FsQYzlshOD5KFYNhhAuk';
const VAPID_PRIVATE = 'pu2BfpkjneMJxspYdrFi_cz-csTWcQBfXevuuERFIkQ';
const SUPABASE_URL  = 'https://ovjpbdlzfvsgeheuixqh.supabase.co';
const SUPABASE_KEY  = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im92anBiZGx6ZnZzZ2VoZXVpeHFoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzgwMjM4ODYsImV4cCI6MjA5MzU5OTg4Nn0.yOOEXr4UFEvIUKb1pn8ixyjwpxGbfTyYnHQhBT4N6BM';

webpush.setVapidDetails('mailto:jamiljuez@gmail.com', VAPID_PUBLIC, VAPID_PRIVATE);
const supabase = createClient(SUPABASE_URL, SUPABASE_KEY);

async function enviar(titulo, mensaje) {
  console.log(`\n📲 Enviando notificación: "${titulo}"`);
  
  const { data: tokens, error } = await supabase.from('push_tokens').select('*');
  if (error) { console.error('Error:', error); return; }
  console.log(`📋 ${tokens.length} usuarios registrados`);
  
  let exitosos = 0, fallidos = 0;

  for (const t of tokens) {
    try {
      const sub = JSON.parse(t.token);
      await webpush.sendNotification(sub, JSON.stringify({
        title: titulo,
        body: mensaje,
        url: 'https://appjay.netlify.app'
      }));
      console.log(`  ✅ ${t.email} (${t.plataforma})`);
      exitosos++;
    } catch(e) {
      console.log(`  ❌ ${t.email}: ${e.message}`);
      // Token invalido o expirado — borrarlo automaticamente
      if (e.statusCode === 404 || e.statusCode === 410) {
        await supabase.from('push_tokens').delete().eq('email', t.email);
        console.log(`     🗑️ Token eliminado (inválido)`);
      }
      fallidos++;
    }
  }

  console.log(`\n✅ Enviadas: ${exitosos} | ❌ Fallidas: ${fallidos}`);
}

const titulo  = process.argv[2] || 'Jay App';
const mensaje = process.argv[3] || 'Tienes una notificación nueva';
enviar(titulo, mensaje).then(() => process.exit(0));
