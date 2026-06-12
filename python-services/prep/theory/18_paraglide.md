 Paraglide (@inlang/paraglide-js) is an i18n (internationalization) library — it lets your app speak multiple languages. In your case: English
  (en) and German (de).

  It's different from most i18n libraries because it's compile-time, not runtime — it generates static JS functions at build time instead of
  loading JSON at runtime.

  How it works — the pipeline

  messages/en.json + messages/de.json
           ↓  (paraglideVitePlugin at build time)
  src/lib/paraglide/runtime.js   ← generated
  src/lib/paraglide/messages.js  ← generated
           ↓
  app imports functions from there

  vite.config.ts runs the plugin at build time:
  paraglideVitePlugin({ project: './project.inlang', outdir: './src/lib/paraglide' })

  project.inlang/settings.json declares:
  - baseLocale: "en" — English is the default
  - locales: ["en", "de"] — supported languages
  - where message files live: ./messages/{locale}.json
