/* eslint-env node */
module.exports = {
  root: true,
  env: { browser: true, es2020: true },
  extends: [
    "eslint:recommended",
    "plugin:vue/vue3-recommended",
    "@vue/eslint-config-prettier",
    "@vue/eslint-config-typescript",
  ],
  ignorePatterns: ["dist", "*.cjs"],
  rules: {
    "vue/multi-word-component-names": "off",
  },
}
