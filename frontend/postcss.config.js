/**
 * @type {import('postcss-load-config').Config}
 */
module.exports = {
  // Use the plugin object syntax, which explicitly maps the package name
  // to an object of options (which is empty in this case: {}).
  plugins: {
    "@tailwindcss/postcss": {},
    autoprefixer: {},
  },
};
