/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./flask_app/templates/**/*.html", "./public/myJS/**/*.js"],
  theme: {
    extend: {
      colors: {
        "brand-blue": "#1d4ed8",
        "brand-aqua": "#22d3ee",
        "brand-deep": "#0f172a"
      },
      fontFamily: {
        display: ["\"Funnel Display\"", "ui-sans-serif", "system-ui"],
        body: ["\"Open Sans\"", "ui-sans-serif", "system-ui"]
      }
    }
  },
  plugins: []
};
